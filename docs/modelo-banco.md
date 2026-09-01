# Modelo do Banco de Dados

## Tabelas

### companies
- `id_company` (PK)
- `company_name` (único)

### rockets
- `id_rocket` (PK)
- `rocket_name`
- `rocket_status`

### locations
- `id_location` (PK)
- `location_name` (único)

### missions
- `id_mission` (PK)
- `mission_name`
- `mission_date`
- `mission_time`
- `mission_status`
- `price`
- `id_company` (FK)
- `id_rocket` (FK)
- `id_location` (FK)

## Relacionamentos

- Uma empresa realiza muitas missões.
- Um foguete pode aparecer em muitas missões.
- Um local recebe muitas missões.
- Cada missão referencia exatamente uma empresa, um foguete e um local.
