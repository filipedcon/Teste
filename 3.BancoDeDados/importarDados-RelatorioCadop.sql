-- Importar os dados (MySQL)
LOAD DATA INFILE '3.BancoDeDados/OperadorasDePlanos/Relatorio_cadop.csv'
INTO TABLE operadoras_saude
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(registro_ans, cnpj, razao_social, nome_fantasia, modalidade, logradouro, numero, complemento, 
 bairro, cidade, uf, cep, ddd, telefone, fax, endereco_eletronico, representante, 
 cargo_representante, regiao_de_comercializacao, data_registro_ans);

-- Passo 2: Importar os dados (PostgreSQL)
COPY operadoras_saude(registro_ans, cnpj, razao_social, nome_fantasia, modalidade, logradouro, numero, complemento, 
                      bairro, cidade, uf, cep, ddd, telefone, fax, endereco_eletronico, representante, 
                      cargo_representante, regiao_de_comercializacao, data_registro_ans)
FROM '3.BancoDeDados/OperadorasDePlanos/Relatorio_cadop.csv'
DELIMITER ',' CSV HEADER;