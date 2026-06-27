CRUZAMENTO = ['jornal', 'genero', 'secao', 'palavras', 'abrangencia', 'climaticas', 'autoria', 'linguagem', 'enunciador', 'persuasao', 'lead', 'enqDominante', 'enqEficacia', 'enqAcao', 'papJornalistico']

MESES_PT_MAPA = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

MAPA = {
    "Breve/nota (Entre 50 e 150 palavras. Relato breve, objetivo e atual de um fato considerado relevante.":"Nota",
    "Notícia (Relato breve, objetivo e atual de um fato considerado relevante, seguindo em geral a lógica da pirâmide invertida e respondendo às perguntas básicas - quem, o quê, quando, onde, como e porquê.)":"Notícia",
    "Reportagem (Texto mais desenvolvido que descreve e contextualiza acontecimentos, lugares e personagens, exigindo trabalho de terreno e combinação de dados factuais com observação e descrição.)":"Reportagem",
    "Editorial (Artigo assinado ou institucional que exprime a posição oficial do jornal ou da sua direção sobre um tema da atualidade.":"Editorial",
    "Artigo de opinião (Texto em que um autor interpreta e avalia fatos ou temas, defendendo um ponto de vista argumentado.)":"Artigo",
    "Crônica (Texto com marca pessoal do autor, que combina observação da atualidade com reflexão e recursos literários, admitindo opinião explícita.)":"Crônica",
    "Crítica/comentário (Texto avaliativo, geralmente de um especialista.)":"Crítica",
    "Cartas do leitor (Textos enviados pelos leitores.)":"Cartas",

    "Informativo indicativo (Responde às perguntas: quem, o quê, onde, e/ou quando)":"Informativo Indicativo",
    "Informativo explicativo (Apresenta a causa ou consequência do acontecimento. Responde à pergunta como)":"Informativo Explicativo",
    "Expressivo apelativo (Dramatiza o acontecimento)":"Expressivo Apelativo",
    "Expressivo lúdico (Função poética da linguagem)":"Expressivo Lúdico",
    "Expressivo interrogativo (Em forma de pergunta)":"Expressivo Interrogativo",
    "Categorial (Indica uma categoria ou tema, sem sintetizar o conteúdo do artigo)":"Categorial",

    "Declarativo informativo (Declaração de um dos personagens + responde às perguntas: quem, o quê, onde e ou quando)":"Informativo",
    "Declarativo expressivo (Declaração de um dos personagens + apelativo ou lúdico)":"Expressivo",

    "Comprometido (Persuasão explícita. Apresenta uma causa, é empenhado)":"Comprometido",
    "Não Comprometido (Neutro, indicativo, categorial)":"Não Comprometido",

    "Direto informativo (Responde diretamente às questões o quê, quem)":"Direto Informativo",
    "Direto interpretativo (Revistas, semanários, páginas de opinião. Traz elementos subjetivos)":"Direto Interpretativo",
    "Diferido informativo (Responde às perguntas, mas traz elementos secundários, descreve paisagens, ambientes...)":"Diferido Informativo",
    "Diferido interpretativo (apela à imaginação, traz elementos de subjetividade, opiniões)":"Diferido Interpretativo",

    "Catástrofe/risco (foco em impactos, perdas, vítimas, ameaça, linguagem de urgência.)":"Catástrofe/Risco",
    "Tecno‑científico (ênfase em dados, incertezas, relatórios científicos, especialistas, soluções tecnológicas.)":"Técnico/Científico",
    "Político‑institucional (conflitos partidários, negociações, governação, responsabilização de governos/UE/ONU.)":"Político/Institucional",
    "Responsabilidade (ênfase na responsabilização individual ou coletiva.)":"Responsabilidade",
    "Econômico (custos, oportunidades, “economia verde”, competitividade, empregos.)":"Económico",
    "Justiça/ética (desigualdades, gerações futuras, povos vulneráveis, direitos humanos, justiça climática.)":"Justiça/Ética",

    "Não menciona soluções nem ações":"S/Ação ou Solução",
    "Menciona ações genéricas, sem mostrar efeitos (“é preciso agir”, “é necessário mudar”)":"Ações Gener.",
    "Apresenta ações específicas, mas com pouca evidência de resultados":"Ações Especif.",
    "Apresenta ações específicas e indica evidência ou exemplos de impacto (dados, casos, resultados concretos)":"Ações e Result.",

    "Ausente (só ações individuais ou nenhuma ação)":"Ausente",
    "Mencionada de passagem (protestos, políticas, campanhas aparecem, mas não são foco)":"Passagem",
    "Central (protestos, movimentos, políticas públicas, organizações coletivas são o núcleo da notícia)":"Central",

    "Disseminador neutro (apenas relata, sem juízos).":"Notícia Informativa",
    "Intérprete/mediador (explica, pesa evidências).":"Notícia Explicativa",
    "Engajado/advocacy (faz apelos, toma partido explícito a favor de uma causa).":"Notícia Explicitamente Empenhada",

    "Plantas (temas relacionados à flora que não são incêndio)": "Plantas",
    "Animais (espécies ameaçadas, espécies exóticas, desequilíbrio, biodiversidade...)": "Animais",
    "Poluição (ar, água, mar...)": "Poluição",
    "Contaminação por produtos químicos (entram notícias sobre radiação também)": "Contaminação",
    "Consumo/sustentabilidade (entram notícias sobre gestão do lixo, dos alimentos e da água)": "Consumo/Sustentabilidade",
    "Movimentos ambientalistas (entram notícias sobre protetos, manifestações, partidos verdes...)": "Movimentos ambientalistas",
    "Fenômenos naturais extremos (Sismos / Terremotos; Erupções vulcânicas; Tsunamis; Deslizamentos de terra...)": "Fenômenos Naturais Extremos",

    "Principalmente individual (mudanças de consumo, “cada um deve…”)":"Principalmente individual",
    "Principalmente institucional/política (Estado, empresas, instituições, acordos).":"Principalmente institucional/política",
    "Difusa/indeterminada (“todos são culpados”, sem atores claros)":"Difusa/indeterminada",
    "Clima/Tempo/Fenómeno climático (a responsabilidade é atribuída ao próprio tempo/clima e não às pessoas)":"Clima/Tempo/Fenómeno",

    0.0:"Não",
    1.0:"Sim"



}