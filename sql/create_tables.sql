USE space_missions;

CREATE TABLE companies (
    id_company INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL
);

CREATE TABLE rockets (
    id_rocket INT AUTO_INCREMENT PRIMARY KEY,
    rocket_name VARCHAR(200) NOT NULL,
    rocket_status VARCHAR(20)
);

CREATE TABLE locations (
    id_location INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL
);

CREATE TABLE missions (
    id_mission INT AUTO_INCREMENT PRIMARY KEY,
    mission_name VARCHAR(255) NOT NULL,
    mission_date DATE,
    mission_time TIME,
    mission_status VARCHAR(30),
    price DECIMAL(12,2),

    id_company INT,
    id_rocket INT,
    id_location INT,

    CONSTRAINT fk_company
        FOREIGN KEY (id_company)
        REFERENCES companies(id_company),

    CONSTRAINT fk_rocket
        FOREIGN KEY (id_rocket)
        REFERENCES rockets(id_rocket),

    CONSTRAINT fk_location
        FOREIGN KEY (id_location)
        REFERENCES locations(id_location)
);