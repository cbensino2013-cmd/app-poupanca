import flet as ft
from datetime import datetime


# ============================================================
# AURA 360
# Plataforma Financeira + Empresarial
# Versão Web/Desktop
# ============================================================

APP_NAME = "AURA 360"

# ============================================================
# CORES
# ============================================================

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
RED_LIGHT = "#FEF2F2"
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
            "content": label,
            "bgcolor": bgcolor,
            "color": color,
            "on_click": on_click,
        }

        if icon is not None:
            kwargs["icon"] = icon

        if width is not None:
            kwargs["width"] = width

        return ft.Button(**kwargs)

    def card(content, padding=20, radius=18):
        return ft.Container(
            content=content,
            bgcolor=WHITE,
            padding=padding,
            border_radius=radius,
            border=ft.Border.all(1, BORDER),
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

    aura_message = texto(
        "Olá! Eu sou a AURA. Estou aqui para ajudar-te.",
        size=14,
        color=TEXT,
    )

    aura_status = texto(
        "● Online",
        size=12,
        color=GREEN,
    )

    # ========================================================
    # CHAT DA AURA
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

        p = pergunta.lower().strip()

        if any(
            palavra in p
            for palavra in [
                "saldo",
                "dinheiro",
                "patrimonio",
                "património",
            ]
        ):
            return (
                f"O teu saldo registado atualmente é "
                f"{user_data['saldo']:,.2f} €. "
                "Posso também analisar receitas, despesas "
                "e evolução financeira."
            )

        if any(
            palavra in p
            for palavra in [
                "poupar",
                "poupança",
                "poupanca",
                "guardar",
                "economizar",
            ]
        ):
            return (
                f"Neste momento tens uma capacidade de "
                f"poupança registada de "
                f"{user_data['poupanca']:,.2f} € por mês. "
                "Também tens metas financeiras configuradas."
            )

        if any(
            palavra in p
            for palavra in [
                "credito",
                "crédito",
                "prestação",
                "prestacao",
                "divida",
                "dívida",
            ]
        ):
            return (
                f"As prestações registadas totalizam "
                f"{user_data['creditos']:,.2f} € por mês. "
                "Se me disseres o teu rendimento líquido mensal, "
                "posso calcular a taxa de esforço."
            )

        if any(
            palavra in p
            for palavra in [
                "empresa",
                "negócio",
                "negocio",
                "cliente",
                "venda",
                "fatura",
                "fatura",
            ]
        ):
            return (
                "Posso ajudar-te no Perfil Empresarial com "
                "clientes, vendas, orçamentos, inventário, "
                "tesouraria e organização financeira."
            )

        if any(
            palavra in p
            for palavra in [
                "irs",
                "imposto",
                "impostos",
                "efatura",
                "e-fatura",
            ]
        ):
            return (
                "Posso ajudar a organizar informação relacionada "
                "com impostos e documentos. Para regras fiscais "
                "atuais, devemos consultar fontes oficiais."
            )

        if any(
            palavra in p
            for palavra in [
                "ola",
                "olá",
                "bom dia",
                "boa tarde",
                "boa noite",
            ]
        ):
            return (
                "Olá! 👋 Sou a AURA. "
                "Diz-me o que queres resolver e começamos."
            )

        if "ajuda" in p:
            return (
                "Claro. Posso ajudar com finanças pessoais, "
                "poupança, créditos, metas, empresas, clientes, "
                "vendas, orçamento e organização."
            )

        return (
            "Percebi. Posso ajudar-te a analisar essa situação. "
            "Experimenta perguntar, por exemplo: "
            "\"Quanto estou a gastar?\", "
            "\"Como posso poupar?\" ou "
            "\"Quero analisar os meus créditos.\""
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
                padding=12,
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
                padding=12,
                border_radius=12,
            )
        )

        chat_input.value = ""

        page.update()

    def fechar_chat(e=None):
        chat_dialog.open = False
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
                    "AURA — Assistente",
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
                            "Pergunta-me o que quiseres sobre a tua organização financeira.",
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
                content="Fechar",
                on_click=fechar_chat,
            )
        ],
    )

    def abrir_aura(e=None):

        if chat_dialog not in page.overlay:
            page.overlay.append(chat_dialog)

        chat_dialog.open = True
        page.update()

    # ========================================================
    # CARTÃO DA AURA
    # ========================================================

    def aura_card(
        mensagem=None,
        botao_texto="Falar com a AURA",
        on_click=None,
    ):

        if mensagem:
            aura_message.value = mensagem

        return card(
            ft.Row(
                [
                    aura_avatar,
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    texto(
                                        "AURA",
                                        size=17,
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
                            botao(
                                botao_texto,
                                on_click=on_click,
                                bgcolor=NAVY,
                                icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                            ),
                        ],
                        expand=True,
                        spacing=6,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    # ========================================================
    # LOGIN
    # ========================================================

    login_email = ft.TextField(
        label="Email",
        border_color=BORDER,
    )

    login_password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    # ========================================================
    # REGISTO
    # ========================================================

    reg_nome = ft.TextField(
        label="Nome",
        border_color=BORDER,
    )

    reg_email = ft.TextField(
        label="Email",
        border_color=BORDER,
    )

    reg_password = ft.TextField(
        label="Criar password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    login_dialog = None
    registo_dialog = None

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

        if len(reg_password.value) < 6:
            avisar(
                "A password deve ter pelo menos 6 caracteres.",
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

    def abrir_registo():

        login_dialog.open = False
        registo_dialog.open = True
        page.update()

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
                        content="Ainda não tenho conta",
                        on_click=lambda e: abrir_registo(),
                    ),
                ],
                spacing=12,
            ),
        ),
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
                        "Cria a tua conta para começar.",
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

    def abrir_login(e=None):

        if login_dialog not in page.overlay:
            page.overlay.append(login_dialog)

        login_dialog.open = True
        page.update()

    def abrir_registo_principal(e=None):

        if registo_dialog not in page.overlay:
            page.overlay.append(registo_dialog)

        registo_dialog.open = True
        page.update()

    # ========================================================
    # LOGO
    # ========================================================

    def logo():

        return ft.Row(
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
        )

    # ========================================================
    # HEADER LANDING
    # ========================================================

    def header_landing():

        return ft.Container(
            bgcolor=WHITE,
            padding=20,
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        col={
                            "sm": 12,
                            "md": 4,
                            "lg": 4,
                        },
                        content=logo(),
                    ),
                    ft.Container(
                        col={
                            "sm": 12,
                            "md": 8,
                            "lg": 8,
                        },
                        content=ft.Row(
                            [
                                ft.TextButton(
                                    content="Como funciona",
                                ),
                                ft.TextButton(
                                    content="Para empresas",
                                ),
                                ft.TextButton(
                                    content="Ajuda",
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
                            alignment=ft.MainAxisAlignment.END,
                            wrap=True,
                        ),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ========================================================
    # ESCOLHAS HERO
    # ========================================================

    def escolha_hero(emoji, titulo, action):

        return ft.Container(
            content=ft.Row(
                [
                    texto(
                        emoji,
                        size=21,
                    ),
                    ft.Container(
                        content=texto(
                            titulo,
                            size=13,
                            color=WHITE,
                            weight=ft.FontWeight.W_500,
                        ),
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD,
                        color="#64748B",
                        size=17,
                    ),
                ],
            ),
            bgcolor="#162238",
            padding=14,
            border_radius=12,
            on_click=action,
        )

    # ========================================================
    # HERO
    # ========================================================

    def hero():

        return ft.Container(
            bgcolor=NAVY,
            padding=35,
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
                                        abrir_registo_principal,
                                    ),
                                    escolha_hero(
                                        "💳",
                                        "Analisar os meus créditos",
                                        abrir_registo_principal,
                                    ),
                                    escolha_hero(
                                        "🏢",
                                        "Gerir a minha empresa",
                                        abrir_registo_principal,
                                    ),
                                    escolha_hero(
                                        "🎯",
                                        "Criar uma meta de poupança",
                                        abrir_registo_principal,
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

    # ========================================================
    # FEATURE CARD
    # ========================================================

    def feature_card(
        icon,
        titulo,
        descricao,
        cor,
    ):

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
            border=ft.Border.all(
                1,
                BORDER,
            ),
        )

    # ========================================================
    # LANDING PAGE
    # ========================================================

    def mostrar_landing():

        estado["autenticado"] = False
        page.navigation_bar = None
        page.controls.clear()

        landing = ft.Column(
            [
                header_landing(),
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
                                            ft.Icons.FLAG,
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
                        f"© {datetime.now().year} AURA 360 • Gestão Financeira & Empresarial",
                        size=12,
                        color=MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
            spacing=0,
        )

        page.add(
            ft.SafeArea(
                content=landing,
                expand=True,
            )
        )

        page.update()

    # ========================================================
    # MÉTRICAS
    # ========================================================

    def metric_card(
        titulo,
        valor,
        legenda,
        icon,
        cor,
    ):

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
                        color=(
                            GREEN
                            if "+" in legenda
                            else MUTED
                        ),
                    ),
                ],
                spacing=8,
            ),
            bgcolor=WHITE,
            padding=18,
            border_radius=16,
            border=ft.Border.all(
                1,
                BORDER,
            ),
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    dashboard_area = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    def mostrar_dashboard():

        estado["autenticado"] = True

        page.navigation_bar = None
        dashboard_area.controls.clear()

        # HEADER
        dashboard_area.controls.append(
            ft.Container(
                bgcolor=NAVY,
                padding=20,
                content=ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 5,
                            },
                            content=ft.Row(
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
                                ],
                            ),
                        ),

                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 7,
                            },
                            content=ft.Row(
                                [
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
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )

        # SAUDAÇÃO
        dashboard_area.controls.append(
            ft.Container(
                padding=25,
                content=ft.Column(
                    [
                        texto(
                            f"Olá, {user_data['nome']} 👋",
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

        # MÉTRICAS
        dashboard_area.controls.append(
            ft.Container(
                padding=25,
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
                        "Analisei o teu resumo. Tens uma capacidade "
                        "de poupança registada de "
                        f"{user_data['poupanca']:,.2f} € este mês. "
                        "Queres falar comigo?"
                    ),
                    botao_texto="Conversar com a AURA",
                    on_click=abrir_aura,
                ),
            )
        )

        # METAS
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
                    border=ft.Border.all(
                        1,
                        BORDER,
                    ),
                )
            )

        # MOVIMENTOS
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
                                bgcolor=(
                                    GREEN_LIGHT
                                    if positivo
                                    else RED_LIGHT
                                ),
                                border_radius=10,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    (
                                        ft.Icons.ARROW_UPWARD
                                        if positivo
                                        else ft.Icons.ARROW_DOWNWARD
                                    ),
                                    color=(
                                        GREEN
                                        if positivo
                                        else RED
                                    ),
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
                                color=(
                                    GREEN
                                    if positivo
                                    else RED
                                ),
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    padding=10,
                )
            )

        dashboard_area.controls.append(
            ft.Container(
                padding=25,
                content=ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                            },
                            content=card(
                                metas_column,
                            ),
                        ),

                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                            },
                            content=card(
                                movimentos_column,
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            )
        )

        # RODAPÉ
        dashboard_area.controls.append(
            ft.Container(
                padding=20,
                bgcolor=WHITE,
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
                    wrap=True,
                ),
            )
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=dashboard_area,
                expand=True,
            )
        )

        # NAVEGAÇÃO
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
                    icon=ft.Icons.FLAG_OUTLINED,
                    selected_icon=ft.Icons.FLAG,
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

        page.update()

    # ========================================================
    # NAVEGAÇÃO
    # ========================================================

    def dashboard_navigation(e):

        index = e.control.selected_index

        if index == 0:
            mostrar_dashboard()

        elif index == 1:

            mostrar_modulo(
                "💰 Finanças",
                "Centro financeiro pessoal.",
                [
                    "Receitas",
                    "Despesas",
                    "Categorias",
                    "Contas",
                    "Movimentos",
                    "Relatórios",
                ],
                1,
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
                2,
            )

        elif index == 3:

            mostrar_modulo(
                "🏢 Perfil Empresarial",
                "Centro de gestão do teu negócio.",
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
                3,
            )

    # ========================================================
    # MÓDULOS
    # ========================================================

    def mostrar_modulo(
        titulo,
        descricao,
        funcionalidades,
        indice,
    ):

        page.navigation_bar = ft.NavigationBar(
            selected_index=indice,
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
                    icon=ft.Icons.FLAG_OUTLINED,
                    selected_icon=ft.Icons.FLAG,
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
                    border=ft.Border.all(
                        1,
                        BORDER,
                    ),
                )
            )

        controls.append(
            ft.Container(
                padding=25,
                content=aura_card(
                    mensagem=(
                        "Estou contigo neste módulo. "
                        "Se tiveres dúvidas, pergunta-me."
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
    # INICIAR
    # ========================================================

    mostrar_landing()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
    )
