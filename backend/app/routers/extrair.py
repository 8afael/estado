import os
import sys
from googleapiclient.discovery import build
from google.oauth2 import service_account

class importaMaterias():
    # --- CONFIGURATION ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

    SPREADSHEET_ID = '1s4_d4njw-JcoSSu-hIMgzMeljK3piz7a-z02FOURYCg'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    )
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    @staticmethod
    def get_already_imported_names():
        """Lê a planilha e retorna um conjunto (set) com os nomes dos arquivos já importados (Coluna A)"""
        try:
            # Busca todos os dados da coluna A (onde ficam os nomes dos arquivos)
            result = importaMaterias.sheets_service.spreadsheets().values().get(
                spreadsheetId=importaMaterias.SPREADSHEET_ID,
                range="Jornais!A2:A"
            ).execute()
            
            rows = result.get('values', [])
            # Extrai o primeiro elemento de cada linha (o nome) e limpa espaços extras
            return {row[0].strip() for row in rows if row}
        except Exception as e:
            print(f"Aviso ao ler registros existentes (pode ser planilha vazia): {e}")
            return set()

    @staticmethod
    def list_child_folders(parent_folder_id: str):
        query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = importaMaterias.drive_service.files().list(q=query, fields="files(id, name)").execute()
        return results.get("files", [])

    @staticmethod
    def run_year_flow(year_folder_id: str):
        print(f"Iniciando processamento ANUAL: {year_folder_id}")
        month_folders = importaMaterias.list_child_folders(year_folder_id)
        for month in month_folders:
            print(f"Mês: {month['name']}")
            importaMaterias.run_main_flow(month["id"])

    @staticmethod
    def run_main_flow(target_folder_id):
        folder = importaMaterias.drive_service.files().get(fileId=target_folder_id, fields="name").execute()
        print(f"Lendo arquivos da pasta: {folder['name']}...")
        
        # 1. Obtém a lista de arquivos que JÁ ESTÃO na planilha para evitar duplicados
        arquivos_existentes = aumentaMaterias = importaMaterias.get_already_imported_names()
        print(f"Total de arquivos já registrados na planilha: {len(arquivos_existentes)}")

        query = f"'{target_folder_id}' in parents and (mimeType = 'application/pdf' or mimeType = 'image/jpeg' or mimeType = 'image/png') and trashed = false"
        results = importaMaterias.drive_service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
        files = results.get("files", [])

        for f in files:
            nome_arquivo = f["name"].strip()

            # 2. VALIDAÇÃO: Se o nome do arquivo já existir no set, pula o loop sem inserir
            if nome_arquivo in arquivos_existentes:
                print(f"Pulado (Já existe na tabela): {nome_arquivo}")
                continue

            print(f"Inserindo novo arquivo: {nome_arquivo}")
            values = [[f["name"], f["webViewLink"]]]
            
            importaMaterias.sheets_service.spreadsheets().values().append(
                spreadsheetId=importaMaterias.SPREADSHEET_ID,
                range="Jornais!A2",
                valueInputOption="USER_ENTERED",
                body={"values": values}
            ).execute()
            
            # Adiciona ao set local para evitar duplicados caso o Drive tenha arquivos com nomes idênticos no mesmo lote
            arquivos_existentes.add(nome_arquivo)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Erro: Faltam argumentos. Uso: python extrair.py <folder_id> <periodo>")
        sys.exit(1)

    folder_id_arg = sys.argv[1]
    periodo_arg = sys.argv[2]

    if periodo_arg == "Ano":
        importaMaterias.run_year_flow(folder_id_arg)
    else:
        importaMaterias.run_main_flow(folder_id_arg)

# import os
# import sys
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# class importaMaterias():
#     # --- CONFIGURATION ---
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

#     # ID da planilha atualizado conforme solicitado
#     SPREADSHEET_ID = '1s4_d4njw-JcoSSu-hIMgzMeljK3piz7a-z02FOURYCg'

#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, 
#         scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
#     )
#     drive_service = build('drive', 'v3', credentials=creds)
#     sheets_service = build('sheets', 'v4', credentials=creds)

#     @staticmethod
#     def list_child_folders(parent_folder_id: str):
#         query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
#         results = importaMaterias.drive_service.files().list(q=query, fields="files(id, name)").execute()
#         return results.get("files", [])

#     @staticmethod
#     def run_year_flow(year_folder_id: str):
#         print(f"Iniciando processamento ANUAL: {year_folder_id}")
#         month_folders = axes = importaMaterias.list_child_folders(year_folder_id)
#         for month in month_folders:
#             print(f"Mês: {month['name']}")
#             importaMaterias.run_main_flow(month["id"])

#     @staticmethod
#     def run_main_flow(target_folder_id):
#         folder = importaMaterias.drive_service.files().get(fileId=target_folder_id, fields="name").execute()
#         print(f"Lendo arquivos da pasta: {folder['name']}...")
        
#         query = f"'{target_folder_id}' in parents and (mimeType = 'application/pdf' or mimeType = 'image/jpeg' or mimeType = 'image/png') and trashed = false"
#         results = importaMaterias.drive_service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
#         files = results.get("files", [])

#         for f in files:
#             print(f"Processando e inserindo na tabela: {f['name']}")
            
#             # Monta a estrutura com apenas: Nome e Link
#             values = [[f["name"], f["webViewLink"]]]
            
#             # Insere os dados na planilha na aba Jornais começando pela coluna A2 (A=Nome, B=Link)
#             importaMaterias.sheets_service.spreadsheets().values().append(
#                 spreadsheetId=importaMaterias.SPREADSHEET_ID,
#                 range="Jornais!A2",
#                 valueInputOption="USER_ENTERED",
#                 body={"values": values}
#             ).execute()

# if __name__ == '__main__':
#     if len(sys.argv) < 3:
#         print("Erro: Faltam argumentos. Uso: python extrair.py <folder_id> <periodo>")
#         sys.exit(1)

#     folder_id_arg = sys.argv[1]
#     periodo_arg = sys.argv[2]

#     if periodo_arg == "Ano":
#         importaMaterias.run_year_flow(folder_id_arg)
#     else:
#         importaMaterias.run_main_flow(folder_id_arg)