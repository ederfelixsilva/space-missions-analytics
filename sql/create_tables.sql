CREATE DATABASE IF NOT EXISTS space_missions
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE space_missions;

DROP TABLE IF EXISTS missions;
DROP TABLE IF EXISTS rockets;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    id_company INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    CONSTRAINT uq_company_name UNIQUE (company_name)
);

CREATE TABLE rockets (
    id_rocket INT AUTO_INCREMENT PRIMARY KEY,
    rocket_name VARCHAR(200) NOT NULL,
    rocket_status VARCHAR(20) NOT NULL,
    CONSTRAINT uq_rocket UNIQUE (rocket_name, rocket_status)
);

CREATE TABLE locations (
    id_location INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    CONSTRAINT uq_location_name UNIQUE (location_name)
);

CREATE TABLE missions (
    id_mission INT AUTO_INCREMENT PRIMARY KEY,
    mission_name VARCHAR(255) NOT NULL,
    mission_date DATE NOT NULL,
    mission_time TIME,
    mission_status VARCHAR(30) NOT NULL,
    price DECIMAL(12,2),

    id_company INT NOT NULL,
    id_rocket INT NOT NULL,
    id_location INT NOT NULL,

    CONSTRAINT fk_company
        FOREIGN KEY (id_company)
        REFERENCES companies(id_company),

    CONSTRAINT fk_rocket
        FOREIGN KEY (id_rocket)
        REFERENCES rockets(id_rocket),

    CONSTRAINT fk_location
        FOREIGN KEY (id_location)
        REFERENCES locations(id_location),

    INDEX idx_mission_date (mission_date),
    INDEX idx_mission_status (mission_status),
    INDEX idx_mission_company (id_company),
    INDEX idx_mission_rocket (id_rocket),
    INDEX idx_mission_location (id_location)
);
