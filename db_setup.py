import psycopg2

# Укажи свои данные для подключения
DB_CONFIG = {
    "host": "localhost",
    "dbname": "mydb",      # Проверь имя своей базы!
    "user": "postgres",
    "password": "20071004ABA" 
}

# Твой SQL код (я добавил еще удаление, оно есть в задании 3.2.5)
sql_script = """
-- 1. Поиск
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT id, name, phone FROM contacts 
    WHERE name ILIKE '%' || p_pattern || '%' 
       OR phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- 2. Вставка или Обновление
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

-- 3. Пагинация
CREATE OR REPLACE FUNCTION get_contacts_paged(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT id, name, phone FROM contacts 
    ORDER BY id 
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 4. Удаление (из пункта 3.2.5 задания)
CREATE OR REPLACE PROCEDURE delete_contact(p_search VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE name = p_search OR phone = p_search;
END;
$$;
"""

try:
    # Используем твой путь к Python, если запускаешь через терминал
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_script)
            print("✅ Готово! База данных теперь знает все функции и процедуры.")
except Exception as e:
    print(f"❌ Ошибка: {e}")