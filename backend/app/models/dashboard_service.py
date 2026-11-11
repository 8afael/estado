"""
Leitura das extrações para o site de resultados (pasta dashboard/).

Converte o que está gravado nas tabelas extracao_dados, extracao_multivalores,
extracao_outros (e extracao_derivada) para o formato que o assets/app.js do
site espera, o mesmo do antigo dashboard/data/artigos.json:

  - nomes de variável do codebook  (q3_referencia_bibliografica -> q03_referencia)
  - múltipla escolha como lista de CÓDIGOS do codebook  ("Estudo de caso" -> 1)
  - "Outro — especificar" em <variavel>_outro, localização/evidência em <variavel>_evid
  - campos auxiliares do site: ano, _paises_iso, _regioes e as codificações d_*

Nada é agregado no servidor: cada artigo sai com as suas respostas e os
gráficos são calculados no navegador.

Anonimato: o site é público, então NÃO saem usuario_id, nome de usuário,
codificador nem qualquer outro dado de quem fez a extração.
"""
import csv
import io
import logging
import re
import unicodedata
from typing import Iterable, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.field_map import FIELD_MAP
from app.models.dashboard_codigos import CODIGOS, PAISES, VARIAVEIS

log = logging.getLogger(__name__)

STATUS_PUBLICADO = "concluido"

# Rótulos gravados com grafia diferente da do codebook -> rótulo do codebook
APELIDOS = {
    44: {"económicos": "econômicos"},
}

# Códigos usados pelo site para a Q5 (abrangência territorial)
Q5_PAISES_IDENTIFICADOS = 1


def _norm(s) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(s)).strip().lower())


def _num(chave: str) -> int:
    return int(re.match(r"q(\d+)", chave).group(1))


def _vazio(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


# ---------------------------------------------------------------- mapeamento
# coluna de extracao_dados -> nome da variável no site
COLUNAS_SITE: dict[str, str] = {}
for _chave, _m in FIELD_MAP.items():
    if _chave == "q5_paises":
        continue
    _var = VARIAVEIS[_num(_chave)]
    if _m["coluna"]:
        # Q25: o codebook chama a questão de "pares conceituais"; o texto livre
        # que o formulário grava vai para q25_relacoes_texto_livre no site.
        COLUNAS_SITE[_m["coluna"]] = "q25_relacoes_texto_livre" if _chave == "q25" else _var
    if _m["loc_coluna"]:
        COLUNAS_SITE[_m["loc_coluna"]] = _var + "_evid"

# campo de extracao_multivalores / extracao_outros (ex.: "q9") -> variável do site
CAMPOS_SITE = {k: VARIAVEIS[_num(k)] for k in FIELD_MAP if k != "q5_paises"}

_avisados: set = set()


def _codigo(campo: str, rotulo: str) -> Optional[int]:
    n = _num(campo)
    r = _norm(rotulo)
    r = APELIDOS.get(n, {}).get(r, r)
    cod = CODIGOS.get(n, {}).get(r)
    if cod is None and (campo, r) not in _avisados:
        _avisados.add((campo, r))
        log.warning("dashboard: rótulo sem código no codebook: %s = %r", campo, rotulo)
    return cod


def _chave_alfabetica(s: str) -> str:
    """Ordem alfabética sem acento (Índia antes de Indonésia, Áustria entre Argentina e Azerbaijão)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def _ano(referencia: Optional[str]) -> Optional[int]:
    m = re.search(r"\((\d{4})[a-z]?[,)]", referencia or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- leitura
def _ler(db: Session, artigo_id: Optional[int]) -> tuple:
    filtro = "AND e.artigo_id = :aid" if artigo_id is not None else ""
    p = {"st": STATUS_PUBLICADO, "aid": artigo_id}
    dados = db.execute(text(
        f"SELECT e.*, a.codigo AS _artigo_codigo FROM extracao_dados e "
        f"JOIN artigo a ON a.id = e.artigo_id WHERE e.status = :st {filtro}"), p).mappings().all()
    multi = db.execute(text(
        f"SELECT m.extracao_id, m.campo, m.valor FROM extracao_multivalores m "
        f"JOIN extracao_dados e ON e.id = m.extracao_id WHERE e.status = :st {filtro} "
        f"ORDER BY m.id"), p).all()
    outros = db.execute(text(
        f"SELECT o.extracao_id, o.campo, o.texto FROM extracao_outros o "
        f"JOIN extracao_dados e ON e.id = o.extracao_id WHERE e.status = :st {filtro}"), p).all()
    try:
        deriv = db.execute(text(
            f"SELECT d.artigo_id, d.campo, d.valor FROM extracao_derivada d "
            f"JOIN extracao_dados e ON e.artigo_id = d.artigo_id WHERE e.status = :st {filtro}"), p).all()
    except Exception:  # tabela ainda não criada/importada
        db.rollback()
        log.warning("dashboard: tabela extracao_derivada indisponível; d_* ficarão vazios")
        deriv = []
    return dados, multi, outros, deriv


def _montar(row, multi: list, outros: list, deriv: list) -> dict:
    o: dict = {"q01_id_estudo": str(row["artigo_id"])}
    cod = row["_artigo_codigo"]
    if not _vazio(cod) and _norm(cod) not in ("n/a", "na"):
        o["artigo_codigo"] = cod.strip()

    for coluna, var in COLUNAS_SITE.items():
        v = row[coluna]
        if not _vazio(v):
            o[var] = v.strip() if isinstance(v, str) else str(v)

    listas: dict[str, set] = {}
    paises: list[str] = []
    for campo, valor in multi:
        if campo == "q5_paises":
            if valor not in paises:
                paises.append(valor)
            continue
        if campo not in CAMPOS_SITE:
            continue
        c = _codigo(campo, valor)
        if c is not None:
            listas.setdefault(CAMPOS_SITE[campo], set()).add(c)

    # Q5: o formulário grava a lista de países à parte; "países identificados"
    # (código 1) vale sempre que houver país na lista.
    paises.sort(key=_chave_alfabetica)
    if paises:
        listas.setdefault(CAMPOS_SITE["q5"], set()).add(Q5_PAISES_IDENTIFICADOS)
        o["q05_pais_lista"] = "; ".join(paises)
    o["_paises_iso"] = [PAISES[p][0] for p in paises if p in PAISES]
    o["_regioes"] = sorted({PAISES[p][1] for p in paises if p in PAISES})
    for p in paises:
        if p not in PAISES and ("pais", p) not in _avisados:
            _avisados.add(("pais", p))
            log.warning("dashboard: país sem ISO/região em dashboard_codigos.PAISES: %r", p)

    for var, cods in listas.items():
        o[var] = sorted(cods)
    for campo, texto in outros:
        if campo in CAMPOS_SITE and not _vazio(texto):
            o[CAMPOS_SITE[campo] + "_outro"] = texto.strip()
    for campo, valor in deriv:
        if not _vazio(valor):
            o[campo] = valor

    o["ano"] = _ano(o.get("q03_referencia"))
    o["status"] = row["status"]
    if row["data_atualizacao"] is not None:
        o["data_atualizacao"] = str(row["data_atualizacao"])[:19]
    return o


def listar_artigos(db: Session, artigo_id: Optional[int] = None) -> list[dict]:
    dados, multi, outros, deriv = _ler(db, artigo_id)
    m_por, o_por, d_por = {}, {}, {}
    for eid, campo, valor in multi:
        m_por.setdefault(eid, []).append((campo, valor))
    for eid, campo, texto in outros:
        o_por.setdefault(eid, []).append((campo, texto))
    for aid, campo, valor in deriv:
        d_por.setdefault(aid, []).append((campo, valor))
    return [_montar(r, m_por.get(r["id"], []), o_por.get(r["id"], []), d_por.get(r["artigo_id"], []))
            for r in dados]


def obter_artigo(db: Session, artigo_id: int) -> Optional[dict]:
    r = listar_artigos(db, artigo_id)
    return r[0] if r else None


# ---------------------------------------------------------------- triagem
DECISAO_ROTULO = {"inclusao_final": "Incluído", "exclusao_final": "Excluído"}


def listar_triagem(db: Session) -> dict:
    rows = db.execute(text(
        "SELECT artigo_id, titulo, a1, a2, a3, decisao_final, atualizado_em "
        "FROM snapshot_decisao_final ORDER BY artigo_id")).mappings().all()
    regs = [{"id": r["artigo_id"], "titulo": r["titulo"] or "",
             "a1": r["a1"] or "", "a2": r["a2"] or "", "a3": r["a3"] or "",
             "decisao": DECISAO_ROTULO.get(r["decisao_final"], r["decisao_final"])} for r in rows]
    atual = max((r["atualizado_em"] for r in rows if r["atualizado_em"]), default=None)
    return {"atualizado_em": str(atual)[:19] if atual else None, "registros": regs}


# ---------------------------------------------------------------- CSV
def _colunas_csv() -> list[str]:
    """Mesma estrutura da base publicada (formato largo, Sim/Não por opção),
    na ordem do codebook, sem dados de quem codificou."""
    cols = ["q01_id_estudo"]
    for n in sorted(VARIAVEIS):
        if n in (1, 2):
            continue
        var = VARIAVEIS[n]
        chave = f"q{n}"
        if n in CODIGOS:
            cols += [f"{var}_{c}" for c in sorted(set(CODIGOS[n].values()))]
            if FIELD_MAP.get(chave, {}).get("tem_outro"):
                cols.append(var + "_outro")
            if n == 5:
                cols.append("q05_pais_lista")
            continue
        if n == 25:
            cols += ["q25_relacoes_texto_livre", "q25_pares_conceituais_evid"]
            continue
        cols.append(var)
        if FIELD_MAP.get(chave, {}).get("tem_outro"):
            cols.append(var + "_outro")
        if FIELD_MAP.get(chave, {}).get("loc_coluna"):
            cols.append(var + "_evid")
    return cols


def gerar_csv(artigos: Iterable[dict]) -> str:
    artigos = sorted(artigos, key=lambda a: _chave_alfabetica(a.get("q03_referencia", "")))
    base = _colunas_csv()
    derivadas = sorted({k for a in artigos for k in a if k.startswith("d_")})
    cols = base + ["ano", "artigo_codigo", "status", "data_atualizacao"] + derivadas
    # coluna larga -> (variável, código), ex.: "q09_desenho_3" -> ("q09_desenho", 3)
    largas = [(f"{VARIAVEIS[n]}_{c}", VARIAVEIS[n], c) for n in CODIGOS for c in set(CODIGOS[n].values())]
    buf = io.StringIO()
    buf.write("﻿")  # BOM para o Excel reconhecer UTF-8
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for a in artigos:
        linha = {k: v for k, v in a.items() if not isinstance(v, list)}
        for col, var, cod in largas:
            linha[col] = "Sim" if cod in a.get(var, ()) else "Não"
        w.writerow(linha)
    return buf.getvalue()
