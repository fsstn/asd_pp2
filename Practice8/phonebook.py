import psycopg2
from config import DB_CONFIG

def init_database():
    """Инициализация базы данных - создание таблицы если не существует"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Создаем таблицу если её нет
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("База данных инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")

def main_menu():
    print("\n--- Телефонная Книга (Practice 8) ---")
    print("1. Найти контакт (Функция)")
    print("2. Добавить/Обновить контакт (Процедура Upsert)")
    print("3. Показать список с пагинацией (Функция)")
    print("4. Массовая вставка контактов (Процедура)")
    print("5. Удалить контакт (Процедура)")
    print("0. Выход")
    return input("Выбери действие: ")

def search():
    """Поиск контакта"""
    pattern = input("Введите имя или номер для поиска: ")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
                rows = cur.fetchall()
                if not rows:
                    print("Ничего не найдено.")
                else:
                    print("\nНайденные контакты:")
                    for row in rows:
                        print(f"ID: {row[0]} | Имя: {row[1]} | Тел: {row[2]}")
    except Exception as e:
        print(f"Ошибка в поиске: {e}")

def upsert():
    """Добавление или обновление контакта"""
    name = input("Имя: ")
    phone = input("Телефон: ")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
                conn.commit()
                print("Успешно выполнено!")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

def show_paginated():
    """Показать список с пагинацией"""
    try:
        page = int(input("Номер страницы: "))
        per_page = int(input("Количество записей на странице: "))
        offset = (page - 1) * per_page
        
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (per_page, offset))
                rows = cur.fetchall()
                
                if not rows:
                    print("Нет записей на этой странице.")
                else:
                    print(f"\nСтраница {page} (записей: {len(rows)}):")
                    for row in rows:
                        print(f"ID: {row[0]} | Имя: {row[1]} | Тел: {row[2]}")
    except ValueError:
        print("Ошибка: введите корректные числа")
    except Exception as e:
        print(f"Ошибка при получении списка: {e}")

def bulk_insert():
    """Массовая вставка контактов"""
    print("\n--- Массовая вставка контактов ---")
    print("Формат ввода: имя,телефон (каждая запись на новой строке)")
    print("Для завершения введите пустую строку")
    
    names = []
    phones = []
    
    while True:
        line = input().strip()
        if not line:
            break
        parts = line.split(',')
        if len(parts) == 2:
            names.append(parts[0].strip())
            phones.append(parts[1].strip())
        else:
            print("Неверный формат. Используйте: имя,телефон")
    
    if names:
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    # Вызываем процедуру с OUT параметром
                    cur.execute("CALL bulk_insert_contacts(%s, %s, %s)", (names, phones, ''))
                    # Получаем INOUT параметр
                    cur.execute("SELECT %s", ('',))  # Нужно доработать
                    conn.commit()
                    print(f"Обработано {len(names)} контактов")
        except Exception as e:
            print(f"Ошибка при массовой вставке: {e}")

def delete_contact():
    """Удаление контакта"""
    print("\n--- Удаление контакта ---")
    print("1. Удалить по имени")
    print("2. Удалить по телефону")
    choice = input("Выберите: ")
    
    if choice == '1':
        name = input("Введите имя: ")
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("CALL delete_contact(%s, %s)", (name, 'name'))
                    conn.commit()
                    print("Удаление выполнено")
        except Exception as e:
            print(f"Ошибка: {e}")
    elif choice == '2':
        phone = input("Введите телефон: ")
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("CALL delete_contact(%s, %s)", (phone, 'phone'))
                    conn.commit()
                    print("Удаление выполнено")
        except Exception as e:
            print(f"Ошибка: {e}")
    else:
        print("Неверный выбор")

def main():
    init_database()  # Инициализация БД при запуске
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            search()
        elif choice == '2':
            upsert()
        elif choice == '3':
            show_paginated()
        elif choice == '4':
            bulk_insert()
        elif choice == '5':
            delete_contact()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()