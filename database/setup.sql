CREATE DATABASE educan_db;

CREATE USER educan_user WITH PASSWORD 'tu_clave_segura';

ALTER ROLE educan_user SET client_encoding TO 'utf8';

GRANT ALL PRIVILEGES ON DATABASE educan_db TO educan_user;