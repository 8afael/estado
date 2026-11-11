# Site de resultados: revisão sistemática Estado Aberto

Site estático (HTML, CSS e JavaScript, sem etapa de compilação) para incorporar por iframe no WordPress do Politeia Conecta. Ele lê os dados de arquivos JSON e pode passar a ler as mesmas informações direto da plataforma, trocando os endereços em `config.js`.

## Páginas

| Endereço | Conteúdo |
|---|---|
| `#/inicio` | Apresentação do estudo, pergunta, objetivos e proposta de ciência aberta |
| `#/prisma` | Fluxograma PRISMA 2020 clicável; regras de triagem (T1–T4, decisão por avaliador, decisão final, matriz de combinações); resultado da triagem e tabela dos 601 registros |
| `#/artigos` | 282 estudos em ordem alfabética da referência APA, com busca e filtros |
| `#/artigos/{id}` | Formulário de extração preenchido do estudo (sem PDF; link para o DOI do editor) |
| `#/resultados` | Pergunta e objetivo geral com a resposta da revisão; abas OE1 a OE7 e Síntese; seletor de conceito (Governo, Governança, Estado, Parlamento, Justiça Aberta) em dois recortes: conceito central (Q18) ou recorte ampliado (Q16) |
| `#/equipe` | Avaliadores por vínculo |
| `#/codebook` | Download do codebook (PDF e DOCX) e da base de dados dos 282 artigos (CSV), e consulta navegável do codebook |

Os endereços aceitam parâmetros, então qualquer visão pode ser compartilhada por link. Exemplo: `#/resultados?c=justica&m=nucleo&oe=OE6`. Clicar em uma barra, num país do mapa ou numa linha da tabela abre a lista dos artigos daquela categoria (`#/artigos?var=q44_obstaculos&val=7&c=justica&m=nucleo`), e cada artigo abre a sua análise.

Todos os gráficos são calculados no navegador a partir dos artigos, seguindo a regra de leitura dos relatórios: 97 e 98 ficam fora do denominador e 96 conta como achado. Quando o banco da plataforma for atualizado, os gráficos acompanham automaticamente.

## Como publicar

1. Copie a pasta inteira para um endereço público (por exemplo, `wp-content/uploads/estado-aberto/` ou um subdomínio).
2. No WordPress, crie a página e cole o conteúdo de `incorporar-wordpress.html` num bloco "HTML personalizado", ajustando o `src`.
3. O iframe se ajusta sozinho à altura do conteúdo. Para restringir quem pode receber essas mensagens, informe a origem do WordPress em `origemPai` no `config.js`.

Para testar no computador: `python3 -m http.server` dentro da pasta e abrir `http://localhost:8000`. Abrir o `index.html` com duplo clique não funciona, porque o navegador bloqueia a leitura dos JSON fora de um servidor.

As bibliotecas (Chart.js 4.4.1 e D3 7.8.5) estão em `assets/vendor/`; o site só depende de fontes externas (Google Fonts).

## Ligação com o banco de dados da plataforma

Troque os endereços em `config.js` pelas rotas da API. Formatos esperados:

**artigos**: lista de objetos, um por estudo, com as colunas da base de extração (mesmos nomes de `base_geral_corrigida.csv`). As questões de múltipla escolha podem vir de duas formas, e o site aceita ambas:
- formato largo, como na exportação da plataforma: `"q09_desenho_1": "Sim"`, `"q09_desenho_2": "Não"`…
- formato compacto, como no arquivo enviado: `"q09_desenho": [1, 10]`

Campos adicionais usados: `ano`, `_paises_iso` (códigos ISO3 dos países de `q05_pais_lista`), `_regioes` e as codificações derivadas `d_*` da aba 5 da Matriz. O site ordena a lista alfabeticamente pela referência, então a ordem de envio não importa.

**artigoUnico** (opcional): rota que devolve um único estudo, com `{id}` no lugar do identificador. Útil se a plataforma preferir enviar a lista resumida e o formulário completo só quando a pessoa clicar em "Visualizar análise".

**triagem**: `{"atualizado_em": "...", "registros": [{"id": 1, "titulo": "...", "a1": "Excluir", "a2": "Excluir", "a3": "", "decisao": "Excluído"}, …]}` (uma lista simples de registros também é aceita). O arquivo enviado está vazio porque os dados individuais da triagem estão na plataforma; enquanto a rota não for configurada, a página mostra os totais e um aviso.

**downloads.base**: endereço do CSV da base (hoje `downloads/base_estado_aberto_282_artigos.csv`, cópia de `E0/base_geral_corrigida.csv` em UTF-8). Os botões de download aparecem no início, na lista de artigos e na página do codebook; se o endereço ficar vazio, eles somem.

**codebook**, **prisma**, **conteudo**, **equipe**: estrutura dos arquivos em `data/`. Em `equipe.json`, cada pessoa tem `perfil`, `foto` e `lattes`, que podem ser preenchidos para completar os cartões.

## Origem dos dados enviados

Gerados por `ferramentas/build_data.py` a partir de: `E0/base_geral_corrigida.csv` (282 estudos), aba `5_Codificacao_derivada` da `Matriz_sistematizacao_analitica_Estado_Aberto_v4.xlsx`, `codebook/Codebook_extracao_Estado_Aberto.docx`, a síntese temática e os cinco relatórios temáticos (seções "Síntese: mensagens", "Lacunas", "Como o recorte foi construído" e Figura 11), o fluxograma PRISMA e o relatório de atividades da fase 2 (Tabela 1 da triagem).

## API da plataforma (implantada)

As rotas públicas ficam em `backend/app/routers/dashboard_router.py` (somente leitura, sem login, sem dados de quem codificou):

| Rota | Conteúdo |
|---|---|
| `GET /plataforma/estado/api/dashboard/artigos` | estudos com extração concluída, já no formato deste site |
| `GET /plataforma/estado/api/dashboard/artigos/{id}` | um estudo (rota `artigoUnico`) |
| `GET /plataforma/estado/api/dashboard/triagem` | os 601 registros da triagem (`snapshot_decisao_final`) |
| `GET /plataforma/estado/api/dashboard/base.csv` | base em CSV gerada do banco no momento do download |

Para ligar o site à API, troque `SEU-SERVIDOR` em `config.js` pelo domínio da plataforma. Enquanto o marcador estiver lá, o site usa os arquivos estáticos.
O domínio onde o site está publicado precisa estar em `DASHBOARD_ORIGINS` (docker-compose), senão o navegador bloqueia as chamadas (CORS).

A conversão do banco para o formato do site está em `backend/app/models/dashboard_service.py`:
múltipla escolha de rótulo para código do codebook, nomes de coluna para os nomes de variável, `_outro`/`_evid`, `ano`, `_paises_iso` e `_regioes`.
Os códigos e a tabela de países ficam em `backend/app/models/dashboard_codigos.py`, gerado por `ferramentas/gen_codigos.py`; gere de novo se o codebook mudar ou se entrar um país novo
(a API registra um aviso no log quando encontra rótulo ou país sem código).

As codificações derivadas `d_*` ficam na tabela `extracao_derivada`. Para (re)importar a partir do `artigos.json`:
`python3 backend/app/util/importar_derivadas.py --db data/estado_aberto.db --json dashboard/data/artigos.json`

Para conferir a API sem subir o servidor: `python3 dashboard/ferramentas/testar_api_sem_servidor.py . data/estado_aberto.db`
