-- ============================================================================
-- Auction Seeker (I_A_H) — Consultas Analíticas
-- ============================================================================
-- Queries utilizadas durante a análise exploratória e validação dos dados
-- no PostgreSQL (via pgAdmin), organizadas por finalidade.
--
-- Tabelas:
--   auction_items (id, source_mongo_id, name, class, tier, price, seller_id, ...)
--   sellers       (id, name, rank)
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. VENDEDORES — Ranking e distribuição de vendas
-- ----------------------------------------------------------------------------

-- Top vendedores por quantidade de itens vendidos, com a lista de itens distintos
SELECT
    se.name AS "Vendedor",
    COUNT(au.id) AS "Total Itens Vendidos",
    array_agg(DISTINCT au.name) AS "Items"
FROM auction_items au
JOIN sellers se ON au.seller_id = se.id
GROUP BY se.name
ORDER BY COUNT(au.id) DESC
LIMIT 10;

-- Quantidade de itens vendidos por vendedor (visão completa)
SELECT
    se.name AS "Vendedor",
    COUNT(au.seller_id) AS "Itens vendidos"
FROM sellers se
JOIN auction_items au ON se.id = au.seller_id
GROUP BY se.name
ORDER BY COUNT(au.seller_id) DESC;

-- Média de itens vendidos por vendedor
SELECT
    ROUND(AVG(itens_vendidos), 2) AS "Média de itens vendidos"
FROM (
    SELECT se.name AS "Vendedor", COUNT(au.seller_id) AS itens_vendidos
    FROM sellers se
    JOIN auction_items au ON se.id = au.seller_id
    GROUP BY se.name
) AS vendas_por_vendedor;

-- Mediana de itens vendidos por vendedor (menos sensível a outliers que a média)
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY itens_vendidos) AS "Mediana de itens por vendedor"
FROM (
    SELECT se.name AS vendedor, COUNT(au.seller_id) AS itens_vendidos
    FROM sellers se
    JOIN auction_items au ON se.id = au.seller_id
    GROUP BY se.name
) AS vendas_por_vendedor;


-- ----------------------------------------------------------------------------
-- 2. QUALIDADE DE DADOS — Vendedores órfãos e itens sem vínculo
-- ----------------------------------------------------------------------------

-- Vendedores cadastrados sem nenhum item associado (candidatos a limpeza)
SELECT
    se.name AS "Vendedor",
    COUNT(au.id) AS "Quantidade de itens vendidos"
FROM sellers se
LEFT JOIN auction_items au ON au.seller_id = se.id
GROUP BY se.name
ORDER BY COUNT(au.id) DESC;

-- Itens sem seller_id resolvido (falha no fuzzy matching do load.py)
SELECT *
FROM auction_items
WHERE seller_id IS NULL;

-- Remove vendedores que não possuem nenhum item vinculado
-- (rodar apenas após confirmar que não há religação pendente)
DELETE FROM sellers
WHERE id NOT IN (
    SELECT DISTINCT seller_id FROM auction_items WHERE seller_id IS NOT NULL
);


-- ----------------------------------------------------------------------------
-- 3. EXEMPLOS DE BUSCA / DIAGNÓSTICO PONTUAL
-- ----------------------------------------------------------------------------

-- Busca de item por vendedor específico (prefixo de nome)
SELECT
    au.source_mongo_id,
    au.name,
    au.price,
    se.name AS seller_name
FROM auction_items au
JOIN sellers se ON au.seller_id = se.id
WHERE se.name LIKE 'anar%';

-- Busca de um documento específico pelo id de origem no MongoDB
-- (útil para cruzar com o raw_text durante correção manual de OCR)
SELECT *
FROM auction_items
WHERE source_mongo_id = '6a0a685da9d71299ae79fbb1';
