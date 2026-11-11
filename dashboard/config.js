/*
 * Configuração das fontes de dados do site de resultados.
 *
 * API: endereço da API pública da plataforma (rotas em backend/app/routers/dashboard_router.py).
 *   - Preenchido: artigos, artigo individual, triagem e o CSV da base vêm direto do banco.
 *   - Vazio (""): o site usa os arquivos JSON/CSV estáticos de ./data e ./downloads.
 * Se o site for publicado fora do container "resultados", o domínio dele precisa constar
 * em DASHBOARD_ORIGINS no servidor da API (CORS).
 *
 * Codebook, PRISMA, conteúdo, equipe e mapa continuam sempre como JSON estáticos em ./data.
 */
(function () {
  // No Docker (container "resultados"), o nginx repassa api/dashboard para a API: basta o endereço relativo.
  // Fora do Docker: "http://localhost:9000/api/dashboard" (uvicorn + python -m http.server)
  // ou "" para usar só os arquivos estáticos de ./data.
  var API = "api/dashboard";

  var usaAPI = !!API;
  window.POLITEIA_CONFIG = {
    dados: {
      artigos:  usaAPI ? API + "/artigos" : "data/artigos.json",   // estudos incluídos, com o formulário de extração preenchido
      codebook: "data/codebook.json",  // estrutura do codebook (seções, questões e categorias)
      prisma:   "data/prisma.json",    // números do fluxo PRISMA e regras de triagem
      triagem:  usaAPI ? API + "/triagem" : "data/triagem.json",   // 601 registros da triagem (A1, A2, A3 e decisão final)
      conteudo: "data/conteudo.json",  // pergunta, objetivos, sínteses e mensagens dos relatórios temáticos
      equipe:   "data/equipe.json",    // avaliadores e vínculos
      mapa:     "data/mundo.geojson"   // contornos dos países para o mapa
    },
    // Análise de um artigo carregada sob demanda ({id} = id do estudo). Vazia: usa a cópia da lista.
    artigoUnico: usaAPI ? API + "/artigos/{id}" : "",
    downloads: {
      codebookPdf:  "downloads/Codebook_extracao_Estado_Aberto.pdf",
      codebookDocx: "downloads/Codebook_extracao_Estado_Aberto.docx",
      base: usaAPI ? API + "/base.csv" : "downloads/base_estado_aberto_282_artigos.csv"   // base de dados dos artigos analisados (CSV)
    },
    // Origem do WordPress que hospeda o iframe (para o ajuste automático de altura). "*" aceita qualquer uma.
    origemPai: "*"
  };
})();
