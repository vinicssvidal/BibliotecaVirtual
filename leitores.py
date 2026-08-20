"""
leitores.py - Módulo de leitores, empréstimos e histórico

Responsável por:
- Registrar leitores (a biblioteca não é vinculada a nenhum sistema
  externo, então precisa de conta própria)
- Registrar empréstimo e devolução de livros
- Consultar o histórico de um leitor (tudo isso já vive na tabela
  `emprestimos`, não precisa de tabela separada de histórico)

Depende de db.py. Os empréstimos dependem de livro_id e leitor_id
já existirem (cadastrados por leitores.py e bibliotecarios.py).
"""

import hashlib
import sqlite3
from datetime import datetime, timedelta

import db

DIAS_EMPRESTIMO_PADRAO = 14


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def registrar_leitor(nome: str, email: str, senha: str, telefone: str = None) -> int:
    """Cadastra um novo leitor. Lança ValueError se o e-mail já existir."""
    try:
        return db.executar(
            "INSERT INTO leitores (nome, email, senha_hash, telefone) VALUES (?, ?, ?, ?)",
            (nome, email, _hash_senha(senha), telefone)
        )
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe um leitor cadastrado com o e-mail {email}")


def autenticar_leitor(email: str, senha: str):
    """Confere e-mail/senha do leitor. Retorna os dados se bater, senão None."""
    leitor = db.buscar_um("SELECT * FROM leitores WHERE email = ?", (email,))
    if leitor and leitor["senha_hash"] == _hash_senha(senha):
        return leitor
    return None


def registrar_emprestimo(livro_id: int, leitor_id: int, bibliotecario_id: int,
                          dias_para_devolucao: int = DIAS_EMPRESTIMO_PADRAO) -> int:
    """Registra o empréstimo de um livro pra um leitor. Marca o livro
    como indisponível. Lança ValueError se o livro já estiver emprestado
    ou não existir."""
    livro = db.buscar_um("SELECT * FROM livros WHERE id = ?", (livro_id,))
    if livro is None:
        raise ValueError(f"Livro com id {livro_id} não existe.")
    if not livro["disponivel"]:
        raise ValueError(f'O livro "{livro["titulo"]}" já está emprestado.')

    data_prevista = (datetime.now() + timedelta(days=dias_para_devolucao)).strftime("%Y-%m-%d")

    emprestimo_id = db.executar(
        """INSERT INTO emprestimos
           (livro_id, leitor_id, bibliotecario_id, data_prevista_devolucao, status)
           VALUES (?, ?, ?, ?, 'ativo')""",
        (livro_id, leitor_id, bibliotecario_id, data_prevista)
    )
    db.executar("UPDATE livros SET disponivel = 0 WHERE id = ?", (livro_id,))
    return emprestimo_id


def registrar_devolucao(emprestimo_id: int):
    """Marca um empréstimo como devolvido e libera o livro de novo."""
    emprestimo = db.buscar_um("SELECT * FROM emprestimos WHERE id = ?", (emprestimo_id,))
    if emprestimo is None:
        raise ValueError(f"Empréstimo com id {emprestimo_id} não existe.")

    data_devolucao = datetime.now().strftime("%Y-%m-%d")
    db.executar(
        "UPDATE emprestimos SET data_devolucao = ?, status = 'devolvido' WHERE id = ?",
        (data_devolucao, emprestimo_id)
    )
    db.executar("UPDATE livros SET disponivel = 1 WHERE id = ?", (emprestimo["livro_id"],))


def historico_leitor(leitor_id: int):
    """Retorna todos os empréstimos (ativos, devolvidos, atrasados) de
    um leitor específico, com o título do livro junto."""
    query = """
        SELECT e.id, l.titulo, e.data_emprestimo, e.data_prevista_devolucao,
               e.data_devolucao, e.status
        FROM emprestimos e
        JOIN livros l ON l.id = e.livro_id
        WHERE e.leitor_id = ?
        ORDER BY e.data_emprestimo DESC
    """
    return db.buscar_todos(query, (leitor_id,))


def atualizar_emprestimos_atrasados():
    """Varre os empréstimos ativos e marca como 'atrasado' os que
    passaram da data prevista de devolução. Bom rodar isso toda vez
    que o sistema abrir."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    db.executar(
        """UPDATE emprestimos
           SET status = 'atrasado'
           WHERE status = 'ativo' AND data_prevista_devolucao < ?""",
        (hoje,)
    )


if __name__ == "__main__":
    db.criar_tabelas()
    print("Módulo de leitores carregado. Rode main.py pra usar o sistema completo.")
