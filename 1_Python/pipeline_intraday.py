import logging
import os
import time

# importando as funções dos outros scripts
from extrair_airtable import extrair_airtable
from extrair_kaggle import baixar_dados_kaggle, converter_xlsx_para_csv

# configurando os logs para centralizar num arquivo só
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler("1_Python/extracao.log", encoding = "utf-8"),
        logging.StreamHandler()
    ]
)

# os caminhos e confifurações

pasta_dados = os.path.abspath("1_Python/data")
url_forecast = "https://api.airtable.com/v0/appMDw883DjY0pMej/Result%201"
url_depara = "https://api.airtable.com/v0/appnlzAmDtFtGBjyt/Result%201"

def executar_pipeline():
    logging.info("=====INÍCIO DO PIPELINE DO INTRADAY=====")
    os.makedirs(pasta_dados, exist_ok = True)

    # extraindo dados do Airtable (FORECAST e DEPARA_SKILL)
    logging.info("=====1: Extração do Airtable=====")
    df_forecast = extrair_airtable(url_forecast)
    df_depara = extrair_airtable(url_depara)

    df_forecast.to_excel(os.path.join(pasta_dados, "FORECAST.xlsx"), index = False)
    df_forecast.to_csv(os.path.join(pasta_dados, "FORECAST.csv"), index = False, sep = ";", encoding = "utf-8-sig")
    
    df_depara.to_excel(os.path.join(pasta_dados, "DEPARA_SKILL.xlsx"), index = False)
    df_depara.to_csv(os.path.join(pasta_dados, "DEPARA_SKILL.csv"), index = False, sep = ";", encoding = "utf-8-sig")
    
    logging.info(f"Airtable concluído: {len(df_forecast)} linhas de FORECAST, {len(df_depara)} de DEPARA_SKILL.")

    logging.info("=====2: Extração do Kaggle=====")
    baixar_dados_kaggle(pasta_dados)
    converter_xlsx_para_csv(pasta_dados)

    logging.info("===== PIPELINE CONCLUÍDO COM SUCESSO! =====")

# executando o pipeline uma vez imediatamente e repetindo a cada intervalo de segundos
if __name__ == "__main__":
    intervalo = 10 # roda a cada 1 hora (3600 segundos)

    while True:
        executar_pipeline()
        logging.info(f"Aguardando {intervalo // 60} minutos para a próxima execução do pipeline...")
        time.sleep(intervalo)