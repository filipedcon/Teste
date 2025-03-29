-- Importar os dados (MySQL)
LOAD DATA INFILE '3.BancoDeDados/2023/1T2023/1T2023.csv' -- Aqui você pode ir trocando o arquivo dos semestres conforme faz a importação. Não fazer tudo de vez para fins de desempenho e conferência dos dados.
INTO TABLE rol_procedimentos
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(data, reg_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final);

-- Importar os dados (PostgreSQL)
COPY rol_procedimentos(data, reg_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final)
FROM '3.BancoDeDados/2023/1T2023/1T2023.csv'
DELIMITER ',' CSV HEADER;