CREATE DATABASE IF NOT EXISTS phone_retriever_dev;

USE phone_retriever_dev;
CREATE TABLE IF NOT EXISTS error_codes (
    id INT,
    description VARCHAR(200),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS phone_info (
    international_number VARCHAR(50),
    international_calling_code VARCHAR(100) DEFAULT NULL,
    prefix_network VARCHAR(50) DEFAULT NULL,
    is_valid BOOL DEFAULT NULL,
    is_mobile BOOL DEFAULT NULL,
    phone_type VARCHAR(20) DEFAULT NULL,
    country VARCHAR(50) DEFAULT NULL,
    country_code CHAR(2) DEFAULT NULL,
    error_code INT,
    PRIMARY KEY (international_number),
    FOREIGN KEY (error_code)
        REFERENCES error_codes(id)
        ON DELETE SET NULL
);

