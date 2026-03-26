-- upsert_contact
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

-- bulk_insert_contacts
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[],
    INOUT p_invalid_data TEXT DEFAULT ''
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    invalid_records TEXT := '';
    phone_pattern TEXT := '^[0-9]{10,12}$';
BEGIN
    IF array_length(p_names, 1) != array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Массивы разной длины';
    END IF;
    
    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ phone_pattern THEN
            CALL upsert_contact(p_names[i], p_phones[i]);
        ELSE
            invalid_records := invalid_records || 
                format('Имя: %s, Телефон: %s (неверный формат); ', p_names[i], p_phones[i]);
        END IF;
    END LOOP;
    
    p_invalid_data := invalid_records;
END;
$$;

-- delete_contact
CREATE OR REPLACE PROCEDURE delete_contact(
    p_identifier VARCHAR,
    p_by VARCHAR DEFAULT 'name'
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_by = 'name' THEN
        DELETE FROM contacts WHERE name = p_identifier;
    ELSIF p_by = 'phone' THEN
        DELETE FROM contacts WHERE phone = p_identifier;
    ELSE
        RAISE EXCEPTION 'Неверный параметр p_by';
    END IF;
END;
$$;