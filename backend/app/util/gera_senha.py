# gerar_senha.py
import hashlib
import os
import sys

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    pw_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, pw_hash

if __name__ == "__main__":
    # Verifica se você passou a senha como argumento
    if len(sys.argv) > 1:
        senha = sys.argv[1]
        salt, pw_hash = hash_password(senha)
        print(f"\nSenha: {senha}")
        print(f"SALT: {salt}")
        print(f"HASH: {pw_hash}\n")
    else:
        print("Uso: python gerar_senha.py SUA_SENHA")