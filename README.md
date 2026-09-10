# Cadastro e Login de Usuários

Aplicação web simples de cadastro e login, criada como base para estudo e
aplicação prática de **testes de integração** e **testes End-to-End (E2E)**.

## 1. Objetivo

Permitir que um usuário:
1. Crie uma conta (cadastro);
2. Realize login com suas credenciais;
3. Acesse uma área restrita da aplicação;
4. Encerre a sessão (logout).

## 2. Fluxo principal

```
Cadastro -> Armazenamento dos dados -> Login -> Autenticação -> Área do usuário
```

## 3. Stack utilizada

- **Backend:** Python + Flask
- **Banco de dados:** MySQL (via `PyMySQL`), configurado por variáveis de ambiente
- **Frontend:** HTML + CSS + JavaScript (via templates Jinja2)
- **Senhas:** armazenadas com hash (`werkzeug.security`), nunca em texto puro

## 4. Estrutura do projeto

```
cadastro-login-app/
├── app.py                     # Aplicação Flask (rotas, lógica, banco)
├── requirements.txt           # Dependências Python
├── .env.example                # Modelo de variáveis de ambiente (copiar para .env)
├── templates/
│   ├── base.html               # Layout base
│   ├── cadastro.html           # Formulário de cadastro
│   ├── login.html              # Formulário de login
│   └── area_usuario.html       # Área restrita (pós-login)
└── static/
    ├── css/style.css           # Estilos
    └── js/validacao.js         # Validação simples no cliente
```

## 5. Como executar

Pré-requisito: um servidor MySQL acessível (local ou remoto). O usuário
informado em `MYSQL_USER` precisa ter permissão para criar bancos de dados
(`CREATE DATABASE`), pois a aplicação cria o banco automaticamente na
primeira execução caso ele ainda não exista.

```bash
# 1. Criar e ativar um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Configurar as variáveis de ambiente
cp .env
# edite o .env com host/usuário/senha/porta do seu MySQL

# 4. Executar a aplicação
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. Na primeira execução, o
banco de dados MySQL (nome definido em `MYSQL_DATABASE`, padrão
`cadastro_login_db`) e a tabela `usuarios` são criados automaticamente.

### Variáveis de ambiente (`.env`)

| Variável         | Padrão               | Descrição                              |
|------------------|----------------------|-----------------------------------------|
| `SECRET_KEY`     | chave de dev          | Chave de sessão do Flask                |
| `MYSQL_HOST`     | `localhost`           | Host do servidor MySQL                  |
| `MYSQL_PORT`     | `3306`                | Porta do servidor MySQL                 |
| `MYSQL_USER`     | `root`                | Usuário do MySQL                        |
| `MYSQL_PASSWORD` | *(vazio)*             | Senha do usuário do MySQL               |
| `MYSQL_DATABASE` | `cadastro_login_db`   | Nome do banco de dados da aplicação     |

## 6. Rotas disponíveis

| Rota             | Método    | Descrição                                  |
|-------------------|-----------|---------------------------------------------|
| `/`               | GET       | Redireciona para login ou área do usuário   |
| `/cadastro`       | GET, POST | Formulário e processamento de cadastro      |
| `/login`          | GET, POST | Formulário e processamento de login         |
| `/area-usuario`   | GET       | Área restrita (exige login)                 |
| `/logout`         | GET       | Encerra a sessão do usuário                 |

## 7. Regras de validação implementadas

- Todos os campos são obrigatórios no cadastro;
- Senha com no mínimo 6 caracteres;
- Confirmação de senha deve coincidir;
- E-mail não pode se repetir (`UNIQUE` no banco);
- Login exige e-mail e senha correspondentes a um usuário cadastrado;
- Rota `/area-usuario` só é acessível com sessão ativa (`login_required`).

## 8. Fora do escopo

Este projeto tem caráter simples e acadêmico. **Não** incluem-se:
- Recuperação de senha;
- Autenticação via serviços externos (Google, Facebook etc.);
- Pagamentos;
- Notificações por e-mail;
- Sistemas avançados de permissões/perfis.

## 9. Uso pretendido: testes de integração e E2E

A estrutura foi pensada para facilitar a escrita de testes sobre o fluxo
completo (cadastro → login → área do usuário → logout), por exemplo com
`pytest` + `Flask test client` (integração) e ferramentas como
`Selenium`, `Playwright` ou `Cypress` (E2E).
