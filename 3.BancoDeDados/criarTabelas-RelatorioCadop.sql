-- Criação da Tabela para as Operadoras de Saúde
CREATE TABLE operadoras_saude (
    id SERIAL PRIMARY KEY,
    registro_ans INT NOT NULL UNIQUE,
    cnpj BIGINT NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255) NOT NULL,
    modalidade VARCHAR(100) NOT NULL,
    logradouro VARCHAR(255) NOT NULL,
    numero INT NOT NULL,
    complemento VARCHAR(255),
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL,  -- Estado com 2 caracteres
    cep BIGINT NOT NULL,
    ddd SMALLINT NOT NULL,
    telefone BIGINT NOT NULL,
    fax BIGINT,
    endereco_eletronico VARCHAR(255),
    representante VARCHAR(255) NOT NULL,
    cargo_representante VARCHAR(100) NOT NULL,
    regiao_de_comercializacao INT NOT NULL,
    data_registro_ans DATE NOT NULL
);

-- Criar índices para melhorar performance em consultas
CREATE INDEX idx_registro_ans ON operadoras_saude (registro_ans);
CREATE INDEX idx_cnpj ON operadoras_saude (cnpj);
CREATE INDEX idx_cidade ON operadoras_saude (cidade);
CREATE INDEX idx_uf ON operadoras_saude (uf);
