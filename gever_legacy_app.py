import threading
import customtkinter as ctk

from gever.brain import GeversBrain
from gever.listen import GeversListener
from gever.voice import GeversVoice


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GeversApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GEVER")
        self.geometry("900x650")
        self.minsize(760, 560)

        self.brain = GeversBrain()
        self.voice = GeversVoice()
        self.listener = GeversListener()

        self.is_busy = False

        self._build_ui()

        self.add_message(
            "GEVER",
            "Sistema iniciado. Estoy listo."
        )

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, height=90)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="GEVER",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.grid(row=0, column=0, pady=(15, 0))

        self.status_label = ctk.CTkLabel(
            header,
            text="● SISTEMA ACTIVO",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_label.grid(row=1, column=0, pady=(2, 12))

        self.chat_box = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(size=15)
        )
        self.chat_box.grid(
            row=1,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="nsew"
        )
        self.chat_box.configure(state="disabled")

        bottom = ctk.CTkFrame(self)
        bottom.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="ew"
        )
        bottom.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Escribe un mensaje para GEVER...",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.input_entry.grid(
            row=0,
            column=0,
            padx=(10, 6),
            pady=10,
            sticky="ew"
        )
        self.input_entry.bind("<Return>", self.send_text_event)

        self.send_button = ctk.CTkButton(
            bottom,
            text="ENVIAR",
            width=100,
            height=45,
            command=self.send_text
        )
        self.send_button.grid(row=0, column=1, padx=6, pady=10)

        self.mic_button = ctk.CTkButton(
            bottom,
            text="🎙 HABLAR",
            width=120,
            height=45,
            command=self.start_listening
        )
        self.mic_button.grid(row=0, column=2, padx=(6, 10), pady=10)

    def set_status(self, text):
        self.status_label.configure(text=text)

    def add_message(self, sender, message):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n{sender}\n")
        self.chat_box.insert("end", f"{message}\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def send_text_event(self, event):
        self.send_text()

    def send_text(self):
        if self.is_busy:
            return

        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, "end")
        self.add_message("TÚ", text)
        self.process_message(text)

    def process_message(self, text):
        self.is_busy = True
        self.send_button.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        self.set_status("● GEVER ESTÁ PENSANDO")

        thread = threading.Thread(
            target=self._process_message_thread,
            args=(text,),
            daemon=True
        )
        thread.start()

    def _process_message_thread(self, text):
        try:
            answer = self.brain.think(text)
            self.after(0, lambda: self._show_answer(answer))
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))

    def _show_answer(self, answer):
        self.add_message("GEVER", answer)
        self.set_status("● GEVER ESTÁ HABLANDO")

        speech_thread = threading.Thread(
            target=self._speak_thread,
            args=(answer,),
            daemon=True
        )
        speech_thread.start()

    def _speak_thread(self, answer):
        try:
            self.voice.speak(answer)
        finally:
            self.after(0, self._finish_interaction)

    def _finish_interaction(self):
        self.is_busy = False
        self.send_button.configure(state="normal")
        self.mic_button.configure(state="normal")
        self.set_status("● SISTEMA ACTIVO")

    def start_listening(self):
        if self.is_busy:
            return

        self.is_busy = True
        self.send_button.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        self.set_status("● ESCUCHANDO")

        thread = threading.Thread(
            target=self._listen_thread,
            daemon=True
        )
        thread.start()

    def _listen_thread(self):
        try:
            text = self.listener.listen()

            if not text:
                self.after(0, self._no_speech)
                return

            if text.startswith("ERROR_RECONOCIMIENTO:"):
                self.after(0, lambda: self._show_error(text))
                return

            self.after(0, lambda: self._voice_text_ready(text))
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))

    def _voice_text_ready(self, text):
        self.add_message("TÚ", text)
        self.is_busy = False
        self.process_message(text)

    def _no_speech(self):
        self.add_message("GEVER", "No detecté ninguna frase.")
        self._finish_interaction()

    def _show_error(self, error):
        self.add_message("SISTEMA", f"Error: {error}")
        self._finish_interaction()


if __name__ == "__main__":
    app = GeversApp()
    app.mainloop()
