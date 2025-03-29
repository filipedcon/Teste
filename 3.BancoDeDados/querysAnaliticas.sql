-- Código para encontrar as operadoras com maiores despesas do último semestre
WITH ultimo_trimestre AS (
    SELECT DISTINCT DATE_TRUNC('quarter', data) AS trimestre
    FROM rol_procedimentos
    ORDER BY trimestre DESC
    LIMIT 1
)
SELECT 
    o.razao_social, 
    rp.reg_ans, 
    SUM(rp.vl_saldo_final) AS total_despesa
FROM rol_procedimentos rp
JOIN operadoras o ON rp.reg_ans = o.registro_ans
GROUP BY o.razao_social, rp.reg_ans
ORDER BY total_despesa DESC
LIMIT 10;

-- Código para encontrar as operadoras com maiores despesas do último ano
WITH ultimo_ano AS (
    SELECT DISTINCT DATE_TRUNC('year', data) AS ano
    FROM rol_procedimentos
    ORDER BY ano DESC
    LIMIT 1
)
SELECT 
    o.razao_social, 
    rp.reg_ans, 
    SUM(rp.vl_saldo_final) AS total_despesa
FROM rol_procedimentos rp
JOIN operadoras o ON rp.reg_ans = o.registro_ans
GROUP BY o.razao_social, rp.reg_ans
ORDER BY total_despesa DESC
LIMIT 10;
