"""
API pública (somente leitura) do site de resultados — pasta dashboard/.

O site fica hospedado em outro endereço (WordPress do Politeia Conecta) e
chama estas rotas por CORS; as origens permitidas ficam na variável de
ambiente DASHBOARD_ORIGINS (ver app/api/main.py).

Rotas (com o root_path da API: /plataforma/estado/api/dashboard/...):
  GET /artigos          estudos com extração concluída, no formato do site
  GET /artigos/{id}     um estudo (rota "artigoUnico" do config.js)
  GET /triagem          601 registros da triagem (A1, A2, A3 e decisão final)
  GET /base.csv         base de dados dos estudos em CSV (formato largo)

Não exige login e não expõe dados de quem codificou (anonimato).
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.core import database
from app.models import dashboard_service as svc

router = APIRouter(prefix="/api/dashboard", tags=["dashboard (público)"])

# o site pede os dados a cada visita; um cache curto alivia o servidor
CACHE = {"Cache-Control": "public, max-age=300"}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/artigos")
def listar_artigos(db: Session = Depends(get_db)):
    return JSONResponse(svc.listar_artigos(db), headers=CACHE)


@router.get("/artigos/{artigo_id}")
def obter_artigo(artigo_id: int, db: Session = Depends(get_db)):
    artigo = svc.obter_artigo(db, artigo_id)
    if artigo is None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado entre as extrações concluídas.")
    return JSONResponse(artigo, headers=CACHE)


@router.get("/triagem")
def listar_triagem(db: Session = Depends(get_db)):
    return JSONResponse(svc.listar_triagem(db), headers=CACHE)


@router.get("/base.csv")
def baixar_base(db: Session = Depends(get_db)):
    artigos = svc.listar_artigos(db)
    nome = f"base_estado_aberto_{len(artigos)}_artigos_{date.today():%Y-%m-%d}.csv"
    return Response(
        svc.gerar_csv(artigos),
        media_type="text/csv; charset=utf-8",
        headers={**CACHE, "Content-Disposition": f'attachment; filename="{nome}"'},
    )
