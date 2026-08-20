"""
biblioteca_virtual.py - Módulo da "vitrine" de ebooks

Ideia (inspirada no Stremio): a biblioteca virtual mostra só os
METADADOS do livro (capa, sinopse, autor). Quem alimenta o link do
ebook em si é o próprio usuário, apontando pra um repositório externo
dele. O sistema não hospeda nem baixa nada.

Depende da tabela `livros` (pra pegar metadados) e da tabela
`biblioteca_virtual` (pra guardar os links que os usuários adicionam).
Ambas já são criadas pelo db.py — não recrie tabela aqui.
"""

import db


def listar_vitrine():
    """Retorna todos os livros com metadados pra exibir na vitrine
    (capa, título, autor, sinopse, assunto)."""
    query = """
        SELECT id, titulo, autor, assunto, sinopse, capa_url
        FROM livros
        ORDER BY titulo
    """
    return db.buscar_todos(query)


def adicionar_link_externo(livro_id: int, url_repositorio: str,
                            nome_repositorio: str, leitor_id: int) -> int:
    """Usuário adiciona um link de repositório externo pra um livro
    específico (ex: um Google Drive ou site pessoal dele)."""
    livro = db.buscar_um("SELECT id FROM livros WHERE id = ?", (livro_id,))
    if livro is None:
        raise ValueError(f"Livro com id {livro_id} não existe.")

    query = """
        INSERT INTO biblioteca_virtual
            (livro_id, url_repositorio, nome_repositorio, adicionado_por)
        VALUES (?, ?, ?, ?)
    """
    return db.executar(query, (livro_id, url_repositorio, nome_repositorio, leitor_id))


def listar_links_do_livro(livro_id: int):
    """Retorna todos os links externos que os usuários já adicionaram
    pra um livro específico."""
    query = """
        SELECT bv.id, bv.url_repositorio, bv.nome_repositorio, l.nome AS adicionado_por
        FROM biblioteca_virtual bv
        JOIN leitores l ON l.id = bv.adicionado_por
        WHERE bv.livro_id = ?
    """
    return db.buscar_todos(query, (livro_id,))


def remover_link(link_id: int):
    """Remove um link externo (ex: se o usuário quiser tirar o dele)."""
    db.executar("DELETE FROM biblioteca_virtual WHERE id = ?", (link_id,))


def buscar_metadados_openlibrary(isbn: str):
    """Busca metadados (título, autor, capa) na Open Library API a partir
    do ISBN. Útil pra Pessoa 2 preencher o cadastro do livro automaticamente,
    mas também serve aqui pra completar a vitrine se faltar algum dado.

    Retorna um dict com os dados encontrados, ou None se não achar nada.
    """
    import urllib.request
    import json

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        with urllib.request.urlopen(url, timeout=5) as resposta:
            dados = json.loads(resposta.read().decode())
    except Exception as erro:
        print(f"Erro ao buscar na Open Library: {erro}")
        return None

    chave = f"ISBN:{isbn}"
    if chave not in dados:
        return None

    livro = dados[chave]
    return {
        "titulo": livro.get("title"),
        "autores": [a["name"] for a in livro.get("authors", [])],
        "capa_url": livro.get("cover", {}).get("medium"),
        "editora": livro.get("publishers", [{}])[0].get("name") if livro.get("publishers") else None,
    }


if __name__ == "__main__":
    # Teste rápido do módulo (rodar só depois de ter livros cadastrados)
    db.criar_tabelas()
    print("Vitrine atual:")
    for livro in listar_vitrine():
        print(f"  - {livro['titulo']} ({livro['autor']})")
