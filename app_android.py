import flet as ft
import os
import random
from datetime import datetime


# ============================================================
# AURA 360
# Plataforma Financeira + Empresarial
# Página inicial comercial + Mascote AURA + Dashboard
# ============================================================

APP_NAME = "AURA 360"

# Paleta própria da AURA
NAVY = "#0B1220"
NAVY_2 = "#111C32"
BLUE = "#2563EB"
BLUE_LIGHT = "#EFF6FF"
CYAN = "#06B6D4"
GREEN = "#10B981"
GREEN_LIGHT = "#ECFDF5"
PURPLE = "#7C3AED"
PURPLE_LIGHT = "#F5F3FF"
ORANGE = "#F59E0B"
ORANGE_LIGHT = "#FFFBEB"
RED = "#EF4444"
WHITE = "#FFFFFF"
BG = "#F6F8FC"
TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"


# ============================================================
# DADOS DEMONSTRATIVOS
# ============================================================

user_data = {
    "nome": "Cliente",
    "saldo": 12450.00,
    "receitas": 2850.00,
    "despesas": 1120.40,
    "poupanca": 640.00,
    "creditos": 750.00,
    "saude_financeira": 78,
}

metas = [
    {
        "nome": "Fundo de Emergência",
        "atual": 4500,
        "meta": 6000,
        "cor": GREEN,
    },
    {
        "nome": "Férias & Viagens",
        "atual": 1200,
        "meta": 2000,
        "cor": BLUE,
    },
    {
        "nome": "Investimentos",
        "atual": 800,
        "meta": 2000,
        "cor": PURPLE,
    },
]

movimentos = [
    {
        "descricao": "Supermercado",
        "categoria": "Alimentação",
        "valor": -124.50,
    },
    {
        "descricao": "Salário",
        "categoria": "Rendimento",
        "valor": 2100.00,
    },
    {
        "descricao": "Restaurante",
        "categoria": "Restauração",
        "valor": -48.00,
    },
    {
        "descricao": "Transferência Poupança",
        "categoria": "Poupança",
        "valor": -200.00,
    },
]


# ============================================================
# APLICAÇÃO
# ============================================================

def main(page: ft.Page):

    page.title = APP_NAME
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # --------------------------------------------------------
    # CONFIGURAÇÃO RESPONSIVA
    # --------------------------------------------------------

    page.window_min_width = 360
    page.window_min_height = 650

    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    estado = {
        "autenticado": False,
        "perfil": "Pessoal",
        "pagina": "inicio",
    }

    # --------------------------------------------------------
    # FUNÇÕES AUXILIARES
    # --------------------------------------------------------

    def texto(
        value,
        size=14,
        color=TEXT,
        weight=ft.FontWeight.NORMAL,
        **kwargs,
    ):
        return ft.Text(
            value,
            size=size,
            color=color,
            weight=weight,
            **kwargs,
        )

    def botao(
        label,
        on_click=None,
        bgcolor=BLUE,
        color=WHITE,
        icon=None,
        width=None,
    ):
        kwargs = {
            "content": texto(
                label,
                size=14,
                color=color,
                weight=ft.FontWeight.W_600,
            ),
            "bgcolor": bgcolor,
            "color": color,
            "on_click": on_click,
        }

        if icon is not None:
            kwargs["icon"] = icon

        if width is not None:
            kwargs["width"] = width

        return ft.ElevatedButton(**kwargs)

    def card(content, padding=20, radius=18):
        return ft.Container(
            content=content,
            bgcolor=WHITE,
            padding=padding,
            border_radius=radius,
            border=ft.Border.all(1, BORDER),
        )

    def divider():
        return ft.Container(
            height=1,
            bgcolor=BORDER,
        )

    # ========================================================
    # AURA MASCOTE
    # ========================================================

    aura_avatar = ft.Container(
        width=64,
        height=64,
        border_radius=32,
        bgcolor=BLUE,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(
            ft.Icons.AUTO_AWESOME,
            color=WHITE,
            size=32,
        ),
    )

    aura_status = texto(
        "Estou aqui para ajudar.",
        size=12,
        color=MUTED,
    )

    aura_message = texto(
        "Olá! Eu sou a AURA. Posso ajudar-te a organizar o dinheiro, analisar créditos, acompanhar objetivos e gerir a tua empresa.",
        size=14,
        color=TEXT,
    )

    def aura_card(
        mensagem=None,
        titulo="AURA",
        botao_texto="Falar com a AURA",
        on_click=None,
    ):

        if mensagem:
            aura_message.value = mensagem

        aura_status.value = "● Online"

        return card(
            ft.Row(
                [
                    aura_avatar,
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    texto(
                                        titulo,
                                        size=17,
                                        color=TEXT,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Container(
                                        content=texto(
                                            "ONLINE",
                                            size=9,
                                            color=GREEN,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=GREEN_LIGHT,
                                        padding=6,
                                        border_radius=8,
                                    ),
                                ],
                                spacing=10,
                            ),
                            aura_message,
                            aura_status,
                            ft.Container(height=3),
                            botao(
                                botao_texto,
                                on_click=on_click,
                                bgcolor=NAVY,
                                icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                            ),
                        ],
                        expand=True,
                        spacing=5,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    # ========================================================
    # SNACKBAR
    # ========================================================

    def avisar(mensagem, cor=GREEN):
        page.snack_bar = ft.SnackBar(
            content=texto(
                mensagem,
                color=WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=cor,
        )
        page.snack_bar.open = True
        page.update()

    # ========================================================
    # AURA CHAT
    # ========================================================

    chat_messages = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    chat_input = ft.TextField(
        hint_text="Pergunta à AURA...",
        expand=True,
        border_radius=14,
        border_color=BORDER,
        filled=True,
        fill_color=BG,
    )

    def aura_responder(pergunta):

        pergunta = pergunta.lower().strip()

        if any(
            palavra in pergunta
            for palavra in [
                "saldo",
                "dinheiro",
                "património",
            ]
        ):
            return (
                f"O teu saldo atual registado na AURA é "
                f"{user_data['saldo']:,.2f} €. "
                "Posso também ajudar a analisar receitas, despesas "
                "e evolução mensal."
            )

        if any(
            palavra in pergunta
            for palavra in [
                "poupar",
                "poupança",
                "guardar",
            ]
        ):
            return (
                f"Neste momento tens uma capacidade de poupança "
                f"registada de {user_data['poupanca']:,.2f} € por mês. "
                "Também tens metas de poupança configuradas."
            )

        if any(
            palavra in pergunta
            for palavra in [
                "credito",
                "crédito",
                "prestação",
                "divida",
                "dívida",
            ]
        ):
            return (
                f"As prestações/créditos registados totalizam "
                f"{user_data['creditos']:,.2f} € por mês. "
                "Posso calcular a taxa de esforço se me indicares "
                "o rendimento líquido mensal."
            )

        if any(
            palavra in pergunta
            for palavra in [
                "empresa",
                "negócio",
                "negocio",
                "cliente",
                "venda",
            ]
        ):
            return (
                "Posso mudar para o Perfil Empresarial e ajudar "
                "com clientes, vendas, orçamentos, inventário, "
                "tesouraria e análise do negócio."
            )

        if any(
            palavra in pergunta
            for palavra in [
                "irs",
                "imposto",
                "fatura",
                "fatura",
                "efatura",
            ]
        ):
            return (
                "Posso ajudar a organizar despesas e documentos "
                "relacionados com IRS. Para valores fiscais atuais "
                "e decisões fiscais, a versão completa da AURA "
                "deve consultar fontes oficiais."
            )

        if "olá" in pergunta or "ola" in pergunta:
            return (
                "Olá! 👋 Sou a AURA. "
                "Diz-me o que queres resolver e começamos por aí."
            )

        return (
            "Posso ajudar-te com finanças pessoais, poupança, "
            "crédito, documentos, impostos, empresas, vendas, "
            "orçamentos e organização financeira. "
            "Experimenta perguntar, por exemplo: "
            "\"Quanto estou a gastar?\""
        )

    def enviar_mensagem(e):

        pergunta = chat_input.value.strip()

        if not pergunta:
            return

        chat_messages.controls.append(
            ft.Container(
                content=texto(
                    "Tu: " + pergunta,
                    color=WHITE,
                    size=13,
                ),
                bgcolor=BLUE,
                padding=10,
                border_radius=12,
            )
        )

        resposta = aura_responder(pergunta)

        chat_messages.controls.append(
            ft.Container(
                content=texto(
                    "AURA: " + resposta,
                    color=TEXT,
                    size=13,
                ),
                bgcolor=BLUE_LIGHT,
                padding=10,
                border_radius=12,
            )
        )

        chat_input.value = ""

        page.update()

    chat_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(
                    ft.Icons.AUTO_AWESOME,
                    color=BLUE,
                ),
                texto(
                    "AURA — Assistente Financeira",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
        content=ft.Container(
            width=500,
            height=430,
            content=ft.Column(
                [
                    ft.Container(
                        content=texto(
                            "Pergunta-me qualquer coisa sobre a tua organização financeira.",
                            size=13,
                            color=MUTED,
                        ),
                        padding=10,
                    ),
                    chat_messages,
                    ft.Row(
                        [
                            chat_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                icon_color=BLUE,
                                on_click=enviar_mensagem,
                            ),
                        ]
                    ),
                ],
                expand=True,
            ),
        ),
        actions=[
            ft.TextButton(
                content=texto(
                    "Fechar",
                    color=BLUE,
                ),
                on_click=lambda e: fechar_dialog(chat_dialog),
            )
        ],
    )

    def abrir_dialog(dialog):
        if dialog not in page.overlay:
            page.overlay.append(dialog)

        dialog.open = True
        page.update()

    def fechar_dialog(dialog):
        dialog.open = False
        page.update()

    def abrir_aura(e=None):
        abrir_dialog(chat_dialog)

    # ========================================================
    # LOGIN / REGISTO
    # ========================================================

    login_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color=BORDER,
    )

    login_password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    login_dialog = ft.AlertDialog(
        modal=True,
        title=texto(
            "Entrar na AURA 360",
            size=20,
            weight=ft.FontWeight.BOLD,
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(
                [
                    texto(
                        "Entra na tua área pessoal ou empresarial.",
                        color=MUTED,
                    ),
                    login_email,
                    login_password,
                    botao(
                        "Entrar",
                        on_click=lambda e: entrar_conta(),
                        width=200,
                    ),
                    ft.TextButton(
                        content=texto(
                            "Ainda não tenho conta",
                            color=BLUE,
                        ),
                        on_click=lambda e: abrir_registo(),
                    ),
                ],
                tight=True,
                spacing=12,
            ),
        ),
    )

    reg_nome = ft.TextField(
        label="Nome",
        border_color=BORDER,
    )

    reg_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color=BORDER,
    )

    reg_password = ft.TextField(
        label="Criar password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    registo_dialog = ft.AlertDialog(
        modal=True,
        title=texto(
            "Criar conta AURA 360",
            size=20,
            weight=ft.FontWeight.BOLD,
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(
                [
                    texto(
                        "Começa gratuitamente.",
                        color=MUTED,
                    ),
                    reg_nome,
                    reg_email,
                    reg_password,
                    botao(
                        "Criar a minha conta",
                        on_click=lambda e: criar_conta(),
                        width=230,
                    ),
                ],
                spacing=12,
            ),
        ),
    )

    def entrar_conta():

        if not login_email.value or not login_password.value:
            avisar(
                "Preenche o email e a password.",
                RED,
            )
            return

        estado["autenticado"] = True
        user_data["nome"] = (
            login_email.value.split("@")[0].title()
        )

        login_dialog.open = False

        mostrar_dashboard()

    def abrir_registo():

        login_dialog.open = False
        abrir_dialog(registo_dialog)

    def criar_conta():

        if (
            not reg_nome.value
            or not reg_email.value
            or not reg_password.value
        ):
            avisar(
                "Preenche todos os campos.",
                RED,
            )
            return

        estado["autenticado"] = True
        user_data["nome"] = reg_nome.value

        registo_dialog.open = False

        mostrar_dashboard()

        avisar(
            "Conta criada. Bem-vindo à AURA 360!",
            GREEN,
        )

    # ========================================================
    # HEADER LANDING
    # ========================================================

    def abrir_login(e):
        abrir_dialog(login_dialog)

    def abrir_registo_principal(e):
        abrir_dialog(registo_dialog)

    header_landing = ft.Container(
        bgcolor=WHITE,
        padding=ft.Padding(
            left=30,
            right=30,
            top=18,
            bottom=18,
        ),
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=42,
                            height=42,
                            bgcolor=NAVY,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.AUTO_AWESOME,
                                color="#60A5FA",
                                size=23,
                            ),
                        ),
                        texto(
                            "AURA",
                            size=23,
                            color=NAVY,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            "360",
                            size=23,
                            color=BLUE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Row(
                    [
                        ft.TextButton(
                            content=texto(
                                "Como funciona",
                                color=MUTED,
                            ),
                        ),
                        ft.TextButton(
                            content=texto(
                                "Para empresas",
                                color=MUTED,
                            ),
                        ),
                        ft.TextButton(
                            content=texto(
                                "Ajuda",
                                color=MUTED,
                            ),
                        ),
                        botao(
                            "Entrar",
                            on_click=abrir_login,
                            bgcolor=WHITE,
                            color=NAVY,
                        ),
                        botao(
                            "Criar conta",
                            on_click=abrir_registo_principal,
                        ),
                    ],
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # ========================================================
    # HERO
    # ========================================================

    def hero():

        return ft.Container(
            bgcolor=NAVY,
            padding=ft.Padding(
                left=35,
                right=35,
                top=55,
                bottom=55,
            ),
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        col={
                            "sm": 12,
                            "md": 7,
                            "lg": 7,
                        },
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=texto(
                                        "INTELIGÊNCIA PARA A TUA VIDA FINANCEIRA",
                                        size=11,
                                        color="#93C5FD",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor="#172554",
                                    padding=10,
                                    border_radius=20,
                                ),
                                texto(
                                    "O teu dinheiro.\n"
                                    "A tua empresa.\n"
                                    "Uma inteligência contigo.",
                                    size=42,
                                    color=WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                texto(
                                    "AURA 360 reúne finanças pessoais, "
                                    "crédito, poupança e gestão empresarial "
                                    "numa única plataforma.",
                                    size=17,
                                    color="#CBD5E1",
                                ),
                                ft.Row(
                                    [
                                        botao(
                                            "Começar gratuitamente",
                                            on_click=abrir_registo_principal,
                                            bgcolor=WHITE,
                                            color=NAVY,
                                        ),
                                        botao(
                                            "Falar com a AURA",
                                            on_click=abrir_aura,
                                            bgcolor="#1E293B",
                                            color=WHITE,
                                            icon=ft.Icons.AUTO_AWESOME,
                                        ),
                                    ],
                                    wrap=True,
                                ),
                                texto(
                                    "Sem complicações. Começa pela tua realidade.",
                                    size=12,
                                    color="#94A3B8",
                                ),
                            ],
                            spacing=18,
                        ),
                    ),
                    ft.Container(
                        col={
                            "sm": 12,
                            "md": 5,
                            "lg": 5,
                        },
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            aura_avatar,
                                            ft.Column(
                                                [
                                                    texto(
                                                        "Olá 👋",
                                                        size=20,
                                                        color=WHITE,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    texto(
                                                        "Eu sou a AURA",
                                                        size=13,
                                                        color="#93C5FD",
                                                    ),
                                                ]
                                            ),
                                        ],
                                    ),
                                    texto(
                                        "Por onde queres começar?",
                                        size=21,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    escolha_hero(
                                        "💰",
                                        "Organizar as minhas finanças",
                                        lambda e: abrir_registo_principal(e),
                                    ),
                                    escolha_hero(
                                        "💳",
                                        "Analisar os meus créditos",
                                        lambda e: abrir_registo_principal(e),
                                    ),
                                    escolha_hero(
                                        "🏢",
                                        "Gerir a minha empresa",
                                        lambda e: abrir_registo_principal(e),
                                    ),
                                    escolha_hero(
                                        "🎯",
                                        "Criar uma meta de poupança",
                                        lambda e: abrir_registo_principal(e),
                                    ),
                                ],
                                spacing=12,
                            ),
                            bgcolor=NAVY_2,
                            padding=25,
                            border_radius=22,
                            border=ft.Border.all(
                                1,
                                "#24324A",
                            ),
                        ),
                    ),
                ],
                spacing=30,
            ),
        )

    def escolha_hero(emoji, titulo, action):

        return ft.Container(
            content=ft.Row(
                [
                    texto(
                        emoji,
                        size=21,
                    ),
                    texto(
                        titulo,
                        size=13,
                        color=WHITE,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD,
                        color="#64748B",
                        size=17,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="#162238",
            padding=14,
            border_radius=12,
            on_click=action,
        )

    # ========================================================
    # BENEFÍCIOS
    # ========================================================

    def feature_card(icon, titulo, descricao, cor):

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=cor,
                        border_radius=14,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icon,
                            color=WHITE,
                            size=23,
                        ),
                    ),
                    texto(
                        titulo,
                        size=17,
                        weight=ft.FontWeight.BOLD,
                    ),
                    texto(
                        descricao,
                        size=13,
                        color=MUTED,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=WHITE,
            padding=22,
            border_radius=18,
            border=ft.Border.all(1, BORDER),
        )

    # ========================================================
    # LANDING PAGE
    # ========================================================

    landing_content = ft.Column(
        [
            header_landing,
            hero(),
            ft.Container(
                padding=30,
                content=ft.Column(
                    [
                        texto(
                            "Tudo o que precisas num só lugar",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            "A AURA organiza a complexidade para que "
                            "possas tomar decisões melhores.",
                            size=14,
                            color=MUTED,
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    col={
                                        "sm": 12,
                                        "md": 6,
                                        "lg": 3,
                                    },
                                    content=feature_card(
                                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                                        "Finanças pessoais",
                                        "Receitas, despesas, saldo e evolução.",
                                        BLUE,
                                    ),
                                ),
                                ft.Container(
                                    col={
                                        "sm": 12,
                                        "md": 6,
                                        "lg": 3,
                                    },
                                    content=feature_card(
                                        ft.Icons.CREDIT_CARD,
                                        "Crédito",
                                        "Analisa prestações e taxa de esforço.",
                                        GREEN,
                                    ),
                                ),
                                ft.Container(
                                    col={
                                        "sm": 12,
                                        "md": 6,
                                        "lg": 3,
                                    },
                                    content=feature_card(
                                        ft.Icons.TARGET,
                                        "Objetivos",
                                        "Cria metas e acompanha o progresso.",
                                        PURPLE,
                                    ),
                                ),
                                ft.Container(
                                    col={
                                        "sm": 12,
                                        "md": 6,
                                        "lg": 3,
                                    },
                                    content=feature_card(
                                        ft.Icons.BUSINESS,
                                        "Empresas",
                                        "Clientes, vendas, stock e tesouraria.",
                                        ORANGE,
                                    ),
                                ),
                            ],
                            spacing=15,
                        ),
                    ],
                    spacing=15,
                ),
            ),
            ft.Container(
                padding=30,
                content=aura_card(
                    mensagem=(
                        "Eu acompanho-te dentro da plataforma. "
                        "Quando precisares de ajuda, pergunta-me."
                    ),
                    botao_texto="Experimentar a AURA",
                    on_click=abrir_aura,
                ),
            ),
            ft.Container(
                bgcolor=NAVY,
                padding=35,
                content=ft.Column(
                    [
                        texto(
                            "Uma plataforma. Dois mundos.",
                            size=28,
                            color=WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            "Começa nas tuas finanças pessoais e, "
                            "quando precisares, passa para o universo empresarial.",
                            size=14,
                            color="#CBD5E1",
                        ),
                        ft.Row(
                            [
                                botao(
                                    "Perfil Pessoal",
                                    on_click=abrir_registo_principal,
                                    bgcolor=WHITE,
                                    color=NAVY,
                                ),
                                botao(
                                    "Perfil Empresarial",
                                    on_click=abrir_registo_principal,
                                    bgcolor="#1E293B",
                                    color=WHITE,
                                ),
                            ],
                            wrap=True,
                        ),
                    ],
                    spacing=15,
                ),
            ),
            ft.Container(
                padding=25,
                content=texto(
                    "© 2026 AURA 360 • Gestão Financeira & Empresarial",
                    size=12,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
        ],
        spacing=0,
    )

    # ========================================================
    # DASHBOARD
    # ========================================================

    dashboard_area = ft.Column(expand=True)

    def metric_card(titulo, valor, legenda, icon, cor):

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            texto(
                                titulo,
                                size=12,
                                color=MUTED,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Container(
                                width=38,
                                height=38,
                                bgcolor=BLUE_LIGHT,
                                border_radius=11,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    icon,
                                    color=cor,
                                    size=20,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    texto(
                        valor,
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                    texto(
                        legenda,
                        size=12,
                        color=GREEN if "+" in legenda else MUTED,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=WHITE,
            padding=18,
            border_radius=16,
            border=ft.Border.all(1, BORDER),
        )

    def mostrar_dashboard():

        def voltar_inicio(e):
            mostrar_landing()

        dashboard_area.controls.clear()

        # Header dashboard
        dashboard_area.controls.append(
            ft.Container(
                bgcolor=NAVY,
                padding=20,
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    width=40,
                                    height=40,
                                    bgcolor=BLUE,
                                    border_radius=12,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(
                                        ft.Icons.AUTO_AWESOME,
                                        color=WHITE,
                                    ),
                                ),
                                texto(
                                    "AURA 360",
                                    size=20,
                                    color=WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    content=texto(
                                        "Início",
                                        color="#CBD5E1",
                                    ),
                                    on_click=voltar_inicio,
                                ),
                                ft.TextButton(
                                    content=texto(
                                        "AURA AI",
                                        color="#93C5FD",
                                    ),
                                    on_click=abrir_aura,
                                ),
                                ft.Container(
                                    content=texto(
                                        user_data["nome"],
                                        size=12,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=NAVY_2,
                                    padding=10,
                                    border_radius=10,
                                ),
                            ],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )

        # Saudação
        dashboard_area.controls.append(
            ft.Container(
                padding=25,
                content=ft.Column(
                    [
                        texto(
                            f"Bom dia, {user_data['nome']} 👋",
                            size=27,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            "Aqui está o resumo da tua vida financeira.",
                            size=14,
                            color=MUTED,
                        ),
                    ]
                ),
            )
        )

        # Métricas
        dashboard_area.controls.append(
            ft.Container(
                padding=ft.Padding(
                    left=25,
                    right=25,
                    top=0,
                    bottom=20,
                ),
                content=ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                                "lg": 3,
                            },
                            content=metric_card(
                                "Património",
                                f"{user_data['saldo']:,.2f} €",
                                "+8,4% este mês",
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                GREEN,
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                                "lg": 3,
                            },
                            content=metric_card(
                                "Receitas",
                                f"{user_data['receitas']:,.2f} €",
                                "Este mês",
                                ft.Icons.TRENDING_UP,
                                GREEN,
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                                "lg": 3,
                            },
                            content=metric_card(
                                "Despesas",
                                f"{user_data['despesas']:,.2f} €",
                                "Este mês",
                                ft.Icons.TRENDING_DOWN,
                                RED,
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                                "lg": 3,
                            },
                            content=metric_card(
                                "Saúde financeira",
                                f"{user_data['saude_financeira']}/100",
                                "Boa situação",
                                ft.Icons.FAVORITE,
                                PURPLE,
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            )
        )

        # AURA
        dashboard_area.controls.append(
            ft.Container(
                padding=ft.Padding(
                    left=25,
                    right=25,
                    top=0,
                    bottom=20,
                ),
                content=aura_card(
                    mensagem=(
                        "Analisei o teu resumo. "
                        "Tens uma capacidade de poupança de "
                        f"{user_data['poupanca']:,.2f} € este mês. "
                        "Queres que eu te ajude a definir o próximo objetivo?"
                    ),
                    botao_texto="Conversar com a AURA",
                    on_click=abrir_aura,
                ),
            )
        )

        # Metas + movimentos
        metas_column = ft.Column(
            [
                texto(
                    "🎯 As tuas metas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                )
            ],
            spacing=12,
        )

        for meta in metas:

            progresso = min(
                meta["atual"] / meta["meta"],
                1,
            )

            metas_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    texto(
                                        meta["nome"],
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    texto(
                                        f"{meta['atual']:,.0f} € / "
                                        f"{meta['meta']:,.0f} €",
                                        size=12,
                                        color=meta["cor"],
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=progresso,
                                color=meta["cor"],
                                bgcolor="#E5E7EB",
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor=WHITE,
                    padding=15,
                    border_radius=12,
                    border=ft.Border.all(1, BORDER),
                )
            )

        movimentos_column = ft.Column(
            [
                texto(
                    "💳 Movimentos recentes",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                )
            ],
            spacing=10,
        )

        for movimento in movimentos:

            positivo = movimento["valor"] >= 0

            movimentos_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=38,
                                height=38,
                                bgcolor=GREEN_LIGHT
                                if positivo
                                else "#FEF2F2",
                                border_radius=10,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.ARROW_UPWARD
                                    if positivo
                                    else ft.Icons.ARROW_DOWNWARD,
                                    color=GREEN if positivo else RED,
                                    size=18,
                                ),
                            ),
                            ft.Column(
                                [
                                    texto(
                                        movimento["descricao"],
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    texto(
                                        movimento["categoria"],
                                        size=11,
                                        color=MUTED,
                                    ),
                                ],
                                expand=True,
                            ),
                            texto(
                                f"{movimento['valor']:+.2f} €",
                                size=13,
                                color=GREEN if positivo else RED,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    padding=10,
                )
            )

        dashboard_area.controls.append(
            ft.Container(
                padding=ft.Padding(
                    left=25,
                    right=25,
                    top=0,
                    bottom=25,
                ),
                content=ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                            },
                            content=card(
                                metas_column,
                                padding=20,
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                            },
                            content=card(
                                movimentos_column,
                                padding=20,
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            )
        )

        # Barra inferior
        dashboard_area.controls.append(
            ft.Container(
                padding=20,
                bgcolor=WHITE,
                border=ft.Border.only(
                    top=ft.BorderSide(1, BORDER),
                ),
                content=ft.Row(
                    [
                        texto(
                            "AURA 360",
                            size=12,
                            color=MUTED,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            "Tudo sob controlo.",
                            size=12,
                            color=MUTED,
                        ),
                        botao(
                            "Falar com AURA",
                            on_click=abrir_aura,
                            bgcolor=NAVY,
                            icon=ft.Icons.AUTO_AWESOME,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )

        # Navegação inferior
        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            bgcolor=WHITE,
            indicator_color=BLUE_LIGHT,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Início",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                    selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                    label="Finanças",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TARGET_OUTLINED,
                    selected_icon=ft.Icons.TARGET,
                    label="Metas",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BUSINESS_OUTLINED,
                    selected_icon=ft.Icons.BUSINESS,
                    label="Empresa",
                ),
            ],
            on_change=dashboard_navigation,
        )

        page.controls.clear()
        page.add(
            ft.SafeArea(
                content=dashboard_area,
                expand=True,
            )
        )

        page.update()

    def dashboard_navigation(e):

        index = e.control.selected_index

        if index == 0:
            mostrar_dashboard()

        elif index == 1:
            mostrar_modulo(
                "💰 Finanças",
                "Aqui ficará o centro financeiro pessoal.",
                [
                    "Receitas",
                    "Despesas",
                    "Categorias",
                    "Contas",
                    "Movimentos",
                    "Relatórios",
                ],
            )

        elif index == 2:
            mostrar_modulo(
                "🎯 Metas & Poupança",
                "Acompanha objetivos e planos de poupança.",
                [
                    "Fundo de emergência",
                    "Férias",
                    "Investimentos",
                    "PPR",
                    "Objetivos personalizados",
                ],
            )

        elif index == 3:
            mostrar_modulo(
                "🏢 Perfil Empresarial",
                "O centro de gestão do teu negócio.",
                [
                    "CRM",
                    "Clientes",
                    "Vendas",
                    "Orçamentos",
                    "POS",
                    "Inventário FIFO",
                    "Tesouraria",
                    "Impostos",
                ],
            )

    def mostrar_modulo(titulo, descricao, funcionalidades):

        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            bgcolor=WHITE,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    label="Início",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                    label="Finanças",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TARGET_OUTLINED,
                    label="Metas",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BUSINESS_OUTLINED,
                    label="Empresa",
                ),
            ],
            on_change=dashboard_navigation,
        )

        controls = [
            ft.Container(
                padding=25,
                content=ft.Column(
                    [
                        texto(
                            titulo,
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        texto(
                            descricao,
                            size=14,
                            color=MUTED,
                        ),
                    ]
                ),
            )
        ]

        for item in funcionalidades:

            controls.append(
                ft.Container(
                    margin=ft.Margin(
                        left=25,
                        right=25,
                        top=5,
                        bottom=5,
                    ),
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            color=BLUE,
                        ),
                        title=texto(
                            item,
                            size=14,
                            weight=ft.FontWeight.W_500,
                        ),
                        trailing=ft.Icon(
                            ft.Icons.ARROW_FORWARD_IOS,
                            size=16,
                            color=MUTED,
                        ),
                    ),
                    bgcolor=WHITE,
                    border_radius=12,
                    border=ft.Border.all(1, BORDER),
                )
            )

        controls.append(
            ft.Container(
                padding=25,
                content=aura_card(
                    mensagem=(
                        "Este módulo está preparado para crescer "
                        "com funcionalidades reais. "
                        "Pergunta-me o que queres fazer."
                    ),
                    botao_texto="Perguntar à AURA",
                    on_click=abrir_aura,
                ),
            )
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    controls,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        page.update()

    # ========================================================
    # LANDING
    # ========================================================

    def mostrar_landing():

        estado["autenticado"] = False

        page.navigation_bar = None

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        landing_content,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        page.update()

    # ========================================================
    # INICIALIZAÇÃO
    # ========================================================

    mostrar_landing()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        route_url_strategy="path",
    )
