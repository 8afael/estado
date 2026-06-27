import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_login
from app.models import crud
from app.util import fixos
from app.models import models
from app.models import schemas
from app.util import utils

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
@require_login
def listar_jornais(
    request: Request, 
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 50,
    id: str | None = None,            # Alterado de int para str
    data_inicio: str | None = None,
    data_fim: str | None = None,
    jornal: str | None = None,
    apenas_novos: str | None = None
):
    query = db.query(models.Jornal)

    # 2. Filtro por ID (Tratando string vazia)
    if id and id.strip():
        try:
            query = query.filter(models.Jornal.id == int(id))
        except ValueError:
            pass # Se não for um número válido, ignora o filtro
            
    # ... restante do código (datas, total_registros, etc)
    # 3. Filtro por Intervalo de Datas (se informadas)
    if data_inicio:
        try:
            d_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
            query = query.filter(models.Jornal.dataPublicacao >= d_inicio)
        except ValueError:
            pass # Ignora data mal formatada

    if data_fim:
        try:
            d_fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
            query = query.filter(models.Jornal.dataPublicacao <= d_fim)
        except ValueError:
            pass

    if jornal and jornal.strip():
        query = query.filter(models.Jornal.jornal == jornal)

    # Novo filtro: Flag Novo
    if apenas_novos == "true":
        query = query.filter(models.Jornal.is_novo == True)

    # 4. Calcula o total de registros APÓS os filtros aplicados
    total_registros = query.count()
    total_paginas = (total_registros + size - 1) // size if total_registros > 0 else 1

    # 5. Aplica Ordenação, Offset e Limite
    offset = (page - 1) * size
    jornais = query.order_by(desc(models.Jornal.id))\
                   .offset(offset)\
                   .limit(size)\
                   .all()

    return templates.TemplateResponse(
        "jornais/list.html",
        {
            "request": request, 
            "jornais": jornais,
            "jornais_lista": fixos.JORNAIS_FIXOS,
            "page": page,
            "size": size,
            "total_paginas": total_paginas,
            "total_registros": total_registros
        }
    )


@router.get("/novo", response_class=HTMLResponse)
@require_login
def novo_jornal(
    request: Request,
    db: Session = Depends(get_db)
    ):
    temas = crud.get_temas(db)
    fontes = crud.get_fontes(db)
    enquadramentos = crud.get_enquadramentos(db)
    return templates.TemplateResponse(
        "jornais/form.html",
        {
            "request": request,
            "jornal": None,
            "jornais_lista": fixos.JORNAIS_FIXOS,
            "anos_lista": fixos.ANOS_FIXOS,
            "mes_lista": fixos.MES_FIXOS,
            "secao_lista": fixos.SECAO, 
            "genero_lista": fixos.GENERO, 
            "autoria_lista": fixos.AUTORIA,
            "abrangencia_lista": fixos.ABRANGENCIA,
            "linguagem_lista": fixos.LINGUAGEM,
            "enunciador_lista": fixos.ENUNCIADOR,
            "persuasao_lista": fixos.PERSUASAO,
            "dominante_lista": fixos.DOMINANTE,
            "enqEficacia_lista": fixos.EFICACIA, 
            "enqAcao_lista": fixos.ACAOCOLETIVA, 
            "lead_lista": fixos.LEAD,  
            "papJornalistico_lista": fixos.PAPELJORNALISTICO,  
            "temas": temas,
            "fontes": fontes,
            "enquadramentos": enquadramentos
        }
    )

@router.post("/{jid}/editar")
@require_login
async def salvar_edicao_jornal(
    request: Request,
    jid: int,
    jornal: str = Form(...),
    dataPublicacao: str | None = Form(None),
    anoPublicacao: str | None = Form(None),
    mesPublicacao: str | None = Form(None),
    persuasao: str | None = Form(None),  
    lead: str | None = Form(None),    
    pagina: int | None = Form(None),
    palavras: int | None = Form(None),
    percentual: int | None = Form(None),
    palavras_original: int | None = Form(None),
    papJornalistico: str | None = Form(None), 

    secao: str | None = Form(None),
    secao_outro: str | None = Form(None),

    genero: str | None = Form(None),
    genero_outro: str | None = Form(None),

    autoria: str | None = Form(None),
    autoria_outro: str | None = Form(None),

    abrangencia: str | None = Form(None),
    abrangencia_outro: str | None = Form(None),

    linguagem: str | None = Form(None),
    linguagem_outro: str | None = Form(None),

    enunciador: str | None = Form(None),
    enunciador_outro: str | None = Form(None),

    enqDominante: str | None = Form(None),
    enqDominante_outro: str | None = Form(None),

    enqEficacia: str | None = Form(None),
    enqEficacia_outro: str | None = Form(None),

    enqAcao: str | None = Form(None),
    enqAcao_outro: str | None = Form(None),

    fontes: list[str] = Form([]),
    fontes_outro: str | None = Form(None),

    temas: list[str] = Form(default=[]),
    temas_outro: str | None = Form(None),
    enqResponsabilidade: list[str] = Form([]),
    enqResponsabilidade_outro: str | None = Form(None),
    climaticas: bool = Form(False),
    link: str | None = Form(None),
    observacoes: str | None = Form(None),
    nomeArquivo: str | None = Form(None),


    
    db: Session = Depends(get_db)
):
    obj = crud.get_jornal(db, jid)
    
    print(f"Valor: {temas}")

    if not obj:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")

    # -------- Campos com "Outro" --------
    obj.secao = secao_outro.strip() if secao == "Outro" and secao_outro else secao
    obj.genero = genero_outro.strip() if genero == "Outro" and genero_outro else genero
    obj.autoria = autoria_outro.strip() if autoria == "Outro" and autoria_outro else autoria
    obj.abrangencia = abrangencia_outro.strip() if abrangencia == "Outro" and abrangencia_outro else abrangencia
    obj.linguagem = linguagem_outro.strip() if linguagem == "Outro" and linguagem_outro else linguagem
    obj.enunciador = enunciador_outro.strip() if enunciador == "Outro" and enunciador_outro else enunciador
    obj.enqDominante = enqDominante_outro.strip() if enqDominante == "Outro" and enqDominante_outro else enqDominante
    obj.enqEficacia = enqEficacia_outro.strip() if enqEficacia == "Outro" and enqEficacia_outro else enqEficacia
    obj.enqAcao = enqAcao_outro.strip() if enqAcao == "Outro" and enqAcao_outro else enqAcao

    # -------- Datas --------
    if dataPublicacao and dataPublicacao.strip():
        try:
            obj.dataPublicacao = datetime.datetime.strptime(dataPublicacao, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Data inválida")
    else:
        obj.dataPublicacao = None

    obj.anoPublicacao = int(anoPublicacao) if anoPublicacao and anoPublicacao.strip() else None
    obj.mesPublicacao = int(mesPublicacao) if mesPublicacao and mesPublicacao.strip() else None

    # -------- Campos simples --------
    obj.jornal = jornal
    obj.pagina = pagina
    obj.palavras = palavras
    obj.percentual = percentual
    if palavras_original is not None:
        obj.palavras_original = palavras_original
    obj.persuasao = persuasao
    obj.lead = lead
    obj.observacoes = observacoes
    obj.nomeArquivo = nomeArquivo
    obj.papJornalistico = papJornalistico
    obj.climaticas = climaticas
    obj.link = link

    # =====================================================
    # RELACIONAMENTO ENQUADRAMENTO RESPONSABILIDADE
    # =====================================================

    # Limpa relacionamentos anteriores
    obj.enqResponsabilidade.clear()

    # Enquadramentos selecionados (checkbox)
    for eid in enqResponsabilidade:
        if eid.isdigit():
            enquadramento = db.get(models.Enquadramento, int(eid))
            if enquadramento:
                obj.enqResponsabilidade.append(enquadramento)

    # Enquadramento "Outro"
    if enqResponsabilidade_outro and enqResponsabilidade_outro.strip():
        descricao = enqResponsabilidade_outro.strip()

        enquadramento_existente = (
            db.query(models.Enquadramento)
            .filter(models.Enquadramento.descricao.ilike(descricao))
            .first()
        )

        if enquadramento_existente:
            if enquadramento_existente not in obj.enqResponsabilidade:
                obj.enqResponsabilidade.append(enquadramento_existente)
        else:
            novo = models.Enquadramento(descricao=descricao)
            db.add(novo)
            db.flush()
            obj.enqResponsabilidade.append(novo)

    # =====================================================
    # RELACIONAMENTO FONTES (checkbox + Outro com validação)
    # =====================================================

    # Limpa relações anteriores
    obj.fontes.clear()

    # Fontes marcadas via checkbox
    for f_id in fontes:
        if f_id.isdigit():
            fonte = db.query(models.Fonte).get(int(f_id))
            if fonte:
                obj.fontes.append(fonte)

    # Fonte "Outro"
    if fontes_outro and fontes_outro.strip():
        descricao = fontes_outro.strip()

        # Verifica se já existe (case-insensitive)
        fonte_existente = (
            db.query(models.Fonte)
            .filter(models.Fonte.descricao.ilike(descricao))
            .first()
        )

        if fonte_existente:
            if fonte_existente not in obj.fontes:
                obj.fontes.append(fonte_existente)
        else:
            nova_fonte = models.Fonte(descricao=descricao)
            db.add(nova_fonte)
            db.flush()  # evita commit antecipado
            obj.fontes.append(nova_fonte)

    # =====================================================
    # RELACIONAMENTO TEMAS (checkbox + Outro com validação)
    # =====================================================

    # Limpa relações anteriores
    obj.temas.clear()

    # Fontes marcadas via checkbox
    for t_id in temas:
        if t_id.isdigit():
            tema = db.query(models.Tema).get(int(t_id))
            if tema:
                obj.temas.append(tema)

    # Fonte "Outro"
    if temas_outro and temas_outro.strip():
        descricao = temas_outro.strip()

        # Verifica se já existe (case-insensitive)
        tema_existente = (
            db.query(models.Tema)
            .filter(models.Tema.descricao.ilike(descricao))
            .first()
        )

        if tema_existente:
            if tema_existente not in obj.temas:
                obj.temas.append(tema_existente)
        else:
            nova_tema = models.Tema(descricao=descricao)
            db.add(nova_tema)
            db.flush()  # evita commit antecipado
            obj.temas.append(nova_tema)

    # -------- Persistência --------

    form_data = await request.form()    
    q_ini = form_data.get("q_ini", "")
    q_fim = form_data.get("q_fim", "")
    q_id = form_data.get("q_id", "")
    q_page = form_data.get("q_page", "")
    q_jornal = form_data.get("q_jornal", "")
    q_novo = form_data.get("q_novo", "")
    #url_retorno = f"/?data_inicio={q_ini}&data_fim={q_fim}&id={q_id}&page={q_page}&jornal={q_jornal}&novo={q_novo}"
    url_retorno = f"/doutoramento/?data_inicio={q_ini}&data_fim={q_fim}&id={q_id}&page={q_page}&jornal={q_jornal}&novo={q_novo}"

    obj.is_novo = False
    
    db.commit()

    return RedirectResponse(url=url_retorno, status_code=303)

@router.post("/novo")
@require_login
def criar_jornal(
    request: Request,
    jornal: str = Form(...),
    dataPublicacao: str | None = Form(None),
    anoPublicacao: str | None = Form(None),
    mesPublicacao: str | None = Form(None),
    persuasao: str | None = Form(None),   
    lead: str | None = Form(None),  
    papJornalistico: str | None = Form(None), 
    pagina: int | None = Form(None),
    palavras: int | None = Form(None),
    percentual: int | None = Form(None),
    palavras_original: int | None = Form(None),
    secao: str | None = Form(None),
    secao_outro: str | None = Form(None),
    genero: str | None = Form(None),
    genero_outro: str | None = Form(None),
    autoria: str | None = Form(None),
    autoria_outro: str | None = Form(None),
    abrangencia: str | None = Form(None),
    abrangencia_outro: str | None = Form(None),
    linguagem: str | None = Form(None),
    linguagem_outro: str | None = Form(None),
    enunciador: str | None = Form(None),
    enunciador_outro: str | None = Form(None),
    enqDominante: str | None = Form(None),
    dominante_outro: str | None = Form(None),
    enqEficacia: str | None = Form(None),
    enqEficacia_outro: str | None = Form(None),
    enqAcao: str | None = Form(None),
    enqAcao_outro: str | None = Form(None),
    fontes: list[str] = Form([]),
    fontes_outro: str | None = Form(None),
    temas: list[str] = Form(default=[]),
    temas_outro: str | None = Form(None),    
    enqResponsabilidade: list[str] = Form([]),
    enqResponsabilidade_outro: str | None = Form(None),
    climaticas: bool = Form(False),
    link: str | None = Form(None),
    observacoes: str | None = Form(None),
    nomeArquivo: str | None = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Processamento de campos "Outro" (Seleção Simples)
    secao_f = secao_outro.strip() if secao == "Outro" and secao_outro else secao
    genero_f = genero_outro.strip() if genero == "Outro" and genero_outro else genero
    autoria_f = autoria_outro.strip() if autoria == "Outro" and autoria_outro else autoria
    abrang_f = abrangencia_outro.strip() if abrangencia == "Outro" and abrangencia_outro else abrangencia
    ling_f = linguagem_outro.strip() if linguagem == "Outro" and linguagem_outro else linguagem
    enunc_f = enunciador_outro.strip() if enunciador == "Outro" and enunciador_outro else enunciador
    dom_f = dominante_outro.strip() if enqDominante == "Outro" and dominante_outro else enqDominante
    efic_f = enqEficacia_outro.strip() if enqEficacia == "Outro" and enqEficacia_outro else enqEficacia
    acao_f = enqAcao_outro.strip() if enqAcao == "Outro" and enqAcao_outro else enqAcao

    # 2. Tratamento de Datas
    data_obj = None
    if dataPublicacao and dataPublicacao.strip():
        try:
            data_obj = datetime.datetime.strptime(dataPublicacao, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Data inválida")

    # 3. Chamada do CRUD (Aqui os IDs de temas/fontes/enquadramentos já são vinculados)
    jornal_schema = schemas.JornalCreate(
        jornal=jornal,
        dataPublicacao=data_obj,
        anoPublicacao=int(anoPublicacao) if anoPublicacao else None,
        mesPublicacao=int(mesPublicacao) if mesPublicacao else None,
        pagina=pagina,
        palavras=palavras,
        percentual=percentual,
        palavras_original=palavras_original,
        climaticas=climaticas,
        link=link,
        persuasao=persuasao,
        lead=lead,        
        secao=secao_f,
        genero=genero_f,
        autoria=autoria_f,
        abrangencia=abrang_f,
        linguagem=ling_f,
        enunciador=enunc_f,
        enqDominante=dom_f,
        enqEficacia=efic_f,
        enqAcao=acao_f,
        papJornalistico=papJornalistico, 
        temas=[int(t) for t in temas if t.isdigit()], # Envia IDs para o CRUD
        fontes=[int(f) for f in fontes if f.isdigit()],
        enqResponsabilidade=[int(e) for e in enqResponsabilidade if e.isdigit()],
        observacoes=observacoes,
        nomeArquivo=nomeArquivo
    )

    obj = crud.create_jornal(db, jornal_schema)
    # IMPORTANTE: Não use db.refresh(obj) aqui antes de terminar os "Outros"

    # 4. Adicionar TEMAS "Outro" (Sem limpar a lista anterior)
    if temas_outro and temas_outro.strip():
        desc = temas_outro.strip()
        existente = db.query(models.Tema).filter(models.Tema.descricao.ilike(desc)).first()
        if existente:
            if existente not in obj.temas:
                obj.temas.append(existente)
        else:
            novo = models.Tema(descricao=desc)
            db.add(novo)
            db.flush()
            obj.temas.append(novo)

    # 5. Adicionar FONTES "Outro"
    if fontes_outro and fontes_outro.strip():
        desc = fontes_outro.strip()
        existente = db.query(models.Fonte).filter(models.Fonte.descricao.ilike(desc)).first()
        if existente:
            if existente not in obj.fontes:
                obj.fontes.append(existente)
        else:
            nova = models.Fonte(descricao=desc)
            db.add(nova)
            db.flush()
            obj.fontes.append(nova)

    # 6. Adicionar ENQUADRAMENTOS "Outro"
    if enqResponsabilidade_outro and enqResponsabilidade_outro.strip():
        desc = enqResponsabilidade_outro.strip()
        existente = db.query(models.Enquadramento).filter(models.Enquadramento.descricao.ilike(desc)).first()
        if existente:
            if existente not in obj.enqResponsabilidade:
                obj.enqResponsabilidade.append(existente)
        else:
            novo = models.Enquadramento(descricao=desc)
            db.add(novo)
            db.flush()
            obj.enqResponsabilidade.append(novo)

    # 7. Finalização Atômica
    db.commit()
    #return RedirectResponse("/", status_code=303)
    return RedirectResponse("/doutoramento/", status_code=303)

@router.get("/{jid}/editar", response_class=HTMLResponse)
@require_login
def editar_jornal(jid: int, request: Request, db: Session = Depends(get_db)):
    jornal = crud.get_jornal(db, jid)
    if not jornal:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")

    temas = crud.get_temas(db)
    fontes = crud.get_fontes(db)
    enquadramentos = crud.get_enquadramentos(db)
    q_ini = request.query_params.get('data_inicio', '')
    q_fim = request.query_params.get('data_fim', '')
    q_id = request.query_params.get('id', '')
    q_jornal = request.query_params.get('jornal', '')
    q_novo = request.query_params.get('apenas_novos', '')
    q_page = request.query_params.get('page', '')

    #--- Campos "Outro" ---
    secao_db = utils.normalizar(jornal.secao)
    secao_fixos = [utils.normalizar(s) for s in fixos.SECAO]
    if secao_db and secao_db in secao_fixos:
        secao_select = secao_db
        secao_outro = None
    elif secao_db:
        secao_select = "Outro"
        secao_outro = secao_db
    else:
        secao_select = None
        secao_outro = None

    genero_db = utils.normalizar(jornal.genero)
    genero_fixos = [utils.normalizar(s) for s in fixos.GENERO]
    if genero_db and genero_db in genero_fixos:
        genero_select = genero_db
        genero_outro = None
    elif genero_db:
        genero_select = "Outro"
        genero_outro = genero_db
    else:
        genero_select = None
        genero_outro = None

    autoria_db = utils.normalizar(jornal.autoria)
    autoria_fixos = [utils.normalizar(s) for s in fixos.AUTORIA]
    if autoria_db and autoria_db in autoria_fixos:
        autoria_select = autoria_db
        autoria_outro = None
    elif autoria_db:
        autoria_select = "Outro"
        autoria_outro = autoria_db
    else:
        autoria_select = None
        autoria_outro = None

    abrangencia_db = utils.normalizar(jornal.abrangencia)
    abrangencia_fixos = [utils.normalizar(s) for s in fixos.ABRANGENCIA]
    if abrangencia_db and abrangencia_db in abrangencia_fixos:
        abrangencia_select = abrangencia_db
        abrangencia_outro = None
    elif abrangencia_db:
        abrangencia_select = "Outro"
        abrangencia_outro = abrangencia_db
    else:
        abrangencia_select = None
        abrangencia_outro = None

    linguagem_db = utils.normalizar(jornal.linguagem)
    linguagem_fixos = [utils.normalizar(s) for s in fixos.LINGUAGEM]
    if linguagem_db and linguagem_db in linguagem_fixos:
        linguagem_select = linguagem_db
        linguagem_outro = None
    elif linguagem_db:
        linguagem_select = "Outro"
        linguagem_outro = linguagem_db
    else:
        linguagem_select = None
        linguagem_outro = None

    enunciador_db = utils.normalizar(jornal.enunciador)
    enunciador_fixos = [utils.normalizar(s) for s in fixos.ENUNCIADOR]
    if enunciador_db and enunciador_db in enunciador_fixos:
        enunciador_select = enunciador_db
        enunciador_outro = None
    elif enunciador_db:
        enunciador_select = "Outro"
        enunciador_outro = enunciador_db
    else:
        enunciador_select = None
        enunciador_outro = None

    enqDominante_db = utils.normalizar(jornal.enqDominante)
    enqDominante_fixos = [utils.normalizar(s) for s in fixos.DOMINANTE]
    if enqDominante_db and enqDominante_db in enqDominante_fixos:
        enqDominante_select = enqDominante_db
        enqDominante_outro = None
    elif enqDominante_db:
        enqDominante_select = "Outro"
        enqDominante_outro = enqDominante_db
    else:
        enqDominante_select = None
        enqDominante_outro = None

    enqEficacia_db = utils.normalizar(jornal.enqEficacia)
    enqEficacia_fixos = [utils.normalizar(s) for s in fixos.EFICACIA]
    if enqEficacia_db and enqEficacia_db in enqEficacia_fixos:
        enqEficacia_select = enqEficacia_db
        enqEficacia_outro = None
    elif enqEficacia_db:
        enqEficacia_select = "Outro"
        enqEficacia_outro = enqEficacia_db
    else:
        enqEficacia_select = None
        enqEficacia_outro = None

    enqAcao_db = utils.normalizar(jornal.enqAcao)
    enqAcao_fixos = [utils.normalizar(s) for s in fixos.ACAOCOLETIVA]
    if enqAcao_db and enqAcao_db in enqAcao_fixos:
        enqAcao_select = enqAcao_db
        enqAcao_outro = None
    elif enqAcao_db:
        enqAcao_select = "Outro"
        enqAcao_outro = enqAcao_db
    else:
        enqAcao_select = None
        enqAcao_outro = None

    # --- Fontes ---
    fontes_ids = [f.id for f in jornal.fontes if f.descricao in [fo.descricao for fo in fontes]]
    fonte_outro_text = None
    for f in jornal.fontes:
        if f.descricao not in [fo.descricao for fo in fontes]:
            # identifica como "Outro"
            fonte_outro_text = f.descricao

    # --- Enquadramento ---
    enquadramentos_ids = [f.id for f in jornal.enqResponsabilidade if f.descricao in [fo.descricao for fo in enquadramentos]]
    enquadramento_outro_text = None
    for f in jornal.enqResponsabilidade:
        if f.descricao not in [fo.descricao for fo in enquadramentos]:
            # identifica como "Outro"
            enquadramento_outro_text = f.descricao

    temas_base_ids = {t.id for t in temas}

    temas_ids = []
    tema_outro_text = None

    for t in jornal.temas:
        if t.id in temas_base_ids:
            temas_ids.append(t.id)
        else:
            tema_outro_text = t.descricao

    return templates.TemplateResponse(
        "jornais/form.html",
        {
            "request": request,
            "jornal": jornal,
            "secao_select": secao_select,
            "secao_outro": secao_outro,
            "genero_select": genero_select,
            "genero_outro": genero_outro,
            "autoria_select": autoria_select,
            "autoria_outro": autoria_outro,
            "abrangencia_select": abrangencia_select,
            "abrangencia_outro": abrangencia_outro,
            "linguagem_select": linguagem_select,
            "linguagem_outro": linguagem_outro,
            "enunciador_select": enunciador_select,
            "enunciador_outro": enunciador_outro,
            "enqDominante_select": enqDominante_select,
            "enqDominante_outro": enqDominante_outro,
            "enqEficacia_select": enqEficacia_select,
            "enqEficacia_outro": enqEficacia_outro,
            "enqAcao_select": enqAcao_select,
            "enqAcao_outro": enqAcao_outro,
            "fontes_ids": fontes_ids,
            "fonte_outro_text": fonte_outro_text, # campo texto "Outro"
            "temas_ids": temas_ids,
            "tema_outro_text": tema_outro_text, # campo texto "Outro"
            "enquadramentos_ids": enquadramentos_ids,           # fontes existentes selecionadas
            "enquadramento_outro_text": enquadramento_outro_text, # campo texto "Outro"
            "temas": temas,
            "fontes": fontes,
            "enquadramentos": enquadramentos,
            "jornais_lista": fixos.JORNAIS_FIXOS,
            "anos_lista": fixos.ANOS_FIXOS,
            "mes_lista": fixos.MES_FIXOS,
            "secao_lista": fixos.SECAO,
            "genero_lista": fixos.GENERO,
            "autoria_lista": fixos.AUTORIA,
            "abrangencia_lista": fixos.ABRANGENCIA,
            "linguagem_lista": fixos.LINGUAGEM,
            "enqAcao_lista": fixos.ACAOCOLETIVA,
            "enunciador_lista": fixos.ENUNCIADOR,
            "dominante_lista": fixos.DOMINANTE,
            "persuasao_lista": fixos.PERSUASAO,
            "enqEficacia_lista": fixos.EFICACIA,
            "lead_lista": fixos.LEAD,
            "papJornalistico_lista": fixos.PAPELJORNALISTICO,  
            "q_ini": q_ini, 
            "q_fim": q_fim,
            "q_id": q_id,
            "q_page": q_page,
            "q_jornal": q_jornal,
            "q_novo": q_novo       
        }
    )

