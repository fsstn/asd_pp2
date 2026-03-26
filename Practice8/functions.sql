-- 1. Функция поиска контакта по части имени или телефона
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone 
    FROM contacts 
    WHERE name ILIKE '%' || p_pattern || '%'
       OR phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- 2. Процедура Upsert (вставка или обновление)
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

-- 3. Функция с пагинацией
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone 
    FROM contacts 
    ORDER BY id
    LIMIT p_limit 
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 4. Процедура массовой вставки с валидацией телефона
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[],
    INOUT p_invalid_data TEXT DEFAULT ''
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    invalid_records TEXT := '';
    phone_pattern TEXT := '^[0-9]{10,12}$'; -- Простой паттерн для телефона
BEGIN
    -- Проверяем, что массивы одинаковой длины
    IF array_length(p_names, 1) != array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Массивы разной длины';
    END IF;
    
    FOR i IN 1..array_length(p_names, 1) LOOP
        -- Валидация телефона (только цифры, от 10 до 12 символов)
        IF p_phones[i] ~ phone_pattern THEN
            -- Вызываем процедуру upsert для каждого контакта
            CALL upsert_contact(p_names[i], p_phones[i]);
        ELSE
            invalid_records := invalid_records || 
                format('Имя: %s, Телефон: %s (неверный формат); ', p_names[i], p_phones[i]);
        END IF;
    END LOOP;
    
    p_invalid_data := invalid_records;
END;
$$;

-- 5. Процедура удаления контакта
CREATE OR REPLACE PROCEDURE delete_contact(
    p_identifier VARCHAR,
    p_by VARCHAR DEFAULT 'name' -- 'name' или 'phone'
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_by = 'name' THEN
        DELETE FROM contacts WHERE name = p_identifier;
    ELSIF p_by = 'phone' THEN
        DELETE FROM contacts WHERE phone = p_identifier;
    ELSE
        RAISE EXCEPTION 'Неверный параметр p_by. Используйте "name" или "phone"';
    END IF;
    
    IF NOT FOUND THEN
        RAISE NOTICE 'Контакт не найден: %', p_identifier;
    END IF;
END;
$$;