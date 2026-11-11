"""Gera os JSON do site de resultados a partir dos arquivos do projeto."""
import json, re, math, sys, collections
import pandas as pd, openpyxl, docx
from docx.oxml.ns import qn

PF = '/mnt/project-files/'
SCR = sys.argv[1]
OUT = SCR + '/site/data/'

# ---------------------------------------------------------------- codebook
d = docx.Document(PF + 'codebook/Codebook_extracao_Estado_Aberto.docx')
items = []
for el in d.element.body.iterchildren():
    if el.tag == qn('w:p'):
        t = ''.join(x.text or '' for x in el.iter(qn('w:t'))).strip()
        if t: items.append(('P', t))
    elif el.tag == qn('w:tbl'):
        rows = []
        for tr in el.iter(qn('w:tr')):
            rows.append([''.join(x.text or '' for x in tc.iter(qn('w:t'))).strip() for tc in tr.iter(qn('w:tc'))])
        items.append(('T', rows))

sections, cur_sec, cur_q = [], None, None
started = False
for kind, val in items:
    if kind == 'P' and val.startswith('Seção '):
        started = True
        m = re.match(r'Seção (\d+) — (.*)', val)
        cur_sec = {'n': int(m.group(1)), 'titulo': m.group(2), 'questoes': []}
        sections.append(cur_sec); cur_q = None; continue
    if not started: continue
    if kind == 'P':
        m = re.match(r'Q(\d+) · (.*)', val)
        if m:
            cur_q = {'q': int(m.group(1)), 'titulo': m.group(2), 'var': None, 'tipo': None,
                     'orientacao': [], 'opcoes': []}
            cur_sec['questoes'].append(cur_q); continue
        m = re.match(r'Variável: (\S+) · Tipo: (.*)', val)
        if m and cur_q:
            cur_q['var'], cur_q['tipo'] = m.group(1), m.group(2); continue
        if cur_q: cur_q['orientacao'].append(val)
    else:
        if cur_q and val and val[0] and val[0][0] == 'Código':
            for r in val[1:]:
                cur_q['opcoes'].append({'cod': r[0], 'rotulo': r[1], 'criterio': r[2] if len(r) > 2 else ''})

qmap = {q['q']: q for s in sections for q in s['questoes']}
for n in (42, 43):
    qmap[n]['opcoes'] = [dict(o, criterio='') for o in qmap[26]['opcoes']]
for q in qmap.values():
    t = (q['tipo'] or '').lower()
    q['kind'] = ('multi' if ('múltipla' in t or 'caixas' in t) else
                 'single' if 'única' in t else 'scale' if 'escala' in t else
                 'auto' if 'automatic' in t else 'text')
    # drop the "Registro:" technical lines from user-facing guidance
    q['orientacao'] = [o for o in q['orientacao'] if not o.startswith('Registro:')]
qmap[25]['kind'] = 'pairs'
qmap[25]['pares'] = ['Parlamento Aberto / Transparência Parlamentar', 'Parlamento Aberto / Abertura Legislativa',
                     'Justiça Aberta / Transparência Judicial', 'Justiça Aberta / Acesso à Justiça',
                     'Justiça Aberta / Abertura dos Tribunais']
qmap[5]['kind'] = 'multi'
codebook = {'titulo': 'Codebook do formulário de extração de dados', 'versao': 'Outubro de 2026',
            'secoes': sections}
json.dump(codebook, open(OUT + 'codebook.json', 'w'), ensure_ascii=False, indent=1)
print('codebook', sum(len(s['questoes']) for s in sections), 'questões')

# ---------------------------------------------------------------- artigos
df = pd.read_csv(PF + 'E0/base_geral_corrigida.csv', dtype=str)
wb = openpyxl.load_workbook(PF + 'matriz/Matriz_sistematizacao_analitica_Estado_Aberto_v4.xlsx', read_only=True)
rows = list(wb['5_Codificacao_derivada'].iter_rows(values_only=True))
dcols = rows[4]
deriv = {}
for r in rows[6:]:
    if r[0] is None: continue
    deriv[str(r[0])] = {dcols[j]: r[j] for j in range(1, len(dcols)) if r[j] not in (None, '') and dcols[j] != 'd_obs_sintese'}

ISO = {'Alemanha':'DEU','Argentina':'ARG','Austrália':'AUS','Azerbaijão':'AZE','Bolívia':'BOL','Brasil':'BRA','Canadá':'CAN',
'Cazaquistão':'KAZ','Chile':'CHL','China':'CHN','Colômbia':'COL','Coreia do Sul':'KOR','Costa Rica':'CRI','Cuba':'CUB',
'El Salvador':'SLV','Equador':'ECU','Eslovênia':'SVN','Espanha':'ESP','Estados Unidos':'USA','Estônia':'EST','Finlândia':'FIN',
'França':'FRA','Gana':'GHA','Geórgia':'GEO','Grécia':'GRC','Guatemala':'GTM','Haiti':'HTI','Honduras':'HND','Indonésia':'IDN',
'Irã':'IRN','Islândia':'ISL','Itália':'ITA','Jamaica':'JAM','Libéria':'LBR','Malaui':'MWI','México':'MEX','Nicarágua':'NIC',
'Nova Zelândia':'NZL','Panamá':'PAN','Paquistão':'PAK','Paraguai':'PRY','Países Baixos':'NLD','Peru':'PER','Polônia':'POL',
'Portugal':'PRT','Quirguistão':'KGZ','Quênia':'KEN','Reino Unido':'GBR','República Dominicana':'DOM','Romênia':'ROU',
'Ruanda':'RWA','Rússia':'RUS','Serra Leoa':'SLE','Suécia':'SWE','Suíça':'CHE','Sérvia':'SRB','Taiwan':'TWN','Tanzânia':'TZA',
'Trindade e Tobago':'TTO','Tunísia':'TUN','Ucrânia':'UKR','Uganda':'UGA','Uruguai':'URY','Uzbequistão':'UZB','Venezuela':'VEN',
'Vietnã':'VNM','África do Sul':'ZAF','Áustria':'AUT','Índia':'IND'}
geo = json.load(open(PF + 'Base/countries.geojson'))
iso_region = {}
for f in geo['features']:
    p = f['properties']; a3 = p.get('adm0_a3') or p.get('iso_a3')
    cont, sub = p.get('continent'), p.get('subregion')
    if sub in ('Caribbean', 'Central America', 'South America'): reg = 'América Latina e Caribe'
    elif sub == 'Northern America': reg = 'América do Norte'
    elif cont == 'Europe': reg = 'Europa'
    elif cont == 'Asia': reg = 'Ásia'
    elif cont == 'Africa': reg = 'África'
    elif cont == 'Oceania': reg = 'Oceania'
    else: reg = cont
    iso_region[a3] = reg
iso_region['TTO'] = 'América Latina e Caribe'
missing = [k for k, v in ISO.items() if v not in iso_region]
assert not missing, missing

arts = []
for _, r in df.iterrows():
    o = {}
    for k, v in r.items():
        if v is None or (isinstance(v, float) and math.isnan(v)): continue
        v = str(v).strip()
        if v == '' or v == 'nan' or v == 'Não' and re.search(r'_\d+$', k): continue
        o[k] = v
    multi = collections.defaultdict(list)
    for k in list(o):
        m2 = re.match(r'(q\d+_[a-z_]+?)_(\d+)$', k)
        if m2 and o[k] in ('Sim', '1'):
            multi[m2.group(1)].append(int(m2.group(2))); del o[k]
        elif m2: del o[k]
    o.update(multi)
    o.update({k: (str(v) if not isinstance(v, int) else v) for k, v in deriv.get(o['q01_id_estudo'], {}).items()})
    m = re.search(r'\((\d{4})[a-z]?[,)]', o['q03_referencia'])
    o['ano'] = int(o.get('d_ano') or m.group(1))
    o.pop('d_ano', None)
    paises = [p.strip() for p in o.get('q05_pais_lista', '').split(';') if p.strip()]
    o['_paises_iso'] = [ISO[p] for p in paises]
    o['_regioes'] = sorted({iso_region[ISO[p]] for p in paises})
    arts.append(o)

def sortkey(a):
    import unicodedata
    s = unicodedata.normalize('NFKD', a['q03_referencia']).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', '', s)
arts.sort(key=sortkey)
json.dump(arts, open(OUT + 'artigos.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('artigos', len(arts), 'anos', min(a['ano'] for a in arts), max(a['ano'] for a in arts))

# ---------------------------------------------------------------- mapa (geojson simplificado)
def rnd(c):
    if isinstance(c[0], (int, float)): return [round(c[0], 1), round(c[1], 1)]
    out = [rnd(x) for x in c]
    if out and isinstance(out[0][0], float):  # ring: drop consecutive dups
        ded = [out[0]] + [p for i, p in enumerate(out[1:], 1) if p != out[i - 1]]
        return ded if len(ded) >= 4 else out
    return out
feats = []
for f in geo['features']:
    p = f['properties']; a3 = p.get('adm0_a3')
    if a3 == 'ATA': continue
    feats.append({'type': 'Feature', 'id': a3, 'properties': {'n': p.get('name')},
                  'geometry': {'type': f['geometry']['type'], 'coordinates': rnd(f['geometry']['coordinates'])}})
pt = {v: k for k, v in ISO.items()}
for f in feats:
    if f['id'] in pt: f['properties']['pt'] = pt[f['id']]
json.dump({'type': 'FeatureCollection', 'features': feats}, open(OUT + 'mundo.geojson', 'w'), separators=(',', ':'))

# ---------------------------------------------------------------- textos dos relatórios
def plain(path):
    import subprocess
    return subprocess.run(['pandoc', path, '-t', 'plain', '--wrap=none'], capture_output=True, text=True).stdout

def section(txt, start_pat, end_pat):
    m = re.search(start_pat, txt, re.M)
    st0 = txt.index('\n', m.end()) if '\n' in txt[m.end():] else m.end()
    e = re.search(end_pat, txt[st0:], re.M)
    return txt[st0: st0 + e.start()] if e else txt[st0:]

def bullets(block):
    out = []
    for ln in block.split('\n'):
        ln = ln.strip()
        if ln.startswith('-'): out.append(ln.lstrip('- ').strip())
    return out

def split_lead(b):
    m = re.match(r'(.{3,90}?[?.:])\s+(.*)', b)
    return {'titulo': m.group(1), 'texto': m.group(2)} if m else {'titulo': '', 'texto': b}

conceitos = {}
for slug, nome, path in [('governo', 'Governo Aberto', 'governo_aberto/Relatorio_Governo_Aberto.docx'),
                         ('governanca', 'Governança Aberta', 'governanca_aberta/Relatorio_Governanca_Aberta.docx'),
                         ('estado', 'Estado Aberto', 'estado_aberto/Relatorio_Estado_Aberto.docx'),
                         ('parlamento', 'Parlamento Aberto', 'parlamento_aberto/Relatorio_Parlamento_Aberto.docx'),
                         ('justica', 'Justiça Aberta', 'justica_aberta/Relatorio_Justica_Aberta.docx')]:
    t = plain(PF + path)
    s4 = section(t, r'^4\. Síntese: mensagens para a apresentação', r'^5\. ')
    frase = re.search(r'Em uma frase: (.*)', s4)
    s5 = section(t, r'^5\. Lacunas e agenda de pesquisa', r'^6\. ')
    s31 = section(t, r'^3\.1 Lugar d', r'^Figura|^3\.2')
    s39 = section(t, r'^3\.9 O que distingue', r'^Figura')
    s24 = section(t, r'^2\.4 Como o recorte', r'^Figura 2')
    conceitos[slug] = {'nome': nome, 'mensagens': [split_lead(b) for b in bullets(s4)],
                       'em_uma_frase': frase.group(1).strip() if frase else '',
                       'lugar_no_corpus': ' '.join(p.strip() for p in s31.strip().split('\n\n') if p.strip()),
                       'distintivo': s39.strip().split('\n\n')[0].strip(),
                       'recorte': [b for b in bullets(s24)],
                       'lacunas': [split_lead(b) for b in bullets(s5)]}
    print(slug, len(conceitos[slug]['mensagens']), 'mensagens', len(conceitos[slug]['lacunas']), 'lacunas')

st = plain(PF + 'sintese/Sintese_tematica_conceitual_Estado_Aberto.docx')
uma = section(st, r'^Síntese em uma página', r'^1\. Perfil')
uma_b = {split_lead(b)['titulo'].rstrip('.'): split_lead(b)['texto'] for b in bullets(uma)}
intro_uma = uma.strip().split('\n\n')[0].strip()
r81 = section(st, r'^8\.1 Resposta à pergunta de pesquisa', r'^8\.2')
resp = [split_lead(p.strip()) for p in r81.strip().split('\n\n') if p.strip()]
cons = [split_lead(b) for b in bullets(section(st, r'^8\.3 Consensos', r'^\[\]|^Figura'))]
contr = [split_lead(b) for b in bullets(section(st, r'^8\.4 Controvérsias', r'^8\.5'))]
s11 = section(st, r'^1\.1 Volume', r'^\[\]').strip().split('\n\n')

def first_par(pat, endpat=r'^\[\]|^Figura|^Quadro|^Tabela|^\d\.\d'):
    s = section(st, pat, endpat).strip().split('\n\n')
    return s[0].strip()

oes = [
 {'id': 'OE1', 'titulo': 'Caracterizar o perfil da produção científica', 'eixos': 'E0',
  'sintese': s11[0].strip() + ' ' + s11[1].strip() if len(s11) > 1 else s11[0]},
 {'id': 'OE2', 'titulo': 'Identificar como os conceitos são definidos', 'eixos': 'E1', 'sintese': uma_b.get('Definição', '')},
 {'id': 'OE3', 'titulo': 'Analisar a delimitação em relação a conceitos próximos', 'eixos': 'E2', 'sintese': uma_b.get('Delimitação', '')},
 {'id': 'OE4', 'titulo': 'Analisar a relação com Governo Aberto e Governança Aberta', 'eixos': 'E3', 'sintese': uma_b.get('Relação com Governo e Governança Aberta', '')},
 {'id': 'OE5', 'titulo': 'Identificar a operacionalização em dimensões, indicadores e critérios', 'eixos': 'E4', 'sintese': uma_b.get('Operacionalização', '')},
 {'id': 'OE6', 'titulo': 'Analisar a concretização: estágio, obstáculos, condições e efeitos', 'eixos': 'E5', 'sintese': uma_b.get('Concretização', '')},
 {'id': 'OE7', 'titulo': 'Analisar o papel de instituições, direito, ferramentas digitais, sociedade civil e mídia', 'eixos': 'E6–E10', 'sintese': uma_b.get('Fatores', '')},
]
for o in oes: assert o['sintese'], o['id']

conteudo = {
 'projeto': 'Estado Aberto: promovendo a cultura e as práticas de governo, parlamento e justiça aberta',
 'acao': 'Ação 2 – Ciência Aberta',
 'grupo': 'Grupo de Pesquisa Politeia · Udesc/ESAG',
 'pergunta': 'Como Estado Aberto, Parlamento Aberto e Justiça Aberta são conceitualmente definidos, delimitados e operacionalizados na literatura, e como se relacionam com Governo Aberto e Governança Aberta?',
 'pergunta_en': 'How are open state, open parliament, and open justice conceptually defined, delimited, and operationalized in the literature, and how do they relate to open government and open governance?',
 'objetivo_geral': 'Analisar, por meio de uma revisão sistemática da literatura, como os conceitos de Estado Aberto, Parlamento Aberto e Justiça Aberta são definidos, delimitados, operacionalizados e concretizados, e como se relacionam com Governo Aberto e Governança Aberta.',
 'sintese_geral': intro_uma,
 'sintese_achados': [split_lead(b) for b in bullets(uma)],
 'resposta_pergunta': resp,
 'objetivos_especificos': oes,
 'consensos': cons, 'controversias': contr,
 'conceitos': conceitos,
}
json.dump(conteudo, open(OUT + 'conteudo.json', 'w'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- PRISMA
prisma = {
 'identificacao': {'total': 700, 'bases': [{'nome': 'Scopus', 'n': 193, 'data': '25/05/2026'},
                   {'nome': 'Web of Science Core Collection', 'n': 352, 'data': '25/05/2026'},
                   {'nome': 'SciELO', 'n': 155, 'data': '30/05/2026'}],
                   'duplicatas': 99, 'automacao': 0, 'outros': 0},
 'triagem': {'triados': 601, 'incluidos': 291, 'excluidos': 310,
             'convergencia': {'incluidos': 149, 'excluidos': 179, 'total': 328},
             'terceiro': {'incluidos': 142, 'excluidos': 131, 'total': 273},
             'encerramento_rodada': '09/08/2026', 'consolidacao': '31/08/2026'},
 'recuperacao': {'buscados': 291, 'nao_recuperados': 0},
 'elegibilidade': {'avaliados': 291, 'excluidos': 9, 'motivo': 'Duplicatas identificadas na extração (registros não detectados na desduplicação inicial)',
                   'ids_excluidos': [77, 97, 332, 333, 379, 434, 492, 495, 600]},
 'incluidos': 282,
 'extracao': {'avaliadores': 12, 'variaveis': 59, 'secoes': 10, 'periodo': 'setembro a outubro de 2026', 'uso_ia': 258},
 'regras': {
   'perguntas': [
     {'id': 'T1', 'texto': 'O título, o resumo ou as palavras-chave mencionam explicitamente pelo menos um dos seguintes termos, ou suas traduções claras em português ou espanhol?',
      'termos': ['open state / Estado aberto', 'open parliament / parlamento aberto', 'open justice / justiça aberta', 'open government / governo aberto', 'open governance / governança aberta']},
     {'id': 'T2', 'texto': 'O termo “open” é utilizado no contexto de Estado, governo, parlamento, justiça ou governança pública?'},
     {'id': 'T3', 'texto': 'Com base no título e no resumo, o artigo trata a abertura como tema institucional, político, jurídico, organizacional ou relacional no setor público — e não apenas como tema técnico, instrumental ou operacional de tecnologia, sistemas, portais, interoperabilidade, arquitetura da informação, proteção de dados ou gestão de TI?'},
     {'id': 'T4', 'texto': 'O artigo analisa diretamente instituições, políticas ou práticas do setor público relacionadas à abertura?'}],
   'por_avaliador': [
     {'decisao': 'Excluir', 'selo': 'prioridade máxima', 'texto': 'O artigo é classificado como Excluir se qualquer uma das condições abaixo ocorrer — basta uma única ocorrência para excluir.',
      'condicoes': ['Ano = Outro', 'Idioma = Outro', 'T1 = Não', 'T2 = Não', 'T3 = Não', 'T4 = Não']},
     {'decisao': 'Incerto', 'selo': 'avaliado somente se não houver exclusão', 'texto': 'Caso nenhuma condição de exclusão tenha ocorrido, o artigo é classificado como Incerto se houver pelo menos uma resposta “Não sei” em T1, T2, T3 ou T4.',
      'condicoes': ['T1 = Não sei', 'T2 = Não sei', 'T3 = Não sei', 'T4 = Não sei']},
     {'decisao': 'Incluir', 'selo': 'todas as condições simultaneamente', 'texto': 'O artigo é classificado como Incluir somente quando todas as condições abaixo forem atendidas ao mesmo tempo.',
      'condicoes': ['Ano entre 2009 e 2026', 'Idioma: Inglês, Português ou Espanhol', 'T1 = Sim', 'T2 = Sim', 'T3 = Sim', 'T4 = Sim']}],
   'final': [
     {'decisao': 'Inclusão final', 'tipo': 'incluir', 'condicoes': ['A1 = Incluir', 'A2 = Incluir']},
     {'decisao': 'Exclusão final', 'tipo': 'excluir', 'condicoes': ['A1 = Excluir', 'A2 = Excluir']},
     {'decisao': 'Encaminhar para 3º avaliador', 'tipo': 'incerto', 'condicoes': ['Discordância entre os avaliadores (A1 ≠ A2)', 'Qualquer avaliador classificar como Incerto']}],
   'matriz': [
     ['Incluir','Incluir','','Inclusão'],['Excluir','Excluir','','Exclusão'],
     ['Incluir','Excluir','Incluir','Inclusão'],['Incluir','Excluir','Excluir','Exclusão'],['Incluir','Excluir','Incerto','Exclusão'],
     ['Incluir','Incerto','Incluir','Inclusão'],['Incluir','Incerto','Excluir','Exclusão'],['Incluir','Incerto','Incerto','Exclusão'],
     ['Excluir','Incerto','Incluir','Exclusão'],['Excluir','Incerto','Excluir','Exclusão'],['Excluir','Incerto','Incerto','Exclusão'],
     ['Incerto','Incerto','Incluir','Exclusão'],['Incerto','Incerto','Excluir','Exclusão'],['Incerto','Incerto','Incerto','Exclusão']],
   'nota_matriz': 'Modelo conservador: qualquer combinação envolvendo “Incerto” no 3º avaliador — ou divergência não resolvida positivamente — resulta em exclusão final, exceto no caso específico A1 Incluir, A2 Incerto, A3 Incluir.'
 }
}
json.dump(prisma, open(OUT + 'prisma.json', 'w'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- equipe
eq = """Gisiela Klein|Coordenador
Letícia Oliveira Lagos|Coordenador
Edgar Maturana da Silva|Bolsista
Luiz Henrique Casett Horn|Voluntário
Laura de Oliveira|Bolsista
Anelize Lobo Martins|Bolsista
Nicholas solonca Araujo|Bolsista
Davi da Rosa Pizzolatti|Bolsista
Maria Clara Borges Alegri|Bolsista
Ana Clara Dotel Coelho|Voluntário
Alessandra Marjorie de Oliveira|Voluntário
Vitória Santin Rodrigues|Bolsista
Laura de Oliveira Nicontchuk|Bolsista
Camila Pagani|Voluntário
Rogério Samuel Canuto Pacheco|Voluntário
Gabriele Beatriz Ferreira Wience|Voluntário
Jorge Braun Neto|Professor
Eduarda Souza da Silva|Voluntária"""
equipe = {'membros': [{'nome': l.split('|')[0], 'vinculo': l.split('|')[1], 'perfil': '', 'foto': '', 'lattes': ''} for l in eq.split('\n')],
          'apoio': [{'nome': 'Rafael Batista Rodrigues', 'vinculo': 'Analista de sistemas', 'perfil': 'Desenvolveu, de forma voluntária, a plataforma Estado Aberto, que apoiou a distribuição dos artigos e o registro das avaliações.'}]}
json.dump(equipe, open(OUT + 'equipe.json', 'w'), ensure_ascii=False, indent=1)

# triagem: formato esperado (a ser servido pela plataforma). Arquivo de exemplo vazio.
json.dump({'atualizado_em': None, 'registros': []}, open(OUT + 'triagem.json', 'w'), ensure_ascii=False)
print('ok')
