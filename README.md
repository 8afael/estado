#Estado Aberto

A aplicação web foi desenvolvida utilizando tecnologias modernas que proporcionam segurança, desempenho e facilidade de manutenção. O sistema foi implementado em Python, utilizando o framework FastAPI para disponibilizar os serviços da aplicação e gerenciar as requisições dos usuários. Para a visualização dos dados estatísticos foi utilizado o Streamlit, permitindo a construção de dashboards interativos de forma simples e intuitiva.

O armazenamento das informações é realizado em banco de dados SQLite, sendo o acesso aos dados feito por meio da biblioteca SQLAlchemy, responsável pelo mapeamento entre os objetos da aplicação e as tabelas do banco de dados. A interface da aplicação foi desenvolvida utilizando páginas HTML renderizadas com o mecanismo de templates Jinja2, possibilitando uma navegação simples e organizada.

Entre as funcionalidades implementadas destacam-se o cadastro e autenticação de usuários, controle de sessões, gerenciamento de artigos jornalísticos, distribuição de artigos para avaliadores, registro das avaliações realizadas e controle do status de cada processo de análise. O sistema também oferece mecanismos de filtragem e pesquisa, permitindo localizar rapidamente os artigos cadastrados de acordo com diferentes critérios.

A aplicação também possui integração com serviços de processamento de documentos, permitindo a extração de informações de arquivos digitais e automatizando parte do processo de cadastramento dos artigos. Esse recurso reduz o trabalho manual e aumenta a eficiência do sistema.

Para facilitar a implantação em diferentes ambientes, toda a aplicação foi conteinerizada utilizando Docker, permitindo que o servidor da API, o dashboard e os demais componentes sejam executados de forma padronizada e independente da configuração do sistema operacional.

Como resultado, foi desenvolvida uma plataforma integrada capaz de apoiar todo o processo de gerenciamento e avaliação de artigos jornalísticos, desde o cadastro e organização das informações até a geração de análises estatísticas e indicadores que auxiliam pesquisadores na interpretação dos dados coletados.
