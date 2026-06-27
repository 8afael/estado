# core/auth.py
import hashlib
import os
from fastapi import Request
from fastapi.responses import RedirectResponse
from functools import wraps
from typing import Callable, Any, Awaitable

# --- Senha ---
def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    pw_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, pw_hash

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == password_hash

# --- Decorator de login ---
def require_login(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator compatível com FastAPI para rotas async ou sync.
    Redireciona para "/" se usuário não estiver logado.
    Funciona mesmo se o endpoint não tiver request como primeiro argumento.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Tenta localizar Request entre args e kwargs
        request: Request | None = None

        # Procura entre args
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        # Procura entre kwargs
        if request is None:
            for v in kwargs.values():
                if isinstance(v, Request):
                    request = v
                    break

        # Falha segura se não encontrou Request
        if request is None:
            raise RuntimeError(
                f"require_login decorator: Endpoint '{func.__name__}' precisa receber 'request: Request' como argumento"
            )

        # Verifica sessão
        # Verifica sessão
        user = request.session.get("user")
        print(f"DEBUG LOOP: Usuario na sessao é: {user}") # Adicione este print

        if not user:
            return RedirectResponse(url="/estado/login/", status_code=302)
        

        # Executa função (async ou sync)
        result = func(*args, **kwargs)
        if isinstance(result, Awaitable):
            return await result
        return result

    return wrapper



