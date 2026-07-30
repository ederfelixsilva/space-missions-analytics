# Modelo do Banco de Dados

## Tabelas

### companies
- id_company (PK)
- company

### rockets
- id_rocket (PK)
- rocket
- rocket_status

### locations
- id_location (PK)
- location

### missions
- id_mission (PK)
- mission
- mission_date
- mission_time
- mission_status
- price
- company_id (FK)
- rocket_id (FK)
- location_id (FK)