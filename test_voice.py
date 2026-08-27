from gever.voice import GeversVoice


def main():
    voice = GeversVoice()

    print("Probando voz de GEVER...")

    voice.speak(
        "Hola. Soy GEVER. Mi sistema de voz está funcionando correctamente."
    )

    print("Prueba terminada.")


if __name__ == "__main__":
    main()
