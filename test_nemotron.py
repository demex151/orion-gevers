from gever.brain import GeversBrain
from gever.voice import GeversVoice


def main():
    gever = GeversBrain()
    voice = GeversVoice()

    print("\n==============================")
    print("        GEVER INICIADO")
    print("==============================")
    print()
    print("Comandos disponibles:")
    print("/recordar TEXTO   -> guarda una memoria permanente")
    print("/memorias         -> muestra las memorias guardadas")
    print("/salir            -> cierra GEVER")
    print()

    while True:
        user_input = input("Tú: ").strip()

        if not user_input:
            continue

        if user_input.lower() in [
            "/salir",
            "salir",
            "exit",
            "quit"
        ]:
            print("\nGEVER: Sesión finalizada.")
            voice.speak("Sesión finalizada.")
            break

        if user_input.lower().startswith("/recordar "):
            content = user_input[len("/recordar "):].strip()

            if not content:
                print("\nGEVER: No me diste nada para recordar.\n")
                continue

            saved = gever.remember(
                content=content,
                category="manual"
            )

            if saved:
                message = "Información guardada en mi memoria permanente."
            else:
                message = (
                    "Esa información ya estaba guardada "
                    "o no era válida."
                )

            print(f"\nGEVER: {message}\n")
            voice.speak(message)
            continue

        if user_input.lower() == "/memorias":
            memories = gever.memories()

            if not memories:
                print("\nGEVER: No tengo memorias guardadas.\n")
                voice.speak("No tengo memorias guardadas.")
                continue

            print("\nMEMORIAS DE GEVER:")

            for index, memory in enumerate(
                memories,
                start=1
            ):
                category = memory.get(
                    "category",
                    "general"
                )

                content = memory.get(
                    "content",
                    ""
                )

                print(
                    f"{index}. [{category}] {content}"
                )

            print()
            continue

        answer = gever.think(user_input)

        print(f"\nGEVER: {answer}\n")

        voice.speak(answer)


if __name__ == "__main__":
    main()
