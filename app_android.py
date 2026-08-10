import flet as ft
import time
import random


def main(page: ft.Page):
    # =========================================================
    # CONFIGURACAO DA PAGINA
    # =========================================================

    page.title = "AURA 360 | Gestao Financeira & Otimizacao"
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

    CINZENTO = "#64748B"
    CINZENTO_CLARO = "#E2E8F0"

    BRANCO = "#FFFFFF"
    ESCURO = "#0F172A"

    # =========================================================
    # DICAS
    # =========================================================

    dicas = [
        "Como Poupar: experimente a regra 50/30/20 para organizar o seu dinheiro.",
        "Gestao B2B: compare sempre varios orcamentos antes de iniciar uma obra.",
        "Dica de Credito: compare a taxa de juro antes de amortizar ou consolidar creditos.",
        "Contas Bancarias: confirme sempre as condicoes atuais antes de abrir uma conta.",
        "IRS e e-Fatura: confirme regularmente se as suas faturas estao corretamente classificadas.",
        "Otimizacao de Custos: reveja seguros, telecomunicacoes e outros contratos anualmente."
    ]

    dica_sorteada = random.choice(dicas)

    # =========================================================
    # SPLASH SCREEN
    # =========================================================

    progresso = ft.ProgressBar(
        width=280,
        color=AZUL,
        bgcolor="#DBEAFE"
    )

    txt_dica = ft.Text(
        dica_sorteada,
        size=14,
        italic=True,
        color=AZUL_ESCURO,
        text_align=ft.TextAlign.CENTER
    )

    splash_screen = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.LIGHTBULB_OUTLINE,
                    size=80,
                    color="#F59E0B"
                ),

                ft.Text(
                    "AURA 360",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "A gerar as melhores estrategias para si...",
                    size=14,
                    color=CINZENTO
                ),

                ft.Container(
                    height=15
                ),

                progresso,

                ft.Container(
                    height=20
                ),

                ft.Container(
                    content=txt_dica,
                    padding=15,
                    bgcolor=BRANCO,
                    border_radius=12,
                    width=400
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        ),
        expand=True
    )

    # =========================================================
    # AURA AI
    # =========================================================

    chat_messages = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=220,
        spacing=8
    )

    user_input = ft.TextField(
        hint_text="Pergunte sobre IRS, credito, obras...",
        expand=True
    )

    def send_message(e):

        pergunta = user_input.value

        if pergunta and pergunta.strip():

            pergunta_limpa = pergunta.strip()

            chat_messages.controls.append(
                ft.Text(
                    "Voce: " + pergunta_limpa,
                    weight=ft.FontWeight.BOLD,
                    color=ESCURO
                )
            )

            texto = pergunta_limpa.lower()

            resposta = ""

            if (
                "credito" in texto
                or "divida" in texto
                or "juntar" in texto
            ):
                resposta = (
                    "Pode utilizar o simulador de creditos. "
                    "A consolidacao pode reduzir a prestacao mensal, "
                    "mas deve comparar sempre o custo total e a TAEG."
                )

            elif (
                "obra" in texto
                or "pintura" in texto
                or "piso" in texto
                or "orcamento" in texto
            ):
                resposta = (
                    "Abra o separador Orcamentos de Obras. "
                    "Escolha o servico, area e gama de materiais "
                    "para obter uma estimativa."
                )

            elif (
                "banco" in texto
                or "conta" in texto
            ):
                resposta = (
                    "Consulte sempre as condicoes atuais do banco "
                    "antes de abrir uma conta."
                )

            elif (
                "irs" in texto
                or "fatura" in texto
            ):
                resposta = (
                    "Confirme regularmente as suas faturas no e-Fatura "
                    "e verifique se cada despesa esta na categoria correta."
                )

            elif (
                "aima" in texto
                or "residencia" in texto
            ):
                resposta = (
                    "Pode utilizar o botao AIMA no topo da aplicacao "
                    "para aceder ao respetivo portal."
                )

            else:
                resposta = (
                    "Posso ajudar com credito, obras, faturas, "
                    "IRS, poupanca e organizacao financeira."
                )

            chat_messages.controls.append(
                ft.Text(
                    "AURA AI: " + resposta,
                    color=AZUL_ESCURO
                )
            )

            user_input.value = ""

            page.update()

    ai_dialog = ft.AlertDialog(
        title=ft.Row(
            [
                ft.Icon(
                    ft.Icons.AUTO_AWESOME,
                    color=AZUL
                ),
                ft.Text(
                    "AURA AI - Assistente"
                )
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    chat_messages,

                    ft.Row(
                        [
                            user_input,

                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                icon_color=AZUL,
                                on_click=send_message
                            )
                        ]
                    )
                ]
            ),
            width=400,
            height=300
        )
    )

    def open_ai_chat(e):

        if ai_dialog not in page.overlay:
            page.overlay.append(ai_dialog)

        ai_dialog.open = True

        page.update()

    fab_btn = ft.FloatingActionButton(
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
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        ),
        bgcolor=AZUL,
        width=125,
        on_click=open_ai_chat
    )

    # =========================================================
    # MODAL DE INFORMACAO BANCARIA
    # =========================================================

    bank_dialog = ft.AlertDialog(
        title=ft.Text(
            "Guia de Abertura de Conta Bancaria"
        ),

        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Opcoes a pesquisar em Portugal:",
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE
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
                            ft.Icons.ACCOUNT_BALANCE
                        ),
                        title=ft.Text(
                            "Banco CTT"
                        ),
                        subtitle=ft.Text(
                            "Consulte as condicoes atuais da conta."
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

    def open_bank_modal(e):

        if bank_dialog not in page.overlay:
            page.overlay.append(bank_dialog)

        bank_dialog.open = True

        page.update()

    # =========================================================
    # SIMULADOR DE CREDITOS
    # =========================================================

    inp_rendimento = ft.TextField(
        label="Rendimento Liquido Mensal",
        value="1200",
        width=220
    )

    inp_ch = ft.TextField(
        label="Credito Habitacao / mes",
        value="450",
        width=220
    )

    inp_outros_cred = ft.TextField(
        label="Outros Creditos / mes",
        value="300",
        width=220
    )

    res_taxa = ft.Text(
        "Taxa de Esforco Atual: --%",
        size=17,
        weight=ft.FontWeight.BOLD,
        color=ESCURO
    )

    res_recomendacao = ft.Container(
        padding=12,
        border_radius=10
    )

    def simular_reestruturacao(e):

        try:

            rendimento = float(
                inp_rendimento.value.replace(
                    ",",
                    "."
                )
            )

            habitacao = float(
                inp_ch.value.replace(
                    ",",
                    "."
                )
            )

            outros = float(
                inp_outros_cred.value.replace(
                    ",",
                    "."
                )
            )

            if rendimento <= 0:
                raise ValueError

            total = habitacao + outros

            taxa = (
                total / rendimento
            ) * 100

            res_taxa.value = (
                f"Taxa de Esforco Atual: {taxa:.1f}%"
            )

            if taxa <= 35:

                res_recomendacao.bgcolor = VERDE_CLARO

                res_recomendacao.content = ft.Text(
                    "ZONA SAUDAVEL: a taxa de esforco "
                    "esta abaixo de 35%. Compare sempre "
                    "as taxas antes de tomar novas decisoes.",
                    color="#166534"
                )

            elif taxa <= 50:

                res_recomendacao.bgcolor = LARANJA_CLARO

                res_recomendacao.content = ft.Text(
                    "ATENCAO: a taxa de esforco esta entre "
                    "35% e 50%. Analise a consolidacao e "
                    "compare o custo total dos creditos.",
                    color="#9A3412"
                )

            else:

                res_recomendacao.bgcolor = VERMELHO_CLARO

                res_recomendacao.content = ft.Text(
                    "ZONA DE ELEVADO RISCO: a taxa de esforco "
                    "ultrapassa 50%. Procure aconselhamento "
                    "financeiro antes de assumir nova divida.",
                    color="#991B1B"
                )

            page.update()

        except ValueError:

            res_taxa.value = (
                "Introduza valores numericos validos."
            )

            page.update()

    view_creditos = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Reestruturacao, Consolidacao e Taxa de Esforco",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Simule a sua taxa de esforco mensal.",
                    size=13,
                    color=CINZENTO
                ),

                ft.Row(
                    [
                        inp_rendimento,
                        inp_ch,
                        inp_outros_cred
                    ],
                    wrap=True,
                    spacing=10
                ),

                ft.ElevatedButton(
                    "Simular Taxa de Esforco",
                    on_click=simular_reestruturacao,
                    bgcolor=AZUL,
                    color=BRANCO
                ),

                res_taxa,

                res_recomendacao
            ],
            spacing=12
        ),
        padding=15,
        bgcolor=BRANCO,
        border_radius=10
    )

    # =========================================================
    # ORCAMENTOS DE OBRAS
    # =========================================================

    dd_servico = ft.Dropdown(
        label="Tipo de Servico",
        width=270,
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

    inp_area = ft.TextField(
        label="Area Estimada (m2)",
        value="50",
        width=160
    )

    dd_gama = ft.Dropdown(
        label="Gama de Materiais",
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

    res_orcamento = ft.Column(
        spacing=8
    )

    def calcular_orcamento(e):

        try:

            area = float(
                inp_area.value.replace(
                    ",",
                    "."
                )
            )

            if area <= 0:
                raise ValueError

            servico = dd_servico.value
            gama = dd_gama.value

            precos_base = {
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

            preco_base = precos_base.get(
                servico,
                15
            )

            multiplicador = multiplicadores.get(
                gama,
                1.0
            )

            custo_m2 = (
                preco_base * multiplicador
            )

            materiais = (
                custo_m2
                * 0.40
                * area
                * 1.10
            )

            mao_obra = (
                custo_m2
                * 0.60
                * area
            )

            subtotal = (
                materiais
                + mao_obra
            )

            iva = subtotal * 0.06

            total = subtotal + iva

            res_orcamento.controls = [

                ft.Divider(),

                ft.Text(
                    "Estimativa de Orcamento",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    f"Servico: {servico}"
                ),

                ft.Text(
                    f"Area: {area:.2f} m2"
                ),

                ft.Text(
                    f"Gama: {gama}"
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
                    f"IVA calculado a 6%: {iva:.2f} EUR"
                ),

                ft.Text(
                    f"VALOR TOTAL: {total:.2f} EUR",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=VERDE
                ),

                ft.Text(
                    "Nota: o valor e uma estimativa e deve "
                    "ser confirmado pelo profissional e pelas "
                    "condicoes fiscais aplicaveis.",
                    size=11,
                    color=CINZENTO
                )
            ]

            page.update()

        except ValueError:

            res_orcamento.controls = [
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
                    "Gerador de Orcamentos de Remodelacao",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Crie uma estimativa rapida para diferentes tipos de obras.",
                    size=13,
                    color=CINZENTO
                ),

                ft.Row(
                    [
                        dd_servico,
                        inp_area,
                        dd_gama
                    ],
                    wrap=True,
                    spacing=10
                ),

                ft.ElevatedButton(
                    "Gerar Orcamento",
                    on_click=calcular_orcamento,
                    bgcolor=AZUL,
                    color=BRANCO
                ),

                res_orcamento
            ],
            spacing=12
        ),
        padding=15,
        bgcolor=BRANCO,
        border_radius=10
    )

    # =========================================================
    # FATURAS
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

    lista_faturas_col = ft.Column(
        spacing=5
    )

    for fatura in faturas:

        if fatura["pago"]:
            estado = "Pago"
            cor_estado = VERDE
        else:
            estado = "Pendente"
            cor_estado = VERMELHO

        lista_faturas_col.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            color=AZUL
                        ),

                        ft.Column(
                            [
                                ft.Text(
                                    f'{fatura["num"]} - {fatura["entidade"]}',
                                    weight=ft.FontWeight.BOLD,
                                    color=ESCURO
                                ),

                                ft.Text(
                                    f'{fatura["cat"]} | {estado}',
                                    size=12,
                                    color=CINZENTO
                                )
                            ],
                            expand=True,
                            spacing=3
                        ),

                        ft.Text(
                            f'{fatura["valor"]:.2f} EUR',
                            weight=ft.FontWeight.BOLD,
                            color=ESCURO
                        ),

                        ft.Container(
                            content=ft.Text(
                                estado,
                                color=BRANCO,
                                size=11,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=cor_estado,
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
        )

    view_faturas = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Gestao de Faturas e e-Fatura",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_ESCURO
                ),

                ft.Text(
                    "Consulte e organize as suas despesas.",
                    size=13,
                    color=CINZENTO
                ),

                lista_faturas_col,

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Anexar Foto da Fatura",
                            icon=ft.Icons.CAMERA_ALT,
                            bgcolor=AZUL,
                            color=BRANCO
                        ),

                        ft.ElevatedButton(
                            "Validar no e-Fatura",
                            icon=ft.Icons.CHECK_CIRCLE,
                            bgcolor=VERDE,
                            color=BRANCO
                        )
                    ],
                    wrap=True,
                    spacing=10
                )
            ],
            spacing=12
        ),
        padding=15,
        bgcolor=BRANCO,
        border_radius=10
    )

    # =========================================================
    # CABECALHO
    # =========================================================

    header = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.DIAMOND,
                                    color=AZUL,
                                    size=30
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
                                ft.TextButton(
                                    "Abrir Conta",
                                    on_click=open_bank_modal
                                ),

                                ft.ElevatedButton(
                                    "AIMA",
                                    icon=ft.Icons.LINK
                                ),

                                ft.ElevatedButton(
                                    "SIGA",
                                    icon=ft.Icons.CALENDAR_MONTH
                                )
                            ],
                            wrap=True,
                            spacing=5
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True
                ),

                ft.Text(
                    "Gestao Financeira | Creditos | Obras | Faturas",
                    size=13,
                    color=CINZENTO
                )
            ],
            spacing=5
        ),
        padding=15,
        bgcolor=BRANCO,
        border_radius=12,
        border=ft.Border.all(
            1,
            CINZENTO_CLARO
        )
    )

    # =========================================================
    # TABS
    # =========================================================

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True,
        tabs=[
            ft.Tab(
                text="Creditos e Amortizacao",
                content=view_creditos
            ),

            ft.Tab(
                text="Orcamentos de Obras",
                content=view_obras
            ),

            ft.Tab(
                text="Faturas e Impostos",
                content=view_faturas
            )
        ]
    )

    # =========================================================
    # SPLASH
    # =========================================================

    page.add(
        splash_screen
    )

    page.update()

    time.sleep(2)

    # =========================================================
    # PAGINA PRINCIPAL
    # =========================================================

    page.controls.clear()

    page.floating_action_button = fab_btn

    page.add(
        header,

        ft.Container(
            height=10
        ),

        tabs
    )

    page.update()


# =============================================================
# INICIAR A APLICACAO
# =============================================================

if __name__ == "__main__":

    ft.app(
        target=main
    )
