from django.db import models

class Operadora(models.Model):
    Registro_ANS = models.CharField(max_length=200, unique=True)
    CNPJ = models.CharField(max_length=100)
    Razao_Social = models.CharField(max_length=200)
    Modalidade = models.CharField(max_length=100)
    Logradouro = models.CharField(max_length=200)
    Numero = models.CharField(max_length=20)
    Complemento = models.CharField(max_length=100)
    Bairro = models.CharField(max_length=100)
    Cidade = models.CharField(max_length=80)
    UF = models.CharField(max_length=100)
    CEP = models.CharField(max_length=100)
    DDD = models.CharField(max_length=100)
    Telefone = models.CharField(max_length=100)
    Fax = models.CharField(max_length=100)
    Endereco_eletronico = models.CharField(max_length=100)
    Representante = models.CharField(max_length=150)
    Cargo_Representante = models.CharField(max_length=100)
    Regiao_de_Comercializacao = models.CharField(max_length=100)
    Data_Registro_ANS = models.CharField(max_length=100)


    def __str__(self):
        return self.Razao_Social
