total = 0
number = 0

while number < 10:
    number += 1
    if number % 2 == 0:
        continue
    total += number

print("Sum of odd numbers:", total)
