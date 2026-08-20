"""
bibliotecarios.py - Módulo de bibliotecários e cadastro de livros

Responsável por:
- Registrar bibliotecários (login simples)
- Cadastrar novos livros no acervo (com opção de puxar metadado da
  Open Library API a partir do ISBN)

Depende só de db.py. Não escreve SQL fora das funções genéricas.
"""

import hashlib
import sqlite3

import db


def _hash_senha(senha: str) -> str:
    """Hash simples pra não guardar senha em texto puro no banco.
    Pra um MVP acadêmico isso já resolve; não é o nível de segurança
    de produção (faltaria salt, bcrypt etc.), mas é suficiente aqui."""
    return hashlib.sha256(senha.encode()).hexdigest()


def registrar_bibliotecario(nome: str, email: str, senha: str) -> int:
    """Cadastra um novo bibliotecário. Lança ValueError se o e-mail
    já estiver em uso."""
    try:
        return db.executar(
            "INSERT INTO bibliotecarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, _hash_senha(senha))
        )
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe um bibliotecário cadastrado com o e-mail {email}")


def autenticar_bibliotecario(email: str, senha: str):
    """Confere e-mail/senha. Retorna os dados do bibliotecário se bater,
    ou None se não encontrar ou a senha estiver errada."""
    bibliotecario = db.buscar_um(
        "SELECT * FROM bibliotecarios WHERE email = ?", (email,)
    )
    if bibliotecario and bibliotecario["senha_hash"] == _hash_senha(senha):
        return bibliotecario
    return None


def cadastrar_livro(titulo: str, autor: str, isbn: str = None, assunto: str = None,
                     editora: str = None, ano_publicacao: int = None,
                     sinopse: str = None, capa_url: str = None,
                     localizacao_id: int = None, estado_id: int = None) -> int:
    """Cadastra um livro novo no acervo. Todos os campos exceto
    título e autor são opcionais (podem ser preenchidos depois, ex:
    localização física definida pela Pessoa 4)."""
    try:
        return db.executar(
            """INSERT INTO livros
               (titulo, autor, isbn, assunto, editora, ano_publicacao,
                sinopse, capa_url, localizacao_id, estado_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (titulo, autor, isbn, assunto, editora, ano_publicacao,
             sinopse, capa_url, localizacao_id, estado_id)
        )
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe um livro cadastrado com o ISBN {isbn}")


def cadastrar_livro_por_isbn(isbn: str, localizacao_id: int = None, estado_id: int = None) -> int:
    """Busca os metadados na Open Library pelo ISBN e já cadastra o
    livro automaticamente. Levanta ValueError se não achar nada."""
    from biblioteca_virtual import buscar_metadados_openlibrary

    dados = buscar_metadados_openlibrary(isbn)
    if dados is None:
        raise ValueError(f"Não foi possível encontrar metadados para o ISBN {isbn}")

    autor = ", ".join(dados["autores"]) if dados["autores"] else "Desconhecido"
    return cadastrar_livro(
        titulo=dados["titulo"] or "Título não encontrado",
        autor=autor,
        isbn=isbn,
        editora=dados.get("editora"),
        capa_url=dados.get("capa_url"),
        localizacao_id=localizacao_id,
        estado_id=estado_id,
    )


def listar_livros():
    """Retorna todos os livros cadastrados."""
    return db.buscar_todos("SELECT * FROM livros ORDER BY titulo")


if __name__ == "__main__":
    db.criar_tabelas()
    print("Módulo de bibliotecários carregado. Rode main.py pra usar o sistema completo.")
