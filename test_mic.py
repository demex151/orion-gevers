from gever.listen import GeversListener


def main():
    listener = GeversListener()
    text = listener.listen()

    print()
    print("GEVER escuchó:")
    print(text)


if __name__ == "__main__":
    main()
