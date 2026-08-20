"""
acervo.py - Módulo de estado do livro, localização e busca

Responsável por:
- Cadastrar/consultar localizações físicas (prateleira/seção)
- Atualizar o estado de conservação de um livro
- Buscar livros por título, autor, assunto ou disponibilidade
  (essa busca serve tanto pra achar o livro na prateleira quanto
  pra conferir se ele está disponível)

Depende só de db.py.
"""

import db


def cadastrar_localizacao(prateleira: str, secao: str) -> int:
    """Cadastra uma nova localização física (prateleira + seção/assunto)."""
    return db.executar(
        "INSERT INTO localizacoes (prateleira, secao) VALUES (?, ?)",
        (prateleira, secao)
    )


def listar_localizacoes():
    """Retorna todas as localizações cadastradas."""
    return db.buscar_todos("SELECT * FROM localizacoes ORDER BY prateleira")


def definir_localizacao_livro(livro_id: int, localizacao_id: int):
    """Associa um livro a uma localização física existente."""
    localizacao = db.buscar_um("SELECT id FROM localizacoes WHERE id = ?", (localizacao_id,))
    if localizacao is None:
        raise ValueError(f"Localização com id {localizacao_id} não existe.")
    db.executar(
        "UPDATE livros SET localizacao_id = ? WHERE id = ?",
        (localizacao_id, livro_id)
    )


def listar_estados():
    """Retorna os estados de conservação possíveis (Bom estado, Razoável,
    Rasurado, Páginas faltando - já populados pelo db.py)."""
    return db.buscar_todos("SELECT * FROM estados_livro")


def definir_estado_livro(livro_id: int, estado_id: int):
    """Atualiza o estado de conservação de um livro."""
    estado = db.buscar_um("SELECT id FROM estados_livro WHERE id = ?", (estado_id,))
    if estado is None:
        raise ValueError(f"Estado com id {estado_id} não existe.")
    db.executar(
        "UPDATE livros SET estado_id = ? WHERE id = ?",
        (estado_id, livro_id)
    )


def buscar_livros(termo: str = None, assunto: str = None, apenas_disponiveis: bool = False):
    """Busca livros por título/autor (termo livre) e/ou assunto.
    Retorna, pra cada livro, também a prateleira/seção e o estado de
    conservação, já formatados - é o que a vitrine (Pessoa 5) e a tela
    de empréstimo (Pessoa 3) usam pra saber onde o livro está e se
    está disponível.
    """
    query = """
        SELECT
            liv.id, liv.titulo, liv.autor, liv.assunto, liv.disponivel,
            loc.prateleira, loc.secao,
            est.descricao AS estado
        FROM livros liv
        LEFT JOIN localizacoes loc ON loc.id = liv.localizacao_id
        LEFT JOIN estados_livro est ON est.id = liv.estado_id
        WHERE 1=1
    """
    params = []

    if termo:
        query += " AND (liv.titulo LIKE ? OR liv.autor LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])

    if assunto:
        query += " AND liv.assunto LIKE ?"
        params.append(f"%{assunto}%")

    if apenas_disponiveis:
        query += " AND liv.disponivel = 1"

    query += " ORDER BY liv.titulo"

    return db.buscar_todos(query, tuple(params))


if __name__ == "__main__":
    db.criar_tabelas()
    print("Módulo de acervo carregado. Rode main.py pra usar o sistema completo.")
