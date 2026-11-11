"""Gera backend/app/models/dashboard_codigos.py a partir de
dashboard/data/codebook.json (rótulo -> código) e dashboard/data/artigos.json
(país -> ISO3 e região). Uso: python gen_codigos.py <raiz_do_projeto>"""
import json, sys, unicodedata, re, collections, pprint

raiz = sys.argv[1]
cb = json.load(open(f'{raiz}/dashboard/data/codebook.json', encoding='utf-8'))
arts = json.load(open(f'{raiz}/dashboard/data/artigos.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(s)).strip().lower())

variaveis, codigos = {}, {}
for s in cb['secoes']:
    for q in s['questoes']:
        variaveis[q['q']] = q['var']
        if q['kind'] == 'multi':
            codigos[q['q']] = {norm(o['rotulo']): int(o['cod']) for o in q['opcoes']}

# países: nome -> ISO3 (pela posição na lista) e ISO3 -> região
iso = {}
for a in arts:
    nomes = [p.strip() for p in a.get('q05_pais_lista', '').split(';') if p.strip()]
    for n, i in zip(nomes, a['_paises_iso']):
        assert iso.setdefault(n, i) == i, n
regiao = {}
pend = [(set(a['_paises_iso']), set(a['_regioes'])) for a in arts if a['_paises_iso']]
for _ in range(20):
    for paises, regs in pend:
        falta = [p for p in paises if p not in regiao]
        livres = regs - {regiao[p] for p in paises if p in regiao}
        if len(falta) == 1 and len(livres) == 1:
            regiao[falta[0]] = livres.pop()
        elif len(regs) == 1:
            for p in falta: regiao[p] = next(iter(regs))
# países que só aparecem em artigos de várias regiões (mesma regra do build_data.py)
for i, r in {'IDN': 'Ásia', 'IRN': 'Ásia', 'ISL': 'Europa', 'POL': 'Europa', 'SRB': 'Europa',
             'SVN': 'Europa', 'TTO': 'América Latina e Caribe', 'TZA': 'África'}.items():
    regiao.setdefault(i, r)
faltam = sorted(set(iso.values()) - set(regiao))
assert not faltam, faltam
paises = {n: (i, regiao[i]) for n, i in sorted(iso.items())}

out = f'''"""
GERADO AUTOMATICAMENTE por ferramentas/gen_codigos.py — não edite à mão.

Fontes:
  - dashboard/data/codebook.json  (códigos de cada opção das questões de múltipla escolha)
  - dashboard/data/artigos.json   (país -> código ISO3 e região usada no mapa)

O banco grava as respostas de múltipla escolha pelo RÓTULO; o site de
resultados trabalha com o CÓDIGO do codebook. Estes dicionários fazem a ponte.
As chaves de rótulo estão normalizadas (NFKC, minúsculas, espaços simples).
"""

# número da questão -> nome da variável no site/codebook (ex.: 9 -> "q09_desenho")
VARIAVEIS = {pprint.pformat(variaveis, width=110, sort_dicts=True)}

# número da questão -> {{rótulo normalizado: código}}
CODIGOS = {pprint.pformat(codigos, width=110, sort_dicts=True)}

# nome do país (como gravado em extracao_multivalores.q5_paises) -> (ISO3, região)
PAISES = {pprint.pformat(paises, width=110, sort_dicts=True)}
'''
open(f'{raiz}/backend/app/models/dashboard_codigos.py', 'w', encoding='utf-8').write(out)
print(len(codigos), 'questões multi;', len(paises), 'países')
