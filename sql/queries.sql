USE space_missions;

-- 1. Visão geral da base
SELECT
    COUNT(*) AS total_missions,
    COUNT(DISTINCT id_company) AS total_companies,
    COUNT(DISTINCT id_rocket) AS total_rockets,
    COUNT(DISTINCT id_location) AS total_locations,
    MIN(mission_date) AS first_mission,
    MAX(mission_date) AS last_mission
FROM missions;

-- 2. Distribuição e percentual por status
SELECT
    mission_status,
    COUNT(*) AS missions,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM missions
GROUP BY mission_status
ORDER BY missions DESC;

-- 3. Taxa geral de sucesso
SELECT
    COUNT(*) AS total_missions,
    SUM(mission_status = 'Success') AS successful_missions,
    ROUND(100 * AVG(mission_status = 'Success'), 2) AS success_rate_pct
FROM missions;

-- 4. Dez empresas com mais missões
SELECT
    c.company_name,
    COUNT(*) AS missions,
    SUM(m.mission_status = 'Success') AS successes,
    ROUND(100 * AVG(m.mission_status = 'Success'), 2) AS success_rate_pct
FROM missions AS m
JOIN companies AS c ON c.id_company = m.id_company
GROUP BY c.id_company, c.company_name
ORDER BY missions DESC
LIMIT 10;

-- 5. Dez foguetes mais utilizados
SELECT
    r.rocket_name,
    r.rocket_status,
    COUNT(*) AS missions,
    ROUND(100 * AVG(m.mission_status = 'Success'), 2) AS success_rate_pct
FROM missions AS m
JOIN rockets AS r ON r.id_rocket = m.id_rocket
GROUP BY r.id_rocket, r.rocket_name, r.rocket_status
ORDER BY missions DESC
LIMIT 10;

-- 6. Evolução anual das missões e taxa de sucesso
SELECT
    YEAR(mission_date) AS mission_year,
    COUNT(*) AS missions,
    SUM(mission_status = 'Success') AS successes,
    ROUND(100 * AVG(mission_status = 'Success'), 2) AS success_rate_pct
FROM missions
GROUP BY YEAR(mission_date)
ORDER BY mission_year;

-- 7. Locais com maior volume de lançamentos
SELECT
    l.location_name,
    COUNT(*) AS missions,
    ROUND(100 * AVG(m.mission_status = 'Success'), 2) AS success_rate_pct
FROM missions AS m
JOIN locations AS l ON l.id_location = m.id_location
GROUP BY l.id_location, l.location_name
ORDER BY missions DESC
LIMIT 10;

-- 8. Empresas com no mínimo 20 missões e maior taxa de sucesso
SELECT
    c.company_name,
    COUNT(*) AS missions,
    ROUND(100 * AVG(m.mission_status = 'Success'), 2) AS success_rate_pct
FROM missions AS m
JOIN companies AS c ON c.id_company = m.id_company
GROUP BY c.id_company, c.company_name
HAVING COUNT(*) >= 20
ORDER BY success_rate_pct DESC, missions DESC;

-- 9. Cobertura e estatísticas do preço (milhões de USD)
SELECT
    COUNT(*) AS total_missions,
    COUNT(price) AS missions_with_price,
    ROUND(100 * COUNT(price) / COUNT(*), 2) AS price_coverage_pct,
    ROUND(AVG(price), 2) AS average_price_musd,
    ROUND(MIN(price), 2) AS minimum_price_musd,
    ROUND(MAX(price), 2) AS maximum_price_musd
FROM missions;

-- 10. Validação de integridade após o ETL
SELECT
    COUNT(*) AS total_missions,
    SUM(id_company IS NULL) AS missing_company,
    SUM(id_rocket IS NULL) AS missing_rocket,
    SUM(id_location IS NULL) AS missing_location
FROM missions;
