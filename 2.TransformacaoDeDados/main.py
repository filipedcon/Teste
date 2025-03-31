import pdfplumber
import pandas as pd
import zipfile
import os

class PDFExtractor:
    """
    Classe responsável por extrair dados da tabela do Anexo I
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def extract_table(self) -> pd.DataFrame:
        """Extrai a tabela do PDF e retorna um DataFrame"""
        data = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_table()
                if tables:
                    for row in tables:
                        data.append(row)
        
        columns = ["PROCEDIMENTO", "RN", "VIGÊNCIA", "OD", "AMB", "HCO", "HSO", "REF", "PAC", "DUT", "SUBGRUPO", "GRUPO", "CAPÍTULO" ]
        df = pd.DataFrame(data[1:], columns=columns)  # Ignorando cabeçalho duplicado
        return df

class DataProcessor:
    """
    Classe para processar e estruturar os dados extraídos
    """
    @staticmethod
    def replace_abbreviations(df: pd.DataFrame) -> pd.DataFrame:
        """Substitui abreviações OD e AMB por descrições completas"""
        mapping = {
            "OD": "Seg. Odontológica",
            "AMB": "Seg. Ambulatorial"
        }
        df.replace({"OD": mapping["OD"], "AMB": mapping["AMB"]}, inplace=True)
        return df

class CSVCompressor:
    """
    Classe para salvar o CSV e compactar no formato ZIP
    """
    def __init__(self, output_dir: str, user_name: str):
        self.output_dir = output_dir
        self.user_name = user_name
    
    def save_and_compress(self, df: pd.DataFrame):
        """Salva o DataFrame em CSV e compacta em um arquivo ZIP"""
        csv_path = os.path.join(self.output_dir, "Rol_Procedimentos.csv")
        zip_path = os.path.join(self.output_dir, f"Teste_{self.user_name}.zip")
        
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_path, os.path.basename(csv_path))
        
        os.remove(csv_path)  # Remove CSV após compactação
        return zip_path

if __name__ == "__main__":
    pdf_path = "2.TransformacaoDeDados/Anexo_I.pdf"  # Caminho do PDF
    output_dir = "2.TransformacaoDeDados"      # Diretório de saída
    user_name = "{Filipe_Santana}"      
    os.makedirs(output_dir, exist_ok=True)
    
    print("Aguarde...")

    extractor = PDFExtractor(pdf_path)
    df = extractor.extract_table()
    
    processor = DataProcessor()
    df = processor.replace_abbreviations(df)
    
    compressor = CSVCompressor(output_dir, user_name)
    zip_file = compressor.save_and_compress(df)
    
    print(f"Arquivo compactado salvo em: {zip_file}")
