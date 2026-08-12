import csv
import sqlite3

# --- CONFIGURAÇÕES ---
CAMINHO_CSV = '/Users/rafa/Documents/projetos/estado.csv'  # Nome ou caminho do seu arquivo CSV
CAMINHO_BANCO = '/Users/rafa/Documents/projetos/estado_aberto/data/estado_aberto.db'    # Nome ou caminho do seu arquivo de banco SQLite

def atualizar_banco_de_dados():
    # 1. Conecta ao banco de dados SQLite
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()
    
    registros_atualizados = 0
    
    # 2. Abre e lê o arquivo CSV
    with open(CAMINHO_CSV, mode='r', encoding='utf-8-sig') as file:
        # csv.DictReader usa a primeira linha do CSV para mapear os nomes das colunas
        leitor_csv = csv.DictReader(file)
        
        for linha in leitor_csv:
            # Pega os valores das colunas removendo espaços vazios extras (.strip())
            link_compartilhamento = linha['link'].strip()
            link_banco = linha['link'].strip()
            nome_arquivo = linha['nome'].strip()
            
            # 3. Compara se os valores das colunas de link são iguais
            if link_compartilhamento == link_banco:
                # Executa o UPDATE no registro correspondente onde o campo link for igual
                query = """
                    UPDATE artigo 
                    SET nome_arquivo = ? 
                    WHERE link = ?
                """
                cursor.execute(query, (nome_arquivo, link_banco))
                
                # Conta quantos registros foram alterados nessa instrução
                registros_atualizados += cursor.rowcount

    # 4. Salva as alterações e fecha a conexão com o banco
    conn.commit()
    conn.close()
    
    print(f"Sucesso! {registros_atualizados} registros foram atualizados na tabela 'artigo'.")

# --- EXECUÇÃO ---
if __name__ == '__main__':
    atualizar_banco_de_dados()