import flet as ft
import time
import random


def main(page: ft.Page):

    # =========================================================
    # CONFIGURACAO PRINCIPAL
    # =========================================================

    page.title = "AURA 360 | Gestao Financeira"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    # =========================================================
    # CORES
    # =========================================================

    AZUL = "#2563EB"
    AZUL_ESCURO = "#1E3A8A"
    AZUL_CLARO = "#EFF6FF"

    VERDE = "#16A34A"
    VERDE_CLARO = "#DCFCE7"

    LARANJA = "#EA580C"
    LARANJA_CLARO = "#FFEDD5"

    VERMELHO = "#DC2626"
    VERMELHO_CLARO = "#FEE2E2"

    ROXO = "#7C3AED"
    ROXO_CLARO = "#EDE9FE"

    ESCURO = "#0F172A"
    CINZENTO = "#64748B"
    CINZENTO_CLARO = "#E2E8F0"
    FUNDO = "#F8FAFC"
    BRANCO = "#FFFFFF"

    # =========================================================
    # FUNCAO PARA MOSTRAR MENSAGENS
    # =========================================================

    def mostrar_mensagem(texto, cor=AZUL):

        snack = ft.SnackBar(
            content=ft.Text(
                texto,
                color=BRANCO
            ),
            bgcolor=cor
        )

        page.overlay.append(snack)
        snack.open = True
        page.update()

    # =========================================================
    # DADOS
    # =========================================================

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

    metas = [
        {
            "nome": "Fundo de Emergencia",
            "atual": 4500,
            "meta": 6000,
            "cor": VERDE
        },
        {
            "nome": "Ferias e Viagens",
            "atual": 1200,
            "meta": 2000,
            "cor": AZUL
        },
        {
            "nome": "Investimentos / PPR",
            "atual": 800,
            "meta": 2000,
            "cor": ROXO
        }
    ]

    # =========================================================
    # SPLASH SCREEN
    # =========================================================

    dicas = [
        "Organize primeiro as despesas fixas e depois defina o valor mensal de poupanca.",
        "Compare sempre propostas de credito pelo custo total e nao apenas pela prestacao.",
        "Antes de iniciar uma obra, compare varios orcamentos.",
        "Verifique regularmente as suas faturas e classificacoes no e-Fatura.",
        "Reveja seguros, telecomunicacoes e outros contratos pelo menos uma vez por ano."
    ]

    dica = random.choice(dicas)

    progresso = ft.ProgressBar(
        width=280,
        color=AZUL,
        bgcolor="#DBEAFE"
    )

    splash = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.DIAMOND,
                    size=75,
                    color=AZUL
                ),

                ft.Text(
                    "AURA 360",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Gestao Financeira Inteligente",
                    size=15,
                    color=CINZENTO
                ),

                ft.Container(
                    height=15
                ),

                progresso,

                ft.Container(
                    height=15
                ),

                ft.Container(
                    content=ft.Text(
                        dica,
                        size=14,
                        italic=True,
                        color=AZUL_ESCURO,
                        text_align=ft.TextAlign.CENTER
                    ),
                    width=400,
                    padding=15,
                    bgcolor=BRANCO,
                    border_radius=12,
                    border=ft.Border.all(
                        1,
                        CINZENTO_CLARO
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        ),
        expand=True
    )

    # =========================================================
    # CONTEUDO PRINCIPAL
    # =========================================================

    area_conteudo = ft.Container(
        expand=True,
        padding=10
    )

    # =========================================================
    # CABECALHO
    # =========================================================

    def abrir_aima(e):

        mostrar_mensagem(
            "AIMA: aceda ao portal oficial da AIMA.",
            AZUL
        )

    def abrir_siga(e):

        mostrar_mensagem(
            "SIGA: aceda ao portal oficial de marcacoes.",
            AZUL
        )

    header = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.DIAMOND,
                                    size=30,
                                    color=AZUL
                                ),

                                ft.Text(
                                    "AURA 360",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_ESCURO
                                )
                            ]
                        ),

                        ft.Row(
                            [
                                ft.Text(
                                    "Perfil Verificado",
                                    size=12,
                                    color=VERDE,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True
                ),

                ft.Text(
                    "Gestao Financeira | Creditos | Obras | Faturas",
                    size=13,
                    color=CINZENTO
                ),

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Abrir Conta",
                            on_click=lambda e: abrir_banco()
                        ),

                        ft.ElevatedButton(
                            "AIMA",
                            icon=ft.Icons.LINK,
                            on_click=abrir_aima
                        ),

                        ft.ElevatedButton(
                            "SIGA",
                            icon=ft.Icons.CALENDAR_MONTH,
                            on_click=abrir_siga
                        )
                    ],
                    wrap=True,
                    spacing=8
                )
            ],
            spacing=8
        ),
        bgcolor=BRANCO,
        padding=15,
        border_radius=15,
        border=ft.Border.all(
            1,
            CINZENTO_CLARO
        )
    )

    # =========================================================
    # MODAL BANCO
    # =========================================================

    banco_dialog = ft.AlertDialog(
        title=ft.Text(
            "Guia de Abertura de Conta"
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Informacao geral",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=AZUL_ESCURO
                    ),

                    ft.Text(
                        "Algumas opcoes que pode pesquisar em Portugal:"
                    ),

                    ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE,
                            color=AZUL
                        ),
                        title=ft.Text(
                            "ActivoBank / Moey!"
                        ),
                        subtitle=ft.Text(
                            "Consulte as condicoes atuais diretamente no banco."
                        )
                    ),

                    ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE,
                            color=AZUL
                        ),
                        title=ft.Text(
                            "Banco CTT"
                        ),
                        subtitle=ft.Text(
                            "Consulte as condicoes atuais diretamente no banco."
                        )
                    ),

                    ft.Divider(),

                    ft.Text(
                        "Documentos normalmente solicitados:",
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "1. Documento de identificacao\n"
                        "2. NIF\n"
                        "3. Comprovativo de morada\n"
                        "4. Comprovativo de rendimentos, quando aplicavel"
                    )
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            width=450,
            height=350
        )
    )

    def abrir_banco():

        if banco_dialog not in page.overlay:
            page.overlay.append(banco_dialog)

        banco_dialog.open = True

        page.update()

    # =========================================================
    # DASHBOARD
    # =========================================================

    def criar_card(
        titulo,
        valor,
        descricao,
        icone,
        cor
    ):

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                titulo,
                                size=13,
                                color=CINZENTO,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Icon(
                                icone,
                                color=cor,
                                size=22
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    ft.Text(
                        valor,
                        size=25,
                        weight=ft.FontWeight.BOLD,
                        color=ESCURO
                    ),

                    ft.Text(
                        descricao,
                        size=12,
                        color=cor
                    )
                ],
                spacing=8
            ),
            bgcolor=BRANCO,
            padding=18,
            border_radius=15,
            border=ft.Border.all(
                1,
                CINZENTO_CLARO
            ),
            expand=True
        )

    card_patrimonio = criar_card(
        "Patrimonio Liquido",
        "12.450 EUR",
        "+8,4% este mes",
        ft.Icons.ACCOUNT_BALANCE_WALLET,
        VERDE
    )

    card_irs = criar_card(
        "Retorno IRS Estimado",
        "1.257 EUR",
        "82% do objetivo",
        ft.Icons.ACCOUNT_BALANCE,
        AZUL
    )

    card_despesas = criar_card(
        "Despesas do Mes",
        "1.120 EUR",
        "12% abaixo do limite",
        ft.Icons.TRENDING_DOWN,
        VERDE
    )

    dashboard = ft.Column(
        [
            ft.Text(
                "Dashboard Financeiro",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ESCURO
            ),

            ft.Text(
                "Visao geral da sua situacao financeira.",
                size=13,
                color=CINZENTO
            ),

            ft.Row(
                [
                    card_patrimonio,
                    card_irs,
                    card_despesas
                ],
                wrap=True,
                spacing=10
            ),

            ft.Container(
                height=10
            ),

            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Saude Financeira",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ESCURO
                        ),

                        ft.Text(
                            "Acompanhe os principais indicadores.",
                            size=13,
                            color=CINZENTO
                        ),

                        ft.ProgressBar(
                            value=0.82,
                            color=VERDE,
                            bgcolor="#E5E7EB"
                        ),

                        ft.Text(
                            "82% do objetivo financeiro mensal",
                            size=12,
                            color=VERDE
                        )
                    ],
                    spacing=10
                ),
                bgcolor=BRANCO,
                padding=20,
                border_radius=15,
                border=ft.Border.all(
                    1,
                    CINZENTO_CLARO
                )
            )
        ],
        spacing=10
    )

    # =========================================================
    # CREDITO
    # =========================================================

    rendimento = ft.TextField(
        label="Rendimento Liquido Mensal",
        value="1200",
        width=220
    )

    habitacao = ft.TextField(
        label="Credito Habitacao / mes",
        value="450",
        width=220
    )

    outros_creditos = ft.TextField(
        label="Outros Creditos / mes",
        value="300",
        width=220
    )

    resultado_taxa = ft.Text(
        "Taxa de Esforco: --%",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ESCURO
    )

    recomendacao_credito = ft.Container(
        padding=15,
        border_radius=10
    )

    def calcular_credito(e):

        try:

            r = float(
                rendimento.value.replace(
                    ",",
                    "."
                )
            )

            h = float(
                habitacao.value.replace(
                    ",",
                    "."
                )
            )

            o = float(
                outros_creditos.value.replace(
                    ",",
                    "."
                )
            )

            if r <= 0:
                raise ValueError

            total = h + o

            taxa = (
                total / r
            ) * 100

            resultado_taxa.value = (
                f"Taxa de Esforco: {taxa:.1f}%"
            )

            if taxa <= 35:

                recomendacao_credito.bgcolor = VERDE_CLARO

                recomendacao_credito.content = ft.Text(
                    "Zona saudavel. A taxa esta abaixo de 35%.",
                    color="#166534"
                )

            elif taxa <= 50:

                recomendacao_credito.bgcolor = LARANJA_CLARO

                recomendacao_credito.content = ft.Text(
                    "Atencao. A taxa esta entre 35% e 50%. "
                    "Compare propostas antes de assumir novo credito.",
                    color="#9A3412"
                )

            else:

                recomendacao_credito.bgcolor = VERMELHO_CLARO

                recomendacao_credito.content = ft.Text(
                    "Taxa elevada. Evite aumentar o endividamento "
                    "sem analisar primeiro a sua situacao.",
                    color="#991B1B"
                )

            page.update()

        except ValueError:

            resultado_taxa.value = (
                "Introduza valores validos."
            )

            page.update()

    view_creditos = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Creditos e Taxa de Esforco",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Simule rapidamente a sua taxa de esforco mensal.",
                    color=CINZENTO
                ),

                ft.Row(
                    [
                        rendimento,
                        habitacao,
                        outros_creditos
                    ],
                    wrap=True,
                    spacing=10
                ),

                ft.ElevatedButton(
                    "Calcular Taxa de Esforco",
                    icon=ft.Icons.CALCULATE,
                    bgcolor=AZUL,
                    color=BRANCO,
                    on_click=calcular_credito
                ),

                resultado_taxa,

                recomendacao_credito
            ],
            spacing=12
        ),
        bgcolor=BRANCO,
        padding=20,
        border_radius=15
    )

    # =========================================================
    # ORCAMENTOS DE OBRAS
    # =========================================================

    servico = ft.Dropdown(
        label="Tipo de Servico",
        width=280,
        value="Pintura de Interiores",
        options=[
            ft.dropdown.Option(
                "Pintura de Interiores"
            ),
            ft.dropdown.Option(
                "Aplicacao de Flutuante/Vinil"
            ),
            ft.dropdown.Option(
                "Tecto Falso em Pladur"
            ),
            ft.dropdown.Option(
                "Remodelacao de Casa de Banho"
            )
        ]
    )

    area = ft.TextField(
        label="Area (m2)",
        value="50",
        width=160
    )

    gama = ft.Dropdown(
        label="Gama",
        width=190,
        value="Profissional",
        options=[
            ft.dropdown.Option(
                "Economica"
            ),
            ft.dropdown.Option(
                "Profissional"
            ),
            ft.dropdown.Option(
                "Premium"
            )
        ]
    )

    resultado_obra = ft.Column(
        spacing=6
    )

    def calcular_obra(e):

        try:

            metros = float(
                area.value.replace(
                    ",",
                    "."
                )
            )

            if metros <= 0:
                raise ValueError

            precos = {
                "Pintura de Interiores": 12,
                "Aplicacao de Flutuante/Vinil": 22,
                "Tecto Falso em Pladur": 28,
                "Remodelacao de Casa de Banho": 85
            }

            multiplicadores = {
                "Economica": 0.85,
                "Profissional": 1.00,
                "Premium": 1.35
            }

            preco = precos.get(
                servico.value,
                15
            )

            multiplicador = multiplicadores.get(
                gama.value,
                1
            )

            preco_final = (
                preco
                * multiplicador
            )

            materiais = (
                preco_final
                * 0.40
                * metros
                * 1.10
            )

            mao_obra = (
                preco_final
                * 0.60
                * metros
            )

            subtotal = (
                materiais
                + mao_obra
            )

            iva = (
                subtotal
                * 0.06
            )

            total = (
                subtotal
                + iva
            )

            resultado_obra.controls = [

                ft.Divider(),

                ft.Text(
                    "Resultado do Orcamento",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    f"Servico: {servico.value}"
                ),

                ft.Text(
                    f"Area: {metros:.2f} m2"
                ),

                ft.Text(
                    f"Gama: {gama.value}"
                ),

                ft.Divider(),

                ft.Text(
                    f"Materiais: {materiais:.2f} EUR"
                ),

                ft.Text(
                    f"Mao de obra: {mao_obra:.2f} EUR"
                ),

                ft.Text(
                    f"Subtotal: {subtotal:.2f} EUR"
                ),

                ft.Text(
                    f"IVA considerado: {iva:.2f} EUR"
                ),

                ft.Text(
                    f"TOTAL ESTIMADO: {total:.2f} EUR",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                    color=VERDE
                ),

                ft.Text(
                    "Estimativa indicativa. Confirme sempre "
                    "o enquadramento fiscal e o orcamento final.",
                    size=11,
                    color=CINZENTO
                )
            ]

            page.update()

        except ValueError:

            resultado_obra.controls = [
                ft.Text(
                    "Introduza uma area valida.",
                    color=VERMELHO
                )
            ]

            page.update()

    view_obras = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Orcamentos de Obras",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Calcule uma estimativa para diferentes tipos de trabalhos.",
                    color=CINZENTO
                ),

                ft.Row(
                    [
                        servico,
                        area,
                        gama
                    ],
                    wrap=True,
                    spacing=10
                ),

                ft.ElevatedButton(
                    "Gerar Orcamento",
                    icon=ft.Icons.CALCULATE,
                    bgcolor=AZUL,
                    color=BRANCO,
                    on_click=calcular_obra
                ),

                resultado_obra
            ],
            spacing=12
        ),
        bgcolor=BRANCO,
        padding=20,
        border_radius=15
    )

    # =========================================================
    # FATURAS
    # =========================================================

    lista_faturas = ft.Column(
        spacing=8
    )

    def atualizar_faturas():

        lista_faturas.controls.clear()

        for fatura in faturas:

            if fatura["pago"]:
                estado = "PAGO"
                cor = VERDE
            else:
                estado = "PENDENTE"
                cor = VERMELHO

            item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            color=AZUL,
                            size=25
                        ),

                        ft.Column(
                            [
                                ft.Text(
                                    f'{fatura["num"]} - {fatura["entidade"]}',
                                    weight=ft.FontWeight.BOLD,
                                    color=ESCURO
                                ),

                                ft.Text(
                                    f'{fatura["cat"]}',
                                    size=12,
                                    color=CINZENTO
                                )
                            ],
                            expand=True,
                            spacing=2
                        ),

                        ft.Text(
                            f'{fatura["valor"]:.2f} EUR',
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Container(
                            content=ft.Text(
                                estado,
                                color=BRANCO,
                                size=10,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=cor,
                            padding=6,
                            border_radius=6
                        )
                    ],
                    spacing=10
                ),
                bgcolor=BRANCO,
                padding=12,
                border_radius=10,
                border=ft.Border.all(
                    1,
                    CINZENTO_CLARO
                )
            )

            lista_faturas.controls.append(
                item
            )

        page.update()

    atualizar_faturas()

    view_faturas = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Faturas e e-Fatura",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Organize as suas despesas e acompanhe as faturas.",
                    color=CINZENTO
                ),

                lista_faturas,

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Anexar Fatura",
                            icon=ft.Icons.CAMERA_ALT,
                            bgcolor=AZUL,
                            color=BRANCO,
                            on_click=lambda e: mostrar_mensagem(
                                "Funcao de anexar fatura preparada para integracao."
                            )
                        ),

                        ft.ElevatedButton(
                            "Validar e-Fatura",
                            icon=ft.Icons.CHECK_CIRCLE,
                            bgcolor=VERDE,
                            color=BRANCO,
                            on_click=lambda e: mostrar_mensagem(
                                "Validacao preparada para integracao com e-Fatura."
                            )
                        )
                    ],
                    wrap=True,
                    spacing=10
                )
            ],
            spacing=12
        ),
        bgcolor=BRANCO,
        padding=20,
        border_radius=15
    )

    # =========================================================
    # METAS DE POUPANCA
    # =========================================================

    lista_metas = ft.Column(
        spacing=10
    )

    for meta in metas:

        percentagem = (
            meta["atual"]
            / meta["meta"]
        )

        if percentagem > 1:
            percentagem = 1

        lista_metas.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    meta["nome"],
                                    weight=ft.FontWeight.BOLD,
                                    color=ESCURO
                                ),

                                ft.Text(
                                    f'{meta["atual"]} / {meta["meta"]} EUR',
                                    color=meta["cor"],
                                    weight=ft.FontWeight.BOLD
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),

                        ft.ProgressBar(
                            value=percentagem,
                            color=meta["cor"],
                            bgcolor="#E5E7EB"
                        ),

                        ft.Text(
                            f"{percentagem * 100:.0f}% concluido",
                            size=12,
                            color=CINZENTO
                        )
                    ],
                    spacing=7
                ),
                bgcolor=BRANCO,
                padding=15,
                border_radius=12,
                border=ft.Border.all(
                    1,
                    CINZENTO_CLARO
                )
            )
        )

    view_metas = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Metas e Poupanca",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Acompanhe o progresso dos seus objetivos financeiros.",
                    color=CINZENTO
                ),

                lista_metas
            ],
            spacing=12
        ),
        bgcolor=BRANCO,
        padding=20,
        border_radius=15
    )

    # =========================================================
    # AURA AI
    # =========================================================

    mensagens = ft.Column(
        height=220,
        scroll=ft.ScrollMode.AUTO,
        spacing=8
    )

    entrada_ai = ft.TextField(
        hint_text="Escreva a sua pergunta...",
        expand=True
    )

    def enviar_ai(e):

        pergunta = entrada_ai.value

        if not pergunta:
            return

        mensagens.controls.append(
            ft.Text(
                "Voce: " + pergunta,
                weight=ft.FontWeight.BOLD,
                color=ESCURO
            )
        )

        texto = pergunta.lower()

        if "credito" in texto or "divida" in texto:

            resposta = (
                "Para analisar um credito, compare a prestacao, "
                "TAEG, TAN, prazo e custo total."
            )

        elif "obra" in texto or "orcamento" in texto:

            resposta = (
                "Pode utilizar o separador Orcamentos de Obras "
                "para calcular uma estimativa."
            )

        elif "irs" in texto or "fatura" in texto:

            resposta = (
                "Confirme as suas faturas e respetivas categorias "
                "no e-Fatura."
            )

        elif "poupanca" in texto or "poupar" in texto:

            resposta = (
                "Defina primeiro uma meta mensal de poupanca e "
                "automatize a transferencia quando possivel."
            )

        else:

            resposta = (
                "Posso ajudar com credito, obras, faturas, "
                "IRS, poupanca e organizacao financeira."
            )

        mensagens.controls.append(
            ft.Text(
                "AURA AI: " + resposta,
                color=AZUL_ESCURO
            )
        )

        entrada_ai.value = ""

        page.update()

    dialog_ai = ft.AlertDialog(
        title=ft.Text(
            "AURA AI - Assistente"
        ),

        content=ft.Container(
            content=ft.Column(
                [
                    mensagens,

                    ft.Row(
                        [
                            entrada_ai,

                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                icon_color=AZUL,
                                on_click=enviar_ai
                            )
                        ]
                    )
                ]
            ),
            width=420,
            height=300
        )
    )

    def abrir_ai(e):

        if dialog_ai not in page.overlay:
            page.overlay.append(dialog_ai)

        dialog_ai.open = True

        page.update()

    botao_ai = ft.FloatingActionButton(
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.CHAT_BUBBLE,
                    color=BRANCO
                ),

                ft.Text(
                    "AURA AI",
                    color=BRANCO,
                    weight=ft.FontWeight.BOLD
                )
            ],
            spacing=5
        ),
        bgcolor=AZUL,
        width=125,
        on_click=abrir_ai
    )

    # =========================================================
    # NAVEGACAO
    #
    # NAO USAMOS ft.TABS / ft.TAB
    # PARA EVITAR INCOMPATIBILIDADES ENTRE VERSOES
    # =========================================================

    def selecionar_pagina(numero):

        if numero == 0:
            area_conteudo.content = dashboard

        elif numero == 1:
            area_conteudo.content = view_creditos

        elif numero == 2:
            area_conteudo.content = view_obras

        elif numero == 3:
            area_conteudo.content = view_faturas

        elif numero == 4:
            area_conteudo.content = view_metas

        page.update()

    botao_dashboard = ft.ElevatedButton(
        "Dashboard",
        icon=ft.Icons.DASHBOARD,
        bgcolor=AZUL_ESCURO,
        color=BRANCO,
        on_click=lambda e: selecionar_pagina(0)
    )

    botao_creditos = ft.ElevatedButton(
        "Creditos",
        icon=ft.Icons.CREDIT_CARD,
        bgcolor=AZUL,
        color=BRANCO,
        on_click=lambda e: selecionar_pagina(1)
    )

    botao_obras = ft.ElevatedButton(
        "Obras",
        icon=ft.Icons.CONSTRUCTION,
        bgcolor=ROXO,
        color=BRANCO,
        on_click=lambda e: selecionar_pagina(2)
    )

    botao_faturas = ft.ElevatedButton(
        "Faturas",
        icon=ft.Icons.RECEIPT_LONG,
        bgcolor=VERDE,
        color=BRANCO,
        on_click=lambda e: selecionar_pagina(3)
    )

    botao_metas = ft.ElevatedButton(
        "Metas",
        icon=ft.Icons.SAVINGS,
        bgcolor=LARANJA,
        color=BRANCO,
        on_click=lambda e: selecionar_pagina(4)
    )

    navegacao = ft.Container(
        content=ft.Row(
            [
                botao_dashboard,
                botao_creditos,
                botao_obras,
                botao_faturas,
                botao_metas
            ],
            wrap=True,
            spacing=8
        ),
        bgcolor=BRANCO,
        padding=10,
        border_radius=12,
        border=ft.Border.all(
            1,
            CINZENTO_CLARO
        )
    )

    # =========================================================
    # MONTAGEM INICIAL
    # =========================================================

    area_conteudo.content = dashboard

    page.add(
        splash
    )

    page.update()

    # Pequena espera para mostrar o carregamento
    time.sleep(1.5)

    page.controls.clear()

    page.floating_action_button = botao_ai

    page.add(
        header,

        ft.Container(
            height=10
        ),

        navegacao,

        ft.Container(
            height=10
        ),

        area_conteudo
    )

    page.update()


# =============================================================
# EXECUTAR
# =============================================================

if __name__ == "__main__":
    ft.app(
        target=main
    )
