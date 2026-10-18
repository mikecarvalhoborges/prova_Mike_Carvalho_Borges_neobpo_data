import os
import time
import zipfile
import logging
import pandas as pd
from selenium import webdriver # principal controlador do navegador
from selenium.webdriver.chrome.service import Service # gerencia o driver que conecta o Python e o Chrome
from selenium.webdriver.chrome.options import Options # informa o que e onde baixar
from selenium.webdriver.common.by import By # localizar elementos dentro da página HTML 
from webdriver_manager.chrome import ChromeDriverManager # descobre a versão do Chrome, faz o dowload do ChromeDriver certo automaticamente

# configuração dos logs (grava no arquivo e mostra no terminal)
logging.basicConfig (
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler("1_Python/extracao.log", encoding = "utf-8"),
        logging.StreamHandler() # mostrando também no terminal
    ]
)

# caminho completo para salvar o dowload
pasta_download = os.path.abspath("1_Python/data")

# função para receber a pasta em que os dowloads vão cair e deixar o Chrome pronto para ser usado no dowload
def iniciar_driver(pasta_download):
    # cria o objeto de configuração do Chrome e dizemos pra ele como ele tem que se comportar
    chrome_options = Options()

    # preferências para o download ser automático e sem pop-ups
    prefs = {
        "download.default_directory": pasta_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    # aplicar as preferências nas ações do Chrome
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")

    # acha a versão do Chrome e prepara para o driver
    servico = Service(ChromeDriverManager().install())

    # abre o Chrome aplicando o serviço acima e opções
    driver = webdriver.Chrome(service = servico, options = chrome_options)

    return driver

def baixar_dados_kaggle(pasta_download):
    # link do Kaggle
    url_dowload = "https://www.kaggle.com/api/v1/datasets/download/thomassimeo/volumetria-tempos-fictcios"

    logging.info("Iniciando o navegador pelo Selenium para baixar os dados do Kaggle...")
    # chama a função iniciar_driver(), que abre o Chrome com a pasta configurada
    driver = iniciar_driver(pasta_download)

    try:
        # acessa a URL do download
        driver.get(url_dowload)
        logging.info("Dowload acionado. Esperando finalização do arquivo...")

        # esperando terminar o download no Chrome
        arquivo_zip = None
        tempo_limite = 60 # segundos máximos de espera
        segundos = 0

        while segundos < tempo_limite:
            time.sleep(2)
            segundos += 2

            # procurando por arquivos ZIP na pasta
            arquivos = os.listdir(pasta_download)
            zips = [f for f in arquivos if f.endswith(".zip")]
            crdownloads = [f for f in arquivos if f.endswith(".crdownload")]

            # se tem já um ZIP e não há dowload temporário em andamento (.crdownload)
            if zips and not crdownloads:
                arquivo_zip = os.path.join(pasta_download, zips[0])
                break

        if not arquivo_zip:
            raise Exception("O tempo limite foi excedodo: download do arquivo ZIP não foi feito.")

        logging.info(f"Download concluído com sucesso: {arquivo_zip}")

    finally:
        # encerra a janela e finaliza o processo do Chrome na memória
        driver.quit()
    
    # descompactando o ZIP com os 60 arquivos .xlsx
    logging.info("Descompactando arquivos de Excel na pasta 'data'...")
    with zipfile.ZipFile(arquivo_zip, "r") as zip_ref:
        zip_ref.extractall(pasta_download)

    # removendo o arquivo ZIP pra não ocupar espaço duplicado
    os.remove(arquivo_zip)
    logging.info("Arquivos extraídos e arquivo ZIP removido com sucesso!")

def converter_xlsx_para_csv(pasta_dados):
    logging.info("Iniciando a conversão de Excel para para CSV...")

    # pegando os arquivos na pasta que são .converter_xlsx para csv
    arquivos = os.listdir(pasta_dados)
    # list comprehension filtrando só os arquivos do Kaggle, sem mexer nos do Airtable
    arquivos_xlsx = [f for f in arquivos if f.endswith(".xlsx") and (f.startswith("HSPLIT") or f.startswith("HAGENT"))]

    total = len(arquivos_xlsx)
    logging.info(f"Total de {total} arquivos de Excel encontrados para serem convertidos.")

    # loop que converte cada arquivo
    for i, arquivo in enumerate(arquivos_xlsx, 1): # o enumerate() gera um contador começando do 1
        caminho_xlsx = os.path.join(pasta_dados, arquivo)

        # troca de Excel para CSV
        nome_csv = arquivo.replace(".xlsx", ".csv")
        caminho_csv = os.path.join(pasta_dados, nome_csv)

        # lê o arquivo do Excel e salva como CSV no padrão brasileiro e com ";"
        df = pd.read_excel(caminho_xlsx)
        df.to_csv(caminho_csv, index = False, sep = ";", encoding = "utf-8-sig") # cria o CSV sem criar uma coluna de index

        logging.info(f"{i}/{total} Convertido: {arquivo} -> {nome_csv}")     
    
    logging.info("Conversões finalizadas com sucesso!")

# garante a pasta criada e executa download -> descompactação -> conversão
if __name__ == "__main__":
    pasta = os.path.abspath("1_Python/data")
    os.makedirs(pasta, exist_ok = True)

    logging.info("===== INÍCIO DA EXTRAÇÃO DO KAGGLE =====")
    baixar_dados_kaggle(pasta)
    converter_xlsx_para_csv(pasta)
    logging.info("===== AÇÃO FINALIZADA COM SUCESSO! =====")