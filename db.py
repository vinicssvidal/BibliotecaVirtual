"""
db.py - Core do projeto Biblioteca Virtual

Responsável por:
- Abrir conexão com o banco SQLite
- Criar as tabelas do sistema (se ainda não existirem)
- Oferecer funções genéricas de CRUD pra todos os outros módulos usarem

Ninguém deve escrever SQL solto fora daqui, exceto queries específicas
de cada módulo (ex: busca por assunto no acervo.py). Pra insert/update/delete
simples, use sempre as funções abaixo.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "biblioteca.db"


def get_connection():
    """Abre e retorna uma conexão com o banco. Usa row_factory pra
    conseguir acessar colunas pelo nome (ex: linha['titulo'])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # garante integridade das FKs
    return conn


def criar_tabelas():
    """Cria todas as tabelas do sistema, caso ainda não existam.
    Rodar esse arquivo diretamente (python db.py) já cria o banco."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS bibliotecarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        data_cadastro TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS leitores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        telefone TEXT,
        data_cadastro TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS localizacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prateleira TEXT NOT NULL,
        secao TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS estados_livro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        isbn TEXT UNIQUE,
        assunto TEXT,
        editora TEXT,
        ano_publicacao INTEGER,
        sinopse TEXT,
        capa_url TEXT,
        localizacao_id INTEGER,
        estado_id INTEGER,
        disponivel INTEGER DEFAULT 1,
        FOREIGN KEY (localizacao_id) REFERENCES localizacoes(id),
        FOREIGN KEY (estado_id) REFERENCES estados_livro(id)
    );

    CREATE TABLE IF NOT EXISTS emprestimos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livro_id INTEGER NOT NULL,
        leitor_id INTEGER NOT NULL,
        bibliotecario_id INTEGER NOT NULL,
        data_emprestimo TEXT DEFAULT (datetime('now')),
        data_prevista_devolucao TEXT,
        data_devolucao TEXT,
        status TEXT DEFAULT 'ativo',
        FOREIGN KEY (livro_id) REFERENCES livros(id),
        FOREIGN KEY (leitor_id) REFERENCES leitores(id),
        FOREIGN KEY (bibliotecario_id) REFERENCES bibliotecarios(id)
    );

    CREATE TABLE IF NOT EXISTS biblioteca_virtual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livro_id INTEGER NOT NULL,
        url_repositorio TEXT,
        nome_repositorio TEXT,
        adicionado_por INTEGER,
        FOREIGN KEY (livro_id) REFERENCES livros(id),
        FOREIGN KEY (adicionado_por) REFERENCES leitores(id)
    );
    """)

    # Popula estados_livro com valores padrão, só na primeira vez
    estados_padrao = ["Bom estado", "Razoável", "Rasurado", "Páginas faltando"]
    for estado in estados_padrao:
        cursor.execute(
            "INSERT OR IGNORE INTO estados_livro (descricao) VALUES (?)",
            (estado,)
        )

    conn.commit()
    conn.close()
    print(f"Banco criado/atualizado em: {DB_PATH}")


# ---------- Funções genéricas de CRUD ----------
#
# IMPORTANTE: todas usam try/finally pra garantir que a conexão SEMPRE
# fecha, mesmo se der erro no meio (ex: violar FK ou UNIQUE). Sem isso,
# uma conexão que trava aberta pode bloquear ("database is locked") os
# próximos comandos de qualquer módulo que rodar em seguida.

def executar(query: str, params: tuple = ()) -> int:
    """Executa INSERT, UPDATE ou DELETE. Retorna o id da última linha
    inserida (útil pra pegar o id de um livro/leitor recém-criado).

    Se a query violar uma regra do banco (ex: FOREIGN KEY inexistente,
    e-mail duplicado numa coluna UNIQUE), a exceção do sqlite3 sobe
    normalmente pra quem chamou tratar (com try/except)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def buscar_um(query: str, params: tuple = ()):
    """Executa um SELECT e retorna só a primeira linha (ou None)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None
    finally:
        conn.close()


def buscar_todos(query: str, params: tuple = ()):
    """Executa um SELECT e retorna todas as linhas como lista de dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        return [dict(linha) for linha in resultados]
    finally:
        conn.close()


if __name__ == "__main__":
    # Rodar "python db.py" cria o banco do zero
    criar_tabelas()
