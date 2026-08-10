import flet as ft
import os
import math
import re
from datetime import datetime, date

# ============================================================
# AURA 360
# Plataforma Financeira Pessoal + Empresarial + AURA AI
# ============================================================

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ============================================================
# CONFIGURAÇÃO
# ============================================================

APP_NAME = "AURA 360"
AI_MODEL = os.environ.get("AURA_AI_MODEL", "gpt-5.5")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

BLUE = "#2563EB"
BLUE_DARK = "#1D4ED8"
NAVY = "#0F172A"
GREEN = "#10B981"
RED = "#EF4444"
ORANGE = "#F59E0B"
PURPLE = "#7C3AED"
PINK = "#EC4899"
CYAN = "#0891B2"

BG = "#F8FAFC"
WHITE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"
LIGHT_BLUE = "#EFF6FF"
LIGHT_GREEN = "#ECFDF5"
LIGHT_RED = "#FEF2F2"
LIGHT_ORANGE = "#FFF7ED"
LIGHT_PURPLE = "#F5F3FF"


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def dinheiro(valor):
    return f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor):
    try:
        return float(str(valor).replace(",", ".").replace("€", "").strip())
    except Exception:
        return 0.0


def opcao(texto):
    """
    Compatibilidade com diferentes versões do Flet.
    """
    try:
        if hasattr(ft, "DropdownOption"):
            return ft.DropdownOption(key=texto, text=texto)
    except Exception:
        pass

    try:
        return ft.dropdown.Option(texto)
    except Exception:
        return texto


def botao(texto, on_click=None, icon=None, bgcolor=BLUE, width=None):
    return ft.ElevatedButton(
        content=texto,
        icon=icon,
        on_click=on_click,
        bgcolor=bgcolor,
        color=WHITE,
        width=width,
    )


def botao_outline(texto, on_click=None, icon=None, width=None):
    return ft.OutlinedButton(
        content=texto,
        icon=icon,
        on_click=on_click,
        width=width,
    )


def titulo(texto, subtitulo=None):
    controls = [
        ft.Text(
            texto,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=TEXT,
        )
    ]

    if subtitulo:
        controls.append(
            ft.Text(
                subtitulo,
                size=13,
                color=MUTED,
            )
        )

    return ft.Column(controls=controls, spacing=4)


def card(content, padding=20, expand=False):
    return ft.Container(
        content=content,
        bgcolor=WHITE,
        padding=padding,
        border_radius=16,
        border=ft.Border.all(1, BORDER),
        expand=expand,
    )


def metric_card(label, value, description, icon, color):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            label,
                            size=13,
                            color=MUTED,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Container(
                            content=ft.Icon(
                                icon,
                                color=color,
                                size=21,
                            ),
                            bgcolor="#F1F5F9",
                            padding=9,
                            border_radius=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    value,
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Text(
                    description,
                    size=12,
                    color=MUTED,
                ),
            ],
            spacing=8,
        ),
        bgcolor=WHITE,
        padding=18,
        border_radius=16,
        border=ft.Border.all(1, BORDER),
        expand=True,
    )


# ============================================================
# APLICAÇÃO PRINCIPAL
# ============================================================

def main(page: ft.Page):

    page.title = "AURA 360 | Gestão Financeira e Empresarial"
    page.bgcolor = BG
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    try:
        page.theme_mode = ft.ThemeMode.LIGHT
    except Exception:
        pass

    # ========================================================
    # DADOS DA SESSÃO
    # ========================================================

    transacoes = [
        {
            "data": "10/08/2026",
            "descricao": "Salário",
            "categoria": "Rendimento",
            "valor": 1850.00,
            "tipo": "receita",
        },
        {
            "data": "08/08/2026",
            "descricao": "Supermercado",
            "categoria": "Alimentação",
            "valor": 124.50,
            "tipo": "despesa",
        },
        {
            "data": "07/08/2026",
            "descricao": "Eletricidade",
            "categoria": "Casa",
            "valor": 72.30,
            "tipo": "despesa",
        },
    ]

    metas = [
        {
            "nome": "Fundo de Emergência",
            "atual": 4500,
            "meta": 6000,
            "cor": GREEN,
        },
        {
            "nome": "Férias",
            "atual": 1200,
            "meta": 2500,
            "cor": BLUE,
        },
        {
            "nome": "Investimentos",
            "atual": 800,
            "meta": 3000,
            "cor": PURPLE,
        },
    ]

    faturas = [
        {
            "numero": "FT 2026/089",
            "cliente": "Supermercado",
            "valor": 124.50,
            "estado": "Validada",
        },
        {
            "numero": "FT 2026/102",
            "cliente": "Farmácia Central",
            "valor": 45.20,
            "estado": "Validada",
        },
    ]

    clientes = [
        {
            "nome": "João Silva",
            "empresa": "JS Construções",
            "telefone": "912345678",
            "email": "joao@email.pt",
            "estado": "Proposta",
        },
        {
            "nome": "Maria Costa",
            "empresa": "MC Interiors",
            "telefone": "913456789",
            "email": "maria@email.pt",
            "estado": "Contacto",
        },
        {
            "nome": "Pedro Santos",
            "empresa": "PS Imobiliária",
            "telefone": "914567890",
            "email": "pedro@email.pt",
            "estado": "Fechado",
        },
    ]

    produtos = [
        {
            "codigo": "P001",
            "nome": "Tinta Interior Premium",
            "quantidade": 15,
            "custo": 24.50,
            "preco": 39.90,
        },
        {
            "codigo": "P002",
            "nome": "Tinta Exterior",
            "quantidade": 8,
            "custo": 31.00,
            "preco": 49.90,
        },
        {
            "codigo": "P003",
            "nome": "Cola Pavimento",
            "quantidade": 25,
            "custo": 8.50,
            "preco": 16.90,
        },
    ]

    vendas = []

    # ========================================================
    # ESTADO DA NAVEGAÇÃO
    # ========================================================

    estado = {
        "perfil": "pessoal",
        "modulo": "dashboard",
    }

    conteudo = ft.Column(
        expand=True,
        spacing=15,
    )

    # ========================================================
    # AURA AI
    # ========================================================

    ai_client = None

    if OpenAI and OPENAI_API_KEY:
        try:
            ai_client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception:
            ai_client = None

    ai_previous_response = None

    ai_messages = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    ai_input = ft.TextField(
        hint_text="Pergunta ao AURA AI...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=4,
        border_radius=12,
        border_color=BORDER,
    )

    ai_status = ft.Text(
        "● IA ONLINE" if ai_client else "● MODO ASSISTENTE LOCAL",
        size=11,
        color=GREEN if ai_client else ORANGE,
        weight=ft.FontWeight.BOLD,
    )

    def adicionar_mensagem_utilizador(texto):
        ai_messages.controls.append(
            ft.Container(
                content=ft.Text(
                    texto,
                    size=14,
                    color=TEXT,
                ),
                bgcolor="#DBEAFE",
                padding=13,
                border_radius=12,
            )
        )

    def adicionar_mensagem_ai(texto):
        ai_messages.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.AUTO_AWESOME,
                                    color=BLUE,
                                    size=18,
                                ),
                                ft.Text(
                                    "AURA AI",
                                    weight=ft.FontWeight.BOLD,
                                    color=BLUE,
                                ),
                            ]
                        ),
                        ft.Markdown(
                            value=texto,
                            selectable=True,
                            auto_follow_links=True,
                        ),
                    ],
                    spacing=6,
                ),
                bgcolor=WHITE,
                padding=14,
                border_radius=12,
                border=ft.Border.all(1, BORDER),
            )
        )

    def resposta_local(pergunta):
        p = pergunta.lower()

        # Calculadora simples
        if any(x in p for x in ["quanto é", "quanto e", "calcula", "calcular"]):
            numeros = re.findall(r"\d+(?:[.,]\d+)?", p)

            if len(numeros) >= 2:
                try:
                    a = float(numeros[0].replace(",", "."))
                    b = float(numeros[1].replace(",", "."))

                    if "+" in p or "somar" in p:
                        return f"### Resultado\n\n**{a + b:.2f}**"

                    if "-" in p or "menos" in p:
                        return f"### Resultado\n\n**{a - b:.2f}**"

                    if "*" in p or "vezes" in p:
                        return f"### Resultado\n\n**{a * b:.2f}**"

                    if "/" in p or "dividir" in p:
                        if b != 0:
                            return f"### Resultado\n\n**{a / b:.2f}**"
                except Exception:
                    pass

        if "irs" in p or "imposto" in p:
            return """
### IRS

Posso ajudar-te a organizar o IRS, despesas, faturas e deduções.

Posso também:
- analisar despesas;
- explicar conceitos fiscais;
- calcular valores;
- indicar sites oficiais;
- pesquisar informação atualizada quando a AURA AI estiver ligada à Internet.

**Nota:** questões fiscais devem ser confirmadas nas fontes oficiais ou com um contabilista certificado.
"""

        if "credito" in p or "crédito" in p or "empréstimo" in p:
            return """
### Crédito

Posso ajudar a analisar:
- taxa de esforço;
- prestação mensal;
- amortização;
- consolidação;
- custo total;
- impacto de uma amortização extraordinária.

Se quiseres, diz-me:

**rendimento mensal + prestações atuais + saldo em dívida + taxa de juro + prazo restante.**
"""

        if "poupanca" in p or "poupança" in p:
            return """
### Poupança

Uma boa estratégia começa por separar:

1. despesas essenciais;
2. despesas variáveis;
3. fundo de emergência;
4. investimento;
5. amortização de dívida.

A AURA 360 também permite criar metas e acompanhar automaticamente o progresso.
"""

        if "empresa" in p or "negocio" in p or "negócio" in p:
            return """
### Gestão Empresarial

Posso ajudar-te com:

- clientes;
- vendas;
- CRM;
- orçamentos;
- margem;
- stock;
- FIFO;
- tesouraria;
- previsão financeira;
- impostos.

Também posso analisar os números que introduzires na aplicação.
"""

        if "orcamento" in p or "orçamento" in p:
            return """
### Orçamentos

Posso calcular:

**materiais + mão de obra + margem + IVA = preço recomendado.**

Também posso ajudar a comparar uma proposta com o custo estimado e calcular a margem comercial.
"""

        return """
Olá! Eu sou a **AURA AI**, o assistente inteligente da AURA 360.

Posso ajudar-te com:

💰 Finanças pessoais  
💳 Crédito e amortizações  
📊 Orçamentos  
🏢 Empresas  
👥 CRM  
📦 Stock e FIFO  
🧾 Faturas  
📈 Previsões financeiras  
💶 Impostos  
🧮 Cálculos  
🌐 Pesquisa na Internet  

Experimenta perguntar:

**"Como posso reduzir a minha taxa de esforço?"**

ou

**"Calcula uma margem de 25% sobre 1800€."**
"""

    def obter_contexto():
        receitas = sum(
            t["valor"]
            for t in transacoes
            if t["tipo"] == "receita"
        )

        despesas = sum(
            t["valor"]
            for t in transacoes
            if t["tipo"] == "despesa"
        )

        stock_valor = sum(
            p["quantidade"] * p["custo"]
            for p in produtos
        )

        return f"""
CONTEXTO ATUAL DA AURA 360

Perfil ativo: {estado["perfil"]}

Finanças pessoais:
Receitas registadas: {dinheiro(receitas)}
Despesas registadas: {dinheiro(despesas)}
Saldo calculado: {dinheiro(receitas - despesas)}

Metas:
{metas}

Faturas:
{faturas}

CRM:
{clientes}

Inventário:
Produtos: {len(produtos)}
Valor aproximado do stock pelo custo: {dinheiro(stock_valor)}

Vendas:
{vendas}
"""

    def perguntar_ai(pergunta):

        nonlocal ai_previous_response

        if not ai_client:
            return resposta_local(pergunta)

        try:
            instrucoes = """
És a AURA AI, o assistente oficial da plataforma AURA 360.

Responde sempre em português de Portugal.

És um assistente profissional de:
- finanças pessoais;
- gestão empresarial;
- crédito;
- poupança;
- investimento;
- orçamento;
- CRM;
- vendas;
- inventário;
- FIFO;
- tesouraria;
- impostos;
- produtividade.

REGRAS:

1. Conversa naturalmente com o utilizador.
2. Não respondas sempre com a mesma frase.
3. Usa os dados fornecidos pela aplicação quando forem relevantes.
4. Faz cálculos quando necessário.
5. Explica os cálculos.
6. Quando a pergunta depender de informação atual, pesquisa na Internet.
7. Quando pesquisares, apresenta fontes e links úteis.
8. Dá preferência a fontes oficiais para assuntos fiscais, legais e institucionais.
9. Nunca inventes links.
10. Não apresentes aconselhamento financeiro, fiscal ou jurídico como garantia profissional.
11. Se não tiveres informação suficiente, pergunta os dados que faltam.
12. Usa Markdown para apresentar respostas bonitas e organizadas.
13. Sê objetivo, mas completo.
14. Se o utilizador pedir uma comparação, cria uma tabela.
15. Se o utilizador pedir um cálculo, mostra o resultado claramente.
"""

            contexto = obter_contexto()

            input_text = (
                contexto
                + "\n\nPERGUNTA DO UTILIZADOR:\n"
                + pergunta
            )

            kwargs = {
                "model": AI_MODEL,
                "instructions": instrucoes,
                "input": input_text,
                "tools": [
                    {
                        "type": "web_search"
                    }
                ],
            }

            if ai_previous_response:
                kwargs["previous_response_id"] = ai_previous_response

            response = ai_client.responses.create(**kwargs)

            ai_previous_response = response.id

            texto = response.output_text

            if not texto:
                texto = "Não consegui gerar uma resposta neste momento."

            return texto

        except Exception as ex:
            return (
                "### AURA AI\n\n"
                "A ligação à IA encontrou um problema temporário.\n\n"
                f"`{str(ex)}`\n\n"
                "Enquanto isso, posso continuar a funcionar em modo assistente local."
            )

    def enviar_ai(e=None):

        pergunta = (ai_input.value or "").strip()

        if not pergunta:
            return

        adicionar_mensagem_utilizador("👤 " + pergunta)

        ai_input.value = ""

        adicionar_mensagem_ai("⏳ Estou a analisar a tua pergunta...")

        page.update()

        def worker():

            # remove indicador
            if ai_messages.controls:
                ai_messages.controls.pop()

            resposta = perguntar_ai(pergunta)

            adicionar_mensagem_ai(resposta)

            page.update()

        if hasattr(page, "run_thread"):
            page.run_thread(worker)
        else:
            worker()

    ai_input.on_submit = enviar_ai

    ai_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.AUTO_AWESOME,
                    color=BLUE,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "AURA AI",
                            size=21,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ai_status,
                    ],
                    spacing=1,
                ),
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ai_messages,
                    ft.Row(
                        controls=[
                            ai_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                icon_color=BLUE,
                                on_click=enviar_ai,
                            ),
                        ]
                    ),
                ],
                spacing=12,
            ),
            width=600,
            height=500,
        ),
    )

    def abrir_ai(e=None):

        if ai_dialog not in page.overlay:
            page.overlay.append(ai_dialog)

        ai_dialog.open = True
        page.update()

    # ========================================================
    # DASHBOARD PESSOAL
    # ========================================================

    def dashboard_pessoal():

        receitas = sum(
            t["valor"]
            for t in transacoes
            if t["tipo"] == "receita"
        )

        despesas = sum(
            t["valor"]
            for t in transacoes
            if t["tipo"] == "despesa"
        )

        saldo = receitas - despesas

        metas_progress = sum(
            min(m["atual"] / m["meta"], 1)
            for m in metas
        ) / len(metas)

        lista = []

        for t in reversed(transacoes[-5:]):
            cor = GREEN if t["tipo"] == "receita" else RED
            sinal = "+" if t["tipo"] == "receita" else "-"

            lista.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.ARROW_UPWARD
                        if t["tipo"] == "receita"
                        else ft.Icons.ARROW_DOWNWARD,
                        color=cor,
                    ),
                    title=ft.Text(
                        t["descricao"],
                        weight=ft.FontWeight.BOLD,
                    ),
                    subtitle=ft.Text(
                        f"{t['data']} • {t['categoria']}"
                    ),
                    trailing=ft.Text(
                        f"{sinal}{dinheiro(t['valor'])}",
                        color=cor,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )

        return ft.Column(
            controls=[
                titulo(
                    "Dashboard Pessoal",
                    "Visão geral da tua saúde financeira.",
                ),

                ft.Row(
                    controls=[
                        metric_card(
                            "Saldo",
                            dinheiro(saldo),
                            "Saldo calculado",
                            ft.Icons.ACCOUNT_BALANCE_WALLET,
                            BLUE,
                        ),
                        metric_card(
                            "Receitas",
                            dinheiro(receitas),
                            "Total registado",
                            ft.Icons.ARROW_UPWARD,
                            GREEN,
                        ),
                        metric_card(
                            "Despesas",
                            dinheiro(despesas),
                            "Total registado",
                            ft.Icons.ARROW_DOWNWARD,
                            RED,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
                ),

                ft.Row(
                    controls=[
                        card(
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Últimos movimentos",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    *lista,
                                ]
                            ),
                            expand=True,
                        ),

                        card(
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Metas de poupança",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.ProgressBar(
                                        value=metas_progress,
                                        color=GREEN,
                                        bgcolor="#E2E8F0",
                                    ),
                                    ft.Text(
                                        f"{metas_progress * 100:.0f}% de progresso médio",
                                        color=MUTED,
                                    ),
                                    botao(
                                        "Gerir metas",
                                        lambda e: navegar(
                                            "pessoal",
                                            "metas",
                                        ),
                                        ft.Icons.FLAG,
                                        GREEN,
                                    ),
                                ],
                                spacing=12,
                            ),
                            expand=True,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
                ),
            ],
            spacing=15,
        )

    # ========================================================
    # TRANSAÇÕES
    # ========================================================

    def transacoes_view():

        descricao = ft.TextField(
            label="Descrição",
            expand=True,
        )

        valor = ft.TextField(
            label="Valor (€)",
            width=150,
        )

        categoria = ft.Dropdown(
            label="Categoria",
            value="Alimentação",
            options=[
                opcao("Alimentação"),
                opcao("Casa"),
                opcao("Transportes"),
                opcao("Saúde"),
                opcao("Educação"),
                opcao("Lazer"),
                opcao("Rendimento"),
                opcao("Outros"),
            ],
            width=180,
        )

        tipo = ft.Dropdown(
            label="Tipo",
            value="despesa",
            options=[
                opcao("despesa"),
                opcao("receita"),
            ],
            width=150,
        )

        lista = ft.Column()

        def atualizar():

            lista.controls.clear()

            for t in reversed(transacoes):

                cor = GREEN if t["tipo"] == "receita" else RED
                sinal = "+" if t["tipo"] == "receita" else "-"

                lista.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.RECEIPT_LONG,
                                    color=cor,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            t["descricao"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{t['data']} • {t['categoria']}",
                                            color=MUTED,
                                            size=12,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{sinal}{dinheiro(t['valor'])}",
                                    color=cor,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                        bgcolor=WHITE,
                        padding=12,
                        border_radius=10,
                        border=ft.Border.all(1, BORDER),
                    )
                )

            page.update()

        def adicionar(e):

            v = numero(valor.value)

            if not descricao.value or v <= 0:
                return

            transacoes.append(
                {
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "descricao": descricao.value,
                    "categoria": categoria.value,
                    "valor": v,
                    "tipo": tipo.value,
                }
            )

            descricao.value = ""
            valor.value = ""

            atualizar()

        atualizar()

        return ft.Column(
            controls=[
                titulo(
                    "Movimentos Financeiros",
                    "Regista receitas e despesas.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Novo movimento",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                controls=[
                                    descricao,
                                    valor,
                                    categoria,
                                    tipo,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Adicionar movimento",
                                adicionar,
                                ft.Icons.ADD,
                            ),
                        ],
                        spacing=12,
                    )
                ),

                lista,
            ],
            spacing=15,
        )

    # ========================================================
    # CRÉDITO
    # ========================================================

    def credito_view():

        rendimento = ft.TextField(
            label="Rendimento líquido mensal (€)",
            value="1800",
        )

        prestacao = ft.TextField(
            label="Prestações atuais (€)",
            value="650",
        )

        divida = ft.TextField(
            label="Capital em dívida (€)",
            value="85000",
        )

        taxa = ft.TextField(
            label="Taxa anual (%)",
            value="4.5",
        )

        resultado = ft.Column()

        def calcular(e):

            r = numero(rendimento.value)
            p = numero(prestacao.value)
            d = numero(divida.value)
            j = numero(taxa.value)

            if r <= 0:
                resultado.controls = [
                    ft.Text(
                        "Indica um rendimento válido.",
                        color=RED,
                    )
                ]
                page.update()
                return

            esforco = (p / r) * 100

            nova_prestacao = p * 0.85
            poupanca = p - nova_prestacao

            if esforco <= 35:
                cor = GREEN
                mensagem = "Zona financeira confortável."
            elif esforco <= 50:
                cor = ORANGE
                mensagem = "Zona de atenção. Analisa os créditos."
            else:
                cor = RED
                mensagem = "Taxa de esforço elevada."

            resultado.controls = [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"Taxa de esforço: {esforco:.1f}%",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=cor,
                            ),
                            ft.Text(mensagem),
                            ft.Divider(),
                            ft.Text(
                                f"Prestação atual: {dinheiro(p)}"
                            ),
                            ft.Text(
                                f"Simulação de redução de 15%: {dinheiro(nova_prestacao)}"
                            ),
                            ft.Text(
                                f"Poupança mensal estimada: {dinheiro(poupanca)}",
                                color=GREEN,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Capital indicado: {dinheiro(d)}"
                            ),
                            ft.Text(
                                f"Taxa anual indicada: {j:.2f}%"
                            ),
                            ft.Text(
                                "Esta simulação é indicativa e não constitui uma proposta bancária.",
                                size=11,
                                color=MUTED,
                            ),
                        ]
                    ),
                    bgcolor="#F8FAFC",
                    padding=16,
                    border_radius=12,
                )
            ]

            page.update()

        return ft.Column(
            controls=[
                titulo(
                    "Crédito & Amortização",
                    "Analisa taxa de esforço e impacto de uma redução de prestação.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    rendimento,
                                    prestacao,
                                    divida,
                                    taxa,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Calcular",
                                calcular,
                                ft.Icons.CALCULATE,
                            ),
                        ],
                        spacing=15,
                    )
                ),

                resultado,
            ],
            spacing=15,
        )

    # ========================================================
    # METAS
    # ========================================================

    def metas_view():

        lista = ft.Column()

        def atualizar():

            lista.controls.clear()

            for m in metas:

                progresso = min(
                    m["atual"] / m["meta"],
                    1,
                )

                lista.controls.append(
                    card(
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            m["nome"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{dinheiro(m['atual'])} / {dinheiro(m['meta'])}",
                                            color=m["cor"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(
                                    value=progresso,
                                    color=m["cor"],
                                    bgcolor="#E2E8F0",
                                ),
                                ft.Text(
                                    f"{progresso * 100:.0f}% concluído",
                                    color=MUTED,
                                    size=12,
                                ),
                            ]
                        )
                    )
                )

            page.update()

        atualizar()

        return ft.Column(
            controls=[
                titulo(
                    "Metas de Poupança",
                    "Transforma objetivos financeiros em progresso mensurável.",
                ),
                lista,
            ],
            spacing=15,
        )

    # ========================================================
    # CALENDÁRIO / AGENDA
    # ========================================================

    def agenda_view():

        tarefas = [
            ("15/08/2026", "Rever despesas do mês"),
            ("20/08/2026", "Confirmar faturas"),
            ("31/08/2026", "Fecho financeiro mensal"),
            ("15/09/2026", "Revisão de orçamento"),
        ]

        return ft.Column(
            controls=[
                titulo(
                    "Agenda & Calendário Financeiro",
                    "Organiza tarefas, prazos e revisões.",
                ),
                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Próximos eventos",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            *[
                                ft.ListTile(
                                    leading=ft.Icon(
                                        ft.Icons.EVENT,
                                        color=BLUE,
                                    ),
                                    title=ft.Text(tarefa),
                                    subtitle=ft.Text(data),
                                )
                                for data, tarefa in tarefas
                            ],
                        ]
                    )
                ),
            ],
            spacing=15,
        )

    # ========================================================
    # FATURAS
    # ========================================================

    def faturas_view():

        numero_fatura = ft.TextField(
            label="Número da fatura",
            expand=True,
        )

        entidade = ft.TextField(
            label="Entidade",
            expand=True,
        )

        valor_fatura = ft.TextField(
            label="Valor (€)",
            width=150,
        )

        lista = ft.Column()

        def atualizar():

            lista.controls.clear()

            for f in faturas:

                lista.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.RECEIPT_LONG,
                                    color=BLUE,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            f["numero"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f["cliente"],
                                            color=MUTED,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text(
                                    dinheiro(f["valor"]),
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f["estado"],
                                        color=GREEN,
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=LIGHT_GREEN,
                                    padding=7,
                                    border_radius=8,
                                ),
                            ]
                        ),
                        bgcolor=WHITE,
                        padding=14,
                        border_radius=12,
                        border=ft.Border.all(1, BORDER),
                    )
                )

            page.update()

        def adicionar(e):

            v = numero(valor_fatura.value)

            if not numero_fatura.value or v <= 0:
                return

            faturas.append(
                {
                    "numero": numero_fatura.value,
                    "cliente": entidade.value or "Entidade",
                    "valor": v,
                    "estado": "Pendente",
                }
            )

            numero_fatura.value = ""
            entidade.value = ""
            valor_fatura.value = ""

            atualizar()

        atualizar()

        return ft.Column(
            controls=[
                titulo(
                    "Faturas & Documentos",
                    "Centraliza faturas, recibos e despesas.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Nova fatura",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                controls=[
                                    numero_fatura,
                                    entidade,
                                    valor_fatura,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Registar fatura",
                                adicionar,
                                ft.Icons.ADD,
                            ),
                        ]
                    )
                ),

                lista,
            ],
            spacing=15,
        )

    # ========================================================
    # CRM
    # ========================================================

    def crm_view():

        nome = ft.TextField(
            label="Nome do cliente",
            expand=True,
        )

        empresa = ft.TextField(
            label="Empresa",
            expand=True,
        )

        email = ft.TextField(
            label="Email",
            expand=True,
        )

        estado_cliente = ft.Dropdown(
            label="Estado",
            value="Contacto",
            options=[
                opcao("Contacto"),
                opcao("Proposta"),
                opcao("Negociação"),
                opcao("Fechado"),
                opcao("Perdido"),
            ],
            width=170,
        )

        lista = ft.Column()

        def atualizar():

            lista.controls.clear()

            for c in clientes:

                lista.controls.append(
                    card(
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.PERSON,
                                        color=BLUE,
                                    ),
                                    bgcolor=LIGHT_BLUE,
                                    padding=10,
                                    border_radius=10,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            c["nome"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            c["empresa"],
                                            color=MUTED,
                                        ),
                                        ft.Text(
                                            c["email"],
                                            size=12,
                                            color=MUTED,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        c["estado"],
                                        weight=ft.FontWeight.BOLD,
                                        size=11,
                                    ),
                                    bgcolor=LIGHT_BLUE,
                                    padding=8,
                                    border_radius=8,
                                ),
                            ]
                        )
                    )
                )

            page.update()

        def adicionar(e):

            if not nome.value:
                return

            clientes.append(
                {
                    "nome": nome.value,
                    "empresa": empresa.value or "Particular",
                    "telefone": "",
                    "email": email.value,
                    "estado": estado_cliente.value,
                }
            )

            nome.value = ""
            empresa.value = ""
            email.value = ""

            atualizar()

        atualizar()

        return ft.Column(
            controls=[
                titulo(
                    "CRM — Clientes & Vendas",
                    "Controla contactos e pipeline comercial.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Novo cliente",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                controls=[
                                    nome,
                                    empresa,
                                    email,
                                    estado_cliente,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Adicionar cliente",
                                adicionar,
                                ft.Icons.PERSON_ADD,
                            ),
                        ]
                    )
                ),

                lista,
            ],
            spacing=15,
        )

    # ========================================================
    # ORÇAMENTOS EMPRESARIAIS
    # ========================================================

    def orcamentos_view():

        servico = ft.Dropdown(
            label="Serviço",
            value="Pintura",
            options=[
                opcao("Pintura"),
                opcao("Pavimento"),
                opcao("Pladur"),
                opcao("Casa de banho"),
                opcao("Outro"),
            ],
            width=220,
        )

        area = ft.TextField(
            label="Área / quantidade",
            value="50",
            width=160,
        )

        custo = ft.TextField(
            label="Custo base por unidade (€)",
            value="20",
            width=200,
        )

        margem = ft.TextField(
            label="Margem (%)",
            value="25",
            width=150,
        )

        iva = ft.TextField(
            label="IVA (%)",
            value="23",
            width=120,
        )

        resultado = ft.Column()

        def calcular(e):

            a = numero(area.value)
            c = numero(custo.value)
            m = numero(margem.value)
            i = numero(iva.value)

            custo_total = a * c
            lucro = custo_total * (m / 100)
            venda_sem_iva = custo_total + lucro
            valor_iva = venda_sem_iva * (i / 100)
            total = venda_sem_iva + valor_iva

            resultado.controls = [
                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"Orçamento — {servico.value}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Divider(),
                            ft.Text(
                                f"Custo base: {dinheiro(custo_total)}"
                            ),
                            ft.Text(
                                f"Margem: {dinheiro(lucro)}"
                            ),
                            ft.Text(
                                f"Preço sem IVA: {dinheiro(venda_sem_iva)}"
                            ),
                            ft.Text(
                                f"IVA: {dinheiro(valor_iva)}"
                            ),
                            ft.Text(
                                f"TOTAL: {dinheiro(total)}",
                                size=23,
                                weight=ft.FontWeight.BOLD,
                                color=BLUE,
                            ),
                        ]
                    )
                )
            ]

            page.update()

        return ft.Column(
            controls=[
                titulo(
                    "Gerador de Orçamentos",
                    "Calcula custo, margem, IVA e preço final.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    servico,
                                    area,
                                    custo,
                                    margem,
                                    iva,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Gerar orçamento",
                                calcular,
                                ft.Icons.CALCULATE,
                            ),
                        ],
                        spacing=15,
                    )
                ),

                resultado,
            ],
            spacing=15,
        )

    # ========================================================
    # POS + FIFO
    # ========================================================

    def pos_view():

        produto = ft.Dropdown(
            label="Produto",
            options=[
                opcao(p["nome"])
                for p in produtos
            ],
            value=produtos[0]["nome"],
            width=280,
        )

        quantidade = ft.TextField(
            label="Quantidade",
            value="1",
            width=130,
        )

        lista = ft.Column()

        resultado = ft.Text(
            "Selecione um produto e registe a venda.",
            color=MUTED,
        )

        def atualizar():

            lista.controls.clear()

            for p in produtos:

                valor_stock = p["quantidade"] * p["custo"]

                lista.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.INVENTORY_2,
                                    color=BLUE,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            p["nome"],
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"Código: {p['codigo']}",
                                            color=MUTED,
                                            size=12,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{p['quantidade']} un.",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    dinheiro(valor_stock),
                                    color=GREEN,
                                ),
                            ]
                        ),
                        bgcolor=WHITE,
                        padding=12,
                        border_radius=10,
                        border=ft.Border.all(1, BORDER),
                    )
                )

            page.update()

        def vender(e):

            q = int(numero(quantidade.value))

            if q <= 0:
                return

            selecionado = None

            for p in produtos:
                if p["nome"] == produto.value:
                    selecionado = p
                    break

            if not selecionado:
                return

            if q > selecionado["quantidade"]:
                resultado.value = "Stock insuficiente."
                resultado.color = RED
                page.update()
                return

            # FIFO:
            # a quantidade sai do lote mais antigo disponível.
            selecionado["quantidade"] -= q

            total = q * selecionado["preco"]
            custo = q * selecionado["custo"]
            margem = total - custo

            vendas.append(
                {
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "produto": selecionado["nome"],
                    "quantidade": q,
                    "venda": total,
                    "custo": custo,
                    "margem": margem,
                }
            )

            resultado.value = (
                f"Venda registada: {q} × {selecionado['nome']} = "
                f"{dinheiro(total)} | Margem: {dinheiro(margem)}"
            )
            resultado.color = GREEN

            atualizar()

        atualizar()

        return ft.Column(
            controls=[
                titulo(
                    "POS & Inventário FIFO",
                    "Regista vendas e baixa automaticamente o stock.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    produto,
                                    quantidade,
                                    botao(
                                        "Registar venda",
                                        vender,
                                        ft.Icons.POINT_OF_SALE,
                                        GREEN,
                                    ),
                                ],
                                wrap=True,
                            ),
                            resultado,
                        ]
                    )
                ),

                ft.Text(
                    "Inventário atual",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),

                lista,
            ],
            spacing=15,
        )

    # ========================================================
    # PREVISÃO FINANCEIRA
    # ========================================================

    def previsao_view():

        receita = ft.TextField(
            label="Receita mensal prevista (€)",
            value="8000",
        )

        custos = ft.TextField(
            label="Custos mensais (€)",
            value="5000",
        )

        crescimento = ft.TextField(
            label="Crescimento mensal (%)",
            value="3",
        )

        meses = ft.TextField(
            label="Meses",
            value="12",
        )

        resultado = ft.Column()

        def calcular(e):

            r = numero(receita.value)
            c = numero(custos.value)
            g = numero(crescimento.value) / 100
            n = int(numero(meses.value))

            if n <= 0:
                return

            receita_total = 0
            custo_total = 0
            receita_atual = r

            for _ in range(n):
                receita_total += receita_atual
                custo_total += c
                receita_atual *= 1 + g

            lucro = receita_total - custo_total
            margem = (
                (lucro / receita_total) * 100
                if receita_total
                else 0
            )

            resultado.controls = [
                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Previsão financeira",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Receita acumulada: {dinheiro(receita_total)}"
                            ),
                            ft.Text(
                                f"Custos acumulados: {dinheiro(custo_total)}"
                            ),
                            ft.Text(
                                f"Resultado estimado: {dinheiro(lucro)}",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=GREEN if lucro >= 0 else RED,
                            ),
                            ft.Text(
                                f"Margem estimada: {margem:.1f}%"
                            ),
                        ]
                    )
                )
            ]

            page.update()

        return ft.Column(
            controls=[
                titulo(
                    "Previsão Financeira",
                    "Projeta receita, custos, resultado e margem.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    receita,
                                    custos,
                                    crescimento,
                                    meses,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Calcular previsão",
                                calcular,
                                ft.Icons.TRENDING_UP,
                            ),
                        ]
                    )
                ),

                resultado,
            ],
            spacing=15,
        )

    # ========================================================
    # IMPOSTOS
    # ========================================================

    def impostos_view():

        faturacao = ft.TextField(
            label="Faturação (€)",
            value="50000",
        )

        despesas_empresa = ft.TextField(
            label="Despesas dedutíveis (€)",
            value="28000",
        )

        taxa_imposto = ft.TextField(
            label="Taxa estimada (%)",
            value="21",
        )

        resultado = ft.Column()

        def calcular(e):

            f = numero(faturacao.value)
            d = numero(despesas_empresa.value)
            t = numero(taxa_imposto.value)

            lucro = max(f - d, 0)
            imposto = lucro * t / 100
            depois_imposto = lucro - imposto

            resultado.controls = [
                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Simulação fiscal",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Resultado antes de imposto: {dinheiro(lucro)}"
                            ),
                            ft.Text(
                                f"Imposto estimado: {dinheiro(imposto)}",
                                color=RED,
                            ),
                            ft.Text(
                                f"Resultado após imposto: {dinheiro(depois_imposto)}",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=GREEN,
                            ),
                            ft.Text(
                                "Simulação indicativa. A tributação real depende do enquadramento fiscal da empresa.",
                                size=11,
                                color=MUTED,
                            ),
                        ]
                    )
                )
            ]

            page.update()

        return ft.Column(
            controls=[
                titulo(
                    "Simulador de Impostos",
                    "Estimativa simples de resultado e imposto.",
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    faturacao,
                                    despesas_empresa,
                                    taxa_imposto,
                                ],
                                wrap=True,
                            ),
                            botao(
                                "Calcular imposto",
                                calcular,
                                ft.Icons.ACCOUNT_BALANCE,
                            ),
                        ]
                    )
                ),

                resultado,
            ],
            spacing=15,
        )

    # ========================================================
    # DASHBOARD EMPRESARIAL
    # ========================================================

    def dashboard_empresa():

        stock_valor = sum(
            p["quantidade"] * p["custo"]
            for p in produtos
        )

        vendas_total = sum(
            v["venda"]
            for v in vendas
        )

        margem_total = sum(
            v["margem"]
            for v in vendas
        )

        return ft.Column(
            controls=[
                titulo(
                    "Dashboard Empresarial",
                    "Visão geral do negócio.",
                ),

                ft.Row(
                    controls=[
                        metric_card(
                            "Clientes",
                            str(len(clientes)),
                            "Contactos no CRM",
                            ft.Icons.PEOPLE,
                            BLUE,
                        ),
                        metric_card(
                            "Stock",
                            dinheiro(stock_valor),
                            "Valor pelo custo",
                            ft.Icons.INVENTORY_2,
                            PURPLE,
                        ),
                        metric_card(
                            "Vendas",
                            dinheiro(vendas_total),
                            "Vendas registadas",
                            ft.Icons.POINT_OF_SALE,
                            GREEN,
                        ),
                        metric_card(
                            "Margem",
                            dinheiro(margem_total),
                            "Margem das vendas",
                            ft.Icons.TRENDING_UP,
                            ORANGE,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
                ),

                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Pipeline comercial",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Contacto: {sum(1 for c in clientes if c['estado'] == 'Contacto')}"
                            ),
                            ft.Text(
                                f"Proposta: {sum(1 for c in clientes if c['estado'] == 'Proposta')}"
                            ),
                            ft.Text(
                                f"Negociação: {sum(1 for c in clientes if c['estado'] == 'Negociação')}"
                            ),
                            ft.Text(
                                f"Fechado: {sum(1 for c in clientes if c['estado'] == 'Fechado')}"
                            ),
                        ],
                        spacing=8,
                    )
                ),
            ],
            spacing=15,
        )

    # ========================================================
    # MENU
    # ========================================================

    menu = ft.Column(
        spacing=6,
        width=230,
    )

    def construir_menu():

        menu.controls.clear()

        if estado["perfil"] == "pessoal":

            itens = [
                ("Dashboard", "dashboard", ft.Icons.DASHBOARD),
                ("Movimentos", "transacoes", ft.Icons.RECEIPT_LONG),
                ("Crédito", "credito", ft.Icons.CREDIT_CARD),
                ("Metas", "metas", ft.Icons.FLAG),
                ("Agenda", "agenda", ft.Icons.CALENDAR_MONTH),
                ("Faturas", "faturas", ft.Icons.DESCRIPTION),
            ]

        else:

            itens = [
                ("Dashboard", "dashboard", ft.Icons.DASHBOARD),
                ("CRM", "crm", ft.Icons.PEOPLE),
                ("Orçamentos", "orcamentos", ft.Icons.REQUEST_QUOTE),
                ("POS / FIFO", "pos", ft.Icons.POINT_OF_SALE),
                ("Previsão", "previsao", ft.Icons.TRENDING_UP),
                ("Impostos", "impostos", ft.Icons.ACCOUNT_BALANCE),
            ]

        for nome, modulo, icone in itens:

            ativo = (
                estado["modulo"] == modulo
            )

            menu.controls.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                icone,
                                color=WHITE if ativo else NAVY,
                            ),
                            ft.Text(
                                nome,
                                color=WHITE if ativo else NAVY,
                            ),
                        ]
                    ),
                    bgcolor=BLUE if ativo else WHITE,
                    color=WHITE if ativo else NAVY,
                    width=220,
                    on_click=lambda e, m=modulo: navegar(
                        estado["perfil"],
                        m,
                    ),
                )
            )

    # ========================================================
    # NAVEGAÇÃO
    # ========================================================

    def navegar(perfil, modulo):

        estado["perfil"] = perfil
        estado["modulo"] = modulo

        construir_menu()

        if perfil == "pessoal":

            views = {
                "dashboard": dashboard_pessoal,
                "transacoes": transacoes_view,
                "credito": credito_view,
                "metas": metas_view,
                "agenda": agenda_view,
                "faturas": faturas_view,
            }

        else:

            views = {
                "dashboard": dashboard_empresa,
                "crm": crm_view,
                "orcamentos": orcamentos_view,
                "pos": pos_view,
                "previsao": previsao_view,
                "impostos": impostos_view,
            }

        conteudo.controls.clear()

        if modulo in views:
            conteudo.controls.append(
                views[modulo]()
            )

        page.update()

    # ========================================================
    # CABEÇALHO
    # ========================================================

    ai_online_text = (
        "IA ONLINE"
        if ai_client
        else "IA A AGUARDAR CHAVE"
    )

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.AUTO_AWESOME,
                                color=WHITE,
                                size=25,
                            ),
                            bgcolor=BLUE,
                            padding=10,
                            border_radius=12,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "AURA 360",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT,
                                ),
                                ft.Text(
                                    "Gestão financeira inteligente",
                                    size=12,
                                    color=MUTED,
                                ),
                            ],
                            spacing=1,
                        ),
                    ]
                ),

                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                ai_online_text,
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=GREEN if ai_client else ORANGE,
                            ),
                            bgcolor=LIGHT_GREEN if ai_client else LIGHT_ORANGE,
                            padding=8,
                            border_radius=8,
                        ),
                        botao(
                            "AURA AI",
                            abrir_ai,
                            ft.Icons.AUTO_AWESOME,
                            BLUE,
                        ),
                    ],
                    wrap=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=WHITE,
        padding=15,
        border_radius=16,
        border=ft.Border.all(1, BORDER),
    )

    # ========================================================
    # SELETOR PESSOAL / EMPRESARIAL
    # ========================================================

    def selecionar_pessoal(e):

        navegar(
            "pessoal",
            "dashboard",
        )

    def selecionar_empresa(e):

        navegar(
            "empresa",
            "dashboard",
        )

    perfil_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    "Perfil:",
                    weight=ft.FontWeight.BOLD,
                    color=MUTED,
                ),
                botao(
                    "Pessoal",
                    selecionar_pessoal,
                    ft.Icons.PERSON,
                    BLUE,
                ),
                botao(
                    "Empresarial",
                    selecionar_empresa,
                    ft.Icons.BUSINESS,
                    NAVY,
                ),
                ft.Container(
                    expand=True,
                ),
                ft.Text(
                    datetime.now().strftime("%d/%m/%Y"),
                    color=MUTED,
                ),
            ],
            wrap=True,
        ),
        padding=10,
    )

    # ========================================================
    # LINKS INSTITUCIONAIS
    # ========================================================

    links = ft.Row(
        controls=[
            ft.Text(
                "Links úteis:",
                color=MUTED,
                size=12,
            ),
            ft.TextButton(
                content="Portal das Finanças",
                url="https://www.portaldasfinancas.gov.pt/",
            ),
            ft.TextButton(
                content="AIMA",
                url="https://aima.gov.pt/",
            ),
            ft.TextButton(
                content="Segurança Social",
                url="https://www.seg-social.pt/",
            ),
        ],
        wrap=True,
    )

    # ========================================================
    # CONSTRUÇÃO
    # ========================================================

    construir_menu()

    navegar(
        "pessoal",
        "dashboard",
    )

    page.add(
        header,
        perfil_bar,
        ft.Divider(color=BORDER),
        ft.Row(
            controls=[
                menu,
                ft.Container(
                    content=conteudo,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        ft.Divider(color=BORDER),
        links,
    )


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":
    ft.run(main)
