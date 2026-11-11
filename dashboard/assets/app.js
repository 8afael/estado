/* Site de resultados — Revisão sistemática Estado Aberto (Politeia Conecta) */
(function () {
'use strict';
const CFG = window.POLITEIA_CONFIG;
const $app = document.getElementById('app');
const D = {};              // dados carregados
let charts = [];           // instâncias Chart.js ativas

/* ------------------------------------------------------------------ utilidades */
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const h = (strings, ...vals) => strings.reduce((a, s, i) => a + s + (i < vals.length ? vals[i] : ''), '');
const fmt = n => n.toLocaleString('pt-BR');
const pct = (n, d) => d ? (100 * n / d) : 0;
const fpct = v => v.toLocaleString('pt-BR', {maximumFractionDigits: 1, minimumFractionDigits: v < 10 && v % 1 ? 1 : 0}) + '%';
const norm = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
async function getJSON(url) { const r = await fetch(url, {cache: 'no-cache'}); if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }
function wrapLabel(s, n = 34) {
  const words = String(s).split(' '); const lines = []; let cur = '';
  for (const w of words) { if ((cur + ' ' + w).trim().length > n && cur) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
  if (cur) lines.push(cur); return lines.length > 3 ? [...lines.slice(0, 2), lines.slice(2).join(' ').slice(0, n - 1) + '…'] : lines;
}
const LOGO = '<svg class="mark" viewBox="196 316 320 314" aria-hidden="true"><g fill="none" stroke-width="30" stroke-linecap="round"><path d="M221 614V480a135 135 0 0 1 270 0v134" stroke="#0b2545"/><path d="M265 614V480a91 91 0 0 1 182 0v134" stroke="#13a89e"/><path d="M310 614V480a46 46 0 0 1 92 0v134" stroke="#f1c40f"/></g><circle cx="356" cy="606" r="18" fill="#0b2545"/></svg>';
const ICON = {
  flow: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="8" height="5" rx="1"/><rect x="13" y="16" width="8" height="5" rx="1"/><rect x="3" y="16" width="8" height="5" rx="1"/><path d="M7 8v8M11 18.5h2"/></svg>',
  books: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 4v16M8 4v16M12 4v16M15 4.5l5 15"/></svg>',
  chart: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 20h16M7 16v-5M11 16V7M15 16v-7M19 16v-3"/></svg>',
  people: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="9" y="2.5" width="6" height="5" rx="1"/><rect x="3" y="16.5" width="6" height="5" rx="1"/><rect x="15" y="16.5" width="6" height="5" rx="1"/><path d="M12 7.5v4M6 16.5v-3h12v3"/></svg>',
  download: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
  eye: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>',
  lock: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>',
  doc: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 3h8l5 5v13H6Z"/><path d="M14 3v5h5M9 13h7M9 17h7"/></svg>',
  check: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 12l5 5L20 6"/></svg>',
  data: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>',
  users: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5M16 4.8a3.5 3.5 0 0 1 0 6.4M18 14.8c1.8.8 3 2.5 3.5 5.2"/></svg>',
  arrowR: '<svg width="40" height="16" viewBox="0 0 40 16"><path d="M0 8h32" stroke="currentColor" stroke-width="2"/><path d="M30 2l9 6-9 6Z" fill="currentColor"/></svg>',
  arrowD: '<svg width="16" height="26" viewBox="0 0 16 26"><path d="M8 0v18" stroke="currentColor" stroke-width="2"/><path d="M2 16l6 9 6-9Z" fill="currentColor"/></svg>'
};

/* ------------------------------------------------------------------ conceitos e grupos */
const CONCEITOS = [
  {slug: 'governo',    nome: 'Governo Aberto',    q16: 2, cor: '#1f5fa8'},
  {slug: 'governanca', nome: 'Governança Aberta', q16: 3, cor: '#14a08f'},
  {slug: 'estado',     nome: 'Estado Aberto',     q16: 1, cor: '#eda100'},
  {slug: 'parlamento', nome: 'Parlamento Aberto', q16: 4, cor: '#e87ba4'},
  {slug: 'justica',    nome: 'Justiça Aberta',    q16: 5, cor: '#6250d6'},
];
const OUTROS = {nome: 'Outros conceitos / sem conceito único', cor: '#e8692f'};
const conceitoBySlug = s => CONCEITOS.find(c => c.slug === s);
const conceitoDe = a => CONCEITOS.find(c => c.nome === a.q18_conceito_principal);
const ABSENT = new Set(['97', '98']);
const ABSENT_LABEL = /^n[ãa]o aplic[áa]vel$|^n[ãa]o identificad[oa]( no artigo)?$/i;

function grupo(state) {
  if (!state.c || state.c === 'todos') return {arts: D.artigos, label: 'Corpus total', n: D.artigos.length, cor: '#1f5fa8', todos: true};
  const c = conceitoBySlug(state.c);
  const arts = state.m === 'recorte'
    ? D.artigos.filter(a => (a.q16_conceitos_abertura || []).includes(c.q16))
    : D.artigos.filter(a => a.q18_conceito_principal === c.nome);
  return {arts, n: arts.length, cor: c.cor, conceito: c,
          label: c.nome + (state.m === 'recorte' ? ' · recorte ampliado (Q16)' : ' · conceito central (Q18)')};
}

/* normaliza um artigo vindo da plataforma em formato "largo" (q09_desenho_1 = "Sim") */
function normalizeArtigo(a) {
  const o = {};
  for (const [k, v] of Object.entries(a)) {
    const m = /^(q\d+_[a-z_]+?)_(\d+)$/.exec(k);
    if (m && !Array.isArray(a[m[1]])) {
      if (v === 'Sim' || v === 1 || v === '1' || v === true) (o[m[1]] = o[m[1]] || []).push(+m[2]);
      continue;
    }
    o[k] = v;
  }
  if (!o.ano) { const y = /\((\d{4})/.exec(o.q03_referencia || ''); o.ano = y ? +y[1] : null; }
  o.id = String(o.q01_id_estudo);
  return o;
}

/* ------------------------------------------------------------------ codebook helpers */
let QBYVAR = {};
function indexCodebook() {
  QBYVAR = {};
  D.codebook.secoes.forEach(s => s.questoes.forEach(q => { q.secao = s; QBYVAR[q.var] = q; }));
}
function opcoes(v) { return (QBYVAR[v] && QBYVAR[v].opcoes) || []; }
function rotulo(v, cod) { const o = opcoes(v).find(o => o.cod === String(cod)); return o ? o.rotulo : String(cod); }

/* ------------------------------------------------------------------ contagens */
const DERIVED_LABEL = {
  d_nucleo_sentido: 'Núcleo de sentido da definição', d_natureza_conceito: 'Natureza atribuída ao conceito',
  d_fonte_definicao: 'Fonte da definição', d_arquitetura_conceitual: 'Arquitetura conceitual',
  d_problema_delimitacao: 'Problema de delimitação', d_tipo_operacionalizacao: 'Tipo de operacionalização',
  d_funcao_direito: 'Função do direito', d_tipo_contribuicao: 'Tipo de contribuição', d_tipo_lacuna: 'Tipo de lacuna',
  _regioes: 'Região dos países analisados'
};
/* devolve {cats:[{key,label,n}], N, fora} — N exclui 97/98 do denominador */
function contar(arts, spec) {
  const v = spec.var; const q = QBYVAR[v]; const counts = new Map(); let N = 0, fora = 0;
  const add = (key, label) => { const c = counts.get(key) || {key, label, n: 0}; c.n++; counts.set(key, c); };
  const kind = spec.kind || (q ? q.kind : 'derived');
  for (const a of arts) {
    const val = a[v];
    if (kind === 'multi') {
      const codes = (val || []).map(String);
      const subst = codes.filter(c => !ABSENT.has(c));
      if (!subst.length) { fora++; continue; }
      N++; subst.forEach(c => add(c, rotulo(v, c)));
    } else if (kind === 'derived') {
      const parts = Array.isArray(val) ? val : String(val || '').split(';').map(s => s.trim()).filter(Boolean);
      if (!parts.length) { fora++; continue; }
      N++; parts.forEach(p => add(p, p.replace(/¹/g, '')));
    } else {
      if (val == null || val === '') { fora++; continue; }
      const s = String(val);
      if (ABSENT_LABEL.test(s)) { fora++; continue; }
      N++; add(s, s);
    }
  }
  let cats = [...counts.values()];
  if (spec.ordinal && q) {
    const order = q.opcoes.map(o => o.rotulo);
    cats.sort((a, b) => (order.indexOf(a.key) + 1 || 99) - (order.indexOf(b.key) + 1 || 99));
  } else cats.sort((a, b) => b.n - a.n);
  if (spec.top && cats.length > spec.top) cats = cats.slice(0, spec.top);
  return {cats, N, fora};
}
function matches(a, v, key) {
  const q = QBYVAR[v]; const kind = q ? q.kind : 'derived'; const val = a[v];
  if (v === 'ano') return String(a.ano) === String(key);
  if (v === '_paises_iso') return (a._paises_iso || []).includes(key);
  if (kind === 'multi') return (val || []).map(String).includes(String(key));
  if (kind === 'derived' || !q) { const parts = Array.isArray(val) ? val : String(val || '').split(';').map(s => s.trim()); return parts.includes(key); }
  return String(val) === String(key);
}

/* ------------------------------------------------------------------ roteamento */
function parseHash() {
  const raw = location.hash.replace(/^#\/?/, '') || 'inicio';
  const [path, qs] = raw.split('?');
  const parts = path.split('/');
  const params = Object.fromEntries(new URLSearchParams(qs || ''));
  return {page: parts[0] || 'inicio', id: parts[1], params};
}
function go(path, params) {
  const qs = params ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== '')).toString() : '';
  location.hash = '#/' + path + (qs.length > 1 ? qs : '');
}
let lastPage = null;
function route() {
  charts.forEach(c => c.destroy()); charts = [];
  const r = parseHash();
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.toggle('active', a.dataset.r === r.page));
  document.getElementById('nav-links').classList.remove('open');
  const pages = {inicio: pageInicio, prisma: pagePrisma, artigos: r.id ? pageAnalise : pageArtigos, resultados: pageResultados, equipe: pageEquipe, codebook: pageCodebook};
  (pages[r.page] || pageInicio)(r);
  const key = r.page + '/' + (r.id || '');
  if (key !== lastPage) { window.scrollTo(0, 0); postParent({type: 'politeia:scrollTop'}); }
  lastPage = key;
}

/* ------------------------------------------------------------------ iframe: altura automática */
function postParent(msg) { if (window.parent !== window) window.parent.postMessage(msg, CFG.origemPai || '*'); }
function setupIframe() {
  if (window.parent === window) return;
  let last = 0;
  const send = () => { const hgt = Math.ceil(document.body.getBoundingClientRect().height); if (Math.abs(hgt - last) > 2) { last = hgt; postParent({type: 'politeia:height', height: hgt}); } };
  new ResizeObserver(send).observe(document.body); window.addEventListener('load', send); setInterval(send, 1500);
}

/* ================================================================== PÁGINA: INÍCIO */
function pageInicio() {
  const P = D.prisma, C = D.conteudo;
  $app.innerHTML = h`<div class="wrap">
  <section class="hero">
    <span class="kicker">Ciência Aberta</span>
    <div class="lockup">${LOGO}<div><b>Estado Aberto</b><span>Estado, Parlamento e Justiça Aberta</span></div></div>
    <span class="eyebrow">Revisão sistemática da literatura · Ação 2 – Ciência Aberta</span>
    <h1>O que a literatura científica diz sobre Estado, Parlamento e Justiça Aberta</h1>
    <p class="lead">Como a literatura define, delimita e operacionaliza a abertura do Estado, do Legislativo e do sistema de justiça, e como esses conceitos se relacionam com Governo Aberto e Governança Aberta? Este espaço apresenta, de forma aberta e rastreável, todo o percurso da revisão: das ${fmt(P.identificacao.total)} referências encontradas nas bases de dados aos ${fmt(P.incluidos)} artigos lidos na íntegra e codificados.</p>
    <div class="actions">
      <a class="btn btn-teal" href="#/resultados">${ICON.chart.replace(/26/g, 18)} Explorar os resultados</a>
      <a class="btn btn-ghost" href="#/prisma">Ver o procedimento PRISMA</a>
      <a class="btn btn-ghost" href="#/artigos">Consultar os ${P.incluidos} artigos</a>
      ${CFG.downloads.base ? `<a class="btn btn-yellow" href="${esc(CFG.downloads.base)}" download>${ICON.download.replace(/26/g, 18)} Baixar a base de dados</a>` : ''}
    </div>
    <p class="small" style="margin:22px 0 0;color:var(--ink-2)"><b>Projeto:</b> ${esc(D.conteudo.projeto)} · <b>Ação:</b> ${esc(D.conteudo.acao)} · ${esc(D.conteudo.grupo)}</p>
  </section>

  <div class="section grid g4">
    <div class="stat"><b>${fmt(P.identificacao.total)}</b><span>registros identificados</span></div>
    <div class="stat yellow"><b>${fmt(P.triagem.triados)}</b><span>registros triados</span></div>
    <div class="stat teal"><b>${fmt(P.incluidos)}</b><span>estudos incluídos</span></div>
    <div class="stat"><b>${D.equipe.membros.length}</b><span>avaliadores</span></div>
  </div>

  <div class="section question-box">
    <span class="eyebrow">Pergunta de pesquisa</span>
    <p class="q">${esc(C.pergunta)}</p>
    <p class="small" style="margin-top:12px;opacity:.8"><em>${esc(C.pergunta_en)}</em></p>
  </div>

  <div class="section grid g2">
    <div class="card"><h3>Objetivo geral</h3><p class="oe-text" style="margin:0">${esc(C.objetivo_geral)}</p></div>
    <div class="card"><h3>Objetivos específicos</h3>
      <ol style="margin:0;padding-left:1.2em;color:var(--ink-2)">${C.objetivos_especificos.map(o => `<li>${esc(o.titulo)}</li>`).join('')}</ol></div>
  </div>

  <div class="section">
    <h2>Ciência aberta: um processo que pode ser verificado</h2>
    <p class="oe-text" style="max-width:820px">A revisão integra a Ação 2 – Ciência Aberta do Projeto Estado Aberto. Em vez de apresentar apenas as conclusões, publicamos o caminho que levou até elas: os critérios usados para selecionar os estudos, a decisão tomada sobre cada registro, o instrumento de extração e a codificação de cada artigo. Qualquer pessoa pode conferir por que um estudo entrou na revisão, como ele foi lido e de que forma contribui para os resultados.</p>
    <div class="grid g2" style="margin-top:18px">
      <div class="card pillar"><div class="ic">${ICON.doc}</div><div><h4>Protocolo e critérios publicados</h4><p>Bases consultadas, datas das buscas, critérios de triagem T1 a T4 e regras de decisão entre avaliadores, seguindo o PRISMA 2020.</p></div></div>
      <div class="card pillar"><div class="ic">${ICON.check}</div><div><h4>Decisões rastreáveis</h4><p>Cada um dos ${fmt(P.triagem.triados)} registros tem as avaliações independentes e a decisão final. Divergências e incertezas passaram por um terceiro avaliador.</p></div></div>
      <div class="card pillar"><div class="ic">${ICON.data}</div><div><h4>Análises abertas e reutilizáveis</h4><p>O formulário de extração de cada artigo pode ser consultado, com as evidências e as páginas que sustentam cada resposta. A base de dados dos ${P.incluidos} artigos e o codebook estão disponíveis para download e reutilização.</p></div></div>
      <div class="card pillar"><div class="ic">${ICON.lock}</div><div><h4>Respeito aos direitos autorais</h4><p>Os textos integrais dos artigos não estão disponíveis nesta plataforma. Para cada artigo, indicamos a referência bibliográfica padrão APA.</p></div></div>
    </div>
  </div>

  <div class="section">
    <p class="section-title">Navegue pela revisão</p>
    <div class="grid g3">
      <a class="card feature" href="#/prisma">${ICON.flow}<h3>Procedimento PRISMA</h3><p>Da identificação à inclusão: buscas, triagem dos ${fmt(P.triagem.triados)} registros e regras de decisão.</p></a>
      <a class="card feature" href="#/artigos">${ICON.books}<h3>Artigos analisados</h3><p>Lista dos ${P.incluidos} estudos em ordem alfabética, com o formulário de análise de cada um.</p></a>
      <a class="card feature" href="#/resultados">${ICON.chart}<h3>Resultados</h3><p>Gráficos interativos por objetivo, com detalhamento por conceito de abertura.</p></a>
      <a class="card feature" href="#/equipe">${ICON.people}<h3>Equipe</h3><p>Coordenação, bolsistas, voluntários e professor que avaliaram os estudos.</p></a>
      <a class="card feature" href="#/codebook">${ICON.download}<h3>Codebook e base de dados</h3><p>Instrumento de extração com ${P.extracao.variaveis} variáveis em ${P.extracao.secoes} seções e a base dos ${P.incluidos} artigos analisados, para download.</p></a>
    </div>
  </div>
  </div>`;
}

/* ================================================================== PÁGINA: PRISMA */
function pagePrisma(r) {
  const P = D.prisma; const tab = r.params.etapa || 'triagem';
  const box = (id, html) => `<div class="box ${tab === id ? 'sel' : ''}" data-etapa="${id}" role="button" tabindex="0">${html}</div>`;
  $app.innerHTML = h`<div class="wrap">
  <div class="page-head"><h1>Procedimento PRISMA 2020</h1><p>Fluxo de seleção dos estudos, adaptado de Page et al. (2021). Clique em uma etapa para ver os detalhes.</p></div>
  <div class="card">
    <div class="flow-top">Identificação de estudos por meio de bases de dados</div>
    <div class="flow">
      <div class="phase" style="grid-row:1">Identificação</div>
      ${box('identificacao', `<b>Registros identificados nas bases de dados</b> (n = <span class="n">${P.identificacao.total}</span>)<br>${P.identificacao.bases.map(b => `${b.nome} (n = ${b.n})`).join('<br>')}<br><span class="small muted">Buscas: 25/05/2026 (Scopus e WoS); 30/05/2026 (SciELO)</span>`)}
      <div class="arrow">${ICON.arrowR}</div>
      <div class="side"><b>Removidos antes da triagem</b><br>Duplicatas removidas no Mendeley (n = ${P.identificacao.duplicatas})<br>Marcados como inelegíveis por automação (n = ${P.identificacao.automacao})<br>Removidos por outros motivos (n = ${P.identificacao.outros})</div>
      <div class="down">${ICON.arrowD}</div>
      <div class="phase" style="grid-row:3 / span 5">Triagem</div>
      ${box('triagem', `<b>Registros triados por título, resumo e palavras-chave</b> (n = <span class="n">${P.triagem.triados}</span>)`)}
      <div class="arrow">${ICON.arrowR}</div>
      <div class="side"><b>Registros excluídos</b> (n = ${P.triagem.excluidos})<br>Critérios de triagem T1–T4, ano e idioma</div>
      <div class="down">${ICON.arrowD}</div>
      ${box('recuperacao', `<b>Relatórios buscados para recuperação</b> (n = <span class="n">${P.recuperacao.buscados}</span>)`)}
      <div class="arrow">${ICON.arrowR}</div>
      <div class="side"><b>Relatórios não recuperados</b> (n = ${P.recuperacao.nao_recuperados})</div>
      <div class="down">${ICON.arrowD}</div>
      ${box('elegibilidade', `<b>Relatórios avaliados para elegibilidade</b> (leitura integral e extração) (n = <span class="n">${P.elegibilidade.avaliados}</span>)`)}
      <div class="arrow">${ICON.arrowR}</div>
      <div class="side"><b>Relatórios excluídos</b> (n = ${P.elegibilidade.excluidos})<br>${esc(P.elegibilidade.motivo)}</div>
      <div class="down">${ICON.arrowD}</div>
      <div class="phase" style="grid-row:9">Incluídos</div>
      ${box('inclusao', `<b>Estudos incluídos na revisão</b> (n = <span class="n">${P.incluidos}</span>)<br>Relatórios dos estudos incluídos (n = ${P.incluidos})`)}
    </div>
    <p class="small muted" style="margin:16px 0 0">Triagem por dois avaliadores independentes, às cegas, com encaminhamento a um terceiro avaliador em caso de divergência ou incerteza. Nove registros duplicados não foram detectados pelo Mendeley e foram excluídos na extração; os números das etapas anteriores foram preservados como efetivamente registrados.</p>
  </div>
  <div class="section" id="etapa"></div>
  </div>`;
  $app.querySelectorAll('.flow .box').forEach(b => {
    const f = () => go('prisma', {etapa: b.dataset.etapa});
    b.onclick = f; b.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); f(); } };
  });
  const el = document.getElementById('etapa');
  ({identificacao: etapaIdentificacao, triagem: etapaTriagem, recuperacao: etapaRecuperacao, elegibilidade: etapaElegibilidade, inclusao: etapaInclusao}[tab] || etapaTriagem)(el);
  if (r.params.etapa) setTimeout(() => el.scrollIntoView({behavior: 'smooth', block: 'start'}), 50);
}
function etapaIdentificacao(el) {
  const I = D.prisma.identificacao;
  el.innerHTML = h`<h2>Identificação</h2>
  <div class="grid g4">${I.bases.map(b => `<div class="stat teal"><b>${b.n}</b><span>${esc(b.nome)} · ${b.data}</span></div>`).join('')}<div class="stat bad"><b>${I.duplicatas}</b><span>duplicatas removidas</span></div></div>
  <p class="oe-text" style="margin-top:16px">As buscas recuperaram ${I.total} registros. Antes da triagem, ${I.duplicatas} duplicatas foram removidas com o gerenciador de referências Mendeley. Nenhum registro foi marcado como inelegível por ferramentas de automação nem removido por outros motivos, resultando em ${D.prisma.triagem.triados} registros encaminhados à triagem.</p>`;
}
function etapaRecuperacao(el) {
  el.innerHTML = `<h2>Recuperação dos textos completos</h2><p class="oe-text">Os ${D.prisma.recuperacao.buscados} relatórios selecionados na triagem foram buscados para leitura integral. Como os textos completos já haviam sido baixados e organizados na primeira fase, todos foram recuperados (${D.prisma.recuperacao.nao_recuperados} não recuperados).</p>`;
}
function etapaElegibilidade(el) {
  const E = D.prisma.elegibilidade, X = D.prisma.extracao;
  el.innerHTML = h`<h2>Elegibilidade: leitura integral e extração</h2>
  <div class="grid g4"><div class="stat"><b>${E.avaliados}</b><span>relatórios lidos na íntegra</span></div><div class="stat bad"><b>${E.excluidos}</b><span>duplicatas excluídas</span></div><div class="stat teal"><b>${X.variaveis}</b><span>variáveis no formulário</span></div><div class="stat yellow"><b>${X.avaliadores}</b><span>avaliadores na extração</span></div></div>
  <p class="oe-text" style="margin-top:16px">Cada relatório foi lido na íntegra e analisado no formulário de extração (codebook com ${X.variaveis} variáveis em ${X.secoes} seções), entre ${X.periodo}. Nessa etapa foram identificados ${E.excluidos} registros duplicados que não haviam sido detectados na desduplicação inicial (estudos ${E.ids_excluidos.join(', ')}); manteve-se uma cópia de cada estudo e a exclusão foi registrada no log de alterações.</p>
  <div class="note teal">O uso de inteligência artificial era permitido apenas como apoio, com registro da ferramenta, da finalidade e do prompt, e com validação humana obrigatória. Esse registro aparece no fim do formulário de cada artigo (Q58 e Q59).</div>
  <p style="margin-top:14px"><a class="btn btn-ghost btn-sm" href="#/codebook">Consultar o codebook</a></p>`;
}
function etapaInclusao(el) {
  const anos = D.artigos.map(a => a.ano).filter(Boolean);
  el.innerHTML = `<h2>Inclusão</h2><p class="oe-text">Ao final do processo, ${D.prisma.incluidos} estudos foram incluídos na revisão, publicados entre ${Math.min(...anos)} e ${Math.max(...anos)}. A lista completa, com o formulário de análise de cada estudo, está na página de artigos.</p><a class="btn btn-teal" href="#/artigos">Ver os ${D.prisma.incluidos} artigos analisados</a>`;
}
function etapaTriagem(el) {
  const T = D.prisma.triagem, R = D.prisma.regras;
  const dec = d => ({Incluir: 'ok', Excluir: 'bad', Incerto: 'warn'}[d] || '');
  const decLower = d => d ? `<span class="chip ${dec(d)}">${d.toLowerCase()}</span>` : '<span class="chip">—</span>';
  el.innerHTML = h`<h2>Triagem por título, resumo e palavras-chave</h2>
  <div class="note">Cada registro foi avaliado às cegas por dois avaliadores independentes (A1 e A2). Quando houve divergência ou classificação “Incerto”, um terceiro avaliador (A3) decidiu. A seguir estão as perguntas de triagem, a regra aplicada por avaliador, a regra de decisão final e o resultado de cada registro.</div>

  <div class="section"><p class="section-title">Perguntas de triagem (T1 – T4)</p>
  <div class="grid g2">${R.perguntas.map(p => `<div class="card rule-q"><span class="qbadge">${p.id}</span><p style="margin:0">${esc(p.texto)}</p>${p.termos ? `<div style="margin-top:8px">${p.termos.map(t => `<span class="chip">${esc(t)}</span>`).join(' ')}</div>` : ''}</div>`).join('')}</div></div>

  <div class="section"><p class="section-title">Regra de decisão por avaliador</p>
  <div class="grid" style="gap:12px">${R.por_avaliador.map((d, i) => { const cls = ['', 'warn', 'ok'][i]; return `<div class="card decision ${cls}"><div class="num">${i + 1}</div><div><h4 style="display:inline;margin-right:8px">${d.decisao}</h4><span class="chip ${['bad', 'warn', 'ok'][i]}">${esc(d.selo)}</span><p class="small" style="margin:6px 0 0;color:var(--ink-2)">${esc(d.texto)}</p><div>${d.condicoes.map(c => `<span class="chip ${['bad', 'warn', 'ok'][i]}">${esc(c)}</span>`).join('')}</div></div></div>`; }).join('')}</div></div>

  <div class="section"><p class="section-title">Decisão final do artigo (dois avaliadores)</p>
  <div class="grid g3">${R.final.map(f => { const c = {incluir: 'ok', excluir: 'bad', incerto: 'warn'}[f.tipo]; return `<div class="card final ${c}"><div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><h4 style="margin:0">${f.decisao}</h4><span class="pill ${c}">${{incluir: 'Incluir', excluir: 'Excluir', incerto: 'Aguard. 3º avaliador'}[f.tipo]}</span></div><ul>${f.condicoes.map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>`; }).join('')}</div></div>

  <div class="section"><p class="section-title">Matriz de combinações e resultados</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Avaliador A1</th><th>Avaliador A2</th><th>Avaliador A3</th><th>Decisão final</th></tr></thead><tbody>
  ${R.matriz.map(m => `<tr><td>${decLower(m[0])}</td><td>${decLower(m[1])}</td><td>${decLower(m[2])}</td><td><span class="pill ${m[3] === 'Inclusão' ? 'ok' : 'bad'}">${m[3]} final</span></td></tr>`).join('')}
  </tbody></table></div><p class="small muted" style="margin-top:8px">${esc(R.nota_matriz)}</p></div>

  <div class="section"><p class="section-title">Resultado da triagem</p>
  <div class="grid g4"><div class="stat"><b>${T.triados}</b><span>avaliados</span></div><div class="stat yellow"><b>0</b><span>pendentes</span></div><div class="stat ok"><b>${T.incluidos}</b><span>incluídos</span></div><div class="stat bad"><b>${T.excluidos}</b><span>excluídos</span></div></div>
  <div class="table-wrap" style="margin-top:14px"><table class="data"><thead><tr><th>Forma de decisão</th><th>Incluídos</th><th>Excluídos</th><th>Total</th></tr></thead><tbody>
   <tr><td>Convergência dos dois avaliadores</td><td class="num">${T.convergencia.incluidos}</td><td class="num">${T.convergencia.excluidos}</td><td class="num">${T.convergencia.total}</td></tr>
   <tr><td>Decisão com terceiro avaliador</td><td class="num">${T.terceiro.incluidos}</td><td class="num">${T.terceiro.excluidos}</td><td class="num">${T.terceiro.total}</td></tr>
   <tr><td><b>Total</b></td><td class="num"><b>${T.incluidos}</b></td><td class="num"><b>${T.excluidos}</b></td><td class="num"><b>${T.triados}</b></td></tr></tbody></table></div>
  <div id="triagem-lista" class="section" style="margin-top:22px"></div></div>`;
  renderTriagemLista(document.getElementById('triagem-lista'));
}
function renderTriagemLista(el) {
  const regs = (D.triagem && D.triagem.registros) || [];
  if (!regs.length) {
    el.innerHTML = `<div class="note yellow"><b>Registros individuais da triagem.</b> A tabela com os ${D.prisma.triagem.triados} registros (título, A1, A2, A3 e decisão final) é carregada diretamente da plataforma. Nenhum registro foi encontrado na fonte configurada (<code>${esc(CFG.dados.triagem)}</code>).</div>`;
    return;
  }
  const st = {q: '', s: '', p: 0};
  el.innerHTML = h`<div class="toolbar"><input type="search" placeholder="Filtrar por ID ou título…" aria-label="Filtrar registros"><select aria-label="Status"><option value="">Todos os status</option><option value="Incluído">Incluídos</option><option value="Excluído">Excluídos</option></select></div><div class="table-wrap"><table class="data"><thead><tr><th>ID</th><th>Título</th><th>A1</th><th>A2</th><th>A3</th><th>Decisão final</th></tr></thead><tbody></tbody></table></div><div class="pager"></div>`;
  const tb = el.querySelector('tbody'), pg = el.querySelector('.pager');
  const chip = v => { if (!v) return '<span class="chip">—</span>'; const k = norm(v); return `<span class="chip ${k.startsWith('incl') ? 'ok' : k.startsWith('excl') ? 'bad' : 'warn'}">${esc(String(v).toLowerCase())}</span>`; };
  const draw = () => {
    const f = regs.filter(r => (!st.s || norm(r.decisao).startsWith(norm(st.s).slice(0, 4))) && (!st.q || norm(r.id + ' ' + r.titulo).includes(norm(st.q))));
    const per = 25, pages = Math.max(1, Math.ceil(f.length / per)); st.p = Math.min(st.p, pages - 1);
    tb.innerHTML = f.slice(st.p * per, st.p * per + per).map(r => `<tr><td class="num">${esc(r.id)}</td><td>${esc(r.titulo)}</td><td>${chip(r.a1)}</td><td>${chip(r.a2)}</td><td>${chip(r.a3)}</td><td><span class="pill ${norm(r.decisao).startsWith('incl') ? 'ok' : 'bad'}">${esc(r.decisao)}</span></td></tr>`).join('') || '<tr><td colspan="6" class="empty">Nenhum registro.</td></tr>';
    pager(pg, st, pages, f.length, draw);
  };
  el.querySelector('input').oninput = e => { st.q = e.target.value; st.p = 0; draw(); };
  el.querySelector('select').onchange = e => { st.s = e.target.value; st.p = 0; draw(); };
  draw();
}
function pager(el, st, pages, total, draw) {
  el.innerHTML = `<span class="small muted">${fmt(total)} registro(s) · página ${st.p + 1} de ${pages}</span><span><button class="btn btn-ghost btn-sm" ${st.p ? '' : 'disabled'} data-d="-1">Anterior</button> <button class="btn btn-ghost btn-sm" ${st.p < pages - 1 ? '' : 'disabled'} data-d="1">Próxima</button></span>`;
  el.querySelectorAll('button').forEach(b => b.onclick = () => { st.p += +b.dataset.d; draw(); el.parentElement.scrollIntoView({block: 'start'}); });
}

/* ================================================================== PÁGINA: ARTIGOS */
const artState = {q: '', conceito: '', idioma: '', regiao: '', ano: '', p: 0};
function pageArtigos(r) {
  const prm = r.params; const drill = prm.var ? prm : null;
  const idiomas = [...new Set(D.artigos.map(a => a.q04_idioma).filter(Boolean))].sort();
  const regioes = [...new Set(D.artigos.flatMap(a => a._regioes || []))].sort();
  const anos = [...new Set(D.artigos.map(a => a.ano).filter(Boolean))].sort();
  let base = D.artigos, drillLabel = '';
  if (drill) {
    const g = grupo({c: drill.c, m: drill.m});
    base = g.arts.filter(a => matches(a, drill.var, drill.val));
    const q = QBYVAR[drill.var];
    const qname = q ? `Q${q.q} · ${q.titulo}` : (DERIVED_LABEL[drill.var] || (drill.var === 'ano' ? 'Ano de publicação' : drill.var === '_paises_iso' ? 'País analisado' : drill.var));
    const vlabel = drill.var === '_paises_iso' ? paisNome(drill.val) : (q && q.kind === 'multi' ? rotulo(drill.var, drill.val) : drill.val);
    drillLabel = `<b>${esc(qname)}</b>: ${esc(vlabel)} · ${esc(g.label)}`;
  }
  $app.innerHTML = h`<div class="wrap">
  <div class="page-head"><h1>Artigos analisados</h1><p>${D.artigos.length} estudos incluídos, em ordem alfabética das referências (APA 7). Clique em “Visualizar análise” para abrir o formulário de extração preenchido.</p></div>
  <div class="copyright">${ICON.lock}<span>Por respeito aos direitos autorais, os textos integrais (PDF) não são disponibilizados.</span></div>
  ${CFG.downloads.base ? `<div class="note teal" style="margin-bottom:14px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center"><span><b>Base de dados aberta.</b> Baixe as codificações dos ${D.artigos.length} artigos analisados (CSV, uma linha por artigo, variáveis conforme o codebook).</span><a class="btn btn-yellow btn-sm" href="${esc(CFG.downloads.base)}" download>Baixar base (CSV)</a></div>` : ''}
  ${drill ? `<div class="note teal" style="margin-bottom:14px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center"><span>Filtro vindo dos resultados: ${drillLabel} (${base.length} artigo${base.length === 1 ? '' : 's'})</span><span><a class="btn btn-ghost btn-sm" href="javascript:history.back()">Voltar ao gráfico</a> <a class="btn btn-ghost btn-sm" href="#/artigos">Limpar filtro</a></span></div>` : ''}
  <div class="toolbar">
    <input type="search" id="f-q" placeholder="Buscar por autor, título, periódico, país ou ID…" value="${esc(artState.q)}" aria-label="Buscar artigos">
    <select id="f-conceito" aria-label="Conceito principal"><option value="">Todos os conceitos principais</option>${CONCEITOS.map(c => `<option value="${c.nome}">${c.nome}</option>`).join('')}<option value="__outros">Outros / sem conceito único</option></select>
    <select id="f-idioma" aria-label="Idioma"><option value="">Todos os idiomas</option>${idiomas.map(i => `<option>${esc(i)}</option>`).join('')}</select>
    <select id="f-regiao" aria-label="Região"><option value="">Todas as regiões</option>${regioes.map(i => `<option>${esc(i)}</option>`).join('')}</select>
    <select id="f-ano" aria-label="Ano"><option value="">Todos os anos</option>${anos.map(i => `<option>${i}</option>`).join('')}</select>
  </div>
  <div class="table-wrap"><table class="data"><thead><tr><th>#</th><th>Referência (APA)</th><th>Ano</th><th>Idioma</th><th>Conceito principal</th><th><span class="sr-only">Ações</span></th></tr></thead><tbody id="tb"></tbody></table></div>
  <div class="pager" id="pg"></div></div>`;
  ['conceito', 'idioma', 'regiao', 'ano'].forEach(k => { const s = document.getElementById('f-' + k); s.value = artState[k]; s.onchange = () => { artState[k] = s.value; artState.p = 0; draw(); }; });
  document.getElementById('f-q').oninput = e => { artState.q = e.target.value; artState.p = 0; draw(); };
  const tb = document.getElementById('tb'), pg = document.getElementById('pg');
  function draw() {
    const q = norm(artState.q);
    const f = base.filter(a => {
      if (artState.conceito === '__outros' ? conceitoDe(a) : artState.conceito && a.q18_conceito_principal !== artState.conceito) return false;
      if (artState.idioma && a.q04_idioma !== artState.idioma) return false;
      if (artState.regiao && !(a._regioes || []).includes(artState.regiao)) return false;
      if (artState.ano && String(a.ano) !== artState.ano) return false;
      if (q && !norm(a.q03_referencia + ' ' + (a.q05_pais_lista || '') + ' ' + a.id).includes(q)) return false;
      return true;
    });
    const per = 25, pages = Math.max(1, Math.ceil(f.length / per)); artState.p = Math.min(artState.p, pages - 1);
    tb.innerHTML = f.slice(artState.p * per, artState.p * per + per).map((a, i) => {
      const c = conceitoDe(a);
      const cl = c ? `<span class="tag"><span class="dot" style="background:${c.cor}"></span>${c.nome}</span>` : `<span class="tag">${esc(a.q18_conceito_principal === 'Outro — especificar' ? (a.q18_conceito_principal_outro || 'Outro') : a.q18_conceito_principal)}</span>`;
      return `<tr><td class="num">${artState.p * per + i + 1}</td><td class="ref">${esc(a.q03_referencia || '')}</td><td class="num">${a.ano || ''}</td><td>${esc(a.q04_idioma || '')}</td><td>${cl}</td><td class="act"><a class="btn btn-teal btn-sm" href="#/artigos/${a.id}">${ICON.eye} Visualizar análise</a></td></tr>`;
    }).join('') || '<tr><td colspan="6" class="empty">Nenhum artigo encontrado com esses filtros.</td></tr>';
    pager(pg, artState, pages, f.length, draw);
  }
  draw();
}
function paisNome(iso) { const a = D.artigos.find(a => (a._paises_iso || []).includes(iso)); if (!a) return iso; const i = a._paises_iso.indexOf(iso); return (a.q05_pais_lista || '').split(';').map(s => s.trim()).filter(Boolean)[i] || iso; }

/* ================================================================== PÁGINA: ANÁLISE (formulário preenchido) */
async function pageAnalise(r) {
  let a = D.artigos.find(x => x.id === r.id);
  if (CFG.artigoUnico) {
    $app.innerHTML = '<div class="loading">Carregando a análise…</div>';
    try { a = normalizeArtigo(await getJSON(CFG.artigoUnico.replace('{id}', encodeURIComponent(r.id)))); } catch (e) { /* usa a cópia da lista */ }
  }
  if (!a) { $app.innerHTML = `<div class="wrap"><div class="card empty">Artigo ${esc(r.id)} não encontrado. <a href="#/artigos">Voltar à lista</a></div></div>`; return; }
  const doi = (/https?:\/\/doi\.org\/\S+/.exec(a.q03_referencia || '') || [])[0];
  const c = conceitoDe(a);
  $app.innerHTML = h`<div class="wrap">
  <p><a href="#/artigos" onclick="if(history.length>1){history.back();return false}">← Voltar à lista de artigos</a></p>
  <div class="modal" style="width:100%;box-shadow:var(--shadow)">
    <div class="modal-head"><p style="margin-bottom:6px">Formulário de extração · Estudo ${esc(a.id)}</p><h2>${esc(a.q03_referencia)}</h2>
      <p>${[a.ano, a.q04_idioma, a.q05_pais_lista, c ? c.nome : null].filter(Boolean).map(esc).join(' · ')}</p></div>
    <div class="modal-body">
      <div class="copyright">${ICON.lock}<span>O texto integral não é disponibilizado nesta plataforma, em cumprimento aos direitos autorais. ${doi ? `Acesse o artigo pela página do editor: <a href="${esc(doi.replace(/[.,;]$/, ''))}" target="_blank" rel="noopener">${esc(doi)}</a>.` : ''}</span></div>
      <div class="toolbar" style="justify-content:space-between">
        <div class="seg" role="group" aria-label="Exibição"><button class="active" data-v="all">Formulário completo</button><button data-v="on">Somente respostas</button></div>
        <span><button class="btn btn-ghost btn-sm" id="open-all">Expandir tudo</button> <button class="btn btn-ghost btn-sm" onclick="window.print()">Imprimir</button></span>
      </div>
      <div id="form">${formHTML(a)}</div>
    </div></div></div>`;
  const form = document.getElementById('form');
  $app.querySelectorAll('.seg button').forEach(b => b.onclick = () => { $app.querySelectorAll('.seg button').forEach(x => x.classList.toggle('active', x === b)); form.classList.toggle('hide-off', b.dataset.v === 'on'); });
  document.getElementById('open-all').onclick = e => { const open = e.target.textContent === 'Expandir tudo'; form.querySelectorAll('details').forEach(d => d.open = open); e.target.textContent = open ? 'Recolher tudo' : 'Expandir tudo'; };
}
function answerText(a, v) {
  const t = a[v]; const ev = a[v + '_evid'];
  return (t ? `<div class="answer-text">${esc(t)}</div>` : '<span class="blank">Não preenchido</span>') + (ev ? `<div class="evid">${esc(ev)}</div>` : '');
}
function formHTML(a) {
  return D.codebook.secoes.map((s, si) => {
    const qs = s.questoes.filter(q => q.var !== 'q02_arquivo').map(q => {
      let body = '';
      if (q.kind === 'auto') body = `<div class="answer-text">${esc(a[q.var] != null ? a[q.var] : a.id)}</div>`;
      else if (q.kind === 'text') body = answerText(a, q.var);
      else if (q.kind === 'pairs') {
        body = q.pares.map((p, i) => { const rel = a[`q25_${i + 1}_relacao`], ev = a[`q25_${i + 1}_evidencia`];
          return `<div style="margin:6px 0"><b class="small">${esc(p)}</b><br>${rel ? `<span class="opt on">${esc(rel)}</span>` : '<span class="blank">Em branco (par não tratado pelo artigo)</span>'}${ev ? `<div class="answer-text" style="margin-top:4px">${esc(ev)}</div>` : ''}</div>`; }).join('')
          + (a.q25_pares_conceituais_evid ? `<div class="evid">${esc(a.q25_pares_conceituais_evid)}</div>` : '')
          + (a.q25_relacoes_texto_livre ? `<div class="small" style="margin-top:6px"><b>Relações (texto livre):</b> ${esc(a.q25_relacoes_texto_livre)}</div>` : '');
      } else if (q.kind === 'multi') {
        const sel = (a[q.var] || []).map(String);
        body = `<div class="opts">${q.opcoes.map(o => `<span class="opt ${sel.includes(o.cod) ? 'on' : ''}">${esc(o.rotulo)}</span>`).join('')}</div>`;
        if (!sel.length) body += '<span class="blank">Nenhuma opção marcada</span>';
        if (q.var === 'q05_pais' && a.q05_pais_lista) body += `<div class="small" style="margin-top:6px"><b>Países:</b> ${esc(a.q05_pais_lista)}</div>`;
        if (a[q.var + '_outro']) body += `<div class="small" style="margin-top:6px"><b>Outro:</b> ${esc(a[q.var + '_outro'])}</div>`;
      } else { // single / scale
        const val = a[q.var] != null ? String(a[q.var]) : '';
        const isOn = o => q.kind === 'scale' ? o.cod === val : o.rotulo === val;
        const known = q.opcoes.some(isOn);
        body = `<div class="opts">${q.opcoes.map(o => `<span class="opt ${isOn(o) ? 'on' : ''}">${q.kind === 'scale' ? o.cod + ' · ' : ''}${esc(o.rotulo)}</span>`).join('')}${val && !known ? `<span class="opt on">${esc(val)}</span>` : ''}</div>`;
        if (!val) body += '<span class="blank">Não preenchido</span>';
        if (a[q.var + '_outro']) body += `<div class="small" style="margin-top:6px"><b>Especificação:</b> ${esc(a[q.var + '_outro'])}</div>`;
      }
      return `<div class="cb-q"><div class="qt"><span class="qbadge">Q${q.q}</span><b>${esc(q.titulo)}</b></div>${body}</div>`;
    }).join('');
    return `<details class="cb-sec" ${si < 3 ? 'open' : ''}><summary>Seção ${s.n} — ${esc(s.titulo)}<span class="small muted" style="font-family:var(--f-body);font-weight:400;margin-left:auto">${s.questoes.length} questões</span></summary>${qs}</details>`;
  }).join('') + derivedHTML(a) + `<p class="small muted" style="margin-top:12px">Status ${esc(a.status || '—')} · última atualização ${esc(a.data_atualizacao || '—')}</p>`;
}
function derivedHTML(a) {
  const ks = Object.keys(DERIVED_LABEL).filter(k => k.startsWith('d_') && a[k]);
  if (!ks.length) return '';
  return `<details class="cb-sec"><summary>Codificação derivada da síntese (equipe)</summary>${ks.map(k => `<div class="cb-q"><div class="qt"><b>${DERIVED_LABEL[k]}</b></div><div class="opts">${String(a[k]).split(';').map(s => `<span class="opt on">${esc(s.trim().replace(/¹/g, ''))}</span>`).join('')}</div></div>`).join('')}</details>`;
}

/* ================================================================== PÁGINA: RESULTADOS */
const OE_CHARTS = {
  OE1: [{type: 'ano', title: 'Evolução anual da produção', sub: 'Artigos por ano de publicação e conceito principal (2026 é ano parcial)', wide: true},
        {type: 'mapa', title: 'Países analisados nos estudos', sub: 'Número de artigos que analisam cada país (Q5)', wide: true},
        {var: '_regioes', kind: 'derived', title: 'Região dos países analisados'},
        {var: 'q04_idioma', title: 'Idioma da publicação'},
        {var: 'q07_natureza', title: 'Natureza principal do artigo'},
        {var: 'q08_abordagem', title: 'Abordagem metodológica'},
        {var: 'q09_desenho', title: 'Desenho ou estratégia de pesquisa', top: 10},
        {var: 'q13_escala_geo', title: 'Escala geográfica principal'}],
  OE2: [{var: 'q20_tipo_definicao', title: 'Tipo de definição apresentada', ordinal: true},
        {var: 'd_natureza_conceito', kind: 'derived', title: 'Natureza atribuída ao conceito'},
        {var: 'd_nucleo_sentido', kind: 'derived', title: 'Núcleo de sentido da definição'},
        {var: 'd_fonte_definicao', kind: 'derived', title: 'Fonte da definição'},
        {var: 'q26_principios', title: 'Princípios associados ao conceito', top: 12, wide: true}],
  OE3: [{var: 'q21_delimitacao', title: 'Delimitação em relação a conceitos próximos', wide: true},
        {var: 'd_problema_delimitacao', kind: 'derived', title: 'Problema de delimitação'},
        {var: 'q17_conceitos_relac', title: 'Conceitos relacionados explicitamente analisados', top: 12}],
  OE4: [{var: 'q23_rel_gov_aberto', title: 'Relação do conceito principal com Governo Aberto', wide: true},
        {var: 'q24_rel_governanca_aberta', title: 'Relação do conceito principal com Governança Aberta', wide: true},
        {var: 'd_arquitetura_conceitual', kind: 'derived', title: 'Arquitetura conceitual', wide: true}],
  OE5: [{var: 'q27_tem_dimensoes', title: 'Apresenta dimensões, componentes ou pilares?', ordinal: true},
        {var: 'q29_operacionalizado', title: 'O conceito é operacionalizado?', ordinal: true},
        {var: 'd_tipo_operacionalizacao', kind: 'derived', title: 'Tipo de operacionalização'},
        {var: 'q30_forma_operac', title: 'Forma da operacionalização'},
        {var: 'q31_objeto_aplicacao', title: 'Objeto de aplicação do conceito', wide: true}],
  OE6: [{type: 'hiato', title: 'Hiato entre princípios declarados, concretizados e frágeis', sub: 'Q26 (associados ao conceito) × Q42 (manifestação concreta) × Q43 (frágeis ou ausentes)', wide: true},
        {var: 'q41_estagio_impl', title: 'Estágio de implementação', ordinal: true},
        {var: 'q46_extensao_mudanca', title: 'Extensão da mudança', ordinal: true},
        {var: 'q44_obstaculos', title: 'Obstáculos à abertura', top: 12},
        {var: 'q45_condicoes', title: 'Condições para uma abertura efetiva', top: 12},
        {var: 'q47_mudanca_poder', title: 'Evidência de mudança nas relações de poder', wide: true}],
  OE7: [{var: 'q33_atores', title: 'Instituições ou atores incluídos', top: 12},
        {var: 'q34_nivel_inst', title: 'Nível institucional/governamental'},
        {var: 'q35_instrumentos', title: 'Instrumentos normativos, jurídicos ou de política', top: 12},
        {var: 'd_funcao_direito', kind: 'derived', title: 'Função do direito'},
        {var: 'q37_analisa_digital', title: 'Analisa ferramentas ou plataformas digitais?'},
        {var: 'q40_enquadr_tec', title: 'Enquadramento teórico das tecnologias digitais', top: 10},
        {var: 'q38_ferramentas_dig', title: 'Ferramentas ou plataformas digitais analisadas', top: 10},
        {var: 'q39_funcoes_dig', title: 'Funções atribuídas às ferramentas digitais', top: 10},
        {var: 'q48_papel_soc_civil', title: 'Papel da sociedade civil'},
        {var: 'q49_papel_midia', title: 'Papel da mídia ou cobertura mediática'}],
  SINT: [{var: 'd_tipo_contribuicao', kind: 'derived', title: 'Tipo de contribuição dos artigos'},
         {var: 'd_tipo_lacuna', kind: 'derived', title: 'Tipo de lacuna registrada'},
         {var: 'q56_confianca', title: 'Confiança global na codificação', ordinal: true},
         {var: 'q55_clareza', kind: 'scale', title: 'Clareza do artigo para a extração (1 a 5)'}]
};
const OE_TABS = () => [...D.conteudo.objetivos_especificos.map(o => ({id: o.id, label: o.id, titulo: o.titulo, texto: o.sintese, eixos: o.eixos})),
  {id: 'SINT', label: 'Síntese e lacunas', titulo: 'Síntese integradora, consensos, controvérsias e qualidade da revisão', eixos: 'E11, E12'}];

function pageResultados(r) {
  const st = {c: r.params.c || 'todos', m: r.params.m || 'nucleo', oe: r.params.oe || 'OE1'};
  const setSt = patch => { const n = Object.assign({}, st, patch); history.replaceState(null, '', '#/resultados?' + new URLSearchParams(n)); Object.assign(st, n); render(); };
  const C = D.conteudo;
  $app.innerHTML = h`<div class="wrap">
  <div class="page-head"><h1>Resultados</h1><p>Painel construído a partir das respostas do formulário de extração dos ${D.artigos.length} estudos. Escolha um conceito para ver o recorte correspondente e clique em uma barra para listar os artigos.</p></div>
  <div class="question-box">
    <span class="eyebrow">Pergunta de pesquisa</span><p class="q">${esc(C.pergunta)}</p>
    <details style="margin-top:14px"><summary style="cursor:pointer;color:var(--yellow);font-weight:600">Resposta da revisão à pergunta de pesquisa</summary>
      <div style="margin-top:12px">${C.resposta_pergunta.map(p => `<p style="margin:0 0 10px"><b style="color:#fff">${esc(p.titulo)}</b> ${esc(p.texto)}</p>`).join('')}</div></details>
    <p class="small" style="margin-top:14px"><b style="color:#fff">Objetivo geral.</b> ${esc(C.objetivo_geral)}</p>
  </div>
  <div class="filterbar"><div class="row">
    <label>Conceito</label>
    <div class="seg" id="seg-c" role="group" aria-label="Conceito"><button data-c="todos"><span class="dot" style="background:#0b2545"></span>Corpus total</button>${CONCEITOS.map(c => `<button data-c="${c.slug}"><span class="dot" style="background:${c.cor}"></span>${c.nome}</button>`).join('')}</div>
    <span id="mode-wrap"><label style="margin-right:8px">Recorte</label><span class="seg" id="seg-m" role="group" aria-label="Recorte"><button data-m="nucleo" title="Artigos em que o conceito é o principal (Q18)">Conceito central</button><button data-m="recorte" title="Todos os artigos que abordam o conceito (Q16)">Recorte ampliado</button></span></span>
  </div></div>
  <div id="concept-panel"></div>
  <div class="tabs" id="oe-tabs" role="tablist"></div>
  <div id="oe-body"></div>
  </div>`;
  document.querySelectorAll('#seg-c button').forEach(b => b.onclick = () => setSt({c: b.dataset.c}));
  document.querySelectorAll('#seg-m button').forEach(b => b.onclick = () => setSt({m: b.dataset.m}));
  function render() {
    charts.forEach(c => c.destroy()); charts = [];
    document.querySelectorAll('#seg-c button').forEach(b => b.classList.toggle('active', b.dataset.c === st.c));
    document.querySelectorAll('#seg-m button').forEach(b => b.classList.toggle('active', b.dataset.m === st.m));
    document.getElementById('mode-wrap').style.display = st.c === 'todos' ? 'none' : '';
    const g = grupo(st);
    renderConceptPanel(document.getElementById('concept-panel'), st, g);
    const tabs = OE_TABS();
    document.getElementById('oe-tabs').innerHTML = tabs.map(t => `<button role="tab" class="${t.id === st.oe ? 'active' : ''}" data-oe="${t.id}" title="${esc(t.titulo)}">${t.label}</button>`).join('');
    document.querySelectorAll('#oe-tabs button').forEach(b => b.onclick = () => setSt({oe: b.dataset.oe}));
    const t = tabs.find(t => t.id === st.oe) || tabs[0];
    renderOE(document.getElementById('oe-body'), t, st, g);
  }
  render();
}
function renderConceptPanel(el, st, g) {
  if (g.todos) {
    const n18 = c => D.artigos.filter(a => a.q18_conceito_principal === c.nome).length;
    const n16 = c => D.artigos.filter(a => (a.q16_conceitos_abertura || []).includes(c.q16)).length;
    el.innerHTML = h`<div class="grid g2" style="margin-bottom:22px"><div class="card"><h3>O corpus em uma página</h3><p class="oe-text">${esc(D.conteudo.sintese_geral)}</p>${(D.conteudo.sintese_achados || []).map(m => `<div class="msg"><b>${esc(m.titulo.replace(/\.$/, ''))}</b><p>${esc(m.texto)}</p></div>`).join('')}</div>
      <div class="card"><h3>Lugar de cada conceito no corpus</h3><p class="small muted" style="margin-top:-4px">Artigos que têm o conceito como central (Q18) e que o abordam explicitamente (Q16). Clique em um conceito para detalhar.</p>
      <table class="mini-table"><thead><tr><th>Conceito</th><th class="r">Central</th><th class="r">Aborda</th></tr></thead><tbody>${CONCEITOS.map(c => `<tr><td><a href="#/resultados?c=${c.slug}&m=nucleo&oe=${st.oe}"><span class="tag"><span class="dot" style="background:${c.cor}"></span>${c.nome}</span></a></td><td class="r">${n18(c)}</td><td class="r">${n16(c)}</td></tr>`).join('')}
      <tr><td><span class="tag"><span class="dot" style="background:${OUTROS.cor}"></span>Conceitos correlatos e múltiplos</span></td><td class="r">${D.artigos.filter(a => !conceitoDe(a)).length}</td><td class="r">—</td></tr></tbody></table></div></div>`;
    return;
  }
  const c = g.conceito, R = D.conteudo.conceitos[c.slug];
  const nN = D.artigos.filter(a => a.q18_conceito_principal === c.nome).length, nR = D.artigos.filter(a => (a.q16_conceitos_abertura || []).includes(c.q16)).length;
  el.innerHTML = h`<div class="card concept-panel" style="--c:${c.cor};margin-bottom:22px">
    <div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start">
      <div><span class="eyebrow">Relatório temático</span><h2 style="margin:0">${c.nome}</h2></div>
      <div style="display:flex;gap:10px"><div class="stat${st.m !== 'recorte' ? ' ativo' : ''}" style="border-left-color:${c.cor};padding:10px 16px"><b style="font-size:1.4rem">${nN}</b><span>conceito central</span></div><div class="stat${st.m === 'recorte' ? ' ativo' : ''}" style="border-left-color:${c.cor};padding:10px 16px"><b style="font-size:1.4rem">${nR}</b><span>abordam o conceito</span></div></div>
    </div>
    ${R.em_uma_frase ? `<p class="frase">Em uma frase: ${esc(R.em_uma_frase)}</p>` : ''}
    <div class="grid g2" style="margin-top:8px">
      <div>${R.mensagens.map(m => `<div class="msg"><b>${esc(m.titulo)}</b><p>${esc(m.texto)}</p></div>`).join('')}</div>
      <div><figure><img src="assets/figuras/${c.slug}_tracos.png" alt="Traços que distinguem ${esc(c.nome)} do corpus da revisão" loading="lazy"><figcaption>${esc(R.distintivo.replace(/^A Figura 11 reúne/, 'A figura reúne'))}</figcaption></figure>
        <details style="margin-top:12px"><summary style="cursor:pointer;font-weight:600">Lacunas e agenda de pesquisa</summary>${R.lacunas.map(m => `<div class="msg"><b>${esc(m.titulo)}</b><p>${esc(m.texto)}</p></div>`).join('')}</details>
        <details style="margin-top:8px"><summary style="cursor:pointer;font-weight:600">Como o recorte foi construído</summary><ul class="small" style="color:var(--ink-2)">${R.recorte.map(x => `<li>${esc(x)}</li>`).join('')}</ul></details>
      </div>
    </div>
    <p class="small muted" style="margin:14px 0 0">Os gráficos abaixo mostram <b>${esc(g.label)}</b> (n = ${g.n}) em cor, com o corpus total (N = ${D.artigos.length}) em cinza como referência. ${g.n < 20 ? 'Como o grupo é pequeno, leia os resultados em contagens (“6 de 9”), como tendências qualitativas.' : ''}</p>
  </div>`;
}
function renderOE(el, t, st, g) {
  const specs = OE_CHARTS[t.id] || [];
  let intro = t.texto ? `<p class="oe-text">${esc(t.texto)}</p>` : '';
  if (t.id === 'SINT') {
    const C = D.conteudo;
    intro = `<div class="grid g2"><div class="card"><h3>Consensos</h3>${C.consensos.map(x => `<div class="msg"><p>${esc((x.titulo + ' ' + x.texto).trim())}</p></div>`).join('')}</div><div class="card"><h3>Controvérsias</h3>${C.controversias.map(x => `<div class="msg"><b>${esc(x.titulo)}</b><p>${esc(x.texto)}</p></div>`).join('')}</div></div>`;
  }
  el.innerHTML = `<h2>${t.id !== 'SINT' ? t.id + ' · ' : ''}${esc(t.titulo)}</h2><p class="small muted" style="margin-top:-6px">Eixos da matriz de sistematização: ${esc(t.eixos)}</p>${intro}
    <p class="small muted">Regra de leitura: os códigos “não aplicável” (97) e “não identificado” (98) ficam fora do denominador das porcentagens; “não mencionado” (96) é tratado como achado. Em questões de múltipla escolha, as porcentagens somam mais de 100%.</p>
    <div class="grid g2" id="charts" style="margin-top:14px"></div>`;
  const box = el.querySelector('#charts');
  specs.forEach(spec => {
    const card = document.createElement('div'); card.className = 'card chart-card';
    if (spec.wide) card.style.gridColumn = '1 / -1';
    box.appendChild(card);
    if (spec.type === 'ano') chartAno(card, spec, st, g);
    else if (spec.type === 'mapa') chartMapa(card, spec, st, g);
    else if (spec.type === 'hiato') chartHiato(card, spec, st, g);
    else chartBarras(card, spec, st, g);
  });
}

/* ---------- gráficos */
Chart.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.color = '#44526a';
const GRID = '#eceff3', REF = '#c3cad3';
const tooltipBase = {backgroundColor: '#0b2545', titleFont: {weight: '600'}, padding: 10, cornerRadius: 6, displayColors: true, boxPadding: 4};

function chartHead(card, spec, extra) {
  const q = QBYVAR[spec.var];
  card.innerHTML = `<div class="head"><div><h4>${esc(spec.title)}</h4><div class="sub">${esc(spec.sub || (q ? `Q${q.q} · ${q.tipo}` : spec.var && spec.var.startsWith('d_') ? 'Codificação derivada da síntese (equipe)' : spec.var === '_regioes' ? 'Derivado de Q5 (países analisados)' : ''))}</div></div><button class="linkbtn" data-t>Ver tabela</button></div>${extra || ''}<div class="canvas-box"></div><div class="tbl" hidden></div><div class="foot"></div>`;
  const btn = card.querySelector('[data-t]'), tbl = card.querySelector('.tbl'), cb = card.querySelector('.canvas-box');
  btn.onclick = () => { const show = tbl.hidden; tbl.hidden = !show; cb.hidden = show; btn.textContent = show ? 'Ver gráfico' : 'Ver tabela'; };
  return {cb, tbl, foot: card.querySelector('.foot')};
}
function drill(st, v, key) { go('artigos', {var: v, val: key, c: st.c, m: st.m}); }

function chartBarras(card, spec, st, g) {
  const res = contar(g.arts, spec);
  const ref = !g.todos ? contar(D.artigos, Object.assign({}, spec, {top: 0})) : null;
  const {cb, tbl, foot} = chartHead(card, spec, !g.todos ? `<div class="legend"><span><i style="background:${g.cor}"></i>${esc(g.conceito.nome)} (n = ${g.n})</span><span><i style="background:${REF}"></i>Corpus total (N = ${D.artigos.length})</span></div>` : '');
  if (!res.cats.length) { cb.innerHTML = '<div class="empty small">Sem respostas substantivas neste recorte.</div>'; foot.textContent = `${res.fora} artigo(s) sem informação.`; return; }
  const labels = res.cats.map(c => wrapLabel(c.label));
  const vals = res.cats.map(c => pct(c.n, res.N));
  const refMap = ref ? new Map(ref.cats.map(c => [c.key, c])) : null;
  const refVals = ref ? res.cats.map(c => pct((refMap.get(c.key) || {n: 0}).n, ref.N)) : null;
  const lines = Math.max(...labels.map(l => l.length));
  const rowH = (ref ? 34 : 26) + (lines > 1 ? 8 : 0);
  cb.style.height = (res.cats.length * rowH + 50) + 'px';
  const canvas = document.createElement('canvas'); cb.appendChild(canvas);
  canvas.setAttribute('role', 'img'); canvas.setAttribute('aria-label', `${spec.title}: ` + res.cats.map(c => `${c.label} ${c.n}`).join('; '));
  const datasets = [{label: g.todos ? 'Corpus total' : g.conceito.nome, data: vals, backgroundColor: g.cor, borderRadius: 4, borderSkipped: 'start', barPercentage: .9, categoryPercentage: ref ? .82 : .78, maxBarThickness: 20}];
  if (ref) datasets.push({label: 'Corpus total', data: refVals, backgroundColor: REF, borderRadius: 4, borderSkipped: 'start', barPercentage: .9, categoryPercentage: .82, maxBarThickness: 12});
  const small = res.N < 20;
  const chart = new Chart(canvas, {
    type: 'bar', data: {labels, datasets},
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: {duration: 250},
      layout: {padding: {right: 96}},
      scales: {x: {beginAtZero: true, max: Math.min(100, Math.ceil((Math.max(...vals, ...(refVals || [0])) + 6) / 10) * 10), grid: {color: GRID}, border: {display: false}, ticks: {callback: v => v + '%'}},
               y: {grid: {display: false}, border: {color: '#cfd6de'}, ticks: {color: '#0c1f3a', autoSkip: false}}},
      plugins: {legend: {display: false},
        tooltip: Object.assign({}, tooltipBase, {callbacks: {
          title: it => res.cats[it[0].dataIndex].label,
          label: it => { if (it.datasetIndex === 1) { const c = refMap.get(res.cats[it.dataIndex].key) || {n: 0}; return ` Corpus: ${c.n} de ${ref.N} (${fpct(pct(c.n, ref.N))})`; } const c = res.cats[it.dataIndex]; return ` ${g.todos ? 'Corpus' : g.conceito.nome}: ${c.n} de ${res.N} (${fpct(pct(c.n, res.N))})`; },
          footer: () => 'Clique para ver os artigos'}})},
      onClick: (e, els) => { if (els.length) drill(st, spec.var, res.cats[els[0].index].key); },
      onHover: (e, els) => { e.native.target.style.cursor = els.length ? 'pointer' : 'default'; }
    },
    plugins: [{id: 'vlabels', afterDatasetsDraw(ch) {
      const ctx = ch.ctx, meta = ch.getDatasetMeta(0); ctx.save(); ctx.font = '600 11.5px "IBM Plex Mono", monospace'; ctx.fillStyle = '#0c1f3a'; ctx.textBaseline = 'middle';
      meta.data.forEach((bar, i) => { const c = res.cats[i]; const txt = small ? `${c.n} de ${res.N}` : `${c.n} · ${fpct(pct(c.n, res.N))}`; const x = Math.max(bar.x, ref ? ch.getDatasetMeta(1).data[i].x : 0); ctx.fillText(txt, x + 6, bar.y); });
      ctx.restore(); }}]
  });
  charts.push(chart);
  tbl.innerHTML = `<table class="mini-table"><thead><tr><th>Categoria</th><th class="r">n</th><th class="r">%</th>${ref ? '<th class="r">% corpus</th>' : ''}</tr></thead><tbody>${res.cats.map((c, i) => `<tr><td><button class="linkbtn" data-k="${esc(c.key)}">${esc(c.label)}</button></td><td class="r">${c.n}</td><td class="r">${fpct(vals[i])}</td>${ref ? `<td class="r">${fpct(refVals[i])}</td>` : ''}</tr>`).join('')}</tbody></table>`;
  tbl.querySelectorAll('[data-k]').forEach(b => b.onclick = () => drill(st, spec.var, b.dataset.k));
  foot.textContent = `Base: ${res.N} artigo(s) com informação${res.fora ? `; ${res.fora} sem informação (97/98 ou em branco) fora do denominador` : ''}.${spec.top ? ` Mostrando as ${spec.top} categorias mais frequentes.` : ''}`;
}

function chartAno(card, spec, st, g) {
  const {cb, tbl, foot} = chartHead(card, spec);
  const anos = [...new Set(D.artigos.map(a => a.ano))].filter(Boolean).sort();
  const series = g.todos ? [...CONCEITOS.map(c => ({nome: c.nome, cor: c.cor, f: a => a.q18_conceito_principal === c.nome})), {nome: OUTROS.nome, cor: OUTROS.cor, f: a => !conceitoDe(a)}]
                         : [{nome: g.conceito.nome, cor: g.cor, f: () => true}];
  const data = series.map(s => anos.map(y => g.arts.filter(a => a.ano === y && s.f(a)).length));
  cb.style.height = '320px';
  const legend = document.createElement('div'); legend.className = 'legend';
  legend.innerHTML = series.map(s => `<span><i style="background:${s.cor}"></i>${esc(s.nome)}</span>`).join('');
  cb.before(legend);
  const canvas = document.createElement('canvas'); cb.appendChild(canvas);
  canvas.setAttribute('role', 'img'); canvas.setAttribute('aria-label', 'Artigos por ano: ' + anos.map((y, i) => `${y}: ${series.reduce((s, _, j) => s + data[j][i], 0)}`).join('; '));
  const chart = new Chart(canvas, {type: 'bar', data: {labels: anos.map(y => y === 2026 ? '2026*' : String(y)), datasets: series.map((s, j) => ({label: s.nome, data: data[j], backgroundColor: s.cor, borderColor: '#fff', borderWidth: {top: 2}, borderSkipped: 'start', borderRadius: j === series.length - 1 ? 4 : 0, maxBarThickness: 34}))},
    options: {responsive: true, maintainAspectRatio: false, animation: {duration: 250},
      scales: {x: {stacked: true, grid: {display: false}}, y: {stacked: true, beginAtZero: true, grid: {color: GRID}, border: {display: false}, ticks: {precision: 0}}},
      interaction: {mode: 'index', intersect: false},
      plugins: {legend: {display: false}, tooltip: Object.assign({}, tooltipBase, {filter: it => it.raw > 0, callbacks: {footer: it => `Total: ${it.reduce((s, x) => s + x.raw, 0)} · clique para ver os artigos`}})},
      onClick: (e, els) => { if (els.length) drill(st, 'ano', anos[els[0].index]); },
      onHover: (e, els) => { e.native.target.style.cursor = els.length ? 'pointer' : 'default'; }}});
  charts.push(chart);
  tbl.innerHTML = `<div style="overflow:auto"><table class="mini-table"><thead><tr><th>Ano</th>${series.map(s => `<th class="r">${esc(s.nome)}</th>`).join('')}<th class="r">Total</th></tr></thead><tbody>${anos.map((y, i) => `<tr><td>${y}</td>${series.map((s, j) => `<td class="r">${data[j][i]}</td>`).join('')}<td class="r">${series.reduce((s, _, j) => s + data[j][i], 0)}</td></tr>`).join('')}</tbody></table></div>`;
  foot.textContent = `${g.arts.length} artigos · ${g.todos ? 'cores indicam o conceito principal (Q18)' : esc(g.label)}.`;
}

function chartHiato(card, spec, st, g) {
  const {cb, tbl, foot} = chartHead(card, spec);
  const S = [{v: 'q26_principios', nome: 'Associado ao conceito (Q26)', cor: '#1f5fa8'}, {v: 'q42_princ_concretos', nome: 'Manifestação concreta (Q42)', cor: '#14a08f'}, {v: 'q43_princ_frageis', nome: 'Frágil ou ausente (Q43)', cor: '#e8692f'}];
  const res = S.map(s => contar(g.arts, {var: s.v}));
  const keys = res[0].cats.slice(0, 10).map(c => c.key);
  const val = (r, k) => { const c = r.cats.find(c => c.key === k); return c ? c.n : 0; };
  const legend = document.createElement('div'); legend.className = 'legend'; legend.innerHTML = S.map(s => `<span><i style="background:${s.cor}"></i>${s.nome}</span>`).join(''); cb.before(legend);
  cb.style.height = (keys.length * 46 + 50) + 'px';
  const canvas = document.createElement('canvas'); cb.appendChild(canvas);
  canvas.setAttribute('role', 'img'); canvas.setAttribute('aria-label', 'Hiato entre princípios: ' + keys.map(k => `${rotulo('q26_principios', k)} associado ${val(res[0], k)}, concreto ${val(res[1], k)}, frágil ${val(res[2], k)}`).join('; '));
  const chart = new Chart(canvas, {type: 'bar', data: {labels: keys.map(k => rotulo('q26_principios', k)), datasets: S.map((s, i) => ({label: s.nome, data: keys.map(k => pct(val(res[i], k), res[i].N)), backgroundColor: s.cor, borderRadius: 4, borderSkipped: 'start', maxBarThickness: 12, categoryPercentage: .84, barPercentage: .92}))},
    options: {indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: {duration: 250},
      scales: {x: {beginAtZero: true, grid: {color: GRID}, border: {display: false}, ticks: {callback: v => v + '%'}}, y: {grid: {display: false}, ticks: {color: '#0c1f3a'}}},
      plugins: {legend: {display: false}, tooltip: Object.assign({}, tooltipBase, {callbacks: {label: it => ` ${S[it.datasetIndex].nome}: ${val(res[it.datasetIndex], keys[it.dataIndex])} de ${res[it.datasetIndex].N} (${fpct(it.raw)})`, footer: () => 'Clique para ver os artigos'}})},
      onClick: (e, els) => { if (els.length) drill(st, S[els[0].datasetIndex].v, keys[els[0].index]); },
      onHover: (e, els) => { e.native.target.style.cursor = els.length ? 'pointer' : 'default'; }}});
  charts.push(chart);
  tbl.innerHTML = `<table class="mini-table"><thead><tr><th>Princípio</th>${S.map(s => `<th class="r">${s.nome}</th>`).join('')}</tr></thead><tbody>${keys.map(k => `<tr><td>${esc(rotulo('q26_principios', k))}</td>${res.map(r => `<td class="r">${val(r, k)} (${fpct(pct(val(r, k), r.N))})</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  foot.textContent = `Bases: Q26 ${res[0].N}, Q42 ${res[1].N}, Q43 ${res[2].N} artigos com informação · ${g.label}. Princípios ordenados pela frequência em Q26.`;
}

function chartMapa(card, spec, st, g) {
  const {cb, tbl, foot} = chartHead(card, spec);
  const counts = new Map();
  g.arts.forEach(a => (a._paises_iso || []).forEach(i => counts.set(i, (counts.get(i) || 0) + 1)));
  const max = Math.max(1, ...counts.values());
  const W = 960, H = 470;
  const svg = d3.select(cb).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('role', 'img').attr('aria-label', 'Mapa: ' + [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10).map(([k, v]) => `${paisNome(k)} ${v}`).join('; '));
  const proj = d3.geoNaturalEarth1().fitSize([W, H], D.mapa); const path = d3.geoPath(proj);
  const color = d3.scaleSequentialSqrt([0, max], d3.interpolateRgb('#d4efea', '#0a5248'));
  const tip = d3.select(cb).append('div').style('position', 'absolute').style('pointer-events', 'none').style('background', '#0c1f3a').style('color', '#fff').style('padding', '6px 10px').style('border-radius', '6px').style('font-size', '12px').style('display', 'none');
  cb.style.position = 'relative';
  svg.append('g').selectAll('path').data(D.mapa.features).join('path').attr('d', path)
    .attr('fill', f => counts.has(f.id) ? color(counts.get(f.id)) : '#eceff3').attr('stroke', '#fff').attr('stroke-width', .6)
    .style('cursor', f => counts.has(f.id) ? 'pointer' : 'default')
    .on('mousemove', (e, f) => { const [x, y] = d3.pointer(e, cb); tip.style('display', 'block').style('left', (x + 12) + 'px').style('top', (y - 10) + 'px').html(`<b>${esc(f.properties.pt || f.properties.n)}</b><br>${counts.get(f.id) || 0} artigo(s)`); })
    .on('mouseleave', () => tip.style('display', 'none'))
    .on('click', (e, f) => { if (counts.has(f.id)) drill(st, '_paises_iso', f.id); });
  // legenda de cor
  const lg = svg.append('g').attr('transform', `translate(24,${H - 40})`);
  const grad = svg.append('defs').append('linearGradient').attr('id', 'lg-map');
  d3.range(0, 1.01, .1).forEach(t => grad.append('stop').attr('offset', t).attr('stop-color', color(t * max)));
  lg.append('rect').attr('width', 160).attr('height', 10).attr('rx', 3).attr('fill', 'url(#lg-map)');
  lg.append('text').attr('y', 26).attr('font-size', 12).attr('fill', '#44526a').text('1');
  lg.append('text').attr('x', 160).attr('y', 26).attr('text-anchor', 'end').attr('font-size', 12).attr('fill', '#44526a').text(max + ' artigos');
  const rows = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  tbl.innerHTML = `<table class="mini-table"><thead><tr><th>País</th><th class="r">Artigos</th></tr></thead><tbody>${rows.map(([k, v]) => `<tr><td><button class="linkbtn" data-k="${k}">${esc(paisNome(k))}</button></td><td class="r">${v}</td></tr>`).join('')}</tbody></table>`;
  tbl.querySelectorAll('[data-k]').forEach(b => b.onclick = () => drill(st, '_paises_iso', b.dataset.k));
  foot.textContent = `${counts.size} países analisados · ${g.label}. Mais frequentes: ${rows.slice(0, 5).map(([k, v]) => `${paisNome(k)} (${v})`).join(', ')}.`;
}

/* ================================================================== PÁGINA: EQUIPE */
function pageEquipe() {
  const ordem = ['Coordenador', 'Coordenadora', 'Professor', 'Professora', 'Bolsista', 'Voluntário', 'Voluntária'];
  const grupoDe = v => /^coord/i.test(v) ? 'Coordenação' : /^prof/i.test(v) ? 'Professor(a)' : /^bols/i.test(v) ? 'Bolsistas' : /^volunt/i.test(v) ? 'Voluntários(as)' : 'Equipe';
  const grupos = {};
  [...D.equipe.membros].sort((a, b) => ordem.indexOf(a.vinculo) - ordem.indexOf(b.vinculo)).forEach(m => (grupos[grupoDe(m.vinculo)] = grupos[grupoDe(m.vinculo)] || []).push(m));
  const ini = n => n.split(/\s+/).filter(w => w.length > 2 || /^[A-Z]/.test(w)).map(w => w[0]).filter((_, i, arr) => i === 0 || i === arr.length - 1).join('').toUpperCase();
  const person = m => `<div class="card person"><div class="avatar">${m.foto ? `<img src="${esc(m.foto)}" alt="">` : ini(m.nome)}</div><div><h4>${esc(m.nome)}</h4><p><span class="chip">${esc(m.vinculo)}</span></p>${m.perfil ? `<p style="margin-top:6px">${esc(m.perfil)}</p>` : ''}${m.lattes ? `<p><a href="${esc(m.lattes)}" target="_blank" rel="noopener">Currículo Lattes</a></p>` : ''}</div></div>`;
  $app.innerHTML = h`<div class="wrap">
  <div class="page-head"><h1>Equipe de avaliadores</h1><p>${D.equipe.membros.length} pessoas atuaram na triagem por título e resumo, na terceira avaliação e na leitura integral e extração de dados, nas fases 1 e 2 da revisão.</p></div>
  ${Object.entries(grupos).map(([g, ms]) => `<div class="role-head"><h3 style="margin:0">${g}</h3><span class="count">${ms.length}</span></div><div class="grid g3">${ms.map(person).join('')}</div>`).join('')}
  ${D.equipe.apoio && D.equipe.apoio.length ? `<div class="role-head"><h3 style="margin:0">Apoio técnico</h3></div><div class="grid g2">${D.equipe.apoio.map(person).join('')}</div>` : ''}
  </div>`;
}

/* ================================================================== PÁGINA: CODEBOOK */
function pageCodebook() {
  const dl = CFG.downloads; const cb = D.codebook;
  const total = cb.secoes.reduce((s, x) => s + x.questoes.length, 0);
  $app.innerHTML = h`<div class="wrap">
  <div class="page-head"><h1>Codebook do formulário de extração</h1><p>${total} variáveis em ${cb.secoes.length} seções · ${esc(cb.versao)}. Define, para cada variável, o tipo de resposta, as categorias e a regra de codificação.</p></div>
  <div class="grid g2">
    <div class="card"><h3>Baixar o codebook e a base de dados</h3><p class="muted">O codebook é o instrumento usado na leitura integral dos ${D.artigos.length} estudos; a base reúne as codificações de cada artigo, com uma linha por estudo e uma coluna por variável. Ambos podem ser reutilizados por outras pesquisas, com a devida citação.</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap">${dl.codebookPdf ? `<a class="btn btn-yellow" href="${esc(dl.codebookPdf)}" download>${ICON.download.replace(/26/g, 18)} PDF</a>` : ''}${dl.codebookDocx ? `<a class="btn btn-ghost" href="${esc(dl.codebookDocx)}" download>${ICON.download.replace(/26/g, 18)} Word (DOCX)</a>` : ''}${dl.base ? `<a class="btn btn-ghost" href="${esc(dl.base)}" download>${ICON.download.replace(/26/g, 18)} Base de dados dos ${D.artigos.length} artigos (CSV)</a>` : ''}</div></div>
    <div class="card"><h3>Convenções de codificação</h3><table class="mini-table"><tbody><tr><td class="r">88</td><td>Outro — especificar</td></tr><tr><td class="r">96</td><td>Não mencionado (tratado como achado)</td></tr><tr><td class="r">97</td><td>Não aplicável (fora do denominador)</td></tr><tr><td class="r">98</td><td>Não identificado no artigo (fora do denominador)</td></tr></tbody></table></div>
  </div>
  <div class="section">${cb.secoes.map(s => `<details class="cb-sec"><summary>Seção ${s.n} — ${esc(s.titulo)}<span class="small muted" style="font-family:var(--f-body);font-weight:400;margin-left:auto">${s.questoes.length} questões</span></summary>${s.questoes.map(q => `<div class="cb-q"><div class="qt"><span class="qbadge">Q${q.q}</span><b>${esc(q.titulo)}</b></div><div class="var">${esc(q.var)} · ${esc(q.tipo)}</div>${q.orientacao.map(o => `<p class="cb-guide">${esc(o)}</p>`).join('')}${q.opcoes.length ? `<table class="cb-opt-table"><tbody>${q.opcoes.map(o => `<tr><td>${esc(o.cod)}</td><td>${esc(o.rotulo)}</td><td>${esc(o.criterio)}</td></tr>`).join('')}</tbody></table>` : ''}</div>`).join('')}</details>`).join('')}</div>
  </div>`;
}

/* ================================================================== início */
document.querySelector('.nav-toggle').onclick = e => { const l = document.getElementById('nav-links'); l.classList.toggle('open'); e.target.setAttribute('aria-expanded', l.classList.contains('open')); };
async function boot() {
  try {
    const d = CFG.dados;
    const [artigos, codebook, prisma, conteudo, equipe, mapa] = await Promise.all([d.artigos, d.codebook, d.prisma, d.conteudo, d.equipe, d.mapa].map(getJSON));
    Object.assign(D, {codebook, prisma, conteudo, equipe, mapa});
    D.artigos = (Array.isArray(artigos) ? artigos : artigos.artigos || artigos.data).map(normalizeArtigo)
      .sort((x, y) => norm(x.q03_referencia).replace(/[^a-z0-9 ]/g, '').localeCompare(norm(y.q03_referencia).replace(/[^a-z0-9 ]/g, '')));
    try { D.triagem = await getJSON(d.triagem); if (Array.isArray(D.triagem)) D.triagem = {registros: D.triagem}; } catch (e) { D.triagem = {registros: []}; }
    indexCodebook();
  } catch (e) {
    $app.innerHTML = `<div class="wrap"><div class="card empty">Não foi possível carregar os dados (${esc(e.message)}). Se estiver abrindo o arquivo diretamente do computador, use um servidor local (veja o LEIAME).</div></div>`;
    return;
  }
  window.addEventListener('hashchange', route);
  setupIframe();
  route();
}
boot();
})();
