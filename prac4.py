import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="20071004ABA"
)

print("Подключение успешно!")
