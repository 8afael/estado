"""Testa o dashboard_service sem FastAPI/SQLAlchemy instalados: um stub mínimo
de sqlalchemy executa as consultas direto no sqlite3. Compara a saída com o
artigos.json atual. Uso: python stub_test.py <raiz> <db> [saida.json]"""
import sys, types, sqlite3, json, collections

raiz, dbpath = sys.argv[1], sys.argv[2]
sa = types.ModuleType('sqlalchemy'); sa.text = lambda s: s
orm = types.ModuleType('sqlalchemy.orm'); orm.Session = object
sys.modules['sqlalchemy'] = sa; sys.modules['sqlalchemy.orm'] = orm
sys.path.insert(0, raiz + '/backend')

class R:
    def __init__(s, cur): s.rows = cur.fetchall(); s.cols = [d[0] for d in cur.description]
    def all(s): return [tuple(r) for r in s.rows]
    def mappings(s): return types.SimpleNamespace(all=lambda: [dict(zip(s.cols, r)) for r in s.rows])
class Sess:
    def __init__(s, p): s.c = sqlite3.connect(p)
    def execute(s, sql, p=None):
        import re
        p = p or {}
        p = {k: v for k, v in p.items() if ':' + k in sql}
        return R(s.c.execute(sql, p))
    def rollback(s): pass

from app.models import dashboard_service as ds
db = Sess(dbpath)
api = ds.listar_artigos(db)
if len(sys.argv) > 3:
    json.dump(api, open(sys.argv[3], 'w'), ensure_ascii=False, separators=(',', ':'))
ref = {a['q01_id_estudo']: a for a in json.load(open(raiz + '/dashboard/data/artigos.json'))}
got = {a['q01_id_estudo']: a for a in api}
print('artigos API', len(got), '| ref', len(ref), '| só na ref', set(ref) - set(got), '| só na API', set(got) - set(ref))
dif = collections.Counter(); ex = {}
IGNORA = {'codificador'}
for i, r in ref.items():
    g = got.get(i, {})
    for k in (set(r) | set(g)) - IGNORA:
        rv, gv = r.get(k), g.get(k)
        if isinstance(rv, str): rv = rv.strip()
        if rv != gv:
            dif[k] += 1; ex.setdefault(k, (i, rv if not isinstance(rv, str) else rv[:80], gv if not isinstance(gv, str) else gv[:80]))
print('campos com diferença:', dict(dif) or 'nenhum')
for k, v in ex.items(): print('  ', k, v)
print('codificador presente na API?', any('codificador' in a for a in api), '| usuario_id?', any('usuario_id' in a for a in api))
one = ds.obter_artigo(db, 480); print('artigo 480:', one['q03_referencia'][:50], one['q09_desenho'])
print('inexistente:', ds.obter_artigo(db, 97))
t = ds.listar_triagem(db); print('triagem', len(t['registros']), collections.Counter(r['decisao'] for r in t['registros']), t['registros'][0])
csvtxt = ds.gerar_csv(api); linhas = csvtxt.splitlines(); print('csv linhas', len(linhas), 'colunas', len(linhas[0].split(',')))
open('/tmp/base.csv', 'w', encoding='utf-8').write(csvtxt)
