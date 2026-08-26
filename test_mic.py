from gever.listen import GeversListener


listener = GeversListener()

text = listener.listen()

print()
print("GEVER escuchó:")
print(text)