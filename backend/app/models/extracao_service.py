from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import (  # ajuste o import conforme o caminho real do seu projeto
    ExtracaoDadosModel,
    ExtracaoMultivaloresModel,
    ExtracaoOutrosModel,
)
from app.models.field_map import FIELD_MAP, MULTI_FIELDS, OTHER_FIELDS, DIRECT_COLUMN_FIELDS
from app.models.schemas import ExtracaoDadosCreate, ExtracaoDadosUpdate, ExtracaoDadosResponse


def _upsert_multivalores(db: Session, extracao_id: int, campo: str, valores: list[str]) -> None:
    """
    Substitui todas as linhas de extracao_multivalores para (extracao_id, campo)
    pelas novas selecionadas. Evita duplicar em resubmissões e evita ter que
    fazer diff manual — é sempre "apaga o que existia pra esse campo e regrava".
    """
    db.query(ExtracaoMultivaloresModel).filter(
        ExtracaoMultivaloresModel.extracao_id == extracao_id,
        ExtracaoMultivaloresModel.campo == campo,
    ).delete(synchronize_session=False)

    for valor in valores:
        if not valor:
            continue
        db.add(ExtracaoMultivaloresModel(extracao_id=extracao_id, campo=campo, valor=valor))


def _upsert_outro(db: Session, extracao_id: int, campo: str, texto: Optional[str]) -> None:
    """
    extracao_outros tem UniqueConstraint(extracao_id, campo), então
    fazemos get-or-create-or-delete: sem texto -> remove a linha (se existir);
    com texto -> cria ou atualiza.
    """
    existente = db.query(ExtracaoOutrosModel).filter(
        ExtracaoOutrosModel.extracao_id == extracao_id,
        ExtracaoOutrosModel.campo == campo,
    ).first()

    if not texto:
        if existente:
            db.delete(existente)
        return

    if existente:
        existente.texto = texto
    else:
        db.add(ExtracaoOutrosModel(extracao_id=extracao_id, campo=campo, texto=texto))


def salvar_extracao(
    db: Session,
    payload: ExtracaoDadosCreate | ExtracaoDadosUpdate,
    extracao_id: Optional[int] = None,
    somente_enviados: bool = False,   # 🆕 True no autosave, False no submit final
) -> ExtracaoDadosModel:
    dados = payload.model_dump()
    campos_enviados = payload.model_fields_set  # 🆕 quais chaves vieram de fato no payload

    if extracao_id is None:
        registro = ExtracaoDadosModel(
            artigo_id=dados["artigo_id"],
            usuario_id=dados["usuario_id"],
            status=dados.get("status", "em_andamento"),
        )
        db.add(registro)
        db.flush()
    else:
        registro = db.query(ExtracaoDadosModel).filter(ExtracaoDadosModel.id == extracao_id).first()
        if registro is None:
            raise ValueError(f"Extração {extracao_id} não encontrada.")
        if "status" in campos_enviados:
            registro.status = dados["status"]

    # 1) Colunas diretas (single / long / scale)
    for q, coluna in DIRECT_COLUMN_FIELDS.items():
        if somente_enviados and coluna not in campos_enviados:
            continue
        if coluna in dados:
            setattr(registro, coluna, dados[coluna])

    # 2) Colunas de localização/evidência (<qN>_loc)
    for q, meta in FIELD_MAP.items():
        loc_coluna = meta["loc_coluna"]
        if not loc_coluna:
            continue
        if somente_enviados and loc_coluna not in campos_enviados:
            continue
        if loc_coluna in dados:
            setattr(registro, loc_coluna, dados[loc_coluna])

    db.flush()

    # 3) Multi-selects e país -> extracao_multivalores (só os campos enviados)
    for q in MULTI_FIELDS:
        if somente_enviados and q not in campos_enviados:
            continue
        valores = dados.get(q, [])
        campo_eav = FIELD_MAP[q]["eav_campo"]
        _upsert_multivalores(db, registro.id, campo_eav, valores)

    # 4) "Outro — especificar" -> extracao_outros (só os campos enviados)
    for q in OTHER_FIELDS:
        campo_outro = f"{q}_outro"
        if somente_enviados and campo_outro not in campos_enviados:
            continue
        texto = dados.get(campo_outro)
        _upsert_outro(db, registro.id, q, texto)

    return registro


def montar_response(db: Session, registro: ExtracaoDadosModel) -> ExtracaoDadosResponse:
    """Remonta o formato de leitura a partir do ORM + tabelas EAV."""
    campos = {
        coluna: getattr(registro, coluna)
        for coluna in set(DIRECT_COLUMN_FIELDS.values())
        | {meta["loc_coluna"] for meta in FIELD_MAP.values() if meta["loc_coluna"]}
    }

    multivalores_rows = db.query(ExtracaoMultivaloresModel).filter(
        ExtracaoMultivaloresModel.extracao_id == registro.id
    ).all()
    multivalores: dict[str, list[str]] = {}
    for row in multivalores_rows:
        multivalores.setdefault(row.campo, []).append(row.valor)

    outros_rows = db.query(ExtracaoOutrosModel).filter(
        ExtracaoOutrosModel.extracao_id == registro.id
    ).all()
    outros = {row.campo: row.texto for row in outros_rows}

    return ExtracaoDadosResponse(
        id=registro.id,
        artigo_id=registro.artigo_id,
        usuario_id=registro.usuario_id,
        status=registro.status,
        data_criacao=registro.data_criacao,
        data_atualizacao=registro.data_atualizacao,
        campos=campos,
        multivalores=multivalores,
        outros=outros,
    )


def buscar_extracao_por_artigo(db: Session, artigo_id: int) -> Optional[ExtracaoDadosModel]:
    """extracao_dados.artigo_id é unique, então é sempre 0 ou 1 registro."""
    return db.query(ExtracaoDadosModel).filter(ExtracaoDadosModel.artigo_id == artigo_id).first()