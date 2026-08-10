import flet as ft
import sqlite3
import os
import math
from datetime import datetime, date


# ============================================================
# AURA 360
# Plataforma de Gestão Financeira Pessoal e Empresarial
# Versão WEB - aplicação completa
# ============================================================

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aura360.db")


# ============================================================
# BASE DE DADOS
# ============================================================

def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            amount REAL NOT NULL,
            tx_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Lead',
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            client TEXT,
            description TEXT,
            amount REAL NOT NULL,
            vat REAL DEFAULT 23,
            status TEXT DEFAULT 'Pendente',
            invoice_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT,
            sale_price REAL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            purchase_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            total REAL NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            current_amount REAL DEFAULT 0,
            target_amount REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            task_date TEXT NOT NULL,
            category TEXT,
            done INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            principal REAL NOT NULL,
            annual_rate REAL NOT NULL,
            months INTEGER NOT NULL
        )
    """)

    conn.commit()

    # Dados iniciais apenas se a base estiver vazia
    cur.execute("SELECT COUNT(*) AS c FROM savings")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO savings (name,current_amount,target_amount) VALUES (?,?,?)",
            [
                ("Fundo de Emergência", 4500, 6000),
                ("Férias e Viagens", 1200, 2000),
                ("Investimentos / PPR", 800, 2000),
            ],
        )

    cur.execute("SELECT COUNT(*) AS c FROM clients")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO clients (name,email,phone,status,notes) VALUES (?,?,?,?,?)",
            [
                ("Cliente Exemplo", "cliente@email.pt", "910000000", "Lead", "Primeiro contacto"),
                ("Empresa Demo Lda.", "geral@empresa.pt", "211000000", "Proposta", "Orçamento em análise"),
            ],
        )

    cur.execute("SELECT COUNT(*) AS c FROM products")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO products (name,sku,sale_price) VALUES (?,?,?)",
            ("Produto Demonstração", "AURA-001", 25.00),
        )
        product_id = cur.lastrowid

        cur.executemany(
            """
            INSERT INTO stock_lots
            (product_id,quantity,unit_cost,purchase_date)
            VALUES (?,?,?,?)
            """,
            [
                (product_id, 10, 10, "2026-01-10"),
                (product_id, 20, 12, "2026-02-10"),
            ],
        )

    conn.commit()
    conn.close()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def money(value):
    try:
        return f"{float(value):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00 €"


def safe_float(value):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return 0.0


def today():
    return date.today().isoformat()


# ============================================================
# APLICAÇÃO
# ============================================================

def main(page: ft.Page):

    init_database()

    page.title = "AURA 360 | Gestão Financeira & Empresarial"
    page.bgcolor = "#F4F7FB"
    page.padding = 12
    page.scroll = ft.ScrollMode.AUTO

    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    current_profile = "Pessoal"

    # --------------------------------------------------------
    # COMPONENTES GERAIS
    # --------------------------------------------------------

    content_area = ft.Column(
        spacing=15,
        expand=True,
    )

    page_title = ft.Text(
        "AURA 360",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#0F172A",
    )

    page_subtitle = ft.Text(
        "Gestão financeira inteligente",
        size=13,
        color="#64748B",
    )

    status_message = ft.Text(
        "",
        size=13,
        color="#16A34A",
    )

    def notify(message, color="#16A34A"):
        status_message.value = message
        status_message.color = color
        page.update()

    def card(title, value, subtitle="", color="#2563EB", icon=ft.Icons.ANALYTICS):
        return ft.Container(
            bgcolor="#FFFFFF",
            padding=18,
            border_radius=14,
            border=ft.Border.all(1, "#E2E8F0"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                title,
                                size=13,
                                color="#64748B",
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Icon(icon, color=color, size=22),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        value,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#0F172A",
                    ),
                    ft.Text(
                        subtitle,
                        size=12,
                        color="#64748B",
                    ),
                ]
            ),
        )

    def button(text, on_click, color="#2563EB", icon=None):
        kwargs = {
            "content": ft.Text(
                text,
                color="#FFFFFF",
                weight=ft.FontWeight.W_600,
            ),
            "on_click": on_click,
            "bgcolor": color,
        }

        if icon is not None:
            kwargs["icon"] = icon

        return ft.ElevatedButton(**kwargs)

    def outline_button(text, on_click, icon=None):
        kwargs = {
            "content": ft.Text(
                text,
                color="#2563EB",
            ),
            "on_click": on_click,
        }

        if icon is not None:
            kwargs["icon"] = icon

        return ft.OutlinedButton(**kwargs)

    # ========================================================
    # DASHBOARD PESSOAL
    # ========================================================

    def personal_dashboard():

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT COALESCE(SUM(amount),0) AS total FROM transactions WHERE kind='Receita'"
        )
        receitas = cur.fetchone()["total"]

        cur.execute(
            "SELECT COALESCE(SUM(amount),0) AS total FROM transactions WHERE kind='Despesa'"
        )
        despesas = cur.fetchone()["total"]

        cur.execute(
            "SELECT COALESCE(SUM(current_amount),0) AS total FROM savings"
        )
        poupanca = cur.fetchone()["total"]

        conn.close()

        saldo = receitas - despesas

        return ft.Column(
            [
                ft.Text(
                    "📊 Dashboard Pessoal",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="#0F172A",
                ),

                ft.Text(
                    "Visão geral da tua vida financeira.",
                    color="#64748B",
                ),

                ft.ResponsiveRow(
                    [
                        ft.Container(
                            card(
                                "Receitas",
                                money(receitas),
                                "Total registado",
                                "#16A34A",
                                ft.Icons.TRENDING_UP,
                            ),
                            col={"sm": 12, "md": 4},
                        ),
                        ft.Container(
                            card(
                                "Despesas",
                                money(despesas),
                                "Total registado",
                                "#DC2626",
                                ft.Icons.TRENDING_DOWN,
                            ),
                            col={"sm": 12, "md": 4},
                        ),
                        ft.Container(
                            card(
                                "Saldo",
                                money(saldo),
                                "Receitas - despesas",
                                "#2563EB",
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                            ),
                            col={"sm": 12, "md": 4},
                        ),
                    ]
                ),

                ft.ResponsiveRow(
                    [
                        ft.Container(
                            card(
                                "Poupança acumulada",
                                money(poupanca),
                                "Metas financeiras",
                                "#7C3AED",
                                ft.Icons.SAVINGS,
                            ),
                            col={"sm": 12, "md": 4},
                        ),
                        ft.Container(
                            card(
                                "Taxa de poupança",
                                f"{((saldo / receitas) * 100):.1f}%"
                                if receitas > 0
                                else "0,0%",
                                "Estimativa atual",
                                "#0891B2",
                                ft.Icons.PIE_CHART,
                            ),
                            col={"sm": 12, "md": 4},
                        ),
                    ]
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "💡 Centro de Inteligência",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Regista receitas e despesas regularmente para "
                                "obter uma visão realista do teu saldo.",
                                color="#64748B",
                            ),
                        ]
                    ),
                ),
            ],
            spacing=15,
        )

    # ========================================================
    # RECEITAS / DESPESAS
    # ========================================================

    def personal_transactions():

        description = ft.TextField(
            label="Descrição",
            expand=True,
        )

        category = ft.TextField(
            label="Categoria",
            expand=True,
        )

        amount = ft.TextField(
            label="Valor (€)",
            width=160,
        )

        kind = ft.Dropdown(
            label="Tipo",
            width=170,
            value="Despesa",
            options=[
                ft.dropdown.Option("Receita"),
                ft.dropdown.Option("Despesa"),
            ],
        )

        list_area = ft.Column(spacing=5)

        def refresh():

            list_area.controls.clear()

            conn = db()
            rows = conn.execute(
                """
                SELECT * FROM transactions
                ORDER BY tx_date DESC, id DESC
                """
            ).fetchall()
            conn.close()

            if not rows:
                list_area.controls.append(
                    ft.Text(
                        "Ainda não existem movimentos registados.",
                        color="#64748B",
                    )
                )

            for row in rows:

                color = "#16A34A" if row["kind"] == "Receita" else "#DC2626"

                list_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=12,
                        border_radius=10,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            row["description"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{row['category'] or 'Sem categoria'} • {row['tx_date']}",
                                            size=12,
                                            color="#64748B",
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{'+' if row['kind'] == 'Receita' else '-'} {money(row['amount'])}",
                                    weight=ft.FontWeight.BOLD,
                                    color=color,
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_transaction(e):

            if not description.value or safe_float(amount.value) <= 0:
                notify("Preenche a descrição e um valor válido.", "#DC2626")
                return

            conn = db()

            conn.execute(
                """
                INSERT INTO transactions
                (kind,description,category,amount,tx_date)
                VALUES (?,?,?,?,?)
                """,
                (
                    kind.value,
                    description.value,
                    category.value,
                    safe_float(amount.value),
                    today(),
                ),
            )

            conn.commit()
            conn.close()

            description.value = ""
            category.value = ""
            amount.value = ""

            notify("Movimento registado com sucesso.")
            refresh()

        refresh()

        return ft.Column(
            [
                ft.Text(
                    "💰 Receitas & Despesas",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Novo movimento",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Row(
                                [
                                    description,
                                    category,
                                    amount,
                                    kind,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Registar movimento",
                                add_transaction,
                                "#2563EB",
                                ft.Icons.ADD,
                            ),
                        ]
                    ),
                ),

                status_message,
                ft.Text(
                    "Movimentos registados",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                ),
                list_area,
            ]
        )

    # ========================================================
    # CRÉDITOS
    # ========================================================

    def personal_loans():

        principal = ft.TextField(
            label="Capital em dívida (€)",
            value="10000",
            width=200,
        )

        rate = ft.TextField(
            label="Taxa anual (%)",
            value="6",
            width=160,
        )

        months = ft.TextField(
            label="Prazo restante (meses)",
            value="60",
            width=180,
        )

        extra = ft.TextField(
            label="Amortização extraordinária (€)",
            value="1000",
            width=210,
        )

        result = ft.Column()

        def calculate(e):

            p = safe_float(principal.value)
            r = safe_float(rate.value) / 100 / 12
            n = int(safe_float(months.value))
            extra_value = safe_float(extra.value)

            if p <= 0 or n <= 0:
                result.controls = [
                    ft.Text(
                        "Introduz valores válidos.",
                        color="#DC2626",
                    )
                ]
                page.update()
                return

            if r == 0:
                payment = p / n
                new_payment = max((p - extra_value) / n, 0)
            else:
                payment = p * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

                new_p = max(p - extra_value, 0)

                new_payment = (
                    new_p
                    * (r * (1 + r) ** n)
                    / ((1 + r) ** n - 1)
                    if new_p > 0
                    else 0
                )

            interest_without = max(payment * n - p, 0)

            new_p = max(p - extra_value, 0)

            if r == 0:
                new_interest = 0
            else:
                new_interest = max(new_payment * n - new_p, 0)

            saving = max(interest_without - new_interest, 0)

            result.controls = [
                ft.Divider(),
                ft.Text(
                    f"Prestação estimada atual: {money(payment)}",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"Prestação após amortização: {money(new_payment)}",
                    color="#2563EB",
                ),
                ft.Text(
                    f"Juros estimados evitados: {money(saving)}",
                    color="#16A34A",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    bgcolor="#ECFDF5",
                    padding=15,
                    border_radius=10,
                    content=ft.Text(
                        "A simulação é indicativa. O resultado real depende "
                        "do contrato, taxa, seguros e condições do banco.",
                        color="#166534",
                    ),
                ),
            ]

            page.update()

        return ft.Column(
            [
                ft.Text(
                    "💳 Simulador de Crédito & Amortização",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Simula o impacto de uma amortização extraordinária.",
                    color="#64748B",
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    principal,
                                    rate,
                                    months,
                                    extra,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Calcular amortização",
                                calculate,
                                "#2563EB",
                                ft.Icons.CALCULATE,
                            ),

                            result,
                        ]
                    ),
                ),
            ]
        )

    # ========================================================
    # METAS DE POUPANÇA
    # ========================================================

    def personal_savings():

        name = ft.TextField(
            label="Nome da meta",
            expand=True,
        )

        target = ft.TextField(
            label="Objetivo (€)",
            width=170,
        )

        current = ft.TextField(
            label="Valor atual (€)",
            width=170,
        )

        goals_area = ft.Column()

        def refresh():

            goals_area.controls.clear()

            conn = db()
            rows = conn.execute(
                "SELECT * FROM savings ORDER BY id DESC"
            ).fetchall()
            conn.close()

            for row in rows:

                percentage = 0

                if row["target_amount"] > 0:
                    percentage = min(
                        row["current_amount"] / row["target_amount"],
                        1,
                    )

                goals_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=16,
                        border_radius=12,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            row["name"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{money(row['current_amount'])} / "
                                            f"{money(row['target_amount'])}",
                                            color="#2563EB",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),

                                ft.ProgressBar(
                                    value=percentage,
                                    color="#2563EB",
                                    bgcolor="#E2E8F0",
                                ),

                                ft.Text(
                                    f"{percentage * 100:.0f}% concluído",
                                    size=12,
                                    color="#64748B",
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_goal(e):

            if not name.value or safe_float(target.value) <= 0:
                notify("Preenche o nome e o objetivo.", "#DC2626")
                return

            conn = db()

            conn.execute(
                """
                INSERT INTO savings
                (name,current_amount,target_amount)
                VALUES (?,?,?)
                """,
                (
                    name.value,
                    safe_float(current.value),
                    safe_float(target.value),
                ),
            )

            conn.commit()
            conn.close()

            name.value = ""
            target.value = ""
            current.value = ""

            notify("Meta criada.")
            refresh()

        refresh()

        return ft.Column(
            [
                ft.Text(
                    "🎯 Metas de Poupança",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    name,
                                    target,
                                    current,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Criar meta",
                                add_goal,
                                "#16A34A",
                                ft.Icons.SAVINGS,
                            ),
                        ]
                    ),
                ),

                goals_area,
            ]
        )

    # ========================================================
    # AGENDA
    # ========================================================

    def personal_agenda():

        title = ft.TextField(
            label="Tarefa / obrigação",
            expand=True,
        )

        task_date = ft.TextField(
            label="Data",
            value=today(),
            width=180,
        )

        category = ft.TextField(
            label="Categoria",
            width=180,
        )

        tasks_area = ft.Column()

        def refresh():

            tasks_area.controls.clear()

            conn = db()

            rows = conn.execute(
                """
                SELECT * FROM tasks
                ORDER BY done ASC, task_date ASC
                """
            ).fetchall()

            conn.close()

            for row in rows:

                def mark_done(e, task_id=row["id"]):
                    conn2 = db()
                    conn2.execute(
                        "UPDATE tasks SET done=1 WHERE id=?",
                        (task_id,),
                    )
                    conn2.commit()
                    conn2.close()
                    refresh()

                tasks_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=12,
                        border_radius=10,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE
                                    if row["done"]
                                    else ft.Icons.EVENT,
                                    color="#16A34A"
                                    if row["done"]
                                    else "#2563EB",
                                ),

                                ft.Column(
                                    [
                                        ft.Text(
                                            row["title"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{row['task_date']} • "
                                            f"{row['category'] or 'Geral'}",
                                            size=12,
                                            color="#64748B",
                                        ),
                                    ],
                                    expand=True,
                                ),

                                (
                                    ft.Text(
                                        "Concluída",
                                        color="#16A34A",
                                    )
                                    if row["done"]
                                    else outline_button(
                                        "Concluir",
                                        mark_done,
                                        ft.Icons.CHECK,
                                    )
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_task(e):

            if not title.value:
                notify("Escreve uma tarefa.", "#DC2626")
                return

            conn = db()

            conn.execute(
                """
                INSERT INTO tasks
                (title,task_date,category)
                VALUES (?,?,?)
                """,
                (
                    title.value,
                    task_date.value or today(),
                    category.value,
                ),
            )

            conn.commit()
            conn.close()

            title.value = ""
            category.value = ""

            notify("Tarefa adicionada.")
            refresh()

        refresh()

        return ft.Column(
            [
                ft.Text(
                    "📅 Agenda & Calendário Fiscal",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    title,
                                    task_date,
                                    category,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Adicionar tarefa",
                                add_task,
                                "#7C3AED",
                                ft.Icons.ADD_TASK,
                            ),
                        ]
                    ),
                ),

                tasks_area,
            ]
        )

    # ========================================================
    # CRM EMPRESARIAL
    # ========================================================

    def business_crm():

        name = ft.TextField(
            label="Nome / Empresa",
            expand=True,
        )

        email = ft.TextField(
            label="Email",
            expand=True,
        )

        phone = ft.TextField(
            label="Telefone",
            width=170,
        )

        status = ft.Dropdown(
            label="Estado",
            width=180,
            value="Lead",
            options=[
                ft.dropdown.Option("Lead"),
                ft.dropdown.Option("Contacto"),
                ft.dropdown.Option("Proposta"),
                ft.dropdown.Option("Negociação"),
                ft.dropdown.Option("Cliente"),
                ft.dropdown.Option("Perdido"),
            ],
        )

        clients_area = ft.Column()

        def refresh():

            clients_area.controls.clear()

            conn = db()

            rows = conn.execute(
                "SELECT * FROM clients ORDER BY id DESC"
            ).fetchall()

            conn.close()

            for row in rows:

                clients_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=14,
                        border_radius=12,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.PERSON,
                                    color="#2563EB",
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            row["name"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{row['email'] or '-'} • "
                                            f"{row['phone'] or '-'}",
                                            size=12,
                                            color="#64748B",
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Container(
                                    bgcolor="#EFF6FF",
                                    padding=8,
                                    border_radius=8,
                                    content=ft.Text(
                                        row["status"],
                                        color="#2563EB",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_client(e):

            if not name.value:
                notify("Indica o nome do cliente.", "#DC2626")
                return

            conn = db()

            conn.execute(
                """
                INSERT INTO clients
                (name,email,phone,status)
                VALUES (?,?,?,?)
                """,
                (
                    name.value,
                    email.value,
                    phone.value,
                    status.value,
                ),
            )

            conn.commit()
            conn.close()

            name.value = ""
            email.value = ""
            phone.value = ""

            notify("Cliente criado.")
            refresh()

        refresh()

        return ft.Column(
            [
                ft.Text(
                    "👥 CRM — Clientes & Vendas",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Novo cliente",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Row(
                                [
                                    name,
                                    email,
                                    phone,
                                    status,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Adicionar cliente",
                                add_client,
                                "#2563EB",
                                ft.Icons.PERSON_ADD,
                            ),
                        ]
                    ),
                ),

                clients_area,
            ]
        )

    # ========================================================
    # ORÇAMENTOS EMPRESARIAIS
    # ========================================================

    def business_quotes():

        service = ft.Dropdown(
            label="Serviço",
            width=280,
            value="Pintura",
            options=[
                ft.dropdown.Option("Pintura"),
                ft.dropdown.Option("Pavimento"),
                ft.dropdown.Option("Pladur"),
                ft.dropdown.Option("Remodelação"),
                ft.dropdown.Option("Consultoria"),
                ft.dropdown.Option("Outro"),
            ],
        )

        area = ft.TextField(
            label="Quantidade / Área",
            value="50",
            width=170,
        )

        price = ft.TextField(
            label="Preço unitário (€)",
            value="20",
            width=180,
        )

        vat = ft.TextField(
            label="IVA (%)",
            value="23",
            width=130,
        )

        result = ft.Column()

        def calculate(e):

            quantity = safe_float(area.value)
            unit_price = safe_float(price.value)
            vat_rate = safe_float(vat.value)

            if quantity <= 0 or unit_price < 0:
                notify("Introduz valores válidos.", "#DC2626")
                return

            subtotal = quantity * unit_price
            tax = subtotal * vat_rate / 100
            total = subtotal + tax

            result.controls = [
                ft.Divider(),

                ft.Text(
                    f"Serviço: {service.value}",
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),

                ft.Text(
                    f"Subtotal: {money(subtotal)}"
                ),

                ft.Text(
                    f"IVA ({vat_rate:.2f}%): {money(tax)}"
                ),

                ft.Container(
                    bgcolor="#ECFDF5",
                    padding=15,
                    border_radius=10,
                    content=ft.Text(
                        f"TOTAL DA PROPOSTA: {money(total)}",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#166534",
                    ),
                ),
            ]

            page.update()

        return ft.Column(
            [
                ft.Text(
                    "🧾 Gerador de Orçamentos",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Cria estimativas comerciais com cálculo automático de IVA.",
                    color="#64748B",
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    service,
                                    area,
                                    price,
                                    vat,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Calcular orçamento",
                                calculate,
                                "#2563EB",
                                ft.Icons.RECEIPT_LONG,
                            ),

                            result,
                        ]
                    ),
                ),
            ]
        )

    # ========================================================
    # FATURAS EMPRESARIAIS
    # ========================================================

    def business_invoices():

        number = ft.TextField(
            label="N.º Fatura",
            width=160,
        )

        client = ft.TextField(
            label="Cliente",
            expand=True,
        )

        description = ft.TextField(
            label="Descrição",
            expand=True,
        )

        amount = ft.TextField(
            label="Valor sem IVA",
            width=160,
        )

        vat = ft.TextField(
            label="IVA %",
            value="23",
            width=100,
        )

        invoices_area = ft.Column()

        def refresh():

            invoices_area.controls.clear()

            conn = db()

            rows = conn.execute(
                """
                SELECT * FROM invoices
                ORDER BY id DESC
                """
            ).fetchall()

            conn.close()

            for row in rows:

                total = row["amount"] * (1 + row["vat"] / 100)

                invoices_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=14,
                        border_radius=12,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.RECEIPT_LONG,
                                    color="#2563EB",
                                ),

                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{row['number'] or 'Sem número'} • "
                                            f"{row['client'] or 'Cliente'}",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{row['description'] or ''} • "
                                            f"{row['invoice_date']}",
                                            size=12,
                                            color="#64748B",
                                        ),
                                    ],
                                    expand=True,
                                ),

                                ft.Column(
                                    [
                                        ft.Text(
                                            money(total),
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            row["status"],
                                            size=11,
                                            color="#F59E0B"
                                            if row["status"] == "Pendente"
                                            else "#16A34A",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def add_invoice(e):

            value = safe_float(amount.value)

            if value <= 0:
                notify("Indica um valor válido.", "#DC2626")
                return

            conn = db()

            conn.execute(
                """
                INSERT INTO invoices
                (number,client,description,amount,vat,status,invoice_date)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    number.value,
                    client.value,
                    description.value,
                    value,
                    safe_float(vat.value),
                    "Pendente",
                    today(),
                ),
            )

            conn.commit()
            conn.close()

            number.value = ""
            client.value = ""
            description.value = ""
            amount.value = ""

            notify("Fatura registada.")
            refresh()

        refresh()

        return ft.Column(
            [
                ft.Text(
                    "📄 Faturas & Fiscalidade",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    number,
                                    client,
                                    description,
                                    amount,
                                    vat,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Registar fatura",
                                add_invoice,
                                "#2563EB",
                                ft.Icons.ADD,
                            ),
                        ]
                    ),
                ),

                invoices_area,
            ]
        )

    # ========================================================
    # POS + INVENTÁRIO FIFO
    # ========================================================

    def business_pos():

        product_select = ft.Dropdown(
            label="Produto",
            expand=True,
        )

        quantity = ft.TextField(
            label="Quantidade",
            value="1",
            width=140,
        )

        stock_area = ft.Column()

        def load_products():

            conn = db()

            rows = conn.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.sku,
                    p.sale_price,
                    COALESCE(SUM(s.quantity),0) AS stock
                FROM products p
                LEFT JOIN stock_lots s ON s.product_id = p.id
                GROUP BY p.id
                ORDER BY p.name
                """
            ).fetchall()

            conn.close()

            product_select.options = [
                ft.dropdown.Option(
                    str(row["id"]),
                    row["name"],
                )
                for row in rows
            ]

            if rows and not product_select.value:
                product_select.value = str(rows[0]["id"])

            stock_area.controls.clear()

            for row in rows:

                stock_area.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=12,
                        border_radius=10,
                        border=ft.Border.all(1, "#E2E8F0"),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.INVENTORY_2,
                                    color="#7C3AED",
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            row["name"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"SKU: {row['sku'] or '-'}",
                                            size=11,
                                            color="#64748B",
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text(
                                    f"Stock: {row['stock']:.0f}",
                                    weight=ft.FontWeight.BOLD,
                                    color="#16A34A"
                                    if row["stock"] > 0
                                    else "#DC2626",
                                ),
                            ]
                        ),
                    )
                )

            page.update()

        def sell(e):

            if not product_select.value:
                notify("Seleciona um produto.", "#DC2626")
                return

            qty = safe_float(quantity.value)

            if qty <= 0:
                notify("Quantidade inválida.", "#DC2626")
                return

            product_id = int(product_select.value)

            conn = db()

            product = conn.execute(
                "SELECT * FROM products WHERE id=?",
                (product_id,),
            ).fetchone()

            lots = conn.execute(
                """
                SELECT * FROM stock_lots
                WHERE product_id=? AND quantity>0
                ORDER BY purchase_date ASC, id ASC
                """,
                (product_id,),
            ).fetchall()

            available = sum(row["quantity"] for row in lots)

            if available < qty:
                conn.close()
                notify(
                    f"Stock insuficiente. Disponível: {available:.2f}",
                    "#DC2626",
                )
                return

            remaining = qty
            cost = 0

            for lot in lots:

                if remaining <= 0:
                    break

                used = min(remaining, lot["quantity"])

                cost += used * lot["unit_cost"]

                conn.execute(
                    """
                    UPDATE stock_lots
                    SET quantity=quantity-?
                    WHERE id=?
                    """,
                    (used, lot["id"]),
                )

                remaining -= used

            sale_total = qty * product["sale_price"]

            conn.execute(
                """
                INSERT INTO sales
                (product_id,quantity,total,sale_date)
                VALUES (?,?,?,?)
                """,
                (
                    product_id,
                    qty,
                    sale_total,
                    today(),
                ),
            )

            conn.commit()
            conn.close()

            margin = sale_total - cost

            notify(
                f"Venda registada: {money(sale_total)} | Margem estimada: {money(margin)}"
            )

            load_products()

        return ft.Column(
            [
                ft.Text(
                    "🛒 POS & Inventário FIFO",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "As vendas consomem automaticamente os lotes mais antigos primeiro.",
                    color="#64748B",
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    product_select,
                                    quantity,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Registar venda",
                                sell,
                                "#16A34A",
                                ft.Icons.POINT_OF_SALE,
                            ),
                        ]
                    ),
                ),

                ft.Text(
                    "Inventário atual",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                ),

                stock_area,
            ]
        )

    # ========================================================
    # STOCK / COMPRA
    # ========================================================

    def business_stock():

        name = ft.TextField(
            label="Produto",
            expand=True,
        )

        sku = ft.TextField(
            label="SKU",
            width=150,
        )

        sale_price = ft.TextField(
            label="Preço venda",
            width=150,
        )

        quantity = ft.TextField(
            label="Quantidade comprada",
            width=170,
        )

        unit_cost = ft.TextField(
            label="Custo unitário",
            width=160,
        )

        result = ft.Text()

        def add_stock(e):

            if not name.value:
                notify("Indica o produto.", "#DC2626")
                return

            conn = db()

            product = conn.execute(
                """
                SELECT * FROM products
                WHERE name=?
                """,
                (name.value,),
            ).fetchone()

            if product is None:

                conn.execute(
                    """
                    INSERT INTO products
                    (name,sku,sale_price)
                    VALUES (?,?,?)
                    """,
                    (
                        name.value,
                        sku.value,
                        safe_float(sale_price.value),
                    ),
                )

                product_id = conn.execute(
                    "SELECT last_insert_rowid()"
                ).fetchone()[0]

            else:

                product_id = product["id"]

                conn.execute(
                    """
                    UPDATE products
                    SET sale_price=?
                    WHERE id=?
                    """,
                    (
                        safe_float(sale_price.value),
                        product_id,
                    ),
                )

            conn.execute(
                """
                INSERT INTO stock_lots
                (product_id,quantity,unit_cost,purchase_date)
                VALUES (?,?,?,?)
                """,
                (
                    product_id,
                    safe_float(quantity.value),
                    safe_float(unit_cost.value),
                    today(),
                ),
            )

            conn.commit()
            conn.close()

            result.value = "Entrada de stock registada."
            result.color = "#16A34A"

            name.value = ""
            sku.value = ""
            sale_price.value = ""
            quantity.value = ""
            unit_cost.value = ""

            notify("Stock atualizado.")
            page.update()

        return ft.Column(
            [
                ft.Text(
                    "📦 Entrada de Stock",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=18,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    name,
                                    sku,
                                    sale_price,
                                    quantity,
                                    unit_cost,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Registar compra / entrada",
                                add_stock,
                                "#7C3AED",
                                ft.Icons.ADD_BOX,
                            ),

                            result,
                        ]
                    ),
                ),
            ]
        )

    # ========================================================
    # PREVISÃO FINANCEIRA EMPRESARIAL
    # ========================================================

    def business_forecast():

        monthly_revenue = ft.TextField(
            label="Faturação mensal média (€)",
            value="10000",
            width=220,
        )

        monthly_costs = ft.TextField(
            label="Custos mensais (€)",
            value="6000",
            width=200,
        )

        months = ft.TextField(
            label="Horizonte (meses)",
            value="12",
            width=150,
        )

        tax_rate = ft.TextField(
            label="Taxa fiscal estimada (%)",
            value="21",
            width=190,
        )

        result = ft.Column()

        def calculate(e):

            revenue = safe_float(monthly_revenue.value)
            costs = safe_float(monthly_costs.value)
            horizon = int(safe_float(months.value))
            tax = safe_float(tax_rate.value)

            if revenue < 0 or costs < 0 or horizon <= 0:
                notify("Valores inválidos.", "#DC2626")
                return

            annual_revenue = revenue * horizon
            annual_costs = costs * horizon
            operating_profit = annual_revenue - annual_costs
            estimated_tax = max(operating_profit, 0) * tax / 100
            net = operating_profit - estimated_tax

            result.controls = [
                ft.Divider(),

                ft.Text(
                    f"Faturação projetada: {money(annual_revenue)}",
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    f"Custos projetados: {money(annual_costs)}"
                ),

                ft.Text(
                    f"Resultado antes de imposto: {money(operating_profit)}"
                ),

                ft.Text(
                    f"Imposto estimado: {money(estimated_tax)}",
                    color="#DC2626",
                ),

                ft.Container(
                    bgcolor="#ECFDF5",
                    padding=15,
                    border_radius=10,
                    content=ft.Text(
                        f"Resultado estimado após imposto: {money(net)}",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color="#166534",
                    ),
                ),

                ft.Text(
                    "Esta é uma projeção financeira e não substitui o apuramento "
                    "fiscal efetuado por contabilista certificado.",
                    size=11,
                    color="#64748B",
                ),
            ]

            page.update()

        return ft.Column(
            [
                ft.Text(
                    "📈 Previsão Financeira & Fiscal",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=14,
                    border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    monthly_revenue,
                                    monthly_costs,
                                    months,
                                    tax_rate,
                                ],
                                wrap=True,
                            ),

                            button(
                                "Gerar previsão",
                                calculate,
                                "#0891B2",
                                ft.Icons.INSIGHTS,
                            ),

                            result,
                        ]
                    ),
                ),
            ]
        )

    # ========================================================
    # DASHBOARD EMPRESARIAL
    # ========================================================

    def business_dashboard():

        conn = db()

        clients = conn.execute(
            "SELECT COUNT(*) AS c FROM clients"
        ).fetchone()["c"]

        invoices = conn.execute(
            "SELECT COUNT(*) AS c FROM invoices"
        ).fetchone()["c"]

        sales = conn.execute(
            "SELECT COALESCE(SUM(total),0) AS total FROM sales"
        ).fetchone()["total"]

        stock = conn.execute(
            """
            SELECT COALESCE(SUM(quantity),0) AS total
            FROM stock_lots
            """
        ).fetchone()["total"]

        conn.close()

        return ft.Column(
            [
                ft.Text(
                    "🏢 Dashboard Empresarial",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Centro de controlo da atividade da empresa.",
                    color="#64748B",
                ),

                ft.ResponsiveRow(
                    [
                        ft.Container(
                            card(
                                "Clientes",
                                str(clients),
                                "CRM",
                                "#2563EB",
                                ft.Icons.GROUP,
                            ),
                            col={"sm": 12, "md": 3},
                        ),

                        ft.Container(
                            card(
                                "Faturas",
                                str(invoices),
                                "Documentos registados",
                                "#7C3AED",
                                ft.Icons.RECEIPT,
                            ),
                            col={"sm": 12, "md": 3},
                        ),

                        ft.Container(
                            card(
                                "Vendas POS",
                                money(sales),
                                "Vendas registadas",
                                "#16A34A",
                                ft.Icons.POINT_OF_SALE,
                            ),
                            col={"sm": 12, "md": 3},
                        ),

                        ft.Container(
                            card(
                                "Stock",
                                f"{stock:.0f}",
                                "Unidades disponíveis",
                                "#F59E0B",
                                ft.Icons.INVENTORY_2,
                            ),
                            col={"sm": 12, "md": 3},
                        ),
                    ]
                ),

                ft.Container(
                    bgcolor="#0F172A",
                    padding=22,
                    border_radius=16,
                    content=ft.Column(
                        [
                            ft.Text(
                                "AURA 360 Business",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                "CRM • Orçamentos • Faturação • POS • FIFO • Tesouraria",
                                color="#CBD5E1",
                            ),
                        ]
                    ),
                ),
            ]
        )

    # ========================================================
    # NAVEGAÇÃO
    # ========================================================

    personal_buttons = []
    business_buttons = []

    def show_view(view, title, subtitle):

        page_title.value = title
        page_subtitle.value = subtitle

        content_area.controls.clear()
        content_area.controls.append(view())

        page.update()

    def personal_dashboard_click(e):
        show_view(
            personal_dashboard,
            "AURA 360",
            "Dashboard Pessoal",
        )

    def transactions_click(e):
        show_view(
            personal_transactions,
            "AURA 360",
            "Receitas & Despesas",
        )

    def loans_click(e):
        show_view(
            personal_loans,
            "AURA 360",
            "Crédito & Amortização",
        )

    def savings_click(e):
        show_view(
            personal_savings,
            "AURA 360",
            "Metas de Poupança",
        )

    def agenda_click(e):
        show_view(
            personal_agenda,
            "AURA 360",
            "Agenda & Calendário",
        )

    def business_dashboard_click(e):
        show_view(
            business_dashboard,
            "AURA 360",
            "Dashboard Empresarial",
        )

    def crm_click(e):
        show_view(
            business_crm,
            "AURA 360",
            "CRM",
        )

    def quotes_click(e):
        show_view(
            business_quotes,
            "AURA 360",
            "Orçamentos",
        )

    def invoices_click(e):
        show_view(
            business_invoices,
            "AURA 360",
            "Faturas",
        )

    def pos_click(e):
        show_view(
            business_pos,
            "AURA 360",
            "POS & FIFO",
        )

    def stock_click(e):
        show_view(
            business_stock,
            "AURA 360",
            "Inventário",
        )

    def forecast_click(e):
        show_view(
            business_forecast,
            "AURA 360",
            "Previsão Financeira",
        )

    # ========================================================
    # BOTÕES DE PERFIL
    # ========================================================

    personal_nav = ft.Row(
        [
            button(
                "Dashboard",
                personal_dashboard_click,
                "#0F172A",
                ft.Icons.DASHBOARD,
            ),
            button(
                "Receitas & Despesas",
                transactions_click,
                "#2563EB",
                ft.Icons.ACCOUNT_BALANCE_WALLET,
            ),
            button(
                "Créditos",
                loans_click,
                "#7C3AED",
                ft.Icons.CREDIT_CARD,
            ),
            button(
                "Metas",
                savings_click,
                "#16A34A",
                ft.Icons.SAVINGS,
            ),
            button(
                "Agenda",
                agenda_click,
                "#0891B2",
                ft.Icons.CALENDAR_MONTH,
            ),
        ],
        wrap=True,
    )

    business_nav = ft.Row(
        [
            button(
                "Dashboard",
                business_dashboard_click,
                "#0F172A",
                ft.Icons.DASHBOARD,
            ),
            button(
                "CRM",
                crm_click,
                "#2563EB",
                ft.Icons.GROUP,
            ),
            button(
                "Orçamentos",
                quotes_click,
                "#7C3AED",
                ft.Icons.REQUEST_QUOTE,
            ),
            button(
                "Faturas",
                invoices_click,
                "#0891B2",
                ft.Icons.RECEIPT_LONG,
            ),
            button(
                "POS",
                pos_click,
                "#16A34A",
                ft.Icons.POINT_OF_SALE,
            ),
            button(
                "Inventário",
                stock_click,
                "#F59E0B",
                ft.Icons.INVENTORY_2,
            ),
            button(
                "Previsão",
                forecast_click,
                "#DC2626",
                ft.Icons.INSIGHTS,
            ),
        ],
        wrap=True,
    )

    # ========================================================
    # TROCA DE PERFIL
    # ========================================================

    navigation_area = ft.Column()

    profile_personal = button(
        "PERFIL PESSOAL",
        lambda e: switch_profile("Pessoal"),
        "#2563EB",
        ft.Icons.PERSON,
    )

    profile_business = button(
        "PERFIL EMPRESARIAL",
        lambda e: switch_profile("Empresarial"),
        "#7C3AED",
        ft.Icons.BUSINESS,
    )

    def switch_profile(profile):

        nonlocal current_profile

        current_profile = profile

        navigation_area.controls.clear()

        if profile == "Pessoal":

            navigation_area.controls.extend(
                [
                    ft.Text(
                        "👤 PERFIL PESSOAL",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#2563EB",
                    ),
                    personal_nav,
                ]
            )

            show_view(
                personal_dashboard,
                "AURA 360",
                "Dashboard Pessoal",
            )

        else:

            navigation_area.controls.extend(
                [
                    ft.Text(
                        "🏢 PERFIL EMPRESARIAL",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#7C3AED",
                    ),
                    business_nav,
                ]
            )

            show_view(
                business_dashboard,
                "AURA 360",
                "Dashboard Empresarial",
            )

        page.update()

    # ========================================================
    # CABEÇALHO
    # ========================================================

    header = ft.Container(
        bgcolor="#FFFFFF",
        padding=18,
        border_radius=16,
        border=ft.Border.all(1, "#E2E8F0"),
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            bgcolor="#0F172A",
                            padding=10,
                            border_radius=12,
                            content=ft.Icon(
                                ft.Icons.AUTO_AWESOME,
                                color="#38BDF8",
                                size=28,
                            ),
                        ),

                        ft.Column(
                            [
                                page_title,
                                page_subtitle,
                            ],
                            spacing=2,
                        ),
                    ],
                    expand=True,
                ),

                ft.Row(
                    [
                        profile_personal,
                        profile_business,
                    ],
                    wrap=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
        ),
    )

    # ========================================================
    # ASSISTENTE AURA AI
    # ========================================================

    chat_messages = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=260,
    )

    chat_input = ft.TextField(
        label="Pergunta ao AURA AI",
        expand=True,
    )

    def ai_answer(text):

        question = text.lower()

        if "crédito" in question or "credito" in question:
            return (
                "Para analisar um crédito, utiliza o módulo "
                "'Créditos' no Perfil Pessoal. Podes simular "
                "uma amortização e comparar a prestação estimada."
            )

        if "cliente" in question or "crm" in question:
            return (
                "No Perfil Empresarial tens o CRM para registar "
                "clientes e acompanhar o estado do processo comercial."
            )

        if "stock" in question or "inventário" in question:
            return (
                "O módulo POS & FIFO controla as entradas e as vendas. "
                "Quando existe uma venda, o sistema consome primeiro "
                "os lotes mais antigos."
            )

        if "orçamento" in question or "orcamento" in question:
            return (
                "No módulo Orçamentos podes indicar serviço, quantidade, "
                "preço unitário e IVA para obter automaticamente o total."
            )

        if "fatura" in question or "fatura" in question:
            return (
                "O módulo Faturas permite registar documentos, cliente, "
                "valor e IVA e acompanhar o estado."
            )

        if "poupança" in question or "poupanca" in question:
            return (
                "No módulo Metas podes criar objetivos financeiros e "
                "acompanhar visualmente a percentagem alcançada."
            )

        return (
            "Sou o assistente AURA 360. Posso orientar-te pelos módulos "
            "de finanças pessoais, créditos, poupança, CRM, orçamentos, "
            "faturas, POS, inventário e previsão financeira."
        )

    def send_ai(e):

        if not chat_input.value or not chat_input.value.strip():
            return

        question = chat_input.value.strip()

        chat_messages.controls.append(
            ft.Container(
                padding=8,
                bgcolor="#EFF6FF",
                border_radius=8,
                content=ft.Text(
                    f"Tu: {question}",
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

        chat_messages.controls.append(
            ft.Container(
                padding=8,
                bgcolor="#F8FAFC",
                border_radius=8,
                content=ft.Text(
                    f"AURA AI: {ai_answer(question)}",
                    color="#1D4ED8",
                ),
            )
        )

        chat_input.value = ""

        page.update()

    ai_dialog = ft.AlertDialog(
        title=ft.Row(
            [
                ft.Icon(
                    ft.Icons.AUTO_AWESOME,
                    color="#2563EB",
                ),
                ft.Text(
                    "AURA AI",
                    weight=ft.FontWeight.BOLD,
                ),
            ]
        ),
        content=ft.Container(
            width=500,
            height=360,
            content=ft.Column(
                [
                    chat_messages,
                    ft.Row(
                        [
                            chat_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                icon_color="#2563EB",
                                on_click=send_ai,
                            ),
                        ]
                    ),
                ]
            ),
        ),
    )

    def open_ai(e):

        if ai_dialog not in page.overlay:
            page.overlay.append(ai_dialog)

        ai_dialog.open = True
        page.update()

    ai_button = ft.FloatingActionButton(
        icon=ft.Icons.AUTO_AWESOME,
        bgcolor="#2563EB",
        foreground_color="#FFFFFF",
        on_click=open_ai,
    )

    page.floating_action_button = ai_button

    # ========================================================
    # RODAPÉ
    # ========================================================

    footer = ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Divider(color="#E2E8F0"),

                ft.Row(
                    [
                        ft.Text(
                            "AURA 360",
                            weight=ft.FontWeight.BOLD,
                            color="#0F172A",
                        ),
                        ft.Text(
                            "Gestão Financeira • Empresarial • POS • CRM",
                            size=11,
                            color="#64748B",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True,
                ),

                ft.Text(
                    "Os simuladores financeiros e fiscais são indicativos "
                    "e não substituem aconselhamento profissional.",
                    size=10,
                    color="#94A3B8",
                ),
            ]
        ),
    )

    # ========================================================
    # MONTAGEM FINAL
    # ========================================================

    page.add(
        header,
        ft.Container(height=5),
        navigation_area,
        status_message,
        content_area,
        footer,
    )

    # Começa no Perfil Pessoal
    switch_profile("Pessoal")


# ============================================================
# ARRANQUE WEB
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    ft.app(
        target=main,
        port=port,
        view=ft.AppView.WEB_BROWSER,
    )
