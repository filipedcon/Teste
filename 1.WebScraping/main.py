import os
import re
import time
import logging
import zipfile
import sys
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Logger:
    """Classe responsável pelo gerenciamento de logs da aplicação."""
    
    def __init__(self, log_file: str = "1.webScrapingFilipe/download.log"):
        self.logger = logging.getLogger("WebDownloader")
        self.logger.setLevel(logging.INFO)
        
        # Corrige a codificação para evitar erros com caracteres especiais
        # Força a codificação para UTF-8 no console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Configuração para salvar logs em arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona os handlers ao logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Registra uma mensagem de informação."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Registra uma mensagem de erro."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Registra uma mensagem de aviso."""
        self.logger.warning(message)


class WebScraper(ABC):
    """Classe abstrata base para implementações de web scraping."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    @abstractmethod
    def extract_links(self, url: str) -> List[Tuple[str, str]]:
        """
        Extrai links de uma URL.
        
        Args:
            url: URL para extrair os links
            
        Returns:
            Uma lista de tuplas contendo (nome_do_arquivo, url_do_arquivo)
        """
        pass


class StaticWebScraper(WebScraper):
    """Implementação de web scraper para páginas estáticas usando requests e BeautifulSoup."""
    
    def extract_links(self, url: str) -> List[Tuple[str, str]]:
        """
        Extrai links de PDFs de uma página estática.
        
        Args:
            url: URL para extrair os links
            
        Returns:
            Uma lista de tuplas contendo (nome_do_arquivo, url_do_arquivo)
        """
        self.logger.info(f"Acessando a URL: {url}")
        
        try:
            # Adiciona headers para evitar bloqueio
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: imprimir todos os links encontrados para análise
            all_links = [(link.get_text().strip(), link.get('href')) 
                        for link in soup.find_all('a', href=True)]
            self.logger.info(f"Total de links encontrados: {len(all_links)}")
            
            # Estratégia mais ampla para encontrar anexos
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                
                # Critério mais amplo para encontrar anexos: 
                # - Links que contenham "Anexo" no texto e terminem com .pdf
                # - Links que contenham "Anexo" no href e terminem com .pdf
                # - Quaisquer links que pareçam relevantes e terminem com .pdf
                if href.lower().endswith('.pdf') and (
                    'anexo' in text.lower() or 
                    'anexo' in href.lower() or
                    ('rol' in text.lower() and ('i' in text.lower() or 'ii' in text.lower()))
                ):
                    # Garante que a URL está completa
                    full_url = urljoin(url, href)
                    file_name = self._extract_filename(text, full_url)
                    
                    # Analisa o nome ou URL para identificar se é Anexo I ou Anexo II
                    is_anexo_i = 'anexo i' in text.lower() or 'anexo_i' in href.lower() or 'anexoi' in href.lower()
                    is_anexo_ii = 'anexo ii' in text.lower() or 'anexo_ii' in href.lower() or 'anexoii' in href.lower()
                    
                    # Se não estiver explícito no texto, tenta identificar por outros padrões
                    if not (is_anexo_i or is_anexo_ii):
                        if 'i.' in file_name.lower() or '_i_' in file_name.lower():
                            is_anexo_i = True
                        elif 'ii.' in file_name.lower() or '_ii_' in file_name.lower():
                            is_anexo_ii = True
                    
                    # Renomeia explicitamente se identificou o tipo de anexo
                    if is_anexo_i:
                        file_name = 'Anexo_I.pdf'
                    elif is_anexo_ii:
                        file_name = 'Anexo_II.pdf'
                    
                    # Adiciona à lista se for identificado como um dos anexos desejados
                    if is_anexo_i or is_anexo_ii:
                        pdf_links.append((file_name, full_url))
                        self.logger.info(f"Encontrado link: {file_name} - {full_url}")
            
            return pdf_links
        
        except Exception as e:
            self.logger.error(f"Erro ao acessar a URL: {str(e)}")
            return []
    
    def _extract_filename(self, text: str, url: str) -> str:
        """
        Extrai um nome de arquivo adequado baseado no texto do link ou na URL.
        
        Args:
            text: Texto do link
            url: URL do arquivo
            
        Returns:
            Nome do arquivo
        """
        # Tenta extrair um nome limpo do texto do link
        clean_text = re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')
        
        # Se não for possível, usa o final da URL
        if not clean_text:
            clean_text = url.split('/')[-1]
        
        # Garante que o arquivo termine com .pdf
        if not clean_text.lower().endswith('.pdf'):
            clean_text += '.pdf'
            
        return clean_text


class DynamicWebScraper(WebScraper):
    """Implementação de web scraper para páginas dinâmicas usando Selenium."""
    
    def __init__(self, logger: Logger):
        super().__init__(logger)
        self.driver = None
    
    def _initialize_driver(self) -> None:
        """Inicializa o driver do Selenium com as configurações apropriadas."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Para execução sem interface gráfica
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Ajuste para melhor renderização
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def extract_links(self, url: str) -> List[Tuple[str, str]]:
        """
        Extrai links de PDFs de uma página que requer JavaScript.
        
        Args:
            url: URL para extrair os links
            
        Returns:
            Uma lista de tuplas contendo (nome_do_arquivo, url_do_arquivo)
        """
        if not self.driver:
            self._initialize_driver()
            
        self.logger.info(f"Acessando a URL com Selenium: {url}")
        
        try:
            self.driver.get(url)
            
            # Espera a página carregar completamente
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll para garantir que todos os elementos são carregados
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Log do conteúdo da página para debug
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            all_links = soup.find_all('a', href=True)
            self.logger.info(f"Total de links encontrados com Selenium: {len(all_links)}")
            
            # Encontra links para PDFs que possam conter anexos
            pdf_links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    href = element.get_attribute("href")
                    text = element.text.strip()
                    
                    if href and href.lower().endswith('.pdf'):
                        self.logger.info(f"Link PDF encontrado: {text} - {href}")
                        
                        # Critérios mais amplos para identificar anexos
                        is_anexo_i = False
                        is_anexo_ii = False
                        
                        if 'anexo' in text.lower() or 'anexo' in href.lower():
                            if 'i' in text.lower() and not 'ii' in text.lower():
                                is_anexo_i = True
                            elif 'ii' in text.lower():
                                is_anexo_ii = True
                            
                            # Se não está explícito, tenta inferir pelo conteúdo da URL ou texto
                            if not (is_anexo_i or is_anexo_ii):
                                if 'rol' in text.lower() or 'procedimento' in text.lower():
                                    # Primeiro link relevante como Anexo I, segundo como Anexo II
                                    if not pdf_links:
                                        is_anexo_i = True
                                    else:
                                        is_anexo_ii = True
                        
                        if is_anexo_i:
                            file_name = 'Anexo_I.pdf'
                            pdf_links.append((file_name, href))
                            self.logger.info(f"Identificado como Anexo I: {href}")
                        elif is_anexo_ii:
                            file_name = 'Anexo_II.pdf'
                            pdf_links.append((file_name, href))
                            self.logger.info(f"Identificado como Anexo II: {href}")
                
                except Exception as e:
                    self.logger.warning(f"Erro ao processar elemento: {str(e)}")
            
            # Se não encontrou anexos específicos, considera os primeiros dois PDFs como anexos
            if len(pdf_links) < 2:
                pdf_count = 0
                for element in elements:
                    try:
                        href = element.get_attribute("href")
                        if href and href.lower().endswith('.pdf'):
                            # Evita duplicação se já adicionou
                            if not any(href == url for _, url in pdf_links):
                                if pdf_count == 0:
                                    pdf_links.append(('Anexo_I.pdf', href))
                                    self.logger.info(f"Adicionando PDF como Anexo I: {href}")
                                    pdf_count += 1
                                elif pdf_count == 1:
                                    pdf_links.append(('Anexo_II.pdf', href))
                                    self.logger.info(f"Adicionando PDF como Anexo II: {href}")
                                    pdf_count += 1
                                    break  # Já temos os dois anexos
                    except Exception:
                        continue
            
            return pdf_links
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar a URL com Selenium: {str(e)}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None


class FileDownloader:
    """Classe responsável pelo download de arquivos."""
    
    def __init__(self, output_dir: str, logger: Logger):
        self.output_dir = output_dir
        self.logger = logger
        
        # Cria o diretório de saída, se necessário
        os.makedirs(output_dir, exist_ok=True)
    
    def download_file(self, file_url: str, file_name: str) -> Optional[str]:
        """
        Faz o download de um arquivo, garantindo que os nomes sejam únicos.
        """
        file_path = os.path.join(self.output_dir, file_name)

        # Se já existir um arquivo com o mesmo nome, gera um novo nome
        base_name, ext = os.path.splitext(file_name)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(self.output_dir, f"{base_name}_I{ext}")
            counter += 1

        self.logger.info(f"Baixando {file_url} para {file_path}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf'
            }
            
            response = requests.get(file_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if os.path.getsize(file_path) == 0:
                self.logger.error(f"Arquivo baixado está vazio: {file_path}")
                os.remove(file_path)
                return None

            self.logger.info(f"Download concluído: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"Erro ao baixar arquivo {file_url}: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None


class FileCompressor:
    """Classe responsável pela compactação de arquivos."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def compress_files(self, file_paths: List[str], output_path: str) -> bool:
        """
        Compacta uma lista de arquivos em um único arquivo ZIP.
        
        Args:
            file_paths: Lista de caminhos dos arquivos a serem compactados
            output_path: Caminho do arquivo ZIP de saída
            
        Returns:
            True se a compactação for bem-sucedida, False caso contrário
        """
        if not file_paths:
            self.logger.error("Nenhum arquivo para compactar")
            return False
            
        self.logger.info(f"Compactando {len(file_paths)} arquivos para {output_path}")
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    # Adiciona apenas o nome do arquivo, não o caminho completo
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname=arcname)
                    self.logger.info(f"Adicionado {file_path} ao arquivo ZIP")
            
            self.logger.info(f"Compactação concluída: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao compactar arquivos: {str(e)}")
            return False


class ANSDownloader:
    """Classe principal que coordena o processo de download e compactação."""
    
    def __init__(self, 
                 output_dir: str = "1.webScrapingFilipe/downloads",
                 zip_filename: str = "anexos.zip"):
        """
        Inicializa o downloader da ANS.
        
        Args:
            output_dir: Diretório para salvar os arquivos
            zip_filename: Nome do arquivo ZIP de saída
        """
        self.url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
        self.output_dir = output_dir
        self.zip_path = os.path.join(output_dir, zip_filename)
        
        # Inicializa o logger
        self.logger = Logger()
        
        # Inicializa os outros componentes
        self.static_scraper = StaticWebScraper(self.logger)
        self.dynamic_scraper = DynamicWebScraper(self.logger)
        self.downloader = FileDownloader(output_dir, self.logger)
        self.compressor = FileCompressor(self.logger)
    
    def run(self) -> bool:
        """
        Executa o processo completo: extração de links, download e compactação.
        
        Returns:
            True se o processo for bem-sucedido, False caso contrário
        """
        self.logger.info("Iniciando o processo de download dos anexos da ANS")
        
        # Tenta primeiro com o scraper estático
        links = self.static_scraper.extract_links(self.url)
        
        # Se não encontrar os dois anexos, tenta com o scraper dinâmico
        if len(links) < 2:
            self.logger.info(f"Encontrados apenas {len(links)} links com scraper estático. Tentando scraper dinâmico.")
            dynamic_links = self.dynamic_scraper.extract_links(self.url)
            
            # Adiciona novos links encontrados (evitando duplicatas)
            for name, url in dynamic_links:
                if not any(url == existing_url for _, existing_url in links):
                    links.append((name, url))
        
        # Verifica se encontrou pelo menos um link
        if not links:
            self.logger.error("Não foi possível encontrar nenhum link para anexos.")
            return False
        
        self.logger.info(f"Encontrados {len(links)} links de anexos.")
        
        # Debug: exibe todos os links encontrados
        for name, url in links:
            self.logger.info(f"Link encontrado: {name} - {url}")
        
        # Faz o download dos arquivos
        downloaded_files = []
        for file_name, file_url in links:
            file_path = self.downloader.download_file(file_url, file_name)
            if file_path:
                downloaded_files.append(file_path)
        
        if not downloaded_files:
            self.logger.error("Nenhum arquivo foi baixado com sucesso.")
            return False
        
        # Mensagem de aviso se não baixou dois arquivos
        if len(downloaded_files) < 2:
            self.logger.warning(f"Apenas {len(downloaded_files)} arquivo(s) baixado(s) com sucesso. Alguns anexos podem estar faltando.")
        
        # Compacta os arquivos baixados
        compression_result = self.compressor.compress_files(downloaded_files, self.zip_path)
        
        if compression_result:
            self.logger.info(f"Processo concluído com sucesso. Arquivo ZIP gerado: {self.zip_path}")
            return True
        else:
            self.logger.error("Falha ao compactar os arquivos.")
            return False


if __name__ == "__main__":
    # Define o encoding padrão para UTF-8 para evitar problemas com caracteres especiais
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    downloader = ANSDownloader()
    success = downloader.run()
    
    if success:
        print(f"Download e compactação concluídos com sucesso!")
        print(f"Verifique o arquivo ZIP em: {downloader.zip_path}")
    else:
        print("Ocorreu um erro durante o processo. Verifique os logs para mais detalhes.")