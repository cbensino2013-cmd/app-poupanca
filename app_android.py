import flet as ft
import os
import random


def main(page: ft.Page):
    # ---------------------------------------------------------
    # CONFIGURACOES DA PAGINA
    # ---------------------------------------------------------
    page.title = "AURA 360 | Gestao Financeira & Patrimonio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ---------------------------------------------------------
    # DADOS
    # ---------------------------------------------------------
    faturas = [
        {
            "num": "FT 2026/089",
            "entidade": "Supermercado Continente",
            "cat": "Despesas Gerais",
            "valor": 124.50,
            "pago": True
        },
        {
            "num": "FT 2026/102",
            "entidade": "Farmacia Central",
            "cat": "Saude",
            "valor": 45.20,
            "pago": True
        },
        {
            "num": "FT 2026/115",
            "entidade": "Restaurante Alma",
            "cat": "Restauracao",
            "valor": 88.00,
            "pago": False
        }
    ]

    deducoes_irs = [
        {
            "cat": "Despesas Gerais",
            "atual": 240.0,
            "max": 350.0,
            "cor": "#3B82F6",
            "dica": "Faltam 110 EUR para atingir o teto."
        },
        {
            "cat": "Saude e Bem-Estar",
            "atual": 112.5,
            "max": 1000.0,
            "cor": "#10B981",
            "dica": "Guarde todas as faturas de saude."
        },
        {
            "cat": "Educacao e Formacao",
            "atual": 450.0,
            "max": 800.0,
            "cor": "#F59E0B",
            "dica": "Propinas e material escolar podem contar."
        },
        {
            "cat": "Habitacao e Rendas",
            "atual": 320.0,
            "max": 502.0,
            "cor": "#8B5CF6",
            "dica": "Confirme os recibos de renda no e-Fatura."
        },
        {
            "cat": "Restauracao e Lazer",
            "atual": 135.0,
            "max": 250.0,
            "cor": "#EC4899",
            "dica": "Guarde as faturas de restaurantes."
        }
    ]

    metas_poupanca = [
        {
            "nome": "Fundo de Emergencia",
            "atual": 4500,
            "meta": 6000,
            "cor": "#10B981"
        },
        {
            "nome": "Ferias e Viagens",
            "atual": 1200,
            "meta": 2000,
            "cor": "#3B82F6"
        },
        {
            "nome": "Investimentos / PPR",
            "atual": 800,
            "meta": 2000,
            "cor": "#8B5CF6"
        }
    ]

    # ---------------------------------------------------------
    # CARD DE METRICA
    # ---------------------------------------------------------
    def criar_card(titulo, valor, texto, icone, cor):
        return ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=16,
            border=ft.Border.all(1, "#E2E8F0"),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color="#20000000"
            ),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                titulo,
                                size=13,
                                color="#64748B",
                                weight=ft.FontWeight.W_600
                            ),
                            ft.Container(
                                content=ft.Icon(
                                    icone,
                                    color=cor,
                                    size=20
                                ),
                                bgcolor="#EFF6FF",
                                padding=8,
                                border_radius=10
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(
                        valor,
                        size=24,
                        color="#0F172A",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        texto,
                        size=12,
                        color="#10B981"
                    )
                ],
                spacing=10
            )
        )

    # ---------------------------------------------------------
    # CARDS PRINCIPAIS
    # ---------------------------------------------------------
    card_saldo = criar_card(
        "Patrimonio / Saldo Liquido",
        "12.450,00 EUR",
        "+8.4% este mes",
        ft.Icons.ACCOUNT_BALANCE_WALLET,
        "#10B981"
    )

    card_irs = criar_card(
        "Retorno Estimado IRS",
        "1.257,50 EUR",
        "82% do teto maximo",
        ft.Icons.ACCOUNT_BALANCE,
        "#3B82F6"
    )

    card_despesas = criar_card(
        "Gastos do Mes",
        "1.120,40 EUR",
        "12% abaixo do limite",
        ft.Icons.TRENDING_DOWN,
        "#EF4444"
    )

    # ---------------------------------------------------------
    # DEDUCOES IRS
    # ---------------------------------------------------------
    coluna_deducoes = ft.Column(spacing=10)

    for d in deducoes_irs:
        percentagem = min(
            d["atual"] / d["max"],
            1.0
        )

        coluna_deducoes.controls.append(
            ft.Container(
                bgcolor="#FFFFFF",
                padding=16,
                border_radius=12,
                border=ft.Border.all(
                    1,
                    "#E2E8F0"
                ),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    d["cat"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#0F172A",
                                    expand=True
                                ),
                                ft.Text(
                                    f'{d["atual"]:.2f} / {d["max"]:.2f} EUR',
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=d["cor"]
                                )
                            ]
                        ),
                        ft.ProgressBar(
                            value=percentagem,
                            color=d["cor"],
                            bgcolor="#F1F5F9",
                            height=8
                        ),
                        ft.Text(
                            d["dica"],
                            size=12,
                            color="#64748B"
                        )
                    ],
                    spacing=8
                )
            )
        )

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------
    view_dashboard = ft.Column(
        [
            ft.Text(
                "Resumo Executivo e Saude Financeira",
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#0F172A"
            ),
            ft.Row(
                [
                    card_saldo,
                    card_irs,
                    card_despesas
                ],
                spacing=10
            ),
            ft.Container(height=10),
            ft.Text(
                "Otimizador do e-Fatura e Deducoes IRS",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#0F172A"
            ),
            coluna_deducoes
        ],
        spacing=10
    )

    # ---------------------------------------------------------
    # CAMPOS DAS FATURAS
    # ---------------------------------------------------------
    txt_numero = ft.TextField(
        label="Numero da Fatura",
        border_color="#CBD5E1",
        expand=True
    )

    txt_entidade = ft.TextField(
        label="Empresa / Emitente",
        border_color="#CBD5E1",
        expand=True
    )

    txt_valor = ft.TextField(
        label="Valor EUR",
        border_color="#CBD5E1",
        width=150
    )

    dropdown_categoria = ft.Dropdown(
        label="Categoria",
        border_color="#CBD5E1",
        width=250,
        value="Despesas Gerais",
        options=[
            ft.DropdownOption(
                d["cat"]
            )
            for d in deducoes_irs
        ]
    )

    lista_faturas = ft.Column(
        spacing=10
    )

    # ---------------------------------------------------------
    # ATUALIZAR LISTA DE FATURAS
    # ---------------------------------------------------------
    def atualizar_faturas():
        lista_faturas.controls.clear()

        for fatura in faturas:
            if fatura["pago"]:
                cor = "#10B981"
                estado = "VALIDADA"
            else:
                cor = "#EF4444"
                estado = "PENDENTE"

            lista_faturas.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=16,
                    border_radius=12,
                    border=ft.Border.all(
                        1,
                        "#E2E8F0"
                    ),
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.RECEIPT_LONG,
                                color="#3B82F6",
                                size=25
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        f'{fatura["num"]} - {fatura["entidade"]}',
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color="#0F172A"
                                    ),
                                    ft.Text(
                                        f'Categoria: {fatura["cat"]}',
                                        size=12,
                                        color="#64748B"
                                    )
                                ],
                                expand=True
                            ),
                            ft.Text(
                                f'{fatura["valor"]:.2f} EUR',
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#0F172A"
                            ),
                            ft.Container(
                                content=ft.Text(
                                    estado,
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                ),
                                bgcolor=cor,
                                padding=7,
                                border_radius=6
                            )
                        ],
                        spacing=12
                    )
                )
            )

        page.update()

    # ---------------------------------------------------------
    # ADICIONAR FATURA
    # ---------------------------------------------------------
    def adicionar_fatura(e):
        if not txt_numero.value:
            return

        if not txt_valor.value:
            return

        try:
            valor = float(
                txt_valor.value.replace(",", ".")
            )

            faturas.append(
                {
                    "num": txt_numero.value,
                    "entidade": (
                        txt_entidade.value
                        or "Fornecedor"
                    ),
                    "cat": (
                        dropdown_categoria.value
                        or "Despesas Gerais"
                    ),
                    "valor": valor,
                    "pago": True
                }
            )

            txt_numero.value = ""
            txt_entidade.value = ""
            txt_valor.value = ""

            atualizar_faturas()

        except ValueError:
            txt_valor.error_text = (
                "Introduza um valor valido"
            )
            page.update()

    # ---------------------------------------------------------
    # VIEW FATURAS
    # ---------------------------------------------------------
    view_faturas = ft.Column(
        [
            ft.Text(
                "Repositorio Inteligente de Faturas",
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#0F172A"
            ),
            ft.Container(
                bgcolor="#FFFFFF",
                padding=20,
                border_radius=16,
                border=ft.Border.all(
                    1,
                    "#E2E8F0"
                ),
                content=ft.Column(
                    [
                        ft.Text(
                            "Registar Nova Fatura",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color="#0F172A"
                        ),
                        ft.Row(
                            [
                                txt_numero,
                                txt_entidade
                            ],
                            spacing=10
                        ),
                        ft.Row(
                            [
                                txt_valor,
                                dropdown_categoria
                            ],
                            spacing=10
                        ),
                        ft.ElevatedButton(
                            "Guardar Fatura",
                            icon=ft.Icons.SAVE,
                            bgcolor="#3B82F6",
                            color="#FFFFFF",
                            on_click=adicionar_fatura
                        )
                    ],
                    spacing=15
                )
            ),
            ft.Container(height=10),
            lista_faturas
        ],
        spacing=10
    )

    # ---------------------------------------------------------
    # METAS DE POUPANCA
    # ---------------------------------------------------------
    lista_metas = ft.Column(
        spacing=10
    )

    for meta in metas_poupanca:
        progresso = min(
            meta["atual"] / meta["meta"],
            1.0
        )

        lista_metas.controls.append(
            ft.Container(
                bgcolor="#FFFFFF",
                padding=16,
                border_radius=12,
                border=ft.Border.all(
                    1,
                    "#E2E8F0"
                ),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    meta["nome"],
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color="#0F172A",
                                    expand=True
                                ),
                                ft.Text(
                                    f'{meta["atual"]} / {meta["meta"]} EUR',
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=meta["cor"]
                                )
                            ]
                        ),
                        ft.ProgressBar(
                            value=progresso,
                            color=meta["cor"],
                            bgcolor="#F1F5F9",
                            height=10
                        ),
                        ft.Text(
                            f'{progresso * 100:.0f}% concluido',
                            size=12,
                            color="#64748B"
                        )
                    ],
                    spacing=8
                )
            )
        )

    # ---------------------------------------------------------
    # VIEW METAS
    # ---------------------------------------------------------
    view_metas = ft.Column(
        [
            ft.Text(
                "Objetivos e Liberdade Financeira",
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#0F172A"
            ),
            ft.Text(
                "Acompanhe as suas metas de poupanca e investimento.",
                size=13,
                color="#64748B"
            ),
            ft.Container(height=10),
            lista_metas
        ],
        spacing=10
    )

    # ---------------------------------------------------------
    # CABECALHO
    # ---------------------------------------------------------
    frases = [
        "O controlo financeiro de hoje constroi a liberdade de amanha.",
        "Saber onde esta o seu dinheiro e o primeiro passo para o multiplicar.",
        "Pequenas otimizacoes geram grandes resultados."
    ]

    header = ft.Container(
        bgcolor="#0F172A",
        padding=24,
        border_radius=20,
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.DIAMOND,
                                    color="#38BDF8",
                                    size=28
                                ),
                                ft.Text(
                                    "AURA 360",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                )
                            ]
                        ),
                        ft.Text(
                            random.choice(frases),
                            size=13,
                            color="#94A3B8",
                            italic=True
                        )
                    ],
                    expand=True
                ),
                ft.Container(
                    bgcolor="#1E293B",
                    padding=10,
                    border_radius=12,
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.VERIFIED_USER,
                                color="#10B981",
                                size=18
                            ),
                            ft.Text(
                                "Perfil Verificado",
                                color="#FFFFFF",
                                size=12,
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        spacing=6
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    # ---------------------------------------------------------
    # AREA DE CONTEUDO
    # ---------------------------------------------------------
    area_conteudo = ft.Container(
        content=view_dashboard,
        expand=True,
        padding=ft.padding.only(top=10)
    )

    # ---------------------------------------------------------
    # MUDAR DE ABA
    # ---------------------------------------------------------
    def mudar_aba(e):
        indice = int(e.control.data)

        views = [
            view_dashboard,
            view_faturas,
            view_metas
        ]

        area_conteudo.content = views[indice]

        page.update()

    # ---------------------------------------------------------
    # MENU
    # ---------------------------------------------------------
    menu = ft.Row(
        [
            ft.ElevatedButton(
                "Dashboard 360",
                data=0,
                bgcolor="#0F172A",
                color="#FFFFFF",
                on_click=mudar_aba
            ),
            ft.ElevatedButton(
                "e-Fatura e Recibos",
                data=1,
                bgcolor="#3B82F6",
                color="#FFFFFF",
                on_click=mudar_aba
            ),
            ft.ElevatedButton(
                "Metas e Poupanca",
                data=2,
                bgcolor="#10B981",
                color="#FFFFFF",
                on_click=mudar_aba
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10
    )

    # ---------------------------------------------------------
    # MONTAGEM FINAL
    # ---------------------------------------------------------
    page.add(
        header,
        ft.Container(height=5),
        menu,
        ft.Divider(color="#E2E8F0"),
        area_conteudo
    )

    atualizar_faturas()


# ---------------------------------------------------------
# INICIAR A APLICACAO
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    ft.app(
        target=main,
        port=port,
        view=ft.AppView.WEB_BROWSER
    )
