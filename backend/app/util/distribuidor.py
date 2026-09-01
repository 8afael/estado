import sqlite3
import random
import os

class DistribuidorArtigosIntermediario:
    def __init__(self, db_name="estado_aberto.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Ajuste o caminho se necessário para encontrar a pasta "data"
        projeto_root = os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))
        self.db_path = os.path.join(projeto_root, "data", db_name)

    def criar_tabela_intermediaria(self, cursor):
        """Cria a tabela de associação se ela não existir unificada com o modelo do app"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artigo_avaliacoes_final (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artigo_id INTEGER,
                username TEXT,
                status TEXT DEFAULT 'pendente',
                UNIQUE(artigo_id, username),
                FOREIGN KEY (artigo_id) REFERENCES artigo(id),
                FOREIGN KEY (username) REFERENCES users(username)
            );
        ''')

    def obter_usuarios(self, cursor):
        cursor.execute("SELECT username FROM users WHERE username IN ('av01', 'av02', 'av03', 'av05', 'av06', 'av07', 'av11', 'av12', 'av13', 'av14', 'av15', 'av16')")
        return [row[0] for row in cursor.fetchall()]

    def obter_ids_artigos(self, cursor):
        cursor.execute("SELECT id FROM artigo WHERE resultado_final = 'incluir'")
        return [row[0] for row in cursor.fetchall()]

    def distribuir(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            self.criar_tabela_intermediaria(cursor)
            usuarios = self.obter_usuarios(cursor)
            artigos_ids = self.obter_ids_artigos(cursor)

            num_usuarios = len(usuarios)
            num_artigos = len(artigos_ids)

            if num_usuarios < 1:
                print("Erro: É necessário ter pelo menos 1 usuário para a distribuição.")
                return

            if num_artigos == 0:
                print("Nenhum artigo encontrado com resultado_final = 'incluir'.")
                return

            print("Limpando distribuições anteriores para evitar conflitos...")
            cursor.execute("DELETE FROM artigo_avaliacoes_final")

            print(f"Iniciando distribuição igualitária: {num_artigos} artigos para {num_usuarios} avaliadores (1 por artigo)...")

            # Cada artigo precisa de exatamente 1 revisor
            total_vagas = num_artigos
            
            # Gera blocos da lista de usuários embaralhados até atingir a quantidade exata de artigos
            lista_revisores = []
            while len(lista_revisores) < total_vagas:
                bloco = list(usuarios)
                random.shuffle(bloco)  # Garante sorteio aleatório a cada rodada completa
                lista_revisores.extend(bloco)
            
            # Trunca para o número exato de artigos
            lista_revisores = lista_revisores[:total_vagas]

            novas_ligacoes = []
            contagem_usuarios = {str(u): 0 for u in usuarios}

            # Atribuição direta 1 para 1
            for artigo_id, revisor in zip(artigos_ids, lista_revisores):
                novas_ligacoes.append((artigo_id, revisor))
                contagem_usuarios[str(revisor)] += 1

            # Inserção em lote no banco
            query_insert = '''
                INSERT INTO artigo_avaliacoes_final (artigo_id, username)
                VALUES (?, ?)
            '''
            cursor.executemany(query_insert, novas_ligacoes)
            conn.commit()
            
            print("\n=== RELATÓRIO DE DISTRIBUIÇÃO ===")
            for user, qtd in contagem_usuarios.items():
                print(f"Avaliador: {user} -> {qtd} artigos designados.")
            print("=================================")
            print(f"Sucesso! {len(novas_ligacoes)} registros criados na tabela artigo_avaliacoes_final.")

        except Exception as e:
            conn.rollback()
            print(f"Erro durante a distribuição: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    distribuidor = DistribuidorArtigosIntermediario()
    distribuidor.distribuir()

# import sqlite3
# import random
# import os

# class DistribuidorArtigosIntermediario:
#     def __init__(self, db_name="estado_aberto.db"):
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         # Ajuste o caminho se necessário para encontrar a pasta "data"
#         projeto_root = os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))
#         self.db_path = os.path.join(projeto_root, "data", db_name)

#     def criar_tabela_intermediaria(self, cursor):
#         """Cria a tabela de associação se ela não existir unificada com o modelo do app"""
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS artigo_avaliacoes_final (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 artigo_id INTEGER,
#                 username TEXT,
#                 status TEXT DEFAULT 'pendente',
#                 UNIQUE(artigo_id, username),
#                 FOREIGN KEY (artigo_id) REFERENCES artigo(id),
#                 FOREIGN KEY (username) REFERENCES users(username)
#             );
#         ''')

#     def obter_usuarios(self, cursor):
#         cursor.execute("SELECT username FROM users WHERE username IN ('av01', 'av02', 'av03', 'av05', 'av06', 'av07', 'av11', 'av12', 'av13', 'av14', 'av15', 'av16')")
#         return [row[0] for row in cursor.fetchall()]

#     def obter_ids_artigos(self, cursor):
#         cursor.execute("SELECT id FROM artigo where resultado_final = 'incluir'")
#         return [row[0] for row in cursor.fetchall()]

#     def distribuir(self):
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()

#         try:
#             self.criar_tabela_intermediaria(cursor)
#             usuarios = self.obter_usuarios(cursor)
#             artigos_ids = self.obter_ids_artigos(cursor)

#             num_usuarios = len(usuarios)
#             num_artigos = len(artigos_ids)

#             if num_usuarios < 2:
#                 print("Erro: É necessário ter pelo menos 2 usuários para a distribuição.")
#                 return

#             print(f"Limpando distribuições anteriores para evitar conflitos...")
#             cursor.execute("DELETE FROM artigo_avaliacoes_final")

#             print(f"Iniciando distribuição igualitária: {num_artigos} artigos para {num_usuarios} avaliadores...")

#             # Cada artigo precisa de 1 revisor. Total de "vagas" de avaliação necessárias.
#             total_vagas = num_artigos * 1
            
#             # Criamos uma lista de usuários repetida o suficiente para preencher todas as vagas
#             lista_revisores = []
#             while len(lista_revisores) < total_vagas:
#                 bloco = list(usuarios)
#                 random.shuffle(bloco)  # Garante aleatoriedade em cada ciclo
#                 lista_revisores.extend(bloco)
            
#             # Corta exatamente no tamanho do total de vagas necessárias
#             lista_revisores = lista_revisores[:total_vagas]

#             # Dicionário para acompanhar quantos artigos cada usuário pegou (para o relatório final)
#             contagem_usuarios = {u: 0 for u in map(str, usuarios)}
#             novas_ligacoes = []

#             # Distribuímos de 2 em 2 para cada artigo
#             for i, artigo_id in enumerate(artigos_ids):
#                 idx1 = i * 2
#                 idx2 = i * 2 + 1
                
#                 rev1 = lista_revisores[idx1]
#                 rev2 = lista_revisores[idx2]

#                 # SE O MESMO REVISOR FOR SORTEADO DUAS VEZES PARA O MESMO ARTIGO:
#                 # Buscamos o próximo revisor diferente mais adiante na lista e trocamos (swap)
#                 if rev1 == rev2:
#                     for scan_idx in range(idx2 + 1, len(lista_revisores)):
#                         if lista_revisores[scan_idx] != rev1:
#                             # Faz a troca na lista principal
#                             lista_revisores[idx2], lista_revisores[scan_idx] = lista_revisores[scan_idx], lista_revisores[idx2]
#                             rev2 = lista_revisores[idx2]
#                             break

#                 novas_ligacoes.append((artigo_id, rev1))
#                 novas_ligacoes.append((artigo_id, rev2))
                
#                 contagem_usuarios[str(rev1)] += 1
#                 contagem_usuarios[str(rev2)] += 1

#             # Inserção em lote
#             query_insert = '''
#                 INSERT INTO artigo_avaliacoes_final (artigo_id, username)
#                 VALUES (?, ?)
#             '''
#             cursor.executemany(query_insert, novas_ligacoes)
#             conn.commit()
            
#             print("\n=== RELATÓRIO DE DISTRIBUIÇÃO ===")
#             for user, qtd in contagem_usuarios.items():
#                 print(f"Avaliador: {user} -> {qtd} artigos designados.")
#             print("=================================")
#             print(f"Sucesso! {len(novas_ligacoes)} registros criados na tabela artigo_avaliacoes_final.")

#         except Exception as e:
#             conn.rollback()
#             print(f"Erro durante a distribuição: {e}")
#         finally:
#             conn.close()

# if __name__ == '__main__':
#     distribuidor = DistribuidorArtigosIntermediario()
#     distribuidor.distribuir()

