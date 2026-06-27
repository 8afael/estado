from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets
from app.core import database

from app.routers import (
    auth,
    html_avaliacao,
    html_filtros,
    artigos_routes
)

app = FastAPI(
    title="LabGira API",
    root_path="/estado",
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

# --- Criação de tabelas ---
database.Base.metadata.create_all(bind=database.engine)

# --- Rotas de autenticação ---
app.include_router(auth.router)

app.include_router(html_avaliacao.router)
app.include_router(html_filtros.router)
app.include_router(artigos_routes.router)
