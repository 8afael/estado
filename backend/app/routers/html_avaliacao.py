from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core import database
from app.models import models
from app.models import crud
from app.core.auth import require_login
from app.core.dicionarios import DICIONARIOS_AVALIACAO


# Criamos o roteador específico para avaliações
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/avaliacao", response_class=HTMLResponse)
@require_login
def exibir_formulario(
    request: Request, 
    artigo_id: Optional[int] = None, # 1. Ajustado para evitar erros caso a URL venha mal formatada
    db: Session = Depends(get_db)
):
    if not artigo_id:
        raise HTTPException(status_code=400, detail="ID do artigo não fornecido.")

    # 1. Busca o artigo pedido na base de dados pelo ID
    artigo = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")

    # 2. Recupera o utilizador logado direto da sessão
    username_sessao = request.session.get("user")
    class UsuarioSessao:
        def __init__(self, username):
            self.username = username
    current_user = UsuarioSessao(username_sessao)

    # 3. Buscar o ID numérico do usuário
    user_db = db.query(models.User).filter(models.User.username == username_sessao).first()
    
    # 4. Busca se o avaliador atual já possui um registro salvo para este artigo
    avaliacao_existente = None
    if user_db:
        avaliacao_existente = db.query(models.AvaliacaoModel).filter(
            models.AvaliacaoModel.usuario_id == user_db.id,
            models.AvaliacaoModel.artigo_id == artigo_id,
            models.AvaliacaoModel.etapa == 1
        ).first()

    # 🟢 EXTRAI APENAS O LINK DO ARTIGO
    artigo_link = artigo.link if artigo else None

    # 5. Envia as variáveis necessárias para o HTML
    return templates.TemplateResponse(
        "avaliacao_form.html", 
        {
            "request": request,
            "artigo_id": artigo_id,
            "artigo_link": artigo_link,  # 🟢 PASSANDO APENAS O LINK ISOLADO
            "avaliacao": avaliacao_existente,  
            "dicionarios": DICIONARIOS_AVALIACAO,  
            "current_user": current_user
        }
    )

@router.post("/salvar-avaliacao/")
@require_login
async def salvar_formulario(
    request: Request,
    artigo_id_real: int = Form(...),
    page: int = Form(1),
    
    # Dados do artigo recebidos do formulário
    titulo: str = Form(...),
    resumo: str = Form(...),
    codigo: str = Form(...),
    ano_publicacao: int = Form(...),
    idioma: str = Form(...),
    paises_autores: Optional[str] = Form(None),
    pais_estudado: Optional[str] = Form(None),
    tipo_documento: str = Form(...),
    abordagem_metodologica: str = Form(...),
    
    # Critérios de avaliação
    t1_termos_chave: str = Form(...),
    t2_contexto_publico: str = Form(...),
    t3_tema_institucional: str = Form(...),
    t4_analise_direta: str = Form(...),
    
    # Tecnologias e Notas
    usou_ia: Optional[str] = Form(None),
    ia_prompts: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    
    db: Session = Depends(get_db)
):
    username_logado = request.session.get("user")
    user_db = db.query(models.User).filter(models.User.username == username_logado).first()
    
    if not user_db:
        return RedirectResponse(url="/estado/login/", status_code=303)

    # [OPCIONAL] Mantido caso queira manter a tabela global 'artigo' atualizada em paralelo
    artigo = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == artigo_id_real).first()
    if artigo:
        artigo.titulo = titulo
        artigo.resumo = resumo
        artigo.codigo = codigo
        artigo.ano_publicacao = ano_publicacao
        artigo.idioma = idioma
        artigo.paises_autores = paises_autores
        artigo.pais_estudado = pais_estudado
        artigo.tipo_documento = tipo_documento
        artigo.abordagem_metodologica = abordagem_metodologica
        db.add(artigo)

    etapa_atual = 1
          
    avaliacao_existente = db.query(models.AvaliacaoModel).filter(
        models.AvaliacaoModel.usuario_id == user_db.id,
        models.AvaliacaoModel.artigo_id == artigo_id_real,
        models.AvaliacaoModel.etapa == etapa_atual
    ).first()

    if av_existente := avaliacao_existente:
        # 🟢 CORREÇÃO: Atualizando os NOVOS campos também no registro de avaliação existente
        av_existente.titulo = titulo
        av_existente.resumo = resumo
        av_existente.codigo = codigo
        av_existente.ano_publicacao = ano_publicacao
        av_existente.idioma = idioma
        av_existente.paises_autores = paises_autores
        av_existente.pais_estudado = pais_estudado
        av_existente.tipo_documento = tipo_documento
        av_existente.abordagem_metodologica = abordagem_metodologica
        
        # Campos de critérios e IA
        av_existente.t1_termos_chave = t1_termos_chave
        av_existente.t2_contexto_publico = t2_contexto_publico
        av_existente.t3_tema_institucional = t3_tema_institucional
        av_existente.t4_analise_direta = t4_analise_direta
        av_existente.usou_ia = usou_ia
        av_existente.ia_ferramentas_uso = usou_ia
        av_existente.ia_prompts = ia_prompts
        av_existente.observacoes = observacoes
        av_existente.resultado = "Concluído"
        
        db.add(av_existente)
    else:
        # 🟢 CORREÇÃO: Inserindo os NOVOS campos na criação da nova avaliação
        nova_avaliacao = models.AvaliacaoModel(
            usuario_id=user_db.id,
            artigo_id=artigo_id_real,
            etapa=etapa_atual, 
            titulo=titulo,
            resumo=resumo,
            codigo=codigo,
            ano_publicacao=ano_publicacao,
            idioma=idioma,
            paises_autores=paises_autores,
            pais_estudado=pais_estudado,
            tipo_documento=tipo_documento,
            abordagem_metodologica=abordagem_metodologica,
            t1_termos_chave=t1_termos_chave,
            t2_contexto_publico=t2_contexto_publico,
            t3_tema_institucional=t3_tema_institucional,
            t4_analise_direta=t4_analise_direta,
            resultado="Concluído",
            usou_ia=usou_ia,
            ia_ferramentas_uso=usou_ia,
            ia_prompts=ia_prompts,
            observacoes=observacoes
        )
        db.add(nova_avaliacao)

    # Atualiza o status na tabela intermediária de controle de fluxo
    distribuicao = db.query(models.ArtigoAvaliacaoModel).filter(
        models.ArtigoAvaliacaoModel.artigo_id == artigo_id_real,
        models.ArtigoAvaliacaoModel.username == username_logado
    ).first()
    
    if distribuicao:
        print(f"[DEBUG STATUS] Sucesso: {username_logado} concluiu o seu próprio artigo {artigo_id_real}.")
        distribuicao.status = "concluido"
        db.add(distribuicao)
    else:
        # Se cair aqui, significa que o usuário logado tentou forçar o envio de um artigo que não é dele
        print(f"[DEBUG STATUS] ERRO CRÍTICO: Usuário {username_logado} tentou avaliar o artigo {artigo_id_real}, mas não é o dono da distribuição.")
        # Opcional: Descomente a linha abaixo se quiser bloquear a operação com erro na tela
        # raise HTTPException(status_code=403, detail="Você não tem permissão para avaliar este artigo.")

    # Força a gravação síncrona no banco
    db.commit()
    return RedirectResponse(url=f"/estado/artigos/?page={page}", status_code=303)


@router.get("/editar-avaliacao/{artigo_id}/{etapa}")
@require_login
async def editar_avaliacao(
    artigo_id: int, 
    etapa: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    username_sessao = request.session.get("user")
    if not username_sessao:
        raise HTTPException(status_code=401, detail="Usuário não está logado na sessão.")
    
    class UsuarioSessao:
        def __init__(self, username):
            self.username = username
            
    current_user = UsuarioSessao(username_sessao)

    # 1. Busca o ID real do usuário
    user_db = db.query(models.User).filter(models.User.username == username_sessao).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado no banco.")
    
    # 2. SOLUÇÃO DO ERRO: Busca explicitamente o artigo para injetar no formulário
    artigo_obj = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == artigo_id).first()
    if not artigo_obj:
        raise HTTPException(status_code=404, detail="Artigo associado a esta avaliação não encontrado.")

    # 3. Busca os dados gravados da avaliação correspondente
    avaliacao = db.query(models.AvaliacaoModel).filter(
        models.AvaliacaoModel.usuario_id == user_db.id,
        models.AvaliacaoModel.artigo_id == artigo_id,
        models.AvaliacaoModel.etapa == etapa
    ).first()

    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada para edição.")

    # 4. Retorna o template injetando o artigo_obj sem erros de NameError
    return templates.TemplateResponse("avaliacao_form.html", {
        "request": request,
        "avaliacao": avaliacao,
        "artigo": artigo_obj,  # <--- Vinculado de forma explícita agora
        "dicionarios": DICIONARIOS_AVALIACAO,
        "current_user": current_user
    })

