
import db
import bibliotecarios
import leitores
import acervo
import biblioteca_virtual as vitrine


def pausar():
    input("\nPressione ENTER pra continuar...")


def menu_bibliotecarios():
    while True:
        print("\n--- BIBLIOTECÁRIOS ---")
        print("1. Registrar bibliotecário")
        print("2. Cadastrar livro (manual)")
        print("3. Cadastrar livro por ISBN (via Open Library)")
        print("4. Listar livros")
        print("0. Voltar")
        opcao = input("> ").strip()

        if opcao == "1":
            nome = input("Nome: ")
            email = input("E-mail: ")
            senha = input("Senha: ")
            try:
                id_ = bibliotecarios.registrar_bibliotecario(nome, email, senha)
                print(f"Bibliotecário cadastrado com id {id_}.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "2":
            titulo = input("Título: ")
            autor = input("Autor: ")
            isbn = input("ISBN (opcional): ") or None
            assunto = input("Assunto (opcional): ") or None
            try:
                id_ = bibliotecarios.cadastrar_livro(titulo, autor, isbn=isbn, assunto=assunto)
                print(f"Livro cadastrado com id {id_}.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "3":
            isbn = input("ISBN: ")
            try:
                id_ = bibliotecarios.cadastrar_livro_por_isbn(isbn)
                print(f"Livro cadastrado com id {id_} usando dados da Open Library.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "4":
            livros = bibliotecarios.listar_livros()
            if not livros:
                print("Nenhum livro cadastrado ainda.")
            for l in livros:
                status = "disponível" if l["disponivel"] else "emprestado"
                print(f'  [{l["id"]}] {l["titulo"]} - {l["autor"]} ({status})')

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
        pausar()


def menu_leitores():
    while True:
        print("\n--- LEITORES ---")
        print("1. Registrar leitor")
        print("2. Registrar empréstimo")
        print("3. Registrar devolução")
        print("4. Ver histórico de um leitor")
        print("0. Voltar")
        opcao = input("> ").strip()

        if opcao == "1":
            nome = input("Nome: ")
            email = input("E-mail: ")
            senha = input("Senha: ")
            telefone = input("Telefone (opcional): ") or None
            try:
                id_ = leitores.registrar_leitor(nome, email, senha, telefone)
                print(f"Leitor cadastrado com id {id_}.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "2":
            try:
                livro_id = int(input("ID do livro: "))
                leitor_id = int(input("ID do leitor: "))
                bibliotecario_id = int(input("ID do bibliotecário responsável: "))
                id_ = leitores.registrar_emprestimo(livro_id, leitor_id, bibliotecario_id)
                print(f"Empréstimo registrado com id {id_}.")
            except (ValueError, TypeError) as e:
                print(f"Erro: {e}")

        elif opcao == "3":
            try:
                emprestimo_id = int(input("ID do empréstimo: "))
                leitores.registrar_devolucao(emprestimo_id)
                print("Devolução registrada.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "4":
            try:
                leitor_id = int(input("ID do leitor: "))
                historico = leitores.historico_leitor(leitor_id)
                if not historico:
                    print("Nenhum empréstimo encontrado pra esse leitor.")
                for h in historico:
                    print(f'  [{h["id"]}] {h["titulo"]} - status: {h["status"]} '
                          f'(emprestado em {h["data_emprestimo"]})')
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
        pausar()


def menu_acervo():
    while True:
        print("\n--- ACERVO (estado, localização e busca) ---")
        print("1. Cadastrar localização (prateleira/seção)")
        print("2. Definir localização de um livro")
        print("3. Definir estado de conservação de um livro")
        print("4. Buscar livros")
        print("0. Voltar")
        opcao = input("> ").strip()

        if opcao == "1":
            prateleira = input("Prateleira (ex: Prateleira 3): ")
            secao = input("Seção/assunto (ex: Ficção Científica): ")
            id_ = acervo.cadastrar_localizacao(prateleira, secao)
            print(f"Localização cadastrada com id {id_}.")

        elif opcao == "2":
            try:
                livro_id = int(input("ID do livro: "))
                print("Localizações disponíveis:")
                for loc in acervo.listar_localizacoes():
                    print(f'  [{loc["id"]}] {loc["prateleira"]} - {loc["secao"]}')
                localizacao_id = int(input("ID da localização: "))
                acervo.definir_localizacao_livro(livro_id, localizacao_id)
                print("Localização atualizada.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "3":
            try:
                livro_id = int(input("ID do livro: "))
                print("Estados disponíveis:")
                for est in acervo.listar_estados():
                    print(f'  [{est["id"]}] {est["descricao"]}')
                estado_id = int(input("ID do estado: "))
                acervo.definir_estado_livro(livro_id, estado_id)
                print("Estado atualizado.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "4":
            termo = input("Buscar por título/autor (ENTER pra pular): ") or None
            assunto = input("Filtrar por assunto (ENTER pra pular): ") or None
            resultados = acervo.buscar_livros(termo=termo, assunto=assunto)
            if not resultados:
                print("Nenhum livro encontrado.")
            for r in resultados:
                local = f'{r["prateleira"]} - {r["secao"]}' if r["prateleira"] else "sem localização definida"
                estado = r["estado"] or "sem estado definido"
                status = "disponível" if r["disponivel"] else "emprestado"
                print(f'  [{r["id"]}] {r["titulo"]} - {r["autor"]} | {local} | {estado} | {status}')

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
        pausar()


def menu_biblioteca_virtual():
    while True:
        print("\n--- BIBLIOTECA VIRTUAL (vitrine) ---")
        print("1. Ver vitrine de livros")
        print("2. Adicionar link externo a um livro")
        print("3. Ver links de um livro")
        print("0. Voltar")
        opcao = input("> ").strip()

        if opcao == "1":
            livros = vitrine.listar_vitrine()
            if not livros:
                print("Nenhum livro na vitrine ainda.")
            for l in livros:
                print(f'  [{l["id"]}] {l["titulo"]} - {l["autor"]} ({l["assunto"] or "sem assunto"})')

        elif opcao == "2":
            try:
                livro_id = int(input("ID do livro: "))
                url = input("URL do repositório: ")
                nome_repo = input("Nome do repositório: ")
                leitor_id = int(input("ID do leitor que está adicionando: "))
                vitrine.adicionar_link_externo(livro_id, url, nome_repo, leitor_id)
                print("Link adicionado.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "3":
            try:
                livro_id = int(input("ID do livro: "))
                links = vitrine.listar_links_do_livro(livro_id)
                if not links:
                    print("Nenhum link cadastrado pra esse livro.")
                for link in links:
                    print(f'  {link["nome_repositorio"]}: {link["url_repositorio"]} (por {link["adicionado_por"]})')
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
        pausar()


def main():
    db.criar_tabelas()
    leitores.atualizar_emprestimos_atrasados()

    while True:
        print("\n===== BIBLIOTECA VIRTUAL =====")
        print("1. Bibliotecários (cadastro de livros)")
        print("2. Leitores (empréstimos e histórico)")
        print("3. Acervo (estado, localização e busca)")
        print("4. Biblioteca virtual (vitrine)")
        print("0. Sair")
        opcao = input("> ").strip()

        if opcao == "1":
            menu_bibliotecarios()
        elif opcao == "2":
            menu_leitores()
        elif opcao == "3":
            menu_acervo()
        elif opcao == "4":
            menu_biblioteca_virtual()
        elif opcao == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
