

def normalizar(valor: str | None) -> str | None:
    if not valor:
        return None
    return " ".join(valor.strip().split())
