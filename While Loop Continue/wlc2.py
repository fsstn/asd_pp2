while True:
    text = input("Enter text (type 'stop' to quit): ")
    if text == "":
        continue
    if text.lower() == "stop":
        break
    print("You typed:", text)
