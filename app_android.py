import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional

import flet as ft
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ============================================================
# AURA 360
# Plataforma Financeira + Empresarial
# Versão Web
# ============================================================

load_dotenv()

APP_NAME = "AURA 360"

DB_FILE = os.getenv("AURA_DB", "aura360.db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

ADMIN_EMAIL = os.getenv(
    "AURA_ADMIN_EMAIL",
    "admin@aura360.pt",
).strip().lower()

ADMIN_PASSWORD = os.getenv(
    "AURA_ADMIN_PASSWORD",
    "MUDA_ESTA_PASSWORD",
)

# ------------------------------------------------------------
# CORES
# ------------------------------------------------------------

NAVY = "#08111F"
NAVY_2 = "#101D31"
NAVY_3 = "#17263D"

BLUE = "#2563EB"
BLUE_2 = "#3B82F6"
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
BG = "#F5F7FB"

TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"


# ============================================================
# BASE DE DADOS
# ============================================================

def db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = db()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            active INTEGER DEFAULT 1,
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
            current_amount REAL DEFAULT 0,
            target_amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            tax_number TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Lead',
            created_at TEXT NOT NULL
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
        VALUES('maintenance', '0')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings(key, value)
        VALUES('app_name', 'AURA 360')
    """)

    connection.commit()
    connection.close()


# ============================================================
# SEGURANÇA
# ============================================================

def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120000,
    )

    return (
        salt.hex()
        + ":"
        + digest.hex()
    )


def verify_password(password: str, stored: str) -> bool:

    try:

        salt_hex, digest_hex = stored.split(":")

        salt = bytes.fromhex(salt_hex)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120000,
        )

        return secrets.compare_digest(
            digest.hex(),
            digest_hex,
        )

    except Exception:
        return False


# ============================================================
# DADOS / UTILITÁRIOS
# ============================================================

def now():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_setting(key):

    connection = db()

    row = connection.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,),
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
        (key, str(value)),
    )

    connection.commit()
    connection.close()


def money(value):
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def users_count():

    connection = db()

    value = connection.execute(
        "SELECT COUNT(*) AS total FROM users"
    ).fetchone()["total"]

    connection.close()

    return value


def active_users_count():

    connection = db()

    value = connection.execute(
        "SELECT COUNT(*) AS total FROM users WHERE active=1"
    ).fetchone()["total"]

    connection.close()

    return value


def get_user(email):

    connection = db()

    row = connection.execute(
        "SELECT * FROM users WHERE email=?",
        (email.lower().strip(),),
    ).fetchone()

    connection.close()

    return row


def create_user(name, email, password):

    connection = db()

    try:

        cursor = connection.execute(
            """
            INSERT INTO users
            (name,email,password_hash,role,active,created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (
                name.strip(),
                email.lower().strip(),
                hash_password(password),
                "user",
                1,
                now(),
            ),
        )

        user_id = cursor.lastrowid

        # Dados iniciais
        connection.execute(
            """
            INSERT INTO goals
            (user_id,name,current_amount,target_amount,created_at)
            VALUES(?,?,?,?,?)
            """,
            (
                user_id,
                "Fundo de Emergência",
                0,
                5000,
                now(),
            ),
        )

        connection.commit()

        return True, user_id

    except sqlite3.IntegrityError:

        return False, None

    finally:

        connection.close()


# ============================================================
# AURA AI
# ============================================================

SYSTEM_PROMPT = """
És a AURA, assistente inteligente da plataforma AURA 360.

A AURA 360 é uma plataforma portuguesa de organização
financeira pessoal e gestão empresarial.

Fala sempre em português de Portugal.

Tens de ser:
- simpática;
- clara;
- profissional;
- prática;
- humana;
- curta quando a pergunta é simples;
- detalhada quando necessário.

Podes ajudar com:
- orçamento familiar;
- receitas;
- despesas;
- poupança;
- metas;
- crédito;
- taxa de esforço;
- amortizações;
- organização financeira;
- empresas;
- clientes;
- vendas;
- orçamentos;
- tesouraria;
- inventário;
- produtividade;
- preparação de perguntas para contabilista ou banco.

Quando forem necessários cálculos, faz os cálculos.

Quando a questão depender de legislação, impostos,
taxas bancárias ou informação oficial atualizada,
não inventes.

Explica que a informação deve ser confirmada
em fontes oficiais ou com um profissional.

Não te apresentes como contabilista, advogado,
consultor financeiro certificado ou banco.

Se o utilizador perguntar sobre uma funcionalidade
da AURA 360, explica como a pode utilizar.

Se o utilizador ainda não estiver autenticado,
podes explicar a funcionalidade mas incentiva-o
a criar uma conta.

És a assistente permanente do utilizador.
"""


def aura_ai(pergunta, user=None):

    pergunta = pergunta.strip()

    if not pergunta:
        return "Diz-me o que precisas e eu ajudo-te. 😊"

    if not OPENAI_API_KEY or OpenAI is None:

        return aura_fallback(pergunta)

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        context = ""

        if user:

            context = f"""
Utilizador autenticado:
Nome: {user['name']}
Email: {user['email']}
Perfil: {user['role']}
"""

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=SYSTEM_PROMPT + context,
            input=pergunta,
        )

        text = getattr(
            response,
            "output_text",
            None,
        )

        if text:
            return text.strip()

        return aura_fallback(pergunta)

    except Exception as error:

        print("AURA AI ERROR:", error)

        return (
            "Neste momento não consegui contactar o "
            "motor de inteligência artificial. "
            "A plataforma continua disponível. "
            "Confirma a configuração da OPENAI_API_KEY."
        )


def aura_fallback(pergunta):

    p = pergunta.lower()

    if "saldo" in p:
        return (
            "Posso ajudar-te a controlar o saldo, "
            "receitas e despesas. Depois de criares "
            "uma conta podes registar os teus movimentos "
            "e acompanhar a evolução."
        )

    if "credito" in p or "crédito" in p:

        return (
            "Posso calcular a tua taxa de esforço e "
            "simular uma amortização. Para isso preciso "
            "do rendimento líquido mensal, prestações "
            "e saldo dos créditos."
        )

    if "poup" in p:

        return (
            "Podemos criar uma meta de poupança e "
            "calcular quanto precisas de colocar de lado "
            "por mês para a atingir."
        )

    if "empresa" in p:

        return (
            "Na área empresarial podes organizar clientes, "
            "vendas, orçamentos e tesouraria."
        )

    if "irs" in p or "imposto" in p:

        return (
            "Posso ajudar-te a organizar informação fiscal "
            "e explicar conceitos, mas valores e regras "
            "atuais devem ser confirmados nas fontes oficiais."
        )

    return (
        "Sou a AURA. 😊 Posso ajudar-te com dinheiro, "
        "poupança, crédito, empresa, clientes, vendas, "
        "orçamentos, impostos e organização financeira."
    )


# ============================================================
# APLICAÇÃO
# ============================================================

def main(page: ft.Page):

    init_database()

    page.title = APP_NAME
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # --------------------------------------------------------
    # ESTADO DA SESSÃO
    # --------------------------------------------------------

    session = {
        "user": None,
        "screen": "landing",
    }

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def txt(
        value,
        size=14,
        color=TEXT,
        weight=ft.FontWeight.NORMAL,
        **kwargs,
    ):

        return ft.Text(
            value=value,
            size=size,
            color=color,
            weight=weight,
            **kwargs,
        )

    def button(
        label,
        on_click=None,
        bgcolor=BLUE,
        color=WHITE,
        icon=None,
        width=None,
    ):

        kwargs = {
            "content": txt(
                label,
                size=14,
                color=color,
                weight=ft.FontWeight.BOLD,
            ),
            "on_click": on_click,
            "bgcolor": bgcolor,
            "color": color,
        }

        if icon is not None:
            kwargs["icon"] = icon

        if width is not None:
            kwargs["width"] = width

        return ft.Button(**kwargs)

    def card(content, padding=20):

        return ft.Container(
            content=content,
            bgcolor=WHITE,
            padding=padding,
            border_radius=18,
            border=ft.Border.all(
                1,
                BORDER,
            ),
        )

    def snack(message, color=BLUE):

        page.show_dialog(
            ft.SnackBar(
                content=txt(
                    message,
                    color=WHITE,
                ),
                bgcolor=color,
            )
        )

    # --------------------------------------------------------
    # MASCOTE
    # --------------------------------------------------------

    aura_face = ft.Container(
        width=72,
        height=72,
        bgcolor=BLUE,
        border_radius=36,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color="#402563EB",
        ),
        content=ft.Icon(
            ft.Icons.AUTO_AWESOME,
            color=WHITE,
            size=36,
        ),
    )

    def mascot_small():

        return ft.Container(
            width=48,
            height=48,
            bgcolor=BLUE,
            border_radius=24,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(
                ft.Icons.AUTO_AWESOME,
                color=WHITE,
                size=25,
            ),
        )

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    chat_list = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    chat_input = ft.TextField(
        hint_text="Pergunta à AURA...",
        expand=True,
        border_radius=16,
        border_color=BORDER,
        filled=True,
        fill_color=BG,
        on_submit=lambda e: send_chat(),
    )

    chat_dialog = None

    def add_chat_user(message):

        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=txt(
                            message,
                            color=WHITE,
                            size=13,
                        ),
                        bgcolor=BLUE,
                        padding=12,
                        border_radius=16,
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )

    def add_chat_aura(message):

        chat_list.controls.append(
            ft.Row(
                [
                    mascot_small(),
                    ft.Container(
                        content=txt(
                            message,
                            size=13,
                            color=TEXT,
                        ),
                        bgcolor=BLUE_LIGHT,
                        padding=12,
                        border_radius=16,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    def send_chat():

        message = (
            chat_input.value or ""
        ).strip()

        if not message:
            return

        add_chat_user(message)

        chat_input.value = ""

        page.update()

        answer = aura_ai(
            message,
            session["user"],
        )

        add_chat_aura(answer)

        page.update()

    def close_chat(e=None):

        if chat_dialog:
            chat_dialog.open = False
            page.update()

    def open_chat(e=None):

        nonlocal chat_dialog

        if chat_dialog is None:

            chat_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    [
                        mascot_small(),
                        txt(
                            "AURA AI",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
                content=ft.Container(
                    width=560,
                    height=520,
                    content=ft.Column(
                        [
                            ft.Container(
                                content=txt(
                                    "Olá! Sou a AURA. "
                                    "Pergunta-me o que quiseres.",
                                    size=13,
                                    color=MUTED,
                                ),
                                padding=10,
                            ),
                            chat_list,
                            ft.Row(
                                [
                                    chat_input,
                                    ft.IconButton(
                                        icon=ft.Icons.SEND,
                                        icon_color=BLUE,
                                        on_click=lambda e: send_chat(),
                                    ),
                                ],
                            ),
                        ],
                        expand=True,
                    ),
                ),
                actions=[
                    ft.Button(
                        content="Fechar",
                        on_click=close_chat,
                    )
                ],
            )

            page.overlay.append(
                chat_dialog
            )

        chat_dialog.open = True
        page.update()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    login_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    login_password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
    )

    login_dialog = None

    def close_login():

        if login_dialog:
            login_dialog.open = False
            page.update()

    def login():

        email = (
            login_email.value or ""
        ).strip().lower()

        password = (
            login_password.value or ""
        )

        if not email or not password:

            snack(
                "Preenche o email e a password.",
                RED,
            )

            return

        user = get_user(email)

        if not user:

            snack(
                "Conta não encontrada.",
                RED,
            )

            return

        if not user["active"]:

            snack(
                "Esta conta encontra-se bloqueada.",
                RED,
            )

            return

        if not verify_password(
            password,
            user["password_hash"],
        ):

            snack(
                "Email ou password incorretos.",
                RED,
            )

            return

        session["user"] = user

        close_login()

        show_dashboard()

    def open_login(e=None):

        nonlocal login_dialog

        if login_dialog is None:

            login_dialog = ft.AlertDialog(
                modal=True,
                title=txt(
                    "Entrar na AURA 360",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                ),
                content=ft.Container(
                    width=430,
                    content=ft.Column(
                        [
                            txt(
                                "Entra na tua conta.",
                                color=MUTED,
                            ),
                            login_email,
                            login_password,
                            button(
                                "Entrar",
                                on_click=lambda e: login(),
                                width=200,
                            ),
                        ],
                        spacing=14,
                    ),
                ),
            )

            page.overlay.append(
                login_dialog
            )

        login_dialog.open = True

        page.update()

    # --------------------------------------------------------
    # REGISTO
    # --------------------------------------------------------

    register_name = ft.TextField(
        label="Nome",
    )

    register_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    register_password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
    )

    register_dialog = None

    def create_account():

        name = (
            register_name.value or ""
        ).strip()

        email = (
            register_email.value or ""
        ).strip().lower()

        password = (
            register_password.value or ""
        )

        if not name or not email or not password:

            snack(
                "Preenche todos os campos.",
                RED,
            )

            return

        if len(password) < 6:

            snack(
                "A password deve ter pelo menos 6 caracteres.",
                RED,
            )

            return

        ok, user_id = create_user(
            name,
            email,
            password,
        )

        if not ok:

            snack(
                "Já existe uma conta com esse email.",
                RED,
            )

            return

        user = get_user(email)

        session["user"] = user

        if register_dialog:
            register_dialog.open = False

        show_dashboard()

        snack(
            "Conta criada com sucesso. Bem-vindo à AURA 360!",
            GREEN,
        )

    def open_register(e=None):

        nonlocal register_dialog

        if register_dialog is None:

            register_dialog = ft.AlertDialog(
                modal=True,
                title=txt(
                    "Criar conta",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                ),
                content=ft.Container(
                    width=430,
                    content=ft.Column(
                        [
                            txt(
                                "Cria gratuitamente a tua conta.",
                                color=MUTED,
                            ),
                            register_name,
                            register_email,
                            register_password,
                            button(
                                "Criar conta",
                                on_click=lambda e: create_account(),
                                width=220,
                            ),
                        ],
                        spacing=14,
                    ),
                ),
            )

            page.overlay.append(
                register_dialog
            )

        register_dialog.open = True

        page.update()

    # --------------------------------------------------------
    # REQUIRE ACCOUNT
    # --------------------------------------------------------

    def requires_account(feature):

        if not session["user"]:

            snack(
                f"Para utilizar {feature}, é necessário criar uma conta ou iniciar sessão.",
                BLUE,
            )

            open_register()

            return False

        return True

    # --------------------------------------------------------
    # LANDING HEADER
    # --------------------------------------------------------

    def landing_header():

        return ft.Container(
            bgcolor=WHITE,
            padding=20,
            content=ft.Row(
                [
                    ft.Row(
                        [
                            mascot_small(),
                            txt(
                                "AURA",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=NAVY,
                            ),
                            txt(
                                "360",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=BLUE,
                            ),
                        ],
                        spacing=8,
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
                                    "Empresas",
                                    color=MUTED,
                                ),
                                on_click=lambda e: requires_account(
                                    "a área empresarial"
                                ),
                            ),
                            button(
                                "Entrar",
                                on_click=open_login,
                                bgcolor=WHITE,
                                color=NAVY,
                            ),
                            button(
                                "Criar conta",
                                on_click=open_register,
                            ),
                        ],
                        spacing=5,
                        wrap=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

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
                        },
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=txt(
                                        "INTELIGÊNCIA FINANCEIRA",
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
                                    "A tua AURA.",
                                    size=43,
                                    color=WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                txt(
                                    "Uma plataforma inteligente para "
                                    "organizar finanças pessoais, "
                                    "crédito, poupança e gestão empresarial.",
                                    size=17,
                                    color="#CBD5E1",
                                ),
                                ft.Row(
                                    [
                                        button(
                                            "Começar gratuitamente",
                                            on_click=open_register,
                                            bgcolor=WHITE,
                                            color=NAVY,
                                        ),
                                        button(
                                            "Falar com a AURA",
                                            on_click=open_chat,
                                            bgcolor=NAVY_3,
                                            color=WHITE,
                                            icon=ft.Icons.AUTO_AWESOME,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=10,
                                ),
                                txt(
                                    "Sem compromisso. Cria a tua conta e começa.",
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
                        },
                        content=ft.Container(
                            bgcolor=NAVY_2,
                            padding=25,
                            border_radius=24,
                            border=ft.Border.all(
                                1,
                                "#263752",
                            ),
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            aura_face,
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
                                            ),
                                        ],
                                        spacing=15,
                                    ),
                                    txt(
                                        "Por onde queres começar?",
                                        size=22,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    hero_option(
                                        "💰",
                                        "Organizar as minhas finanças",
                                    ),
                                    hero_option(
                                        "💳",
                                        "Analisar os meus créditos",
                                    ),
                                    hero_option(
                                        "🎯",
                                        "Criar uma meta de poupança",
                                    ),
                                    hero_option(
                                        "🏢",
                                        "Gerir a minha empresa",
                                    ),
                                    hero_option(
                                        "🤖",
                                        "Perguntar qualquer coisa à AURA",
                                        open_chat,
                                    ),
                                ],
                                spacing=12,
                            ),
                        ),
                    ),
                ],
                spacing=25,
            ),
        )

    def hero_option(
        emoji,
        label,
        callback=None,
    ):

        if callback is None:

            callback = lambda e: requires_account(
                label
            )

        return ft.Container(
            bgcolor="#162238",
            padding=15,
            border_radius=13,
            on_click=callback,
            content=ft.Row(
                [
                    txt(
                        emoji,
                        size=21,
                    ),
                    txt(
                        label,
                        size=13,
                        color=WHITE,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD,
                        color="#64748B",
                    ),
                ]
            ),
        )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    def feature(
        icon,
        title,
        description,
        color,
        action,
    ):

        return ft.Container(
            bgcolor=WHITE,
            padding=22,
            border_radius=18,
            border=ft.Border.all(
                1,
                BORDER,
            ),
            on_click=action,
            content=ft.Column(
                [
                    ft.Container(
                        width=50,
                        height=50,
                        bgcolor=color,
                        border_radius=14,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icon,
                            color=WHITE,
                            size=24,
                        ),
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
                    txt(
                        "Explorar →",
                        size=12,
                        color=BLUE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
        )

    # --------------------------------------------------------
    # LANDING
    # --------------------------------------------------------

    def show_landing():

        page.navigation_bar = None

        page.controls.clear()

        content = ft.Column(
            [
                landing_header(),
                hero(),
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        [
                            txt(
                                "Tudo num só lugar.",
                                size=29,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                "A AURA transforma informação financeira "
                                "complexa em decisões simples.",
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
                                            lambda e: requires_account("as Finanças"),
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 6, "lg": 3},
                                        content=feature(
                                            ft.Icons.CREDIT_CARD,
                                            "Crédito",
                                            "Taxa de esforço, prestações e amortizações.",
                                            GREEN,
                                            lambda e: requires_account("o módulo de Crédito"),
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 6, "lg": 3},
                                        content=feature(
                                            ft.Icons.TARGET,
                                            "Metas",
                                            "Objetivos de poupança e progresso.",
                                            PURPLE,
                                            lambda e: requires_account("as Metas"),
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 6, "lg": 3},
                                        content=feature(
                                            ft.Icons.BUSINESS,
                                            "Empresas",
                                            "Clientes, vendas e gestão empresarial.",
                                            ORANGE,
                                            lambda e: requires_account("a área Empresarial"),
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
                    content=card(
                        ft.Row(
                            [
                                aura_face,
                                ft.Column(
                                    [
                                        txt(
                                            "A AURA acompanha-te.",
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            "Não é apenas um botão de ajuda. "
                                            "É a assistente inteligente da plataforma.",
                                            size=14,
                                            color=MUTED,
                                        ),
                                        button(
                                            "Conversar com a AURA",
                                            on_click=open_chat,
                                            icon=ft.Icons.AUTO_AWESOME,
                                        ),
                                    ],
                                    spacing=10,
                                    expand=True,
                                ),
                            ],
                            spacing=20,
                        ),
                    ),
                ),
                ft.Container(
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
                                "Vida pessoal e empresa no mesmo ecossistema.",
                                size=14,
                                color="#CBD5E1",
                            ),
                            ft.Row(
                                [
                                    button(
                                        "Começar como Particular",
                                        on_click=open_register,
                                        bgcolor=WHITE,
                                        color=NAVY,
                                    ),
                                    button(
                                        "Conhecer área Empresarial",
                                        on_click=lambda e: requires_account(
                                            "a área Empresarial"
                                        ),
                                        bgcolor=NAVY_3,
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
                    content=txt(
                        "© 2026 AURA 360 • Gestão Financeira & Empresarial",
                        size=12,
                        color=MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        page.add(
            ft.SafeArea(
                content=content,
                expand=True,
            )
        )

        # Mascote flutuante estilo Clippy
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor=BLUE,
            tooltip="Falar com a AURA",
            on_click=open_chat,
        )

        page.update()

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def get_financial_data(user_id):

        connection = db()

        income = connection.execute(
            """
            SELECT COALESCE(SUM(amount),0) AS total
            FROM transactions
            WHERE user_id=? AND type='income'
            """,
            (user_id,),
        ).fetchone()["total"]

        expense = connection.execute(
            """
            SELECT COALESCE(SUM(amount),0) AS total
            FROM transactions
            WHERE user_id=? AND type='expense'
            """,
            (user_id,),
        ).fetchone()["total"]

        goals = connection.execute(
            """
            SELECT * FROM goals
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

        transactions = connection.execute(
            """
            SELECT * FROM transactions
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 8
            """,
            (user_id,),
        ).fetchall()

        customers = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM customers
            WHERE user_id=?
            """,
            (user_id,),
        ).fetchone()["total"]

        sales = connection.execute(
            """
            SELECT COALESCE(SUM(amount),0) AS total
            FROM sales
            WHERE user_id=?
            """,
            (user_id,),
        ).fetchone()["total"]

        connection.close()

        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "goals": goals,
            "transactions": transactions,
            "customers": customers,
            "sales": sales,
        }

    def metric(
        title,
        value,
        icon,
        color,
        subtitle="",
    ):

        return ft.Container(
            bgcolor=WHITE,
            padding=18,
            border_radius=18,
            border=ft.Border.all(
                1,
                BORDER,
            ),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            txt(
                                title,
                                size=12,
                                color=MUTED,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(
                                width=40,
                                height=40,
                                bgcolor=BLUE_LIGHT,
                                border_radius=12,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    icon,
                                    color=color,
                                ),
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
                        size=11,
                        color=MUTED,
                    ),
                ],
                spacing=8,
            ),
        )

    def show_dashboard():

        user = session["user"]

        data = get_financial_data(
            user["id"]
        )

        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor=BLUE,
            tooltip="Falar com a AURA",
            on_click=open_chat,
        )

        def nav_change(e):

            index = e.control.selected_index

            if index == 0:
                show_dashboard()

            elif index == 1:
                show_finances()

            elif index == 2:
                show_goals()

            elif index == 3:
                show_business()

        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            bgcolor=WHITE,
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
            on_change=nav_change,
        )

        def logout(e):

            session["user"] = None

            page.navigation_bar = None

            show_landing()

        content = ft.Column(
            [
                ft.Container(
                    bgcolor=NAVY,
                    padding=20,
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    mascot_small(),
                                    txt(
                                        "AURA 360",
                                        size=20,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    txt(
                                        user["name"],
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.LOGOUT,
                                        icon_color=WHITE,
                                        tooltip="Sair",
                                        on_click=logout,
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
                ft.Container(
                    padding=25,
                    content=ft.Column(
                        [
                            txt(
                                f"Olá, {user['name']} 👋",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                "Aqui está o teu centro de controlo.",
                                size=14,
                                color=MUTED,
                            ),
                        ]
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(
                        left=25,
                        right=25,
                        bottom=20,
                    ),
                    content=ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=metric(
                                    "Saldo",
                                    money(data["balance"]),
                                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                                    BLUE,
                                    "Resultado acumulado",
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=metric(
                                    "Receitas",
                                    money(data["income"]),
                                    ft.Icons.TRENDING_UP,
                                    GREEN,
                                    "Total registado",
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=metric(
                                    "Despesas",
                                    money(data["expense"]),
                                    ft.Icons.TRENDING_DOWN,
                                    RED,
                                    "Total registado",
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6, "lg": 3},
                                content=metric(
                                    "Clientes",
                                    str(data["customers"]),
                                    ft.Icons.PEOPLE,
                                    PURPLE,
                                    "Perfil empresarial",
                                ),
                            ),
                        ],
                        spacing=15,
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(
                        left=25,
                        right=25,
                        bottom=20,
                    ),
                    content=card(
                        ft.Row(
                            [
                                aura_face,
                                ft.Column(
                                    [
                                        txt(
                                            "AURA",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            "Analisei o teu painel. "
                                            "Queres ajuda para decidir "
                                            "o próximo passo?",
                                            size=14,
                                            color=MUTED,
                                        ),
                                        button(
                                            "Perguntar à AURA",
                                            on_click=open_chat,
                                            icon=ft.Icons.AUTO_AWESOME,
                                        ),
                                    ],
                                    expand=True,
                                    spacing=8,
                                ),
                            ],
                            spacing=20,
                        )
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(
                        left=25,
                        right=25,
                        bottom=20,
                    ),
                    content=ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"sm": 12, "md": 6},
                                content=card(
                                    goals_card(
                                        data["goals"]
                                    )
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6},
                                content=card(
                                    transactions_card(
                                        data["transactions"]
                                    )
                                ),
                            ),
                        ],
                        spacing=15,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=content,
                expand=True,
            )
        )

        page.update()

    def goals_card(goals):

        controls = [
            txt(
                "🎯 Metas",
                size=18,
                weight=ft.FontWeight.BOLD,
            )
        ]

        if not goals:

            controls.append(
                txt(
                    "Ainda não tens metas.",
                    color=MUTED,
                )
            )

        for goal in goals:

            progress = 0

            if goal["target_amount"] > 0:

                progress = (
                    goal["current_amount"]
                    / goal["target_amount"]
                )

            progress = min(
                max(progress, 0),
                1,
            )

            controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                txt(
                                    goal["name"],
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                txt(
                                    f"{money(goal['current_amount'])} / "
                                    f"{money(goal['target_amount'])}",
                                    size=11,
                                    color=BLUE,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.ProgressBar(
                            value=progress,
                            color=BLUE,
                            bgcolor="#E5E7EB",
                        ),
                    ],
                    spacing=6,
                )
            )

        return ft.Column(
            controls,
            spacing=15,
        )

    def transactions_card(rows):

        controls = [
            txt(
                "💳 Movimentos recentes",
                size=18,
                weight=ft.FontWeight.BOLD,
            )
        ]

        if not rows:

            controls.append(
                txt(
                    "Ainda não tens movimentos.",
                    color=MUTED,
                )
            )

        for row in rows:

            positive = row["type"] == "income"

            controls.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.ARROW_UPWARD
                        if positive
                        else ft.Icons.ARROW_DOWNWARD,
                        color=GREEN
                        if positive
                        else RED,
                    ),
                    title=txt(
                        row["description"],
                        size=13,
                        weight=ft.FontWeight.BOLD,
                    ),
                    subtitle=txt(
                        row["category"],
                        size=11,
                        color=MUTED,
                    ),
                    trailing=txt(
                        money(row["amount"]),
                        size=12,
                        color=GREEN
                        if positive
                        else RED,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )

        return ft.Column(
            controls,
            spacing=5,
        )

    # --------------------------------------------------------
    # FINANÇAS
    # --------------------------------------------------------

    def show_finances():

        if not session["user"]:

            requires_account("as Finanças")
            return

        user = session["user"]

        description = ft.TextField(
            label="Descrição",
        )

        category = ft.TextField(
            label="Categoria",
        )

        amount = ft.TextField(
            label="Valor (€)",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        transaction_type = ft.Dropdown(
            label="Tipo",
            options=[
                ft.DropdownOption(
                    key="income",
                    text="Receita",
                ),
                ft.DropdownOption(
                    key="expense",
                    text="Despesa",
                ),
            ],
            value="expense",
        )

        list_area = ft.Column()

        def reload():

            connection = db()

            rows = connection.execute(
                """
                SELECT * FROM transactions
                WHERE user_id=?
                ORDER BY id DESC
                """,
                (user["id"],),
            ).fetchall()

            connection.close()

            list_area.controls.clear()

            for row in rows:

                positive = row["type"] == "income"

                list_area.controls.append(
                    ft.Container(
                        bgcolor=WHITE,
                        padding=12,
                        border_radius=12,
                        border=ft.Border.all(
                            1,
                            BORDER,
                        ),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.ARROW_UPWARD
                                    if positive
                                    else ft.Icons.ARROW_DOWNWARD,
                                    color=GREEN
                                    if positive
                                    else RED,
                                ),
                                ft.Column(
                                    [
                                        txt(
                                            row["description"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            row["category"],
                                            size=11,
                                            color=MUTED,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                txt(
                                    money(row["amount"]),
                                    color=GREEN
                                    if positive
                                    else RED,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_transaction(e):

            try:

                value = float(
                    amount.value.replace(
                        ",",
                        ".",
                    )
                )

            except Exception:

                snack(
                    "Introduz um valor válido.",
                    RED,
                )

                return

            if not description.value:

                snack(
                    "Indica uma descrição.",
                    RED,
                )

                return

            connection = db()

            connection.execute(
                """
                INSERT INTO transactions
                (user_id,description,category,amount,type,created_at)
                VALUES(?,?,?,?,?,?)
                """,
                (
                    user["id"],
                    description.value,
                    category.value or "Geral",
                    value,
                    transaction_type.value,
                    now(),
                ),
            )

            connection.commit()
            connection.close()

            description.value = ""
            category.value = ""
            amount.value = ""

            reload()

            snack(
                "Movimento registado.",
                GREEN,
            )

        content = ft.Column(
            [
                ft.Container(
                    padding=25,
                    content=ft.Column(
                        [
                            txt(
                                "💰 Finanças",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),
                            txt(
                                "Regista e acompanha as tuas receitas e despesas.",
                                color=MUTED,
                            ),
                        ]
                    ),
                ),
                ft.Container(
                    padding=25,
                    content=card(
                        ft.Column(
                            [
                                txt(
                                    "Novo movimento",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                description,
                                category,
                                amount,
                                transaction_type,
                                button(
                                    "Guardar movimento",
                                    on_click=add_transaction,
                                    icon=ft.Icons.ADD,
                                ),
                            ],
                            spacing=12,
                        )
                    ),
                ),
                ft.Container(
                    padding=25,
                    content=ft.Column(
                        [
                            txt(
                                "Movimentos",
                                size=19,
                                weight=ft.FontWeight.BOLD,
                            ),
                            list_area,
                        ],
                        spacing=12,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=content,
                expand=True,
            )
        )

        reload()

    # --------------------------------------------------------
    # METAS
    # --------------------------------------------------------

    def show_goals():

        if not session["user"]:

            requires_account("as Metas")
            return

        user = session["user"]

        name = ft.TextField(
            label="Nome da meta",
        )

        target = ft.TextField(
            label="Valor objetivo (€)",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        current = ft.TextField(
            label="Valor já poupado (€)",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        list_area = ft.Column()

        def reload():

            connection = db()

            rows = connection.execute(
                """
                SELECT * FROM goals
                WHERE user_id=?
                ORDER BY id DESC
                """,
                (user["id"],),
            ).fetchall()

            connection.close()

            list_area.controls.clear()

            for goal in rows:

                progress = 0

                if goal["target_amount"]:

                    progress = (
                        goal["current_amount"]
                        / goal["target_amount"]
                    )

                progress = min(
                    max(progress, 0),
                    1,
                )

                list_area.controls.append(
                    card(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        txt(
                                            goal["name"],
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            f"{progress * 100:.0f}%",
                                            color=BLUE,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(
                                    value=progress,
                                    color=BLUE,
                                    bgcolor="#E5E7EB",
                                ),
                                txt(
                                    f"{money(goal['current_amount'])} "
                                    f"de {money(goal['target_amount'])}",
                                    size=12,
                                    color=MUTED,
                                ),
                            ],
                            spacing=10,
                        )
                    )
                )

            page.update()

        def add_goal(e):

            try:

                target_value = float(
                    target.value.replace(",", ".")
                )

                current_value = float(
                    current.value.replace(",", ".")
                    if current.value
                    else 0
                )

            except Exception:

                snack(
                    "Introduz valores válidos.",
                    RED,
                )

                return

            if not name.value:

                snack(
                    "Indica o nome da meta.",
                    RED,
                )

                return

            connection = db()

            connection.execute(
                """
                INSERT INTO goals
                (user_id,name,current_amount,target_amount,created_at)
                VALUES(?,?,?,?,?)
                """,
                (
                    user["id"],
                    name.value,
                    current_value,
                    target_value,
                    now(),
                ),
            )

            connection.commit()
            connection.close()

            name.value = ""
            target.value = ""
            current.value = ""

            reload()

            snack(
                "Meta criada.",
                GREEN,
            )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        ft.Container(
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "🎯 Metas & Poupança",
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "Transforma objetivos em planos concretos.",
                                        color=MUTED,
                                    ),
                                ]
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=card(
                                ft.Column(
                                    [
                                        txt(
                                            "Criar meta",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        name,
                                        target,
                                        current,
                                        button(
                                            "Criar meta",
                                            on_click=add_goal,
                                            icon=ft.Icons.ADD,
                                        ),
                                    ],
                                    spacing=12,
                                )
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "As minhas metas",
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    list_area,
                                ],
                                spacing=12,
                            ),
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        reload()

    # --------------------------------------------------------
    # EMPRESA
    # --------------------------------------------------------

    def show_business():

        if not session["user"]:

            requires_account(
                "a área empresarial"
            )

            return

        user = session["user"]

        customer_name = ft.TextField(
            label="Nome do cliente",
        )

        customer_email = ft.TextField(
            label="Email",
        )

        customer_phone = ft.TextField(
            label="Telefone",
        )

        customer_list = ft.Column()

        def reload():

            connection = db()

            rows = connection.execute(
                """
                SELECT * FROM customers
                WHERE user_id=?
                ORDER BY id DESC
                """,
                (user["id"],),
            ).fetchall()

            connection.close()

            customer_list.controls.clear()

            for row in rows:

                customer_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.PERSON,
                            color=BLUE,
                        ),
                        title=txt(
                            row["name"],
                            weight=ft.FontWeight.BOLD,
                        ),
                        subtitle=txt(
                            f"{row['email'] or ''} "
                            f"{row['phone'] or ''}",
                            size=11,
                            color=MUTED,
                        ),
                        trailing=txt(
                            row["status"],
                            size=11,
                            color=GREEN,
                        ),
                    )
                )

            page.update()

        def add_customer(e):

            if not customer_name.value:

                snack(
                    "Indica o nome do cliente.",
                    RED,
                )

                return

            connection = db()

            connection.execute(
                """
                INSERT INTO customers
                (user_id,name,email,phone,status,created_at)
                VALUES(?,?,?,?,?,?)
                """,
                (
                    user["id"],
                    customer_name.value,
                    customer_email.value,
                    customer_phone.value,
                    "Lead",
                    now(),
                ),
            )

            connection.commit()
            connection.close()

            customer_name.value = ""
            customer_email.value = ""
            customer_phone.value = ""

            reload()

            snack(
                "Cliente adicionado.",
                GREEN,
            )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        ft.Container(
                            bgcolor=NAVY,
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "🏢 AURA Business",
                                        size=29,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "O centro de controlo do teu negócio.",
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
                                        content=card(
                                            ft.Column(
                                                [
                                                    txt(
                                                        "CRM",
                                                        size=20,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    txt(
                                                        "Clientes e leads.",
                                                        color=MUTED,
                                                    ),
                                                ]
                                            )
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 4},
                                        content=card(
                                            ft.Column(
                                                [
                                                    txt(
                                                        "Vendas",
                                                        size=20,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    txt(
                                                        "Acompanhe a faturação.",
                                                        color=MUTED,
                                                    ),
                                                ]
                                            )
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 4},
                                        content=card(
                                            ft.Column(
                                                [
                                                    txt(
                                                        "Tesouraria",
                                                        size=20,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    txt(
                                                        "Visão financeira.",
                                                        color=MUTED,
                                                    ),
                                                ]
                                            )
                                        ),
                                    ),
                                ],
                                spacing=15,
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=card(
                                ft.Column(
                                    [
                                        txt(
                                            "Adicionar cliente",
                                            size=19,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        customer_name,
                                        customer_email,
                                        customer_phone,
                                        button(
                                            "Adicionar cliente",
                                            on_click=add_customer,
                                            icon=ft.Icons.PERSON_ADD,
                                        ),
                                    ],
                                    spacing=12,
                                )
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "Clientes",
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    customer_list,
                                ],
                                spacing=10,
                            ),
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        reload()

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    def show_admin():

        user = session["user"]

        if not user or user["role"] != "admin":

            snack(
                "Acesso reservado ao administrador.",
                RED,
            )

            return

        total = users_count()

        active = active_users_count()

        maintenance = (
            get_setting("maintenance")
            == "1"
        )

        status_text = (
            "MANUTENÇÃO ATIVA"
            if maintenance
            else "PLATAFORMA ONLINE"
        )

        status_color = (
            RED
            if maintenance
            else GREEN
        )

        def toggle_maintenance(e):

            current = (
                get_setting("maintenance")
                == "1"
            )

            set_setting(
                "maintenance",
                "0"
                if current
                else "1",
            )

            show_admin()

        def reload_users():

            users_area.controls.clear()

            connection = db()

            rows = connection.execute(
                """
                SELECT id,name,email,role,active,created_at
                FROM users
                ORDER BY id DESC
                """
            ).fetchall()

            connection.close()

            for row in rows:

                def toggle_user(
                    e,
                    uid=row["id"],
                    current=row["active"],
                ):

                    connection = db()

                    connection.execute(
                        """
                        UPDATE users
                        SET active=?
                        WHERE id=?
                        """,
                        (
                            0
                            if current
                            else 1,
                            uid,
                        ),
                    )

                    connection.commit()
                    connection.close()

                    show_admin()

                users_area.controls.append(
                    ft.Container(
                        bgcolor=WHITE,
                        padding=12,
                        border_radius=12,
                        border=ft.Border.all(
                            1,
                            BORDER,
                        ),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.PERSON,
                                    color=BLUE,
                                ),
                                ft.Column(
                                    [
                                        txt(
                                            row["name"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            row["email"],
                                            size=11,
                                            color=MUTED,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                txt(
                                    row["role"],
                                    size=11,
                                    color=PURPLE,
                                ),
                                txt(
                                    "Ativo"
                                    if row["active"]
                                    else "Bloqueado",
                                    size=11,
                                    color=GREEN
                                    if row["active"]
                                    else RED,
                                ),
                                ft.IconButton(
                                    icon=(
                                        ft.Icons.BLOCK
                                        if row["active"]
                                        else ft.Icons.CHECK
                                    ),
                                    on_click=toggle_user,
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        users_area = ft.Column(
            spacing=10
        )

        page.controls.clear()

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        ft.Container(
                            bgcolor=NAVY,
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "⚙️ AURA Control Center",
                                        size=29,
                                        color=WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    txt(
                                        "Controlo administrativo da plataforma.",
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
                                        content=metric(
                                            "Utilizadores",
                                            str(total),
                                            ft.Icons.PEOPLE,
                                            BLUE,
                                            "Total de contas",
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 4},
                                        content=metric(
                                            "Ativos",
                                            str(active),
                                            ft.Icons.CHECK_CIRCLE,
                                            GREEN,
                                            "Contas ativas",
                                        ),
                                    ),
                                    ft.Container(
                                        col={"sm": 12, "md": 4},
                                        content=metric(
                                            "Estado",
                                            status_text,
                                            ft.Icons.SHIELD,
                                            status_color,
                                            "Estado global",
                                        ),
                                    ),
                                ],
                                spacing=15,
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=card(
                                ft.Column(
                                    [
                                        txt(
                                            "Controlo da plataforma",
                                            size=19,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            "Podes colocar o serviço em manutenção.",
                                            color=MUTED,
                                        ),
                                        button(
                                            (
                                                "Desativar manutenção"
                                                if maintenance
                                                else "Ativar manutenção"
                                            ),
                                            on_click=toggle_maintenance,
                                            bgcolor=(
                                                GREEN
                                                if maintenance
                                                else RED
                                            ),
                                            icon=(
                                                ft.Icons.PLAY_ARROW
                                                if maintenance
                                                else ft.Icons.BUILD
                                            ),
                                        ),
                                    ],
                                    spacing=12,
                                )
                            ),
                        ),
                        ft.Container(
                            padding=25,
                            content=ft.Column(
                                [
                                    txt(
                                        "Utilizadores",
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    users_area,
                                ],
                                spacing=12,
                            ),
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
            )
        )

        reload_users()

    # --------------------------------------------------------
    # ADMIN LOGIN AUTOMÁTICO
    # --------------------------------------------------------

    def ensure_admin():

        user = get_user(
            ADMIN_EMAIL
        )

        if user:

            if user["role"] != "admin":

                connection = db()

                connection.execute(
                    """
                    UPDATE users
                    SET role='admin'
                    WHERE email=?
                    """,
                    (ADMIN_EMAIL,),
                )

                connection.commit()
                connection.close()

            return

        connection = db()

        connection.execute(
            """
            INSERT INTO users
            (name,email,password_hash,role,active,created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (
                "Administrador AURA",
                ADMIN_EMAIL,
                hash_password(
                    ADMIN_PASSWORD
                ),
                "admin",
                1,
                now(),
            ),
        )

        connection.commit()
        connection.close()

    # --------------------------------------------------------
    # INÍCIO
    # --------------------------------------------------------

    ensure_admin()

    show_landing()


# ============================================================
# EXECUÇÃO WEB
# ============================================================

if __name__ == "__main__":

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
    )
