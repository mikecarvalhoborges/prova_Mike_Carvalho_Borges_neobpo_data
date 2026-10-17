import logging
import os
import requests
import pandas as pd

# garantindo a existência das pastas de logs ou data
os.makedirs("1_Python/data", exist_ok = True)

# configuração dos logs (grava no arquivo e mostra no terminal)
logging.basicConfig (
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler("1_Python/extracao.log", encoding = "utf-8"),
        logging.StreamHandler() # mostrando também no terminal
    ]
)

TOKEN = "patESVvgDKVqNN6So.7d1f4391db2749c4476eba35a16e48801457e2621267109c1b11d77b37ea2433"

def extrair_airtable(url):
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    todos_registros = []

    offset = None # variável de controle da página

    while True:
        # prepara os parâmtros da requisição. Caso tenha offset, será mandado ele    
        params = {}
        if offset:
            params["offset"] = offset
            
        # requisição GET
        response = requests.get(url, headers = headers, params = params)
        data = response.json()
        
        # pegando registros da página atual
        records = data.get("records", [])
        for item in records:
            todos_registros.append(item["fields"])

        logging.info(f"Página coletada com sucesso. Total acumulado: {len(todos_registros)} registros...")

        # checa se existe uma próxima página
        offset = data.get("offset")
        if not offset:
            break # se não tem mais, acaba o loop

    # retorna todos os dados transformados em um DataFrame
    return pd.DataFrame(todos_registros)

if __name__ == "__main__":
        url_forecast = "https://api.airtable.com/v0/appMDw883DjY0pMej/Result%201"
        url_depara = "https://api.airtable.com/v0/appnlzAmDtFtGBjyt/Result%201"

        print ("Iniciando a extração do FORECAST e DEPARA...")
        
        df_forecast = extrair_airtable(url_forecast)
        df_depara = extrair_airtable(url_depara)

        print(f"Sucesso! Total de linhas extraídas do FORECAST: {len(df_forecast)}.\nTotal de linhas extraídas do DEPARA: {len(df_depara)}.")
        print(df_forecast.head(3))

        arquivo_xlsx_forecast = "1_Python/data/FORECAST.xlsx"
        arquivo_csv_forecast = "1_Python/data/FORECAST.csv"
        
        arquivo_xlsx_depara = "1_Python/data/DEPARA_SKILL.xlsx"
        arquivo_csv_depara = "1_Python/data/DEPARA_SKILL.csv"
        
        df_forecast.to_excel(arquivo_xlsx_forecast, index = False)
        df_forecast.to_csv(arquivo_csv_forecast, index = False, sep = ";", encoding = "utf-8-sig")

        df_depara.to_excel(arquivo_xlsx_depara, index = False)
        df_depara.to_csv(arquivo_csv_depara, index = False, sep = ";", encoding = "utf-8-sig")