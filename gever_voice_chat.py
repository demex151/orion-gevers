from gever.brain import GeversBrain
from gever.listen import GeversListener
from gever.voice import GeversVoice


def normalize_command(text):
    return (
        text.lower()
        .strip()
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .replace("¿", "")
        .replace("¡", "")
    )


def is_exit_command(text):
    normalized = normalize_command(text)

    return normalized in {
        "salir",
        "cierra",
        "cerrar",
        "termina",
        "terminar",
        "adios",
        "adiós",
        "cierra el programa",
        "sal del programa",
        "termina la sesión",
        "termina la sesion",
        "gever salir",
        "gever cierra",
        "gever cerrar",
    }


def main():
    print()
    print("==============================")
    print("       GEVER VOICE MODE")
    print("==============================")
    print()

    print("Iniciando cerebro...")
    brain = GeversBrain()

    print("Iniciando voz...")
    voice = GeversVoice()

    print("Iniciando micrófono...")
    listener = GeversListener()

    print()
    print("GEVER está listo.")
    print("ENTER = hablar")
    print("salir = cerrar")
    print("Ctrl + C = cierre de emergencia")
    print()

    while True:
        try:
            command = input(
                "ENTER = hablar | salir = cerrar: "
            ).strip().lower()

            if command in {
                "salir",
                "cerrar",
                "exit",
                "quit"
            }:
                print()
                print("GEVER: Sesión finalizada.")
                voice.speak("Sesión finalizada.")
                break

            user_text = listener.listen()

            if not user_text:
                print()
                print("GEVER: No detecté ninguna frase.")
                print()
                continue

            if user_text.startswith(
                "ERROR_RECONOCIMIENTO:"
            ):
                print()
                print(user_text)
                print()
                continue

            print()
            print(f"Tú: {user_text}")

            if is_exit_command(user_text):
                print()
                print("GEVER: Sesión finalizada.")
                voice.speak("Sesión finalizada.")
                break

            print()
            print("GEVER está pensando...")

            answer = brain.think(user_text)

            print()
            print(f"GEVER: {answer}")
            print()

            voice.speak(answer)

        except KeyboardInterrupt:
            print()
            print()
            print("GEVER: Cierre de emergencia.")
            break

        except Exception as e:
            print()
            print(f"GEVER: Ocurrió un error: {e}")
            print()


if __name__ == "__main__":
    main()