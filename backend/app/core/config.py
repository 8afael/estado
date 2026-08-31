import os
from dotenv import load_dotenv

load_dotenv()  # lê o .env na raiz do projeto

def _bool_env(nome: str, default: bool = False) -> bool:
    return os.getenv(nome, str(default)).strip().lower() in ("1", "true", "yes")

BLOQUEAR_EDICAO_AVALIACAO_1 = _bool_env("BLOQUEAR_EDICAO_AVALIACAO_1")
BLOQUEAR_EDICAO_AVALIACAO_3 = _bool_env("BLOQUEAR_EDICAO_AVALIACAO_3")