import os
import sqlite3
import hashlib
import secrets
import asyncio
from dotenv import load_dotenv
import flet as ft
import openai

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES E VARIÁVEIS DE AMBIENTE
# -----------------------------------------------------------------------------
load_dotenv()

DB_FILE = os.getenv("DB_FILE", "aura_finance.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_ADMIN_USER = os.getenv("ADMIN_USER", "Admin")
DEFAULT_ADMIN_PASS = os.getenv("ADMIN_PASS", "Admin123!")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# -----------------------------------------------------------------------------
# 2. SEGURANÇA E CRIPTOGRAFIA
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Gera um hash PBKDF2 seguro para a palavra-passe."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        120000
    )
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifica se a palavra-passe corresponde ao hash armazenado."""
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, stored_hash)

# -----------------------------------------------------------------------------
# 3. BASE DE DADOS (SQLITE)
# -----------------------------------------------------------------------------
def init_db():
    """Inicializa as tabelas da base de dados e cria o utilizador Admin."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabela de Utilizadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de Transações Pessoais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'receita' ou 'despesa'
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tabela de Objetivos Financeiros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tabela de Empresas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nif TEXT UNIQUE NOT NULL,
            sector TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nif TEXT,
            email TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # Tabela de Produtos/Serviços
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # Tabela de Vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            client_id INTEGER,
            total_amount REAL NOT NULL,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'pago',
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # Tabela de Definições do Sistema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Garantir que a definição de manutenção existe
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'false')")

    # Criar utilizador Admin por omissão se não existir
    cursor.execute("SELECT id FROM users WHERE username = ?", (DEFAULT_ADMIN_USER,))
    if not cursor.fetchone():
        pwd_hash, salt = hash_password(DEFAULT_ADMIN_PASS)
        cursor.execute(
            "INSERT INTO users (username, hash, salt, role) VALUES (?, ?, ?, 'admin')",
            (DEFAULT_ADMIN_USER, pwd_hash, salt)
        )

    conn.commit()
    conn.close()

def db_authenticate_user(username, password):
    """Autentica um utilizador na BD."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, hash, salt, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user_id, stored_hash, salt, role = row
        if verify_password(password, stored_hash, salt):
            return {"id": user_id, "username": username, "role": role}
    return None

def db_register_user(username, password):
    """Regista um novo utilizador."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        pwd_hash, salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, hash, salt, role) VALUES (?, ?, ?, 'user')",
            (username, pwd_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_get_maintenance_mode() -> bool:
    """Verifica se o modo de manutenção está ativo."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'maintenance'")
    row = cursor.fetchone()
    conn.close()
    return row[0] == 'true' if row else False

# -----------------------------------------------------------------------------
# 4. INTEGRAÇÃO COM AURA (OPENAI IA)
# -----------------------------------------------------------------------------
async def ask_aura(prompt: str) -> str:
    """Envia uma mensagem para a AURA e devolve a resposta da OpenAI."""
    if not OPENAI_API_KEY:
        return "⚠️ A chave da API da OpenAI não está configurada no ficheiro .env!"

    system_prompt = (
        "És a AURA, uma assistente virtual especialista em Gestão Financeira Pessoal "
        "e Empresarial para Portugal. Respondes de forma clara, profissional, motivadora "
        "e estruturada. Conheces a legislação fiscal portuguesa (IRS, IRC, IVA, SS, e-fatura) "
        "e boas práticas de literacia financeira."
    )

    def _call_api():
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    try:
        reply = await asyncio.to_thread(_call_api)
        return reply
    except Exception as e:
        return f" Erro ao comunicar com a AURA: {str(e)}"

# -----------------------------------------------------------------------------
# 5. APLICAÇÃO PRINCIPAL (FLET UI)
# -----------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "AURA Finance - A Tua Mascote Financeira"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#0B0E14"

    # Estado da sessão
    current_user = {"data": None}

    # Notificações Snackbar
    def show_toast(message: str, color: str = "#3B82F6"):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=3000
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # -------------------------------------------------------------------------
    # DIÁLOGO DE LOGIN / REGISTO
    # -------------------------------------------------------------------------
    txt_username = ft.TextField(label="Utilizador", width=300)
    txt_password = ft.TextField(label="Palavra-passe", password=True, can_reveal_password=True, width=300)

    def close_login_dialog():
        login_dialog.open = False
        page.update()

    def handle_login(e):
        u = txt_username.value.strip()
        p = txt_password.value.strip()
        if not u or not p:
            show_toast("Preencha todos os campos!", ft.Colors.RED_400)
            return

        user = db_authenticate_user(u, p)
        if user:
            current_user["data"] = user
            close_login_dialog()
            show_toast(f"Bem-vindo, {user['username']}!", ft.Colors.GREEN_600)
            navigate_to_dashboard()
        else:
            show_toast("Credenciais inválidas!", ft.Colors.RED_400)

    def handle_register(e):
        u = txt_username.value.strip()
        p = txt_password.value.strip()
        if not u or not p:
            show_toast("Preencha todos os campos!", ft.Colors.RED_400)
            return

        if db_register_user(u, p):
            show_toast("Conta criada com sucesso! Faça login.", ft.Colors.GREEN_600)
        else:
            show_toast("Utilizador já existe!", ft.Colors.RED_400)

    login_dialog = ft.AlertDialog(
        title=ft.Text("Aceder à AURA Finance", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                txt_username,
                txt_password,
                ft.Row(
                    controls=[
                        ft.ElevatedButton(content=ft.Text("Entrar"), on_click=handle_login, bgcolor="#1D4ED8", color=ft.Colors.WHITE),
                        ft.OutlinedButton(content=ft.Text("Registar"), on_click=handle_register),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            ],
            tight=True,
            spacing=15
        ),
        on_dismiss=lambda e: None
    )

    def open_login(e):
        page.overlay.append(login_dialog)
        login_dialog.open = True
        page.update()

    # -------------------------------------------------------------------------
    # MODAL DE CHAT COM A AURA
    # -------------------------------------------------------------------------
    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    chat_input = ft.TextField(
        placeholder="Pergunta algo à AURA...",
        expand=True,
        border_radius=12,
        on_submit=lambda e: asyncio.create_task(send_aura_message(e))
    )

    async def send_aura_message(e):
        msg = chat_input.value.strip()
        if not msg:
            return

        chat_input.value = ""
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"Tu: {msg}", color=ft.Colors.WHITE),
                alignment=ft.alignment.center_right,
                bgcolor="#1E293B",
                padding=10,
                border_radius=10
            )
        )
        page.update()

        loading_msg = ft.Text("AURA está a pensar...", italic=True, color="#94A3B8")
        chat_history.controls.append(loading_msg)
        page.update()

        response = await ask_aura(msg)

        chat_history.controls.remove(loading_msg)
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"🤖 AURA: {response}", color=ft.Colors.WHITE),
                alignment=ft.alignment.center_left,
                bgcolor="#0F172A",
                padding=10,
                border_radius=10,
                border=ft.border.all(1, "#3B82F6")
            )
        )
        page.update()

    chat_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color="#60A5FA"),
            ft.Text("Falar com a AURA", weight=ft.FontWeight.BOLD)
        ]),
        content=ft.Container(
            content=ft.Column([
                chat_history,
                ft.Row([
                    chat_input,
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="#3B82F6",
                        on_click=lambda e: asyncio.create_task(send_aura_message(e))
                    )
                ])
            ]),
            width=500,
            height=400
        )
    )

    def open_aura_chat(e):
        page.overlay.append(chat_dialog)
        chat_dialog.open = True
        page.update()

    # -------------------------------------------------------------------------
    # NAVEGAÇÃO PARA DASHBOARD
    # -------------------------------------------------------------------------
    def navigate_to_dashboard():
        page.controls.clear()

        def logout(e):
            current_user["data"] = None
            render_landing_page()

        sidebar = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Geral"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                    selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                    label="Pessoal"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BUSINESS_OUTLINED,
                    selected_icon=ft.Icons.BUSINESS,
                    label="Empresa"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                    selected_icon=ft.Icons.AUTO_AWESOME,
                    label="AURA IA"
                ),
            ],
            on_change=lambda e: show_toast(f"Menu alterado para o índice: {e.control.selected_index}")
        )

        dashboard_content = ft.Container(
            padding=30,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        f"Painel Principal - {current_user['data']['username']}",
                        size=28,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("Sair"),
                        icon=ft.Icons.LOGOUT,
                        on_click=logout,
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1E293B"),
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Saldo Pessoal", color="#94A3B8"),
                            ft.Text("2.450,00 €", size=24, weight=ft.FontWeight.BOLD, color="#10B981")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=20,
                        border_radius=12
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Faturação Empresarial", color="#94A3B8"),
                            ft.Text("12.890,00 €", size=24, weight=ft.FontWeight.BOLD, color="#3B82F6")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=20,
                        border_radius=12
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Objetivos Atingidos", color="#94A3B8"),
                            ft.Text("75%", size=24, weight=ft.FontWeight.BOLD, color="#F59E0B")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=20,
                        border_radius=12
                    ),
                ], spacing=20),
                ft.Container(height=30),
                ft.ElevatedButton(
                    content=ft.Text("Abrir Assistente AURA"),
                    icon=ft.Icons.AUTO_AWESOME,
                    on_click=open_aura_chat,
                    bgcolor="#1D4ED8",
                    color=ft.Colors.WHITE,
                    height=50
                )
            ])
        )

        page.add(
            ft.Row([
                sidebar,
                ft.VerticalDivider(width=1, color="#1E293B"),
                dashboard_content
            ], expand=True)
        )
        page.update()

    # -------------------------------------------------------------------------
    # LANDING PAGE (PÁGINA INICIAL)
    # -------------------------------------------------------------------------
    def render_landing_page():
        page.controls.clear()

        # Navbar
        navbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=15),
            bgcolor="#0B0E14",
            border=ft.border.only(bottom=ft.BorderSide(1, "#1E293B")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME, color="#3B82F6", size=28),
                        ft.Text("AURA Finance", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                    ]),
                    ft.Row([
                        ft.TextButton("Recursos", style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton("Empresas", style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.ElevatedButton(
                            content=ft.Text("Entrar"),
                            on_click=open_login,
                            bgcolor="#1D4ED8",
                            color=ft.Colors.WHITE
                        )
                    ], spacing=10)
                ]
            )
        )

        # Mascot Visual Component
        mascot_badge = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.AUTO_AWESOME, size=60, color="#60A5FA"),
                ft.Text("AURA", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("A tua Mascote Financeira", size=12, color="#94A3B8"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220,
            height=220,
            bgcolor="#1E293B",
            border_radius=110,
            border=ft.border.all(3, "#3B82F6"),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color="#1D4ED8"),
            on_click=open_aura_chat,
            tooltip="Clica para falar com a AURA"
        )

        # Hero Section
        hero = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=60),
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Container(
                        content=ft.Text("✨ Inteligência Financeira ao teu alcance", color="#60A5FA", weight=ft.FontWeight.W_500),
                        bgcolor="#1E293B",
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=20
                    ),
                    ft.Text(
                        "Domina o teu dinheiro com a ajuda da AURA",
                        size=42,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    ft.Text(
                        "Gestão financeira pessoal e empresarial num só lugar. "
                        "Acompanha orçamentos, faturação, impostos portugueses e recebe conselhos inteligentes da tua mascote IA.",
                        size=16,
                        color="#94A3B8"
                    ),
                    ft.Row([
                        ft.ElevatedButton(
                            content=ft.Text("Começar Agora"),
                            on_click=open_login,
                            bgcolor="#1D4ED8",
                            color=ft.Colors.WHITE,
                            height=48
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Falar com a AURA"),
                            on_click=open_aura_chat,
                            height=48
                        )
                    ], spacing=15)
                ], col={"sm": 12, "md": 7}, spacing=20),

                ft.Column([
                    mascot_badge
                ], col={"sm": 12, "md": 5}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

        # Features Section
        features = ft.Container(
            padding=40,
            content=ft.Column([
                ft.Text("Tudo o que precisas num só local", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#3B82F6", size=32),
                            ft.Text("Finanças Pessoais", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Controlo de receitas, despesas, orçamentos mensais e metas de poupança.", color="#94A3B8")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=25,
                        border_radius=16
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.BUSINESS_CENTER, color="#10B981", size=32),
                            ft.Text("Gestão Empresarial", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Faturação, gestão de clientes, inventário e análise de fluxo de caixa.", color="#94A3B8")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=25,
                        border_radius=16
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.AUTO_AWESOME, color="#F59E0B", size=32),
                            ft.Text("Assistente AURA", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Inteligência Artificial pronta para esclarecer dúvidas de impostos e finanças.", color="#94A3B8")
                        ]),
                        col={"sm": 12, "md": 4},
                        bgcolor="#1E293B",
                        padding=25,
                        border_radius=16
                    ),
                ], spacing=20)
            ])
        )

        # Footer
        footer = ft.Container(
            padding=20,
            border=ft.border.only(top=ft.BorderSide(1, "#1E293B")),
            content=ft.Row([
                ft.Text("© 2026 AURA Finance. Todos os direitos reservados.", color="#64748B", size=12)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

        # Layout Final da Landing Page
        page.add(
            ft.Column([
                navbar,
                hero,
                features,
                footer
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )
        page.update()

    # Inicializar Base de Dados e Arrancar Aplicação
    init_db()

    # Verificar se o sistema está em manutenção
    if db_get_maintenance_mode():
        page.add(
            ft.Container(
                alignment=ft.alignment.center,
                expand=True,
                content=ft.Column([
                    ft.Icon(ft.Icons.BUILD_ROUNDED, size=60, color="#F59E0B"),
                    ft.Text("Sistema em Manutenção", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Estamos a realizar melhorias. Por favor, volte mais tarde.", color="#94A3B8")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
    else:
        render_landing_page()

# -----------------------------------------------------------------------------
# 6. PONTO DE ENTRADA (ENTRY POINT)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ft.app(target=main)
