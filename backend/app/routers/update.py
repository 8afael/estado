import sqlite3
import os
import sys
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 1. Configuração de Caminhos Dinâmicos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para o credentials.json
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

# Caminho atualizado para a base de dados 'estado_aberto.db'
PROJETO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DB_PATH = os.path.join(PROJETO_ROOT, "data", "estado_aberto.db")

# --- CONFIGURATION ---
SPREADSHEET_ID = '1s4_d4njw-JcoSSu-hIMgzMeljK3piz7a-z02FOURYCg'
# Alterado para buscar apenas as colunas A e B (Nome e Link)
SHEET_RANGE = 'Jornais!A2:B'

def update_local_db():
    print(f"Tentando conectar ao banco em: {DB_PATH}")
    print(f"Usando credenciais em: {SERVICE_ACCOUNT_FILE}")

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERRO: Ficheiro de credenciais não encontrado em {SERVICE_ACCOUNT_FILE}")
        return

    try:
        # Authentication
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        sheets_service = build('sheets', 'v4', credentials=creds)

        # 1. Fetch data from Google Sheets
        print("Lendo dados do Google Sheets...")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            print("Nenhum dado encontrado para sincronizar.")
            return

        # 2. Connect ao SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Garante que a tabela exista com as colunas corretas (caso seja um banco novo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artigo (
                titulo TEXT UNIQUE,
                link TEXT
            )
        ''')

        # 3. Update table (Apenas colunas nome e link)
        # INSERT OR IGNORE evita erros se o arquivo com o mesmo nome já existir
        sql_query = '''
            INSERT OR IGNORE INTO artigo 
            (titulo, link)
            VALUES (?, ?)
        '''

        print(f"Atualizando {len(rows)} registos...")
        cursor.executemany(sql_query, rows)
        conn.commit()
        conn.close()
        print("Base de dados atualizada com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        sys.exit(1) 

if __name__ == '__main__':
    update_local_db()