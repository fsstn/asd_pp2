choice = input("Choose an option (1-3): ")

match choice:
    case "1":
        print("Start Game")
    case "2":
        print("Load Game")
    case "3":
        print("Exit")
    case _:
        print("Invalid choice")
