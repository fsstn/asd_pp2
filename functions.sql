-- 1. Функция поиска по паттерну
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT id, name, phone FROM contacts 
    WHERE name ILIKE '%' || p_pattern || '%' 
       OR phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- 2. Процедура Upsert (вставить или обновить)
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

-- 3. Функция для пагинации
CREATE OR REPLACE FUNCTION get_contacts_paged(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT id, name, phone FROM contacts 
    ORDER BY id 
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;