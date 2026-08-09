import ssl
import json
import os

# Desativar verificação rigorosa de SSL
ssl._create_default_https_context = ssl._create_unverified_context

import flet as ft

FICHEIRO_DADOS = "dados_orcamento.json"

def main(page: ft.Page):
    page.title = "Gestor de Poupança"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Carregar Dados Guardados
    def carregar_dados():
        if os.path.exists(FICHEIRO_DADOS):
            try:
                with open(FICHEIRO_DADOS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"salario": 1500.0, "meta_poupanca": 300.0, "despesas": []}

    dados = carregar_dados()

    # Campos da Interface Mobile
    txt_rendimento = ft.TextField(
        label="Rendimento (€)", 
        value=str(dados.get("salario", 1500.0)), 
        keyboard_type=ft.KeyboardType.NUMBER
    )
    txt_meta = ft.TextField(
        label="Meta de Poupança (€)", 
        value=str(dados.get("meta_poupanca", 300.0)), 
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    txt_nome_despesa = ft.TextField(label="Nome da Despesa")
    txt_valor_despesa = ft.TextField(label="Valor (€)", keyboard_type=ft.KeyboardType.NUMBER)
    dd_categoria = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option("Essencial"), ft.dropdown.Option("Lazer")],
        value="Essencial"
    )

    lista_despesas_ui = ft.Column()

    def atualizar_lista():
        lista_despesas_ui.controls.clear()
        for d in dados.get("despesas", []):
            lista_despesas_ui.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ATTACH_MONEY),
                    title=ft.Text(f"{d['nome']} - {d['valor']:.2f}€"),
                    subtitle=ft.Text(f"Categoria: {d['categoria']}")
                )
            )
        page.update()

    def adicionar_despesa(e):
        if txt_nome_despesa.value and txt_valor_despesa.value:
            try:
                v = float(txt_valor_despesa.value.replace(',', '.'))
                dados["despesas"].append({
                    "nome": txt_nome_despesa.value,
                    "valor": v,
                    "categoria": dd_categoria.value
                })
                with open(FICHEIRO_DADOS, "w", encoding="utf-8") as f:
                    json.dump(dados, f, indent=4)
                txt_nome_despesa.value = ""
                txt_valor_despesa.value = ""
                atualizar_lista()
                page.snack_bar = ft.SnackBar(ft.Text("Despesa guardada com sucesso!"))
                page.snack_bar.open = True
                page.update()
            except ValueError:
                pass

    btn_adicionar = ft.Button("➕ Adicionar Despesa", on_click=adicionar_despesa)

    atualizar_lista()

    # Layout do Telemóvel
    page.add(
        ft.Text("💰 Gestor de Poupança", size=24, weight=ft.FontWeight.BOLD),
        txt_rendimento,
        txt_meta,
        ft.Divider(),
        ft.Text("Registar Despesa", size=18, weight=ft.FontWeight.BOLD),
        txt_nome_despesa,
        txt_valor_despesa,
        dd_categoria,
        btn_adicionar,
        ft.Divider(),
        ft.Text("Lista de Gastos", size=18, weight=ft.FontWeight.BOLD),
        lista_despesas_ui
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)