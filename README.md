# Estado Aberto

Sistema web desenvolvido para apoiar o gerenciamento e a avaliação de artigos jornalísticos, oferecendo uma plataforma integrada para cadastro, organização, distribuição, análise e geração de indicadores estatísticos.

---

## Visão Geral

O **Estado Aberto** foi desenvolvido com foco em desempenho, organização e facilidade de manutenção, utilizando uma arquitetura baseada em serviços independentes e tecnologias modernas do ecossistema Python.

A aplicação permite que pesquisadores e avaliadores realizem todo o fluxo de avaliação de artigos, desde o cadastramento das informações até a consolidação dos resultados e geração de estatísticas por meio de dashboards interativos.

---

# Arquitetura

A solução é composta pelos seguintes componentes:

* **FastAPI** para disponibilização da API REST.
* **Streamlit** para geração de dashboards estatísticos.
* **SQLite** como banco de dados relacional.
* **SQLAlchemy** para mapeamento objeto-relacional (ORM).
* **Jinja2** para renderização das páginas HTML.
* **Docker** para conteinerização e implantação.

```
┌────────────────────┐
│     Navegador      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│       FastAPI      │
│   API + Templates  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│    SQLAlchemy ORM  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│     SQLite DB      │
└────────────────────┘

          │
          ▼
┌────────────────────┐
│     Streamlit      │
│ Dashboards e BI    │
└────────────────────┘
```

---

# Tecnologias Utilizadas

| Tecnologia | Finalidade                           |
| ---------- | ------------------------------------ |
| Python     | Linguagem principal da aplicação     |
| FastAPI    | Desenvolvimento da API REST          |
| Streamlit  | Dashboard e visualização estatística |
| SQLAlchemy | ORM para acesso ao banco de dados    |
| SQLite     | Persistência das informações         |
| Jinja2     | Renderização de páginas HTML         |
| Docker     | Conteinerização da aplicação         |

---

# Banco de Dados

Um dos principais componentes do sistema é o banco de dados **SQLite**, responsável pelo armazenamento permanente de todas as informações da aplicação.

O banco concentra dados relacionados a:

* usuários;
* autenticação;
* artigos jornalísticos;
* temas;
* fontes;
* enquadramentos;
* distribuição de artigos;
* avaliações;
* histórico de alterações;
* indicadores estatísticos.

A utilização do **SQLAlchemy** abstrai o acesso ao banco de dados, permitindo manipular registros utilizando objetos Python em vez de comandos SQL diretamente.

Exemplo de configuração da conexão:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///estado.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

Exemplo de modelo utilizando ORM:

```python
class Artigo(Base):
    __tablename__ = "artigo"

    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    autor = Column(String)
    data = Column(Date)
```

Consulta utilizando SQLAlchemy:

```python
artigos = (
    session
    .query(Artigo)
    .filter(Artigo.status == "Pendente")
    .all()
)
```

Essa abordagem proporciona:

* maior organização do código;
* redução da complexidade das consultas;
* facilidade de manutenção;
* independência entre aplicação e banco de dados;
* maior segurança na manipulação das informações.

---

# Funcionalidades

## Gerenciamento de Usuários

* Cadastro de usuários
* Login e autenticação
* Controle de sessões
* Gerenciamento de permissões

---

## Gerenciamento de Artigos

* Cadastro de artigos
* Organização por temas
* Associação de fontes
* Registro de metadados
* Controle de status

---

## Processo de Avaliação

O sistema automatiza todo o fluxo de avaliação dos artigos.

Entre as funcionalidades estão:

* distribuição automática para avaliadores;
* registro das avaliações;
* armazenamento do histórico;
* controle das etapas do processo;
* acompanhamento do status das análises.

---

## Pesquisa e Filtragem

A aplicação disponibiliza mecanismos de busca que permitem localizar rapidamente informações armazenadas no banco de dados.

É possível realizar pesquisas considerando diversos critérios, como:

* título;
* autor;
* tema;
* fonte;
* status;
* avaliador;
* período.

---

# Processamento de Documentos

O sistema possui integração com serviços de processamento de documentos digitais, permitindo automatizar parte do cadastramento dos artigos.

Entre os recursos disponíveis destacam-se:

* extração automática de informações;
* leitura de documentos digitais;
* redução da digitação manual;
* maior padronização dos dados armazenados.

---

# Dashboard Estatístico

A camada analítica foi desenvolvida utilizando **Streamlit**, permitindo a criação de painéis interativos para acompanhamento dos dados.

Os dashboards apresentam indicadores como:

* quantidade de artigos cadastrados;
* artigos avaliados;
* artigos pendentes;
* distribuição por tema;
* produtividade dos avaliadores;
* evolução das avaliações ao longo do tempo.

---

# API REST

A comunicação entre os componentes ocorre por meio de uma API REST desenvolvida com FastAPI.

Exemplo de endpoint:

```python
@app.get("/artigos")
def listar_artigos():
    return session.query(Artigo).all()
```

A utilização do FastAPI oferece:

* documentação automática (Swagger/OpenAPI);
* alta performance;
* validação automática dos dados;
* serialização utilizando Pydantic.

---

# Implantação

Toda a solução foi conteinerizada utilizando **Docker**, garantindo facilidade de instalação e padronização do ambiente de execução.

A arquitetura permite executar separadamente:

* API FastAPI;
* Dashboard Streamlit;
* Banco de Dados;
* Serviços auxiliares.

Exemplo simplificado:

```yaml
version: "3"

services:
  api:
    build: .

  dashboard:
    build: .
```

---

# Principais Benefícios

* Arquitetura modular
* API REST moderna
* Persistência de dados utilizando banco relacional
* Manipulação de dados através do SQLAlchemy ORM
* Dashboards interativos
* Interface web simples e intuitiva
* Processamento automatizado de documentos
* Controle completo do fluxo de avaliação
* Implantação simplificada com Docker

---

# Resultado

O **Estado Aberto** constitui uma plataforma integrada para gerenciamento e avaliação de artigos jornalísticos, centralizando todas as etapas do processo em um único ambiente.

A utilização de um banco de dados relacional associado ao SQLAlchemy garante integridade, organização e rastreabilidade das informações, permitindo consultas eficientes, geração de indicadores estatísticos e apoio à tomada de decisão baseada nos dados coletados.
