"""
Importa as codificações derivadas (d_*) para a tabela extracao_derivada.

A fonte é o artigos.json do site de resultados (gerado pelo build_data.py a
partir da aba 5_Codificacao_derivada da Matriz). Só usa a biblioteca padrão,
então roda tanto no servidor quanto fora do container.

Uso (na raiz do projeto):
    python3 backend/app/util/importar_derivadas.py \
        --db data/estado_aberto.db --json dashboard/data/artigos.json

É idempotente: reimportar atualiza os valores existentes (upsert) e apaga as
variáveis d_* que deixaram de existir para cada artigo do arquivo.
"""
import argparse
import json
import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS extracao_derivada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artigo_id INTEGER NOT NULL REFERENCES artigo(id) ON DELETE CASCADE,
    campo VARCHAR NOT NULL,
    valor TEXT NOT NULL,
    CONSTRAINT uq_extracao_derivada_campo UNIQUE (artigo_id, campo)
);
CREATE INDEX IF NOT EXISTS ix_extracao_derivada_artigo_id ON extracao_derivada (artigo_id);
"""


def importar(con: sqlite3.Connection, artigos: list) -> dict:
    con.executescript(DDL)
    existentes = {r[0] for r in con.execute("SELECT id FROM artigo")}
    gravados, ignorados = 0, []
    with con:
        for a in artigos:
            aid = int(a["q01_id_estudo"])
            if aid not in existentes:
                ignorados.append(aid)
                continue
            campos = {k: str(v) for k, v in a.items() if k.startswith("d_") and v not in (None, "")}
            for campo, valor in campos.items():
                con.execute(
                    "INSERT INTO extracao_derivada (artigo_id, campo, valor) VALUES (?, ?, ?) "
                    "ON CONFLICT(artigo_id, campo) DO UPDATE SET valor = excluded.valor",
                    (aid, campo, valor),
                )
                gravados += 1
            marcadores = ",".join("?" * len(campos)) or "''"
            con.execute(
                f"DELETE FROM extracao_derivada WHERE artigo_id = ? AND campo NOT IN ({marcadores})",
                (aid, *campos),
            )
    total = con.execute("SELECT COUNT(*) FROM extracao_derivada").fetchone()[0]
    return {"gravados": gravados, "artigos_ignorados": ignorados, "total_na_tabela": total}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db", required=True)
    p.add_argument("--json", required=True)
    args = p.parse_args()
    with open(args.json, encoding="utf-8") as f:
        artigos = json.load(f)
    con = sqlite3.connect(args.db)
    print(importar(con, artigos))
    con.close()
