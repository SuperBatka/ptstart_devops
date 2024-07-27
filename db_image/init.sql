CREATE USER repl_user with replication encrypted password '123';
SELECT pg_create_physical_replication_slot('replication_slot');
ALTER USER postgres WITH PASSWORD '123';

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS phone_number (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(100) NOT NULL
);
INSERT INTO emails (email) VALUES ('example@example.ru');
INSERT INTO phone_number (phone) VALUES ('+88888888888');