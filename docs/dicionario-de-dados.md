# Dicionário de Dados

## Dataset
Space Missions (1957–2022)

## Informações Gerais

- Total de registros: 4.630
- Total de colunas: 9

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Company | Texto | Empresa responsável pela missão |
| Location | Texto | Local de lançamento |
| Date | Data | Data da missão |
| Time | Hora | Horário do lançamento |
| Rocket | Texto | Nome do foguete |
| Mission | Texto | Nome da missão |
| RocketStatus | Texto | Status do foguete |
| Price | Decimal | Custo informado da missão, em milhões de USD; 3.365 valores ausentes |
| MissionStatus | Texto | Resultado da missão |

## Valores categóricos

- `MissionStatus`: Success, Failure, Partial Failure e Prelaunch Failure.
- `RocketStatus`: Active ou Retired.

## Qualidade

- `Time`: 127 valores ausentes.
- `Price`: 3.365 valores ausentes (72,68%).
- As demais colunas não possuem valores ausentes no arquivo original.
