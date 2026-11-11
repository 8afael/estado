import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets
from app.core import database

from app.routers import (
    auth,
    html_avaliacao,
    html_filtros,
    artigos_routes,
    resultados_router,
    avaliacoes_router,
    avaliacao3_router,
    extracao_router,
    avaliacao_final_router,
    regras_router,
    dashboard_router
)

app = FastAPI(
    title="Estado API",
    root_path="/plataforma/estado",
    docs_url="/docs",          
    openapi_url="/openapi.json"
)


# --- Middleware de sessão ---
app.add_middleware(
    SessionMiddleware, 
    secret_key=secrets.token_hex(32),
    session_cookie="session_jornais_v1",
    same_site="lax",
    https_only=False,
    path="/")

# --- Site de resultados (dashboard/) hospedado em outro endereço ---
# Origens que podem ler a API pública /api/dashboard, separadas por vírgula.
# Ex.: DASHBOARD_ORIGINS=https://politeiaconecta.org,http://localhost:8000
DASHBOARD_ORIGINS = [o.strip() for o in os.getenv(
    "DASHBOARD_ORIGINS", "https://politeiaconecta.org,http://localhost:8000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=DASHBOARD_ORIGINS,
    allow_methods=["GET"],
    allow_credentials=False,   # a API pública não usa cookie de sessão
)
# a lista de artigos tem ~2,6 MB; comprimida cai para algumas centenas de KB
app.add_middleware(GZipMiddleware, minimum_size=1024)

# --- Criação de tabelas ---
database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
async def raiz_para_login():
    # Usamos o caminho completo que o navegador deve seguir
    return RedirectResponse(url="/plataforma/estado/login/", status_code=302)


# --- Rotas de autenticação ---
app.include_router(auth.router)
app.include_router(html_avaliacao.router)
app.include_router(html_filtros.router)
app.include_router(artigos_routes.router)
app.include_router(resultados_router.router)
app.include_router(avaliacoes_router.router)
app.include_router(avaliacao3_router.router)
app.include_router(extracao_router.router)
app.include_router(avaliacao_final_router.router)
app.include_router(regras_router.router)
app.include_router(dashboard_router.router)
