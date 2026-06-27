import subprocess
import os
import sys
import sqlite3
from typing import Optional
from app.core.auth import require_login
from fastapi import APIRouter, HTTPException, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Configuração dos caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJETO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DB_PATH = os.path.join(PROJETO_ROOT, "data", "jornaisn.db")
CURRENT_DIR = BASE_DIR  # Para compatibilidade com os scripts extrair.py e update.py

class DeleteResponse(BaseModel):
    status: str
    mensagem: str

@router.get("/tools", response_class=HTMLResponse)
@require_login
async def get_tools(request: Request):
    return templates.TemplateResponse("tools.html", {"request": request})


@router.post("/executar-extrair")
@require_login
async def executar_extrair(
    request: Request,
    link: str = Form(None),    
    periodo: str = Form(None)  # "Mês" ou "Ano"
):
    script_path = os.path.join(CURRENT_DIR, "extrair.py")
    
    if not link or not periodo:
        return {"status": "erro", "mensagem": "ID da pasta ou Período não fornecidos."}

    try:
        # Chamada do subprocesso passando os argumentos lidos pelo sys.argv no extrair.py
        processo = subprocess.run(
            [sys.executable, script_path, link, periodo],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "sucesso", "output": processo.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "erro", "detalhes": e.stderr or e.stdout}


@router.post("/executar-update")
@require_login
async def executar_update(request: Request):
    script_path = os.path.join(CURRENT_DIR, "update.py")
    
    try:
        processo = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "base de dados atualizada", "output": processo.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "erro no update", "detalhes": e.stderr or e.stdout}


# ==================== NOVAS ROTAS PARA PESQUISA E EXCLUSÃO ====================

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite"""
    try:
        # Verifica se o diretório existe, se não, cria
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@router.get("/api/buscar-por-id/{id_registro}")
@require_login
async def buscar_por_id(id_registro: int, request: Request):
    """
    Busca um registro pelo ID na tabela jornais
    """
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": "Erro ao conectar ao banco de dados"}
        )
    
    try:
        cursor = conn.cursor()
        
        # Busca diretamente na tabela jornais pelo ID
        cursor.execute("""
            SELECT id, nomeArquivo, * FROM jornais WHERE id = ?
        """, (id_registro,))
        
        registro = cursor.fetchone()
        
        if registro:
            # Converte o registro para dicionário
            registro_dict = dict(registro)
            return {
                "status": "sucesso",
                "dados": [registro_dict],
                "tabela": "jornais"
            }
        else:
            return {
                "status": "erro",
                "mensagem": f"Nenhum registro encontrado com ID {id_registro} na tabela jornais",
                "dados": []
            }
            
    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": f"Erro no banco de dados: {str(e)}"}
        )
    finally:
        conn.close()


@router.get("/api/buscar-por-nome/{nome_arquivo}")
@require_login
async def buscar_por_nome(nome_arquivo: str, request: Request):
    """
    Busca registros pelo nome do arquivo na tabela jornais (busca parcial, case-insensitive)
    """
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": "Erro ao conectar ao banco de dados"}
        )
    
    try:
        cursor = conn.cursor()
        
        # Busca na tabela jornais pelo nomeArquivo
        cursor.execute("""
            SELECT id, nomeArquivo, * FROM jornais 
            WHERE nomeArquivo LIKE ? 
            ORDER BY id
        """, (f'%{nome_arquivo}%',))
        
        registros = cursor.fetchall()
        
        if registros:
            resultados = []
            for registro in registros:
                registro_dict = dict(registro)
                resultados.append(registro_dict)
            
            return {
                "status": "sucesso",
                "dados": resultados,
                "quantidade": len(resultados),
                "tabela": "jornais"
            }
        else:
            return {
                "status": "erro",
                "mensagem": f"Nenhum registro encontrado com nome de arquivo contendo '{nome_arquivo}' na tabela jornais",
                "dados": []
            }
            
    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": f"Erro no banco de dados: {str(e)}"}
        )
    finally:
        conn.close()


@router.delete("/api/excluir-registro/{id_registro}")
@require_login
async def excluir_registro(id_registro: int, request: Request):
    """
    Exclui um registro pelo ID na tabela jornais
    """
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": "Erro ao conectar ao banco de dados"}
        )
    
    try:
        cursor = conn.cursor()
        
        # Primeiro, busca o registro para confirmar que existe e obter seus dados
        cursor.execute("SELECT id, nomeArquivo FROM jornais WHERE id = ?", (id_registro,))
        registro_antes = cursor.fetchone()
        
        if not registro_antes:
            return {
                "status": "erro",
                "mensagem": f"Registro com ID {id_registro} não encontrado na tabela jornais"
            }
        
        # Executa a exclusão
        cursor.execute("DELETE FROM jornais WHERE id = ?", (id_registro,))
        
        if cursor.rowcount == 0:
            return {
                "status": "erro",
                "mensagem": f"Nenhum registro foi excluído (ID {id_registro} não encontrado)"
            }
        
        conn.commit()
        
        # Converte o registro excluído para dicionário
        registro_dict = dict(registro_antes) if registro_antes else {}
        
        return {
            "status": "sucesso",
            "mensagem": f"Registro com ID {id_registro} e nome '{registro_dict.get('nomeArquivo', 'N/A')}' excluído com sucesso da tabela 'jornais'",
            "registro_excluido": registro_dict,
            "tabela": "jornais"
        }
        
    except sqlite3.Error as e:
        conn.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": f"Erro ao excluir registro: {str(e)}"}
        )
    finally:
        conn.close()


@router.get("/api/verificar-tabela")
@require_login
async def verificar_tabela(request: Request):
    """
    Verifica se a tabela jornais existe e mostra sua estrutura
    """
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": "Erro ao conectar ao banco de dados"}
        )
    
    try:
        cursor = conn.cursor()
        
        # Verifica se a tabela jornais existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='jornais'
        """)
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            return {
                "status": "erro",
                "mensagem": "Tabela 'jornais' não encontrada no banco de dados",
                "tabela_existe": False
            }
        
        # Obtém informações da tabela
        cursor.execute("PRAGMA table_info(jornais)")
        colunas = cursor.fetchall()
        
        # Conta o número de registros
        cursor.execute("SELECT COUNT(*) as total FROM jornais")
        total_registros = cursor.fetchone()['total']
        
        # Obtém os últimos 5 registros como exemplo
        cursor.execute("SELECT id, nomeArquivo FROM jornais ORDER BY id DESC LIMIT 5")
        ultimos_registros = [dict(row) for row in cursor.fetchall()]
        
        return {
            "status": "sucesso",
            "tabela_existe": True,
            "nome_tabela": "jornais",
            "colunas": [{"nome": col[1], "tipo": col[2]} for col in colunas],
            "total_registros": total_registros,
            "ultimos_registros": ultimos_registros
        }
        
    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": str(e)}
        )
    finally:
        conn.close()


@router.get("/api/buscar")
@require_login
async def buscar_registros(request: Request,
    id: Optional[int] = Query(None, description="ID do registro"),
    nome: Optional[str] = Query(None, description="Nome do arquivo")
):
    """
    Busca registros usando query parameters (alternativa mais flexível)
    """
    if id:
        return await buscar_por_id(id)
    elif nome:
        return await buscar_por_nome(nome)
    else:
        return JSONResponse(
            status_code=400,
            content={"status": "erro", "mensagem": "Forneça 'id' ou 'nome' como parâmetro"}
        )


@router.get("/api/listar-todos")
@require_login
async def listar_todos(request: Request,
    limite: int = Query(100, description="Limite de registros a retornar", ge=1, le=1000),
    offset: int = Query(0, description="Offset para paginação", ge=0)
):
    """
    Lista todos os registros da tabela jornais com paginação
    """
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": "Erro ao conectar ao banco de dados"}
        )
    
    try:
        cursor = conn.cursor()
        
        # Conta total de registros
        cursor.execute("SELECT COUNT(*) as total FROM jornais")
        total = cursor.fetchone()['total']
        
        # Busca registros com paginação
        cursor.execute("""
            SELECT id, nomeArquivo, * FROM jornais 
            ORDER BY id 
            LIMIT ? OFFSET ?
        """, (limite, offset))
        
        registros = cursor.fetchall()
        resultados = [dict(registro) for registro in registros]
        
        return {
            "status": "sucesso",
            "dados": resultados,
            "total": total,
            "limite": limite,
            "offset": offset,
            "tabela": "jornais"
        }
        
    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "mensagem": f"Erro no banco de dados: {str(e)}"}
        )
    finally:
        conn.close()
        
