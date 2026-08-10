import os
import sqlite3
import hashlib
import secrets
import asyncio
from datetime import datetime

import flet as ft
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# AURA 360
# Plataforma Financeira + Empresarial
# Versão Web
# ============================================================

load_dotenv()

APP_NAME = "AURA 360"

# ------------------------------------------------------------
# OPENAI
# ------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

openai_client = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------------------------------------------
# CORES
# ------------------------------------------------------------

NAVY = "#08111F"
NAVY_2 = "#101C30"
BLUE = "#2563EB"
BLUE_2 = "#3B82F6"
CYAN = "#06B6D4"
GREEN = "#10B981"
RED = "#EF4444"
ORANGE = "#F59E0B"
PURPLE = "#7C3AED"

WHITE = "#FFFFFF"
BG = "#F5F7FB"
TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"

LIGHT_BLUE = "#EFF6FF"
LIGHT_GREEN = "#ECFDF5"
LIGHT_RED = "#FEF2F2"
LIGHT_PURPLE = "#F5F3FF"
LIGHT_ORANGE = "#FFFBEB"


# ============================================================
# BASE DE DADOS
# ============================================================

DB_FILE = "aura360.db"


def db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    connection = db()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            current REAL DEFAULT 0,
            target REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nif TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Lead'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            price REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings(key, value)
        VALUES ('maintenance', '0')
    """)

    # --------------------------------------------------------
    # CRIAR ADMIN AUTOMATICAMENTE
    # --------------------------------------------------------

    admin_email = os.getenv(
        "AURA_ADMIN_EMAIL",
        "admin@aura360.pt"
    )

    admin_password = os.getenv(
        "AURA_ADMIN_PASSWORD",
        "AURA360-admin-2026!"
    )

    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    )

    if not cursor.fetchone():

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, active, is_admin, created_at)
            VALUES (?, ?, ?, 1, 1, ?)
            """,
            (
                "Administrador",
                admin_email,
                hash_password(admin_password),
                datetime.now().isoformat(),
            ),
        )

    connection.commit()
    connection.close()


# ============================================================
# SEGURANÇA
# ============================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        120000,
    ).hex()

    return f"{salt}${hashed}"


def verify_password(password, stored):

    try:

        salt, hashed = stored.split("$")

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            120000,
        ).hex()

        return secrets.compare_digest(
            calculated,
            hashed,
        )

    except Exception:
        return False


# ============================================================
# UTILITÁRIOS
# ============================================================

def get_setting(key):

    connection = db()

    row = connection.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,)
    ).fetchone()

    connection.close()

    return row["value"] if row else None


def set_setting(key, value):

    connection = db()

    connection.execute(
        """
        INSERT INTO settings(key,value)
        VALUES(?,?)
        ON CONFLICT(key)
        DO UPDATE SET value=excluded.value
        """,
        (key, value)
    )

    connection.commit()
    connection.close()


def is_maintenance():

    return get_setting("maintenance") == "1"


def money(value):

    return f"{value:,.2f} €".replace(
        ",",
        "X"
    ).replace(
        ".",
        ","
    ).replace(
        "X",
        "."
    )


# ============================================================
# AURA AI
# ============================================================

SYSTEM_PROMPT = """
Tu és a AURA, a assistente inteligente da plataforma AURA 360.

A AURA 360 é uma plataforma portuguesa para:
- finanças pessoais;
- receitas e despesas;
- poupança;
- créditos;
- amortização;
- metas financeiras;
- empresas;
- CRM;
- clientes;
- vendas;
- orçamentos;
- inventário;
- tesouraria;
- organização administrativa.

Personalidade:
- profissional;
- simpática;
- clara;
- portuguesa;
- prática;
- nunca arrogante;
- fala em português de Portugal.

Comportamento:
1. Responde diretamente à pergunta.
2. Se for necessário calcular algo, calcula.
3. Explica os cálculos de forma simples.
4. Se faltar informação, pergunta o que falta.
5. Não inventes leis, taxas ou valores oficiais.
6. Em assuntos fiscais, legais ou financeiros de alto impacto,
   deixa claro quando é necessário confirmar informação oficial.
7. Quando fizer sentido, fornece links úteis.
8. Nunca digas que és ChatGPT.
9. Apresenta-te como AURA.
10. A AURA deve sentir-se como uma assistente pessoal que acompanha
    o utilizador dentro da aplicação.

Links oficiais úteis:
Portal das Finanças:
https://www.portaldasfinancas.gov.pt/

ePortugal:
https://eportugal.gov.pt/

AIMA:
https://aima.gov.pt/

Banco de Portugal:
https://www.bportugal.pt/
"""


async def ask_aura(question, context=""):

    if not openai_client:

        return (
            "A AURA está instalada, mas a inteligência artificial "
            "ainda não está configurada neste servidor. "
            "O administrador precisa de definir OPENAI_API_KEY no "
            "ficheiro .env."
        )

    prompt = f"""
CONTEXTO DA APLICAÇÃO:
{context}

PERGUNTA DO UTILIZADOR:
{question}
"""

    try:

        response = await asyncio.to_thread(
            openai_client.responses.create,
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )

        return response.output_text

    except Exception as error:

        print("ERRO OPENAI:", error)

        return (
            "Não consegui contactar o serviço de IA neste momento. "
            "Verifica a configuração da API ou tenta novamente."
        )


# ============================================================
# COMPONENTES UI
# ============================================================

def txt(
    value,
    size=14,
    color=TEXT,
    weight=ft.FontWeight.NORMAL,
    **kwargs
):

    return ft.Text(
        value,
        size=size,
        color=color,
        weight=weight,
        **kwargs
    )


def button(
    label,
    on_click=None,
    bgcolor=BLUE,
    color=WHITE,
    icon=None,
    width=None,
):

    return ft.ElevatedButton(
        content=txt(
            label,
            size=14,
            color=color,
            weight=ft.FontWeight.W_600,
        ),
        bgcolor=bgcolor,
        color=color,
        on_click=on_click,
        icon=icon,
        width=width,
    )


def card(content, padding=22):

    return ft.Container(
        content=content,
        bgcolor=WHITE,
        padding=padding,
        border_radius=18,
        border=ft.Border.all(1, BORDER),
    )


def icon_box(icon, color=BLUE, bgcolor=LIGHT_BLUE):

    return ft.Container(
        width=46,
        height=46,
        bgcolor=bgcolor,
        border_radius=13,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(
            icon,
            color=color,
            size=23,
        ),
    )


# ============================================================
# APLICAÇÃO
# ============================================================

def main(page: ft.Page):

    page.title = APP_NAME
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    init_db()

    state = {
        "user": None,
        "page": "home",
        "profile": "personal",
    }

    # ========================================================
    # SNACKBAR
    # ========================================================

    def notify(message, color=GREEN):

        page.snack_bar = ft.SnackBar(
            content=txt(
                message,
                color=WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=color,
        )

        page.snack_bar.open = True
        page.update()

    # ========================================================
    # AUTH
    # ========================================================

    email_input = ft.TextField(
        label="Email",
        border_color=BORDER,
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    name_input = ft.TextField(
        label="Nome",
        border_color=BORDER,
    )

    reg_email_input = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color=BORDER,
    )

    reg_password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
    )

    login_dialog = ft.AlertDialog(
        modal=True,
    )

    register_dialog = ft.AlertDialog(
        modal=True,
    )

    def close_dialog(dialog):

        dialog.open = False
        page.update()

    def open_dialog(dialog):

        if dialog not in page.overlay:
            page.overlay.append(dialog)

        dialog.open = True
        page.update()

    # ========================================================
    # LOGIN
    # ========================================================

    def login(e):

        email = email_input.value.strip().lower()
        password = password_input.value

        if not email or not password:

            notify(
                "Preenche o email e a password.",
                RED,
            )

            return

        connection = db()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if not user:

            notify(
                "Conta não encontrada.",
                RED,
            )

            return

        if not verify_password(password, user["password"]):

            notify(
                "Email ou password incorretos.",
                RED,
            )

            return

        if not user["active"]:

            notify(
                "Esta conta está temporariamente desativada.",
                RED,
            )

            return

        state["user"] = dict(user)

        login_dialog.open = False

        show_dashboard()

    # ========================================================
    # REGISTO
    # ========================================================

    def register(e):

        name = name_input.value.strip()
        email = reg_email_input.value.strip().lower()
        password = reg_password_input.value

        if not name or not email or not password:

            notify(
                "Preenche todos os campos.",
                RED,
            )

            return

        if len(password) < 8:

            notify(
                "A password deve ter pelo menos 8 caracteres.",
                RED,
            )

            return

        connection = db()

        try:

            cursor = connection.execute(
                """
                INSERT INTO users
                (name,email,password,active,is_admin,created_at)
                VALUES(?,?,?,?,?,?)
                """,
                (
                    name,
                    email,
                    hash_password(password),
                    1,
                    0,
                    datetime.now().isoformat(),
                ),
            )

            connection.commit()

            user_id = cursor.lastrowid

            user = connection.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()

            state["user"] = dict(user)

            register_dialog.open = False

            connection.close()

            show_dashboard()

            notify(
                "Conta criada com sucesso. Bem-vindo à AURA 360!",
                GREEN,
            )

        except sqlite3.IntegrityError:

            connection.close()

            notify(
                "Já existe uma conta com esse email.",
                RED,
            )

    # ========================================================
    # DIALOG LOGIN
    # ========================================================

    login_dialog.title = txt(
        "Entrar na AURA 360",
        size=21,
        weight=ft.FontWeight.BOLD,
    )

    login_dialog.content = ft.Container(
        width=420,
        content=ft.Column(
            [
                txt(
                    "Acede à tua área pessoal ou empresarial.",
                    color=MUTED,
                ),
                email_input,
                password_input,
                button(
                    "Entrar",
                    login,
                    width=220,
                ),
                ft.TextButton(
                    content=txt(
                        "Criar uma conta",
                        color=BLUE,
                    ),
                    on_click=lambda e: open_register(),
                ),
            ],
            spacing=14,
        ),
    )

    login_dialog.actions = [
        ft.TextButton(
            content=txt(
                "Fechar",
                color=MUTED,
            ),
            on_click=lambda e: close_dialog(login_dialog),
        )
    ]

    # ========================================================
    # DIALOG REGISTO
    # ========================================================

    def open_register():

        login_dialog.open = False
        open_dialog(register_dialog)

    register_dialog.title = txt(
        "Criar conta AURA 360",
        size=21,
        weight=ft.FontWeight.BOLD,
    )

    register_dialog.content = ft.Container(
        width=420,
        content=ft.Column(
            [
                txt(
                    "Começa a organizar a tua vida financeira.",
                    color=MUTED,
                ),
                name_input,
                reg_email_input,
                reg_password_input,
                button(
                    "Criar conta",
                    register,
                    width=220,
                ),
            ],
            spacing=14,
        ),
    )

    register_dialog.actions = [
        ft.TextButton(
            content=txt(
                "Fechar",
                color=MUTED,
            ),
            on_click=lambda e: close_dialog(register_dialog),
        )
    ]

    # ========================================================
    # AURA CHAT
    # ========================================================

    chat_messages = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    chat_input = ft.TextField(
        hint_text="Pergunta à AURA...",
        expand=True,
        border_radius=15,
        filled=True,
        fill_color=BG,
        border_color=BORDER,
        on_submit=lambda e: send_chat(),
    )

    chat_dialog = ft.AlertDialog(
        modal=True,
    )

    def add_chat(text_value, user=False):

        if user:

            bubble = ft.Container(
                content=txt(
                    text_value,
                    size=13,
                    color=WHITE,
                ),
                bgcolor=BLUE,
                padding=12,
                border_radius=14,
            )

        else:

            bubble = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                icon_box(
                                    ft.Icons.AUTO_AWESOME,
                                    BLUE,
                                    LIGHT_BLUE,
                                ),
                                txt(
                                    "AURA",
                                    size=12,
                                    color=BLUE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=7,
                        ),
                        txt(
                            text_value,
                            size=13,
                            color=TEXT,
                        ),
                    ],
                    spacing=7,
                ),
                bgcolor=LIGHT_BLUE,
                padding=12,
                border_radius=14,
            )

        chat_messages.controls.append(
            ft.Row(
                [bubble],
                alignment=(
                    ft.MainAxisAlignment.END
                    if user
                    else ft.MainAxisAlignment.START
                ),
            )
        )

        page.update()

    async def send_chat_async(question):

        context = ""

        if state["user"]:

            context = (
                f"Utilizador: {state['user']['name']}. "
                f"Perfil: {state['profile']}. "
                "Está autenticado na AURA 360."
            )

        answer = await ask_aura(
            question,
            context,
        )

        add_chat(
            answer,
            False,
        )

    def send_chat():

        question = chat_input.value.strip()

        if not question:
            return

        chat_input.value = ""

        add_chat(
            question,
            True,
        )

        page.run_task(
            send_chat_async,
            question,
        )

    chat_dialog.title = ft.Row(
        [
            icon_box(
                ft.Icons.AUTO_AWESOME,
                WHITE,
                BLUE,
            ),
            txt(
                "AURA — Assistente Inteligente",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
        ]
    )

    chat_dialog.content = ft.Container(
        width=560,
        height=500,
        content=ft.Column(
            [
                ft.Container(
                    content=txt(
                        "Pergunta-me o que quiseres.",
                        size=12,
                        color=MUTED,
                    ),
                    padding=8,
                ),
                chat_messages,
                ft.Row(
                    [
                        chat_input,
                        ft.IconButton(
                            icon=ft.Icons.SEND,
                            icon_color=BLUE,
                            on_click=lambda e: send_chat(),
                        ),
                    ]
                ),
            ],
            expand=True,
        ),
    )

    chat_dialog.actions = [
        ft.TextButton(
            content=txt(
                "Fechar",
                color=BLUE,
            ),
            on_click=lambda e: close_dialog(chat_dialog),
        )
    ]

    def open_aura(e=None):

        if not chat_messages.controls:

            add_chat(
                "Olá! 👋 Eu sou a AURA. "
                "Estou aqui contigo. "
                "Podes perguntar-me sobre dinheiro, "
                "crédito, poupança, empresa, impostos, "
                "orçamentos ou simplesmente pedir ajuda.",
                False,
            )

        open_dialog(chat_dialog)

    # ========================================================
    # MASCOTE
    # ========================================================

    def aura_mascot():

        return ft.Container(
            width=72,
            height=72,
            bgcolor=NAVY,
            border_radius=36,
            alignment=ft.Alignment.CENTER,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=18,
                color="#40000000",
            ),
            content=ft.Icon(
                ft.Icons.AUTO_AWESOME,
                color="#60A5FA",
                size=34,
            ),
            on_click=open_aura,
            tooltip="Falar com a AURA",
        )

    # ========================================================
    # LANDING
    # ========================================================

    def open_login(e=None):

        open_dialog(login_dialog)

    def open_register_main(e=None):

        open_dialog(register_dialog)

    def feature(
        icon,
        title,
        description,
        color,
        background,
    ):

        return card(
            ft.Column(
                [
                    icon_box(
                        icon,
                        color,
                        background,
                    ),
                    txt(
                        title,
                        size=17,
                        weight=ft.FontWeight.BOLD,
                    ),
                    txt(
                        description,
                        size=13,
                        color=MUTED,
                    ),
                ],
                spacing=10,
            )
        )

    def landing():

        header = ft.Container(
            bgcolor=WHITE,
            padding=ft.Padding(
                left=25,
                right=25,
                top=16,
                bottom=16,
            ),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            icon_box(
                                ft.Icons.AUTO_AWESOME,
                                "#60A5FA",
                                NAVY,
                            ),
                            txt(
                                "AURA",
                                size=23,
                                color=NAVY,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                "360",
                                size=23,
                                color=BLUE,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=6,
                    ),
                    ft.Row(
                        [
                            ft.TextButton(
                                content=txt(
                                    "Como funciona",
                                    color=MUTED,
                                ),
                            ),
                            ft.TextButton(
                                content=txt(
                                    "Para empresas",
                                    color=MUTED,
                                ),
                            ),
                            ft.TextButton(
                                content=txt(
                                    "Ajuda",
                                    color=MUTED,
                                ),
                                on_click=open_aura,
                            ),
                            button(
                                "Entrar",
                                open_login,
                                bgcolor=WHITE,
                                color=NAVY,
                            ),
                            button(
                                "Criar conta",
                                open_register_main,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        hero = ft.Container(
            bgcolor=NAVY,
            padding=ft.Padding(
                left=35,
                right=35,
                top=65,
                bottom=65,
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
                                    content=txt(
                                        "INTELIGÊNCIA PARA A TUA VIDA FINANCEIRA",
                                        size=11,
                                        color="#93C5FD",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor="#172554",
                                    padding=10,
                                    border_radius=20,
                                ),
                                txt(
                                    "O teu dinheiro.\n"
                                    "A tua empresa.\n"
                                    "Uma inteligência contigo.",
                                    size=44,
                                    color=WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                txt(
                                    "AURA 360 junta finanças pessoais, "
                                    "crédito, poupança e gestão empresarial "
                                    "numa única plataforma inteligente.",
                                    size=17,
                                    color="#CBD5E1",
                                ),
                                ft.Row(
                                    [
                                        button(
                                            "Começar gratuitamente",
                                            open_register_main,
                                            bgcolor=WHITE,
                                            color=NAVY,
                                        ),
                                        button(
                                            "Falar com a AURA",
                                            open_aura,
                                            bgcolor=NAVY_2,
                                            color=WHITE,
                                            icon=ft.Icons.AUTO_AWESOME,
                                        ),
                                    ],
                                    wrap=True,
                                ),
                                txt(
                                    "A AURA acompanha-te dentro da aplicação.",
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
                            bgcolor=NAVY_2,
                            padding=25,
                            border_radius=24,
                            border=ft.Border.all(
                                1,
                                "#24324A",
                            ),
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            aura_mascot(),
                                            ft.Column(
                                                [
                                                    txt(
                                                        "Olá 👋",
                                                        size=20,
                                                        color=WHITE,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    txt(
                                                        "Eu sou a AURA",
                                                        size=13,
                                                        color="#93C5FD",
                                                    ),
                                                ],
                                                spacing=3,
                                            ),
                                        ],
                                    ),
                                    txt(
                                        "Por onde queres começar?",
                                        size=21,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    hero_action(
                                        "💰",
                                        "Organizar as minhas finanças",
                                    ),
                                    hero_action(
                                        "💳",
                                        "Analisar os meus créditos",
                                    ),
                                    hero_action(
                                        "🎯",
                                        "Criar uma meta de poupança",
                                    ),
                                    hero_action(
                                        "🏢",
                                        "Gerir a minha empresa",
                                    ),
                                ],
                                spacing=12,
                            ),
                        ),
                    ),
                ],
                spacing=30,
            ),
        )

        features = ft.Container(
            padding=30,
            content=ft.Column(
                [
                    txt(
                        "Tudo o que precisas num só lugar",
                        size=29,
                        weight=ft.FontWeight.BOLD,
                    ),
                    txt(
                        "Uma plataforma pensada para acompanhar decisões reais.",
                        size=14,
                        color=MUTED,
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=feature(
                                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                                    "Finanças",
                                    "Receitas, despesas, contas e relatórios.",
                                    BLUE,
                                    LIGHT_BLUE,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=feature(
                                    ft.Icons.CREDIT_CARD,
                                    "Crédito",
                                    "Prestação, taxa de esforço e amortização.",
                                    GREEN,
                                    LIGHT_GREEN,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=feature(
                                    ft.Icons.TRENDING_UP,
                                    "Poupança",
                                    "Metas, progresso e planeamento.",
                                    PURPLE,
                                    LIGHT_PURPLE,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=feature(
                                    ft.Icons.BUSINESS,
                                    "Empresas",
                                    "Clientes, vendas, stock e tesouraria.",
                                    ORANGE,
                                    LIGHT_ORANGE,
                                ),
                            ),
                        ],
                        spacing=15,
                    ),
                ],
                spacing=16,
            ),
        )

        aura_section = ft.Container(
            padding=30,
            content=card(
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 3,
                            },
                            content=ft.Column(
                                [
                                    aura_mascot(),
                                    txt(
                                        "AURA AI",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "A tua inteligência dentro da plataforma.",
                                        size=13,
                                        color=MUTED,
                                    ),
                                ]
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 9,
                            },
                            content=ft.Column(
                                [
                                    txt(
                                        "Não sabes por onde começar?",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "Pergunta à AURA. "
                                        "Ela pode explicar, calcular, "
                                        "organizar e orientar-te.",
                                        size=15,
                                        color=MUTED,
                                    ),
                                    button(
                                        "Conversar com a AURA",
                                        open_aura,
                                        bgcolor=NAVY,
                                        icon=ft.Icons.AUTO_AWESOME,
                                    ),
                                ],
                                spacing=12,
                            ),
                        ),
                    ],
                    spacing=20,
                )
            ),
        )

        footer = ft.Container(
            bgcolor=NAVY,
            padding=35,
            content=ft.Column(
                [
                    txt(
                        "Uma plataforma. Dois mundos.",
                        size=28,
                        color=WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    txt(
                        "Finanças pessoais e gestão empresarial "
                        "num único ecossistema.",
                        size=14,
                        color="#CBD5E1",
                    ),
                    button(
                        "Começar agora",
                        open_register_main,
                        bgcolor=WHITE,
                        color=NAVY,
                    ),
                ],
                spacing=15,
            ),
        )

        return ft.Stack(
            [
                ft.Column(
                    [
                        header,
                        hero,
                        features,
                        aura_section,
                        footer,
                        ft.Container(
                            padding=25,
                            content=txt(
                                "© 2026 AURA 360",
                                size=12,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                ft.Container(
                    right=25,
                    bottom=25,
                    content=aura_mascot(),
                ),
            ],
            expand=True,
        )

    def hero_action(emoji, label):

        def action(e):

            open_register_main()

            notify(
                "Cria uma conta para começar a utilizar esta área.",
                BLUE,
            )

        return ft.Container(
            bgcolor="#162238",
            padding=14,
            border_radius=13,
            on_click=action,
            content=ft.Row(
                [
                    txt(
                        emoji,
                        size=20,
                    ),
                    txt(
                        label,
                        size=13,
                        color=WHITE,
                        weight=ft.FontWeight.W_500,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD,
                        color="#64748B",
                        size=17,
                    ),
                ]
            ),
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    dashboard = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    def stat_card(title, value, subtitle, icon, color):

        return card(
            ft.Column(
                [
                    ft.Row(
                        [
                            txt(
                                title,
                                size=12,
                                color=MUTED,
                                weight=ft.FontWeight.W_600,
                            ),
                            icon_box(
                                icon,
                                color,
                                LIGHT_BLUE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    txt(
                        value,
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                    txt(
                        subtitle,
                        size=12,
                        color=MUTED,
                    ),
                ],
                spacing=8,
            )
        )

    def get_financial_data():

        if not state["user"]:
            return 0, 0

        connection = db()

        rows = connection.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE WHEN type='income'
                    THEN amount ELSE 0 END
                ),0) AS income,

                COALESCE(SUM(
                    CASE WHEN type='expense'
                    THEN amount ELSE 0 END
                ),0) AS expense

            FROM transactions
            WHERE user_id = ?
            """,
            (state["user"]["id"],)
        ).fetchone()

        connection.close()

        return rows["income"], rows["expense"]

    def add_transaction_dialog():

        description = ft.TextField(
            label="Descrição",
            border_color=BORDER,
        )

        category = ft.TextField(
            label="Categoria",
            border_color=BORDER,
        )

        amount = ft.TextField(
            label="Valor (€)",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=BORDER,
        )

        type_dropdown = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("income", "Receita"),
                ft.dropdown.Option("expense", "Despesa"),
            ],
            value="expense",
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=txt(
                "Adicionar movimento",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
        )

        def save(e):

            try:

                value = float(
                    amount.value.replace(",", ".")
                )

                connection = db()

                connection.execute(
                    """
                    INSERT INTO transactions
                    (user_id,description,category,amount,type,created_at)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (
                        state["user"]["id"],
                        description.value,
                        category.value,
                        value,
                        type_dropdown.value,
                        datetime.now().isoformat(),
                    ),
                )

                connection.commit()
                connection.close()

                dialog.open = False

                show_dashboard()

                notify(
                    "Movimento guardado.",
                    GREEN,
                )

            except:

                notify(
                    "Introduz um valor válido.",
                    RED,
                )

        dialog.content = ft.Container(
            width=400,
            content=ft.Column(
                [
                    description,
                    category,
                    amount,
                    type_dropdown,
                    button(
                        "Guardar",
                        save,
                    ),
                ],
                spacing=12,
            ),
        )

        open_dialog(dialog)

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard():

        income, expense = get_financial_data()

        balance = income - expense

        dashboard.controls.clear()

        topbar = ft.Container(
            bgcolor=NAVY,
            padding=18,
            content=ft.Row(
                [
                    ft.Row(
                        [
                            icon_box(
                                ft.Icons.AUTO_AWESOME,
                                "#60A5FA",
                                NAVY_2,
                            ),
                            txt(
                                "AURA 360",
                                size=20,
                                color=WHITE,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            button(
                                "AURA AI",
                                open_aura,
                                bgcolor=NAVY_2,
                                color=WHITE,
                                icon=ft.Icons.AUTO_AWESOME,
                            ),
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        content=txt(
                                            "Sair",
                                            color=TEXT,
                                        ),
                                        on_click=lambda e: logout(),
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        dashboard.controls.append(topbar)

        dashboard.controls.append(
            ft.Container(
                padding=25,
                content=ft.Column(
                    [
                        txt(
                            f"Olá, {state['user']['name']} 👋",
                            size=29,
                            weight=ft.FontWeight.BOLD,
                        ),
                        txt(
                            "Aqui tens o centro de controlo da AURA 360.",
                            size=14,
                            color=MUTED,
                        ),
                    ]
                ),
            )
        )

        dashboard.controls.append(
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
                            content=stat_card(
                                "Saldo",
                                money(balance),
                                "Resultado registado",
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
                            content=stat_card(
                                "Receitas",
                                money(income),
                                "Total registado",
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
                            content=stat_card(
                                "Despesas",
                                money(expense),
                                "Total registado",
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
                            content=stat_card(
                                "Perfil",
                                state["profile"],
                                "Área atual",
                                ft.Icons.PERSON,
                                PURPLE,
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            )
        )

        dashboard.controls.append(
            ft.Container(
                padding=ft.Padding(
                    left=25,
                    right=25,
                    top=0,
                    bottom=20,
                ),
                content=card(
                    ft.Row(
                        [
                            aura_mascot(),
                            ft.Column(
                                [
                                    txt(
                                        "AURA está contigo",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "Precisas de ajuda? "
                                        "Pergunta diretamente à AURA.",
                                        size=13,
                                        color=MUTED,
                                    ),
                                    button(
                                        "Falar com a AURA",
                                        open_aura,
                                        bgcolor=NAVY,
                                        icon=ft.Icons.AUTO_AWESOME,
                                    ),
                                ],
                                spacing=7,
                                expand=True,
                            ),
                        ],
                        spacing=15,
                    )
                ),
            )
        )

        dashboard.controls.append(
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
                            },
                            content=card(
                                ft.Column(
                                    [
                                        txt(
                                            "Finanças pessoais",
                                            size=19,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            "Organiza receitas, despesas "
                                            "e movimentos.",
                                            size=13,
                                            color=MUTED,
                                        ),
                                        button(
                                            "Abrir Finanças",
                                            lambda e: show_module(
                                                "Finanças"
                                            ),
                                            icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                                        ),
                                    ],
                                    spacing=12,
                                )
                            ),
                        ),
                        ft.Container(
                            col={
                                "sm": 12,
                                "md": 6,
                            },
                            content=card(
                                ft.Column(
                                    [
                                        txt(
                                            "Perfil Empresarial",
                                            size=19,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            "CRM, clientes, vendas, "
                                            "stock e tesouraria.",
                                            size=13,
                                            color=MUTED,
                                        ),
                                        button(
                                            "Abrir Empresa",
                                            lambda e: show_module(
                                                "Empresa"
                                            ),
                                            bgcolor=ORANGE,
                                            icon=ft.Icons.BUSINESS,
                                        ),
                                    ],
                                    spacing=12,
                                )
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            )
        )

        dashboard.controls.append(
            ft.Container(
                padding=25,
                content=button(
                    "＋ Adicionar movimento",
                    add_transaction_dialog,
                    icon=ft.Icons.ADD,
                ),
            )
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=dashboard,
                expand=True,
            )
        )

        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
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
            on_change=navigation_change,
        )

        page.update()

    # ========================================================
    # MÓDULOS
    # ========================================================

    def show_module(module):

        dashboard.controls.clear()

        title = module

        if module == "Finanças":

            description = (
                "Centro financeiro pessoal."
            )

            items = [
                "Receitas",
                "Despesas",
                "Contas",
                "Movimentos",
                "Relatórios",
                "Análise financeira",
                "Taxa de esforço",
            ]

            icon = ft.Icons.ACCOUNT_BALANCE_WALLET

        elif module == "Metas":

            description = (
                "Objetivos de poupança e planeamento."
            )

            items = [
                "Fundo de emergência",
                "Férias",
                "Investimentos",
                "PPR",
                "Objetivos personalizados",
            ]

            icon = ft.Icons.TARGET

        else:

            description = (
                "Centro de gestão empresarial."
            )

            items = [
                "CRM",
                "Clientes",
                "Vendas",
                "Orçamentos",
                "POS",
                "Inventário FIFO",
                "Tesouraria",
                "Impostos",
            ]

            icon = ft.Icons.BUSINESS

        dashboard.controls.append(
            ft.Container(
                bgcolor=NAVY,
                padding=22,
                content=ft.Row(
                    [
                        ft.Icon(
                            icon,
                            color=WHITE,
                        ),
                        txt(
                            title,
                            size=23,
                            color=WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            expand=True,
                        ),
                        button(
                            "AURA AI",
                            open_aura,
                            bgcolor=NAVY_2,
                            color=WHITE,
                            icon=ft.Icons.AUTO_AWESOME,
                        ),
                    ]
                ),
            )
        )

        dashboard.controls.append(
            ft.Container(
                padding=25,
                content=ft.Column(
                    [
                        txt(
                            title,
                            size=30,
                            weight=ft.FontWeight.BOLD,
                        ),
                        txt(
                            description,
                            size=14,
                            color=MUTED,
                        ),
                    ]
                ),
            )
        )

        for item in items:

            dashboard.controls.append(
                ft.Container(
                    margin=ft.Margin(
                        left=25,
                        right=25,
                        top=5,
                        bottom=5,
                    ),
                    content=ft.ListTile(
                        leading=icon_box(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            BLUE,
                            LIGHT_BLUE,
                        ),
                        title=txt(
                            item,
                            size=14,
                            weight=ft.FontWeight.W_500,
                        ),
                        subtitle=txt(
                            "Abrir esta funcionalidade",
                            size=11,
                            color=MUTED,
                        ),
                        trailing=ft.Icon(
                            ft.Icons.ARROW_FORWARD_IOS,
                            size=16,
                            color=MUTED,
                        ),
                        on_click=lambda e, item=item:
                            restricted_feature(item),
                    ),
                    bgcolor=WHITE,
                    border_radius=12,
                    border=ft.Border.all(
                        1,
                        BORDER,
                    ),
                )
            )

        dashboard.controls.append(
            ft.Container(
                padding=25,
                content=card(
                    ft.Row(
                        [
                            aura_mascot(),
                            ft.Column(
                                [
                                    txt(
                                        "Precisas de ajuda?",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "A AURA pode explicar este módulo.",
                                        size=13,
                                        color=MUTED,
                                    ),
                                    button(
                                        "Perguntar à AURA",
                                        open_aura,
                                        bgcolor=NAVY,
                                        icon=ft.Icons.AUTO_AWESOME,
                                    ),
                                ],
                                expand=True,
                            ),
                        ]
                    )
                ),
            )
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=dashboard,
                expand=True,
            )
        )

        page.update()

    def restricted_feature(name):

        notify(
            f"Funcionalidade '{name}' selecionada. "
            "A AURA pode acompanhar-te nesta área.",
            BLUE,
        )

        question = (
            f"Explica-me como funciona a funcionalidade "
            f"{name} da AURA 360."
        )

        add_chat(
            question,
            True,
        )

        page.run_task(
            send_chat_async,
            question,
        )

    # ========================================================
    # ADMIN
    # ========================================================

    def show_admin():

        if not state["user"] or not state["user"]["is_admin"]:

            notify(
                "Acesso reservado ao administrador.",
                RED,
            )

            return

        connection = db()

        total = connection.execute(
            "SELECT COUNT(*) AS n FROM users"
        ).fetchone()["n"]

        active = connection.execute(
            "SELECT COUNT(*) AS n FROM users WHERE active=1"
        ).fetchone()["n"]

        inactive = connection.execute(
            "SELECT COUNT(*) AS n FROM users WHERE active=0"
        ).fetchone()["n"]

        users = connection.execute(
            """
            SELECT id,name,email,active,is_admin,created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        admin_controls = [
            ft.Container(
                bgcolor=NAVY,
                padding=25,
                content=ft.Column(
                    [
                        txt(
                            "AURA 360 — Administração",
                            size=25,
                            color=WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        txt(
                            "Controlo central da plataforma.",
                            size=13,
                            color="#CBD5E1",
                        ),
                    ]
                ),
            ),
            ft.Container(
                padding=25,
                content=ft.ResponsiveRow(
                    [
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=stat_card(
                                "Utilizadores",
                                str(total),
                                "Total",
                                ft.Icons.PEOPLE,
                                BLUE,
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=stat_card(
                                "Ativos",
                                str(active),
                                "Com acesso",
                                ft.Icons.CHECK_CIRCLE,
                                GREEN,
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=stat_card(
                                "Bloqueados",
                                str(inactive),
                                "Sem acesso",
                                ft.Icons.BLOCK,
                                RED,
                            ),
                        ),
                    ],
                    spacing=15,
                ),
            ),
        ]

        maintenance = is_maintenance()

        def toggle_maintenance(e):

            set_setting(
                "maintenance",
                "0" if maintenance else "1",
            )

            notify(
                "Modo manutenção atualizado.",
                ORANGE,
            )

            show_admin()

        admin_controls.append(
            ft.Container(
                padding=25,
                content=card(
                    ft.Column(
                        [
                            txt(
                                "Estado da plataforma",
                                size=19,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                (
                                    "MANUTENÇÃO ATIVA"
                                    if maintenance
                                    else
                                    "PLATAFORMA ONLINE"
                                ),
                                size=14,
                                color=RED if maintenance else GREEN,
                                weight=ft.FontWeight.BOLD,
                            ),
                            button(
                                (
                                    "Desativar manutenção"
                                    if maintenance
                                    else
                                    "Ativar manutenção"
                                ),
                                toggle_maintenance,
                                bgcolor=RED if not maintenance else GREEN,
                            ),
                        ],
                        spacing=10,
                    )
                ),
            )
        )

        user_column = ft.Column(
            spacing=8,
        )

        for user in users:

            def toggle_user(e, user_id=user["id"], current=user["active"]):

                if user_id == state["user"]["id"]:

                    notify(
                        "Não podes bloquear a tua própria conta.",
                        RED,
                    )

                    return

                connection = db()

                connection.execute(
                    """
                    UPDATE users
                    SET active = ?
                    WHERE id = ?
                    """,
                    (
                        0 if current else 1,
                        user_id,
                    ),
                )

                connection.commit()
                connection.close()

                show_admin()

            user_column.controls.append(
                ft.Container(
                    bgcolor=WHITE,
                    padding=15,
                    border_radius=12,
                    border=ft.Border.all(
                        1,
                        BORDER,
                    ),
                    content=ft.Row(
                        [
                            icon_box(
                                ft.Icons.PERSON,
                                BLUE,
                                LIGHT_BLUE,
                            ),
                            ft.Column(
                                [
                                    txt(
                                        user["name"],
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        user["email"],
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                                expand=True,
                            ),
                            txt(
                                (
                                    "ADMIN"
                                    if user["is_admin"]
                                    else
                                    (
                                        "ATIVO"
                                        if user["active"]
                                        else
                                        "BLOQUEADO"
                                    )
                                ),
                                size=11,
                                color=(
                                    PURPLE
                                    if user["is_admin"]
                                    else
                                    (
                                        GREEN
                                        if user["active"]
                                        else
                                        RED
                                    )
                                ),
                                weight=ft.FontWeight.BOLD,
                            ),
                            (
                                ft.IconButton(
                                    icon=(
                                        ft.Icons.BLOCK
                                        if user["active"]
                                        else
                                        ft.Icons.CHECK
                                    ),
                                    icon_color=(
                                        RED
                                        if user["active"]
                                        else
                                        GREEN
                                    ),
                                    on_click=toggle_user,
                                )
                                if not user["is_admin"]
                                else
                                ft.Container(width=48)
                            ),
                        ]
                    ),
                )
            )

        admin_controls.append(
            ft.Container(
                padding=25,
                content=card(
                    ft.Column(
                        [
                            txt(
                                "Utilizadores",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            user_column,
                        ],
                        spacing=12,
                    )
                ),
            )
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    admin_controls,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        page.update()

    # ========================================================
    # NAVEGAÇÃO
    # ========================================================

    def navigation_change(e):

        index = e.control.selected_index

        if index == 0:

            show_dashboard()

        elif index == 1:

            show_module("Finanças")

        elif index == 2:

            show_module("Metas")

        elif index == 3:

            show_module("Empresa")

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout():

        state["user"] = None
        state["profile"] = "personal"

        page.navigation_bar = None

        show_landing()

    # ========================================================
    # LANDING
    # ========================================================

    def show_landing():

        page.navigation_bar = None

        page.controls.clear()

        if is_maintenance():

            page.add(
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=NAVY,
                    content=ft.Column(
                        [
                            icon_box(
                                ft.Icons.BUILD,
                                ORANGE,
                                NAVY_2,
                            ),
                            txt(
                                "AURA 360",
                                size=32,
                                color=WHITE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                "Estamos a realizar manutenção.",
                                size=17,
                                color="#CBD5E1",
                            ),
                            txt(
                                "Voltaremos em breve.",
                                size=13,
                                color="#94A3B8",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                )
            )

            page.update()

            return

        page.add(
            landing()
        )

        page.update()

    # ========================================================
    # INÍCIO
    # ========================================================

    show_landing()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
    )
