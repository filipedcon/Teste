import pandas as pd
from .models import Operadora

def importar_csv(caminho_arquivo):
    
    try:
        df = pd.read_csv(caminho_arquivo, delimiter=";", encoding="utf-8") # Como só precisamos da busca, estou utilizando string para evitar problemas.
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return
  
    print(df.head(5))

    for _, row in df.iterrows():
        try:
            Operadora.objects.create(
                Registro_ANS=row.get("Registro_ANS", ""),
                CNPJ=row.get("CNPJ", ""),
                Razao_Social=row.get("Razao_Social", ""),
                Modalidade=row.get("Modalidade", ""),
                Logradouro=row.get("Logradouro", ""),
                Numero=row.get("Numero", ""),
                Complemento=row.get("Complemento", ""),
                Bairro=row.get("Bairro", ""),
                Cidade=row.get("Cidade", ""),
                UF=row.get("UF", ""),
                CEP=row.get("CEP", ""),
                DDD=row.get("DDD", ""),
                Telefone=row.get("Telefone", ""),
                Fax=row.get("Fax", ""),
                Endereco_eletronico=row.get("Endereco_eletronico", ""),
                Representante=row.get("Representante", ""),
                Cargo_Representante=row.get("Cargo_Representante", ""),
                Regiao_de_Comercializacao=row.get("Regiao_de_Comercializacao", ""),
                Data_Registro_ANS=row.get("Data_Registro_ANS", ""),
            )
        except Exception as e:
            print(f"Erro ao importar operadora: {row.get('Registro_ANS')} | Erro: {e}")

    print(f"✅ {len(df)} linhas importadas com sucesso!")
