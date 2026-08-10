import flet as ft
import os
import random

def main(page: ft.Page):
    # -------------------------------------------------------------------------
    # CONFIGURAÇÕES DE TEMA & PÁGINA
    # -------------------------------------------------------------------------
    page.title = "AURA 360 | Gestão Financeira & Otimização B2B/B2C"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    # -------------------------------------------------------------------------
    # 🤖 WIDGET FLUTUANTE DA IA NO RODAPÉ (AURA AI)
    # -------------------------------------------------------------------------
    chat_messages = ft.Column(scroll=ft.ScrollMode.AUTO, height=220)
    user_input = ft.TextField(hint_text="Pergunte sobre IRS, Créditos, Obras, AIMA...", expand=True)

    def send_message(e):
        if user_input.value.strip():
            chat_messages.controls.append(
                ft.Text(f"👤 Você: {user_input.value}", weight=ft.FontWeight.BOLD)
            )
            txt = user_input.value.lower()
            res = "🤖 AURA AI: "
            if "credito" in txt or "divida" in txt or "juntar" in txt:
                res += "Utilize o simulador de 'Créditos'! Ao juntar créditos pessoais e cartões, pode reduzir significativamente a sua taxa de esforço."
            elif "orcamento" in txt or "obra" in txt or "pintura" in txt or "piso" in txt:
                res += "No separador 'Orçamentos de Obras', selecione o tipo de serviço e a área em m² para obter uma estimativa com IVA a 6%."
            elif "banco" in txt or "conta" in txt:
                res += "Bancos como ActivoBank, Moey! e Banco CTT não cobram comissão de manutenção base. Consulte os detalhes no botão 'Abrir Conta'."
            elif "aima" in txt or "residencia" in txt:
                res += "Pode aceder ao portal oficial da AIMA diretamente através do botão no cabeçalho da aplicação."
            elif "irs" in txt or "fatura" in txt:
                res += "Valide as suas faturas pendentes no e-Fatura. Despesas de saúde com IVA a 23% requerem receita médica associada."
            else:
                res += "Estou à disposição para ajudar com dúvidas sobre orçamentos, crédito, finanças pessoais e serviços institucionais!"

            chat_messages.controls.append(ft.Text(res, color=ft.Colors.BLUE_800))
            user_input.value = ""
            page.update()

    ai_dialog = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.BLUE_600), ft.Text("AURA AI - Assistente 24/7")]),
        content=ft.Container(
            content=ft.Column([
                chat_messages,
                ft.Row([user_input, ft.IconButton(ft.Icons.SEND, on_click=send_message, icon_color=ft.Colors.BLUE_600)])
            ]),
            width=400, height=300
        )
    )

    def open_ai_chat(e):
        page.overlay.append(ai_dialog)
        ai_dialog.open = True
        page.update()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.CHAT_BUBBLE,
        text="AURA AI",
        bgcolor=ft.Colors.BLUE_700,
        content_color=ft.Colors.WHITE,
        on_click=open_ai_chat
    )

    # -------------------------------------------------------------------------
    # 🏦 MODAL: ABERTURA DE CONTA BANCÁRIA
    # -------------------------------------------------------------------------
    bank_dialog = ft.AlertDialog(
        title=ft.Text("🏦 Guia de Abertura de Conta Bancária"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Melhores Opções em Portugal (Sem Comissões):", weight=ft.FontWeight.BOLD),
                ft.ListTile(leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE), title=ft.Text("ActivoBank / Moey!"), subtitle=ft.Text("Conta 100% gratuita com cartão e app móvel.")),
                ft.ListTile(leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE), title=ft.Text("Banco CTT"), subtitle=ft.Text("Isento de manutenção base com balcões físicos.")),
                ft.Divider(),
                ft.Text("📄 Documentos Necessários:", weight=ft.FontWeight.BOLD),
                ft.Text("1. Documento de Identificação (CC, Passaporte ou Título AIMA)\n2. NIF (Número de Identificação Fiscal)\n3. Comprovativo de Morada (Fatura da Água/Luz/Atestado de Junta)\n4. Comprovativo de Emprego (Recibo de Vencimento/Contrato)"),
            ], scroll=ft.ScrollMode.AUTO),
            width=450, height=350
        )
    )

    def open_bank_modal(e):
        page.overlay.append(bank_dialog)
        bank_dialog.open = True
        page.update()

    # -------------------------------------------------------------------------
    # 💳 SEPARADOR 1: REESTRUTURAÇÃO E CONSOLIDAÇÃO DE CRÉDITOS
    # -------------------------------------------------------------------------
    inp_rendimento = ft.TextField(label="Rendimento Líquido Mensal (€)", value="1200", width=220)
    inp_ch = ft.TextField(label="Crédito Habitação (€/mês)", value="450", width=220)
    inp_outros_cred = ft.TextField(label="Outros Créditos/Cartões (€/mês)", value="300", width=220)

    res_taxa = ft.Text("Taxa de Esforço Atual: --%", size=16, weight=ft.FontWeight.BOLD)
    res_recomendacao = ft.Container(padding=12, border_radius=8)

    def simular_reestruturacao(e):
        try:
            r = float(inp_rendimento.value)
            ch = float(inp_ch.value)
            outros = float(inp_outros_cred.value)
            total_prest = ch + outros
            taxa = (total_prest / r) * 100

            res_taxa.value = f"Taxa de Esforço Atual: {taxa:.1f}%"

            if taxa <= 35:
                res_recomendacao.bgcolor = ft.Colors.GREEN_100
                res_recomendacao.content = ft.Text("🟢 ZONA SAUDÁVEL: A sua taxa de esforço está controlada. Se tiver margem, compensa amortizar no crédito de maior taxa de juro.", color=ft.Colors.GREEN_900)
            elif taxa <= 50:
                res_recomendacao.bgcolor = ft.Colors.ORANGE_100
                res_recomendacao.content = ft.Text(f"🟡 ATENÇÃO - RISCO MODERADO: Ao consolidar os seus outros créditos ({outros:.0f}€), a prestação mensal estimada pode baixar para cerca de {outros*0.5:.0f}€/mês!", color=ft.Colors.ORANGE_900)
            else:
                res_recomendacao.bgcolor = ft.Colors.RED_100
                res_recomendacao.content = ft.Text("🔴 ZONA CRÍTICA: Taxa superior a 50%! Recomendamos acionar o plano de reestruturação urgente (PARI/PERSI) ou requerer consolidação de créditos.", color=ft.Colors.RED_900)
            
            page.update()
        except:
            res_taxa.value = "Por favor, insira valores válidos."
            page.update()

    view_creditos = ft.Container(
        content=ft.Column([
            ft.Text("💳 Reestruturação, Consolidação & Taxa de Esforço", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Row([inp_rendimento, inp_ch, inp_outros_cred], wrap=True),
            ft.ElevatedButton("Simular Poupança & Taxa de Esforço", on_click=simular_reestruturacao, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
            res_taxa,
            res_recomendacao,
        ]),
        padding=15, bgcolor=ft.Colors.WHITE, border_radius=10, border=ft.border.all(1, ft.Colors.GREY_300)
    )

    # -------------------------------------------------------------------------
    # 🏗️ SEPARADOR 2: MOTOR DE ORÇAMENTOS DE OBRAS (B2B/B2C)
    # -------------------------------------------------------------------------
    dd_servico = ft.Dropdown(
        label="Tipo de Serviço",
        options=[
            ft.dropdown.Option("🎨 Pintura de Interiores"),
            ft.dropdown.Option("🪵 Aplicação de Flutuante/Vinil"),
            ft.dropdown.Option("🧱 Tecto Falso em Pladur"),
            ft.dropdown.Option("🚿 Remodelação de Casa de Banho"),
        ],
        value="🎨 Pintura de Interiores",
        width=250
    )
    inp_area = ft.TextField(label="Área Estimada (m²)", value="50", width=150)
    dd_gama = ft.Dropdown(
        label="Gama de Materiais",
        options=[
            ft.dropdown.Option("Económica"),
            ft.dropdown.Option("Profissional"),
            ft.dropdown.Option("Premium"),
        ],
        value="Profissional",
        width=180
    )

    res_orcamento = ft.Column()

    def calcular_orcamento(e):
        try:
            area = float(inp_area.value)
            servico = dd_servico.value
            gama = dd_gama.value

            # Valores base por m²
            precos_base = {
                "🎨 Pintura de Interiores": 12,
                "🪵 Aplicação de Flutuante/Vinil": 22,
                "🧱 Tecto Falso em Pladur": 28,
                "🚿 Remodelação de Casa de Banho": 85
            }

            multiplicador = {"Económica": 0.85, "Profissional": 1.0, "Premium": 1.35}[gama]
            
            custo_m2 = precos_base.get(servico, 15) * multiplicador
            subtotal_materiais = (custo_m2 * 0.4) * area * 1.10  # +10% margem desperdício
            subtotal_mao_obra = (custo_m2 * 0.6) * area
            subtotal = subtotal_materiais + subtotal_mao_obra
            iva = subtotal * 0.06  # Taxa reduzida de IVA para remodelações
            total = subtotal + iva

            res_orcamento.controls = [
                ft.Divider(),
                ft.Text(f"📋 Estimativa para: {servico} ({area} m² - Gama {gama})", weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"• Materiais (+10% desperdício): {subtotal_materiais:.2f} €"),
                ft.Text(f"• Mão de Obra Especializada: {subtotal_mao_obra:.2f} €"),
                ft.Text(f"• IVA (Taxa Reduzida 6%): {iva:.2f} €"),
                ft.Text(f"💰 VALOR TOTAL ESTIMADO: {total:.2f} €", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
            ]
            page.update()
        except:
            res_orcamento.controls = [ft.Text("Por favor, introduza uma área válida.", color=ft.Colors.RED)]
            page.update()

    view_obras = ft.Container(
        content=ft.Column([
            ft.Text("🏗️ Gerador de Orçamentos de Remodelação", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Row([dd_servico, inp_area, dd_gama], wrap=True),
            ft.ElevatedButton("Gerar Orçamento Rigoroso", on_click=calcular_orcamento, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
            res_orcamento
        ]),
        padding=15, bgcolor=ft.Colors.WHITE, border_radius=10, border=ft.border.all(1, ft.Colors.GREY_300)
    )

    # -------------------------------------------------------------------------
    # 📄 SEPARADOR 3: GESTÃO DE FATURAS E E-FATURA
    # -------------------------------------------------------------------------
    faturas = [
        {"num": "FT 2026/089", "entidade": "Supermercado Continente", "cat": "🛒 Despesas Gerais", "valor": 124.50, "pago": True},
        {"num": "FT 2026/102", "entidade": "Farmácia Central", "cat": "⚕️ Saúde", "valor": 45.20, "pago": True},
    ]

    lista_faturas_col = ft.Column()
    for f in faturas:
        lista_faturas_col.controls.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.BLUE_600),
                title=ft.Text(f"{f['num']} - {f['entidade']}"),
                subtitle=ft.Text(f"{f['cat']} | Status: {'Pago' if f['pago'] else 'Pendente'}"),
                trailing=ft.Text(f"{f['valor']:.2f} €", weight=ft.FontWeight.BOLD)
            )
        )

    view_faturas = ft.Container(
        content=ft.Column([
            ft.Text("📄 Gestão de Faturas & e-Fatura", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            lista_faturas_col,
            ft.Row([
                ft.ElevatedButton("📷 Anexar Foto da Fatura", icon=ft.Icons.CAMERA_ALT),
                ft.ElevatedButton("Validar no e-Fatura", icon=ft.Icons.CHECK_CIRCLE)
            ], wrap=True)
        ]),
        padding=15, bgcolor=ft.Colors.WHITE, border_radius=10, border=ft.border.all(1, ft.Colors.GREY_300)
    )

    # -------------------------------------------------------------------------
    # 🌐 CABEÇALHO SUPERIOR COM LINKS INSTITUCIONAIS
    # -------------------------------------------------------------------------
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("AURA 360", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Row([
                    ft.TextButton("🏦 Abrir Conta", on_click=open_bank_modal),
                    ft.ElevatedButton("🌐 AIMA", icon=ft.Icons.LINK, url="https://aima.gov.pt"),
                    ft.ElevatedButton("📅 SIGA", icon=ft.Icons.CALENDAR_MONTH, url="https://siga.marcacaodeatendimento.pt"),
                ], wrap=True)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
        ]),
        padding=10, bgcolor=ft.Colors.WHITE, border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300))
    )

    # -------------------------------------------------------------------------
    # MONTAGEM FINAL DA APLICAÇÃO EM SEPARADORES (TABS)
    # -------------------------------------------------------------------------
    page.add(
        header,
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="💳 Créditos & Amortização", content=view_creditos),
                ft.Tab(text="🏗️ Orçamentos de Obras", content=view_obras),
                ft.Tab(text="📄 Faturas & Impostos", content=view_faturas),
            ],
            expand=True
        )
    )

ft.app(target=main)
