-- Criação da tabela para Demonstrações Contábeis
CREATE TABLE rol_procedimentos (
    id SERIAL PRIMARY KEY,  -- Chave primária auto-incremental (PostgreSQL) | No MySQL use AUTO_INCREMENT
    data DATE NOT NULL,
    reg_ans INT NOT NULL,
    cd_conta_contabil INT NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    vl_saldo_inicial DECIMAL(18,2) NOT NULL,
    vl_saldo_final DECIMAL(18,2) NOT NULL,
);

-- índices para melhorar performance em consultas
CREATE INDEX idx_data ON rol_procedimentos (data);
CREATE INDEX idx_reg_ans ON rol_procedimentos (reg_ans);
CREATE INDEX idx_cd_conta_contabil ON rol_procedimentos (cd_conta_contabil);