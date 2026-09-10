"""
Aplicação web simples de Cadastro e Login de Usuários.

Objetivo: servir como base para estudo e aplicação prática de
testes de integração e testes End-to-End (E2E).

Fluxo principal:
    Cadastro -> Armazenamento dos dados -> Login -> Autenticação -> Área do usuário
"""

import os
from functools import wraps

import pymysql
import pymysql.cursors
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-dev-trocar-em-producao")

# ---------------------------------------------------------------------------
# Configuração do banco de dados (MySQL)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "cadastro_login_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
}


def get_db():
    """Retorna a conexão com o banco de dados da requisição atual."""
    if "db" not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Fecha a conexão com o banco ao final de cada requisição."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Cria o banco de dados (se necessário) e a tabela de usuários."""
    # Primeiro conecta sem selecionar um banco específico para poder criá-lo.
    config_sem_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conexao = pymysql.connect(**config_sem_db)
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conexao.commit()
    finally:
        conexao.close()

    # Agora conecta já no banco e cria a tabela.
    db = pymysql.connect(**DB_CONFIG)
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    senha_hash VARCHAR(255) NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Autenticação / decorators
# ---------------------------------------------------------------------------
def login_required(view):
    """Protege rotas que exigem usuário autenticado."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("usuario_id") is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if session.get("usuario_id"):
        return redirect(url_for("area_usuario"))
    return redirect(url_for("login"))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        erro = None
        if not nome or not email or not senha:
            erro = "Preencha todos os campos."
        elif len(senha) < 6:
            erro = "A senha deve ter ao menos 6 caracteres."
        elif senha != confirmar_senha:
            erro = "As senhas não coincidem."

        db = get_db()
        if erro is None:
            with db.cursor() as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                existente = cursor.fetchone()
            if existente is not None:
                erro = f"O e-mail '{email}' já está cadastrado."

        if erro is None:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
                    (nome, email, generate_password_hash(senha)),
                )
            db.commit()
            return render_template(
                "cadastro.html", sucesso="Cadastro realizado com sucesso! Faça login."
            )

        return render_template("cadastro.html", erro=erro)

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        erro = None
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()

        if usuario is None:
            erro = "E-mail ou senha inválidos."
        elif not check_password_hash(usuario["senha_hash"], senha):
            erro = "E-mail ou senha inválidos."

        if erro is None:
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("area_usuario"))

        return render_template("login.html", erro=erro)

    return render_template("login.html")


@app.route("/area-usuario")
@login_required
def area_usuario():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, criado_em FROM usuarios WHERE id = %s",
            (session["usuario_id"],),
        )
        usuario = cursor.fetchone()
    return render_template("area_usuario.html", usuario=usuario)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
