total = 0

while True:
    number = int(input("Enter number (0 to stop): "))
    if number == 0:
        break
    total += number

print("Total:", total)
