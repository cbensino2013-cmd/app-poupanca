import flet as ft
import os
import random

def main(page: ft.Page):
    page.title = "Plataforma de Gestão 360"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # ---------------------------------------------------------
    # BASE DE DADOS EM MEMÓRIA
    # ---------------------------------------------------------
    despesas_pessoais = []
    clientes_empresa = []
    faturas_recibos = [
        {"num": "FT 2026/001", "entidade": "Lidl / Fornecedor", "tipo": "Empresa", "valor": 450.00, "pago": True},
        {"num": "FT 2026/014", "entidade": "EDP Comercial", "tipo": "Particular", "valor": 85.50, "pago": False},
    ]
    
    caixa_inicio_dia = 100.0
    vendas_dia = []
    stock_fifo = []

    impostos_lista = [
        {"nome": "IUC (Carro)", "tipo": "Particular", "mes": "Mês da Matrícula", "pago": False},
        {"nome": "IMI (1ª Prestação)", "tipo": "Particular", "mes": "Maio", "pago": False},
        {"nome": "IRS (Entrega)", "tipo": "Particular", "mes": "Abril - Junho", "pago": True},
        {"nome": "IVA (Trimestral)", "tipo": "Empresa", "mes": "Fev / Mai / Ago / Nov", "pago": False},
        {"nome": "IRC / Pag. por Conta", "tipo": "Empresa", "mes": "Jul / Set / Dez", "pago": False},
        {"nome": "Segurança Social (TSU)", "tipo": "Empresa", "mes": "Mensal (Dia 20)", "pago": True},
    ]

    # Frases do Dia & Dicas do Pro
    frases_motivacionais = [
        "«O sucesso é a soma de pequenos esforços repetidos dia após dia.»",
        "«Gestão não é sobre ter controlo total, é sobre ter clareza de direção.»",
        "«O dinheiro que poupas hoje financia a tua liberdade de amanhã.»",
        "«Pequenos cortes nas despesas desnecessárias geram grandes investimentos no futuro.»"
    ]
    
    dicas_smart = [
        "💡 **Dica de Mercado:** Valida sempre as tuas faturas no *e-Fatura* até ao final de Fevereiro para maximizar as deduções do IRS.",
        "💡 **Dica de Gestão:** No teu negócio, aplica a regra FIFO (First-In, First-Out) para não ficares com stock antigo encalhado.",
        "💡 **Dica Finanças:** Tenta manter pelo menos 20% do teu rendimento mensal alocado a uma reserva de emergência."
    ]

    lbl_frase = ft.Text(random.choice(frases_motivacionais), italic=True, size=14, color=ft.Colors.CYAN_200)
    lbl_dica = ft.Markdown(random.choice(dicas_smart))

    # =========================================================
    # 🏢 PERFIL EMPRESA & CRM
    # =========================================================
    txt_cli_nome = ft.TextField(label="Nome do Contacto / Empresa", expand=True)
    txt_cli_contacto = ft.TextField(label="Telefone / Email", width=180)
    dd_cli_papel = ft.Dropdown(
        label="Função", width=180, value="Comprador Potencial",
        options=[ft.dropdown.Option("Comprador Potencial"), ft.dropdown.Option("Comprador Confirmado"), ft.dropdown.Option("Parceiro / Divulgador"), ft.dropdown.Option("Fornecedor")]
    )
    lista_clientes = ft.Column()

    def add_cliente(e):
        if txt_cli_nome.value:
            clientes_empresa.append({"nome": txt_cli_nome.value, "contacto": txt_cli_contacto.value, "papel": dd_cli_papel.value})
            txt_cli_nome.value = ""; txt_cli_contacto.value = ""
            atualizar_empresa()

    txt_emp_fat = ft.TextField(label="Faturação Prevista (€)", value="5000", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    txt_emp_gastos = ft.TextField(label="Gastos Previstos (€)", value="2200", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    lbl_emp_lucro = ft.Text("Lucro Previsto: 0.00 €", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)

    txt_orc_cliente = ft.TextField(label="Cliente", expand=True)
    txt_orc_servico = ft.TextField(label="Descrição do Serviço", expand=True)
    txt_orc_valor_base = ft.TextField(label="Mão de Obra (€)", value="1200", width=140)
    txt_orc_materiais = ft.TextField(label="Materiais (€)", value="500", width=130)
    dd_orc_iva = ft.Dropdown(label="IVA", width=110, value="23%", options=[ft.dropdown.Option("6%"), ft.dropdown.Option("13%"), ft.dropdown.Option("23%")])
    lbl_orc_resultado = ft.Text("Preenche os campos para simular a proposta comercial.", size=13)

    def gerar_orcamento_empresa(e):
        try:
            base = float(txt_orc_valor_base.value or 0)
            mat = float(txt_orc_materiais.value or 0)
            subtotal = base + mat
            taxa = float(dd_orc_iva.value.replace("%", "")) / 100.0
            iva = subtotal * taxa
            total = subtotal + iva

            lbl_orc_resultado.value = (
                f"📄 **PROPOSTA COMERCIAL**\n"
                f"👤 Cliente: {txt_orc_cliente.value or 'Cliente'}\n"
                f"🛠️ Serviço: {txt_orc_servico.value or 'Serviço Técnico'}\n"
                f"----------------------------------------\n"
                f"• Mão de Obra: {base:.2f} €\n"
                f"• Materiais: {mat:.2f} €\n"
                f"• Subtotal Líquido: {subtotal:.2f} €\n"
                f"• IVA ({dd_orc_iva.value}): {iva:.2f} €\n"
                f"💰 **TOTAL COM IVA: {total:.2f} €**\n"
                f"----------------------------------------\n"
                f"📌 Orçamento válido por 30 dias."
            )
        except Exception:
            lbl_orc_resultado.value = "⚠️ Erro ao calcular orçamento."
        page.update()

    def atualizar_empresa():
        try:
            fat = float(txt_emp_fat.value or 0)
            gastos = float(txt_emp_gastos.value or 0)
            lucro = fat - gastos
            lbl_emp_lucro.value = f"🟢 Lucro Liquido Previsto: {lucro:.2f} €"
        except ValueError: pass

        lista_clientes.controls.clear()
        for c in clientes_empresa:
            lista_clientes.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.CYAN),
                    title=ft.Text(f"{c['nome']} ({c['contacto']})"),
                    subtitle=ft.Text(f"Função: {c['papel']}")
                )
            )
        page.update()

    perfil_empresa = ft.Column([
        ft.Text("🏢 Gestão Corporativa & CRM", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Balanço & Previsão Financeira", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([txt_emp_fat, txt_emp_gastos]),
                    lbl_emp_lucro
                ]), padding=15
            )
        ),
        ft.Text("👥 Carteira de Clientes & Contactos", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_cli_nome, txt_cli_contacto, dd_cli_papel]),
        ft.ElevatedButton("Registar Contacto", icon=ft.Icons.PERSON_ADD, on_click=add_cliente),
        lista_clientes,
        ft.Divider(),
        ft.Text("📄 Gerador de Orçamentos", size=16, weight=ft.FontWeight.BOLD),
        txt_orc_cliente,
        txt_orc_servico,
        ft.Row([txt_orc_valor_base, txt_orc_materiais, dd_orc_iva]),
        ft.ElevatedButton("Gerar Proposta Visual", icon=ft.Icons.RECEIPT, on_click=gerar_orcamento_empresa),
        ft.Card(content=ft.Container(content=lbl_orc_resultado, padding=15)),
    ])

    # =========================================================
    # 🟢 PERFIL PARTICULAR
    # =========================================================
    txt_rendimento_p = ft.TextField(label="Rendimento Mensal (€)", value="1500", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())
    txt_meta_p = ft.TextField(label="Meta de Poupança (€)", value="300", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())

    txt_nome_p = ft.TextField(label="Nome do Gasto", expand=True)
    txt_valor_p = ft.TextField(label="Valor (€)", keyboard_type=ft.KeyboardType.NUMBER, width=120)
    dd_cat_p = ft.Dropdown(
        label="Categoria", width=150, value="Essencial",
        options=[ft.dropdown.Option("Essencial"), ft.dropdown.Option("Alimentação"), ft.dropdown.Option("Lazer"), ft.dropdown.Option("Transportes"), ft.dropdown.Option("Outros")]
    )

    lbl_status_p = ft.Text("🟢 Poupança dentro do objetivo!", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    lista_desp_p = ft.Column()
    lbl_tot_gastos_p = ft.Text("Gastos: 0.00 €", weight=ft.FontWeight.BOLD)
    lbl_saldo_p = ft.Text("Saldo: 0.00 €", weight=ft.FontWeight.BOLD)

    def add_despesa_p(e):
        if txt_nome_p.value and txt_valor_p.value:
            try:
                despesas_pessoais.append({"nome": txt_nome_p.value, "valor": float(txt_valor_p.value), "cat": dd_cat_p.value})
                txt_nome_p.value = ""; txt_valor_p.value = ""
                atualizar_particular()
            except ValueError: pass

    def atualizar_particular():
        try: rend = float(txt_rendimento_p.value or 0); meta = float(txt_meta_p.value or 0)
        except ValueError: rend = meta = 0

        tot = sum(d["valor"] for d in despesas_pessoais)
        saldo = rend - tot

        lbl_tot_gastos_p.value = f"🔴 Gastos: -{tot:.2f} €"
        lbl_saldo_p.value = f"🟢 Saldo Restante: {saldo:.2f} €"

        if saldo >= meta:
            lbl_status_p.value = "🟢 Situação Excelente: Meta de poupança atingida!"; lbl_status_p.color = ft.Colors.GREEN_400
        elif saldo > 0:
            lbl_status_p.value = "🟡 Atenção: Abaixo da meta de poupança estipulada."; lbl_status_p.color = ft.Colors.AMBER_400
        else:
            lbl_status_p.value = "🔴 ALERTA: Orçamento Ultrapassado!"; lbl_status_p.color = ft.Colors.RED_400

        lista_desp_p.controls.clear()
        for d in despesas_pessoais:
            lista_desp_p.controls.append(
                ft.ListTile(
                    leading=ft.Text("🔴 ⬇️", size=16),
                    title=ft.Text(f"{d['nome']} ({d['cat']})"),
                    trailing=ft.Text(f"-{d['valor']:.2f} €", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD)
                )
            )
        page.update()

    perfil_particular = ft.Column([
        ft.Text("👤 Perfil Particular (Orçamento Familiar)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([txt_rendimento_p, txt_meta_p]),
                    lbl_status_p
                ]), padding=15
            )
        ),
        ft.Row([txt_nome_p, txt_valor_p, dd_cat_p]),
        ft.ElevatedButton("Registar Despesa", icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, on_click=add_despesa_p),
        ft.Divider(),
        ft.Row([lbl_tot_gastos_p, lbl_saldo_p], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        lista_desp_p
    ])

    # =========================================================
    # 📑 MÓDULO DE FATURAS & RECIBOS
    # =========================================================
    txt_fat_num = ft.TextField(label="Nº da Fatura / Recibo", expand=True)
    txt_fat_entidade = ft.TextField(label="Emitente / Fornecedor", expand=True)
    txt_fat_valor = ft.TextField(label="Valor (€)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    dd_fat_tipo = ft.Dropdown(
        label="Âmbito", width=140, value="Empresa",
        options=[ft.dropdown.Option("Empresa"), ft.dropdown.Option("Particular")]
    )
    lista_faturas_ui = ft.Column()

    def alternar_pago_fatura(fat):
        fat["pago"] = not fat["pago"]
        atualizar_faturas()

    def add_fatura(e):
        if txt_fat_num.value and txt_fat_valor.value:
            try:
                faturas_recibos.append({
                    "num": txt_fat_num.value,
                    "entidade": txt_fat_entidade.value or "Geral",
                    "tipo": dd_fat_tipo.value,
                    "valor": float(txt_fat_valor.value),
                    "pago": False
                })
                txt_fat_num.value = ""; txt_fat_entidade.value = ""; txt_fat_valor.value = ""
                atualizar_faturas()
            except ValueError: pass

    def atualizar_faturas():
        lista_faturas_ui.controls.clear()
        for f in faturas_recibos:
            status_icon = "🟢 ⬆️ PAGO" if f["pago"] else "🔴 ⬇️ PENDENTE"
            status_color = ft.Colors.GREEN_400 if f["pago"] else ft.Colors.RED_400
            
            lista_faturas_ui.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{f['num']} - {f['entidade']}", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(f"Âmbito: {f['tipo']} | Valor: {f['valor']:.2f} €", size=13, color=ft.Colors.GREY_400)
                            ], expand=True),
                            ft.OutlinedButton(
                                status_icon,
                                style=ft.ButtonStyle(color=status_color),
                                on_click=lambda e, fat=f: alternar_pago_fatura(fat)
                            )
                        ]), padding=12
                    )
                )
            )
        page.update()

    perfil_faturas = ft.Column([
        ft.Text("📑 Repositório de Faturas & Recibos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300),
        ft.Text("Guarda o registo de todas as faturas e altera o estado com 1 clique:"),
        ft.Row([txt_fat_num, txt_fat_entidade]),
        ft.Row([txt_fat_valor, dd_fat_tipo, ft.ElevatedButton("Guardar Fatura", icon=ft.Icons.SAVE, on_click=add_fatura)]),
        ft.Divider(),
        lista_faturas_ui
    ])

    # =========================================================
    # 🏪 MÓDULO LOJA & POS
    # =========================================================
    txt_fundo_caixa = ft.TextField(label="Fundo de Caixa (€)", value="100.00", width=180)
    lbl_status_caixa = ft.Text("🟢 Caixa Pronta", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)

    txt_prod_nome = ft.TextField(label="Produto", expand=True)
    txt_prod_qtd = ft.TextField(label="Qtd", width=90, keyboard_type=ft.KeyboardType.NUMBER)
    txt_prod_custo = ft.TextField(label="Custo Un (€)", width=110, keyboard_type=ft.KeyboardType.NUMBER)
    lista_stock_fifo = ft.Column()

    txt_venda_item = ft.TextField(label="Item a Vender", expand=True)
    txt_venda_valor = ft.TextField(label="Valor Venda (€)", width=130, keyboard_type=ft.KeyboardType.NUMBER)
    lista_vendas_dia = ft.Column()
    lbl_tot_vendas_dia = ft.Text("Total Vendas: 0.00 €", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)

    def dar_entrada_fifo(e):
        if txt_prod_nome.value and txt_prod_qtd.value and txt_prod_custo.value:
            try:
                stock_fifo.append({
                    "lote": len(stock_fifo) + 1,
                    "item": txt_prod_nome.value,
                    "qtd": int(txt_prod_qtd.value),
                    "custo": float(txt_prod_custo.value)
                })
                txt_prod_nome.value = ""; txt_prod_qtd.value = ""; txt_prod_custo.value = ""
                atualizar_loja()
            except ValueError: pass

    def registar_venda(e):
        if txt_venda_item.value and txt_venda_valor.value:
            try:
                vendas_dia.append({"item": txt_venda_item.value, "valor": float(txt_venda_valor.value)})
                txt_venda_item.value = ""; txt_venda_valor.value = ""
                atualizar_loja()
            except ValueError: pass

    def atualizar_loja():
        tot_vendas = sum(v["valor"] for v in vendas_dia)
        lbl_tot_vendas_dia.value = f"🟢 Total Vendas Hoje: +{tot_vendas:.2f} €"

        lista_stock_fifo.controls.clear()
        for s in stock_fifo:
            lista_stock_fifo.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2),
                    title=ft.Text(f"{s['item']} (Lote #{s['lote']})"),
                    subtitle=ft.Text(f"Qtd: {s['qtd']} | Custo: {s['custo']:.2f} €")
                )
            )

        lista_vendas_dia.controls.clear()
        for v in vendas_dia:
            lista_vendas_dia.controls.append(
                ft.ListTile(
                    leading=ft.Text("🟢 ⬆️", size=16),
                    title=ft.Text(v["item"]),
                    trailing=ft.Text(f"+{v['valor']:.2f} €", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)
                )
            )
        page.update()

    perfil_loja = ft.Column([
        ft.Text("🏪 Gestão de Loja, POS & Stock", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_300),
        ft.Card(
            content=ft.Container(
                content=ft.Row([txt_fundo_caixa, lbl_status_caixa], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=12
            )
        ),
        ft.Text("📦 Entrada no Stock (FIFO)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_prod_nome, txt_prod_qtd, txt_prod_custo]),
        ft.ElevatedButton("Registar Lote", icon=ft.Icons.ADD_BOX, on_click=dar_entrada_fifo),
        lista_stock_fifo,
        ft.Divider(),
        ft.Text("🛒 Ponto de Venda Rápido", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_venda_item, txt_venda_valor]),
        ft.ElevatedButton("Registar Venda", icon=ft.Icons.SHOPPING_CART, on_click=registar_venda),
        lbl_tot_vendas_dia,
        lista_vendas_dia
    ])

    # =========================================================
    # 🏛️ ALERTAS DE IMPOSTOS
    # =========================================================
    lista_impostos_ui = ft.Column()

    def alternar_imposto(imp):
        imp["pago"] = not imp["pago"]
        atualizar_impostos()

    def atualizar_impostos():
        lista_impostos_ui.controls.clear()
        for imp in impostos_lista:
            status_txt = "🟢 ⬆️ PAGO" if imp["pago"] else "🔴 ⬇️ PENDENTE"
            status_col = ft.Colors.GREEN_400 if imp["pago"] else ft.Colors.RED_400
            
            lista_impostos_ui.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE, color=status_col),
                    title=ft.Text(f"{imp['nome']} [{imp['tipo']}]", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Prazo: {imp['mes']}"),
                    trailing=ft.OutlinedButton(
                        status_txt,
                        style=ft.ButtonStyle(color=status_col),
                        on_click=lambda e, i=imp: alternar_imposto(i)
                    )
                )
            )
        page.update()

    perfil_impostos = ft.Column([
        ft.Text("🏛️ Calendário Fiscal & Impostos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300),
        lista_impostos_ui
    ])

    # =========================================================
    # 🧮 SIMULADOR DE IRS
    # =========================================================
    txt_irs_rendimento = ft.TextField(label="Rendimento Anual Bruto (€)", value="18000", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_irs_retencao = ft.TextField(label="Retenção Paga (€)", value="2100", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_irs_deducoes = ft.TextField(label="Deduções e-Fatura (€)", value="600", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_irs_filhos = ft.TextField(label="Dependentes", value="0", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    lbl_simulacao_resultado = ft.Text("Clica abaixo para simular.", size=14)

    def calcular_simulacao_irs(e):
        try:
            rend_bruto = float(txt_irs_rendimento.value or 0)
            retencao = float(txt_irs_retencao.value or 0)
            deducoes = float(txt_irs_deducoes.value or 0)
            num_filhos = int(txt_irs_filhos.value or 0)

            materia_coletavel = max(0.0, rend_bruto - 4104.0)
            taxa = 0.22 if materia_coletavel <= 16472 else 0.25
            imposto_bruto = materia_coletavel * taxa
            imposto_liquido = max(0.0, imposto_bruto - deducoes - (num_filhos * 600.0))
            diferenca = retencao - imposto_liquido

            if diferenca >= 0:
                lbl_simulacao_resultado.value = f"🟢 ⬆️ REEMBOLSO ESTIMADO: +{diferenca:.2f} €\n🎉 Recebes acerto das Finanças!"
            else:
                lbl_simulacao_resultado.value = f"🔴 ⬇️ IMPOSTO A PAGAR ESTIMADO: -{abs(diferenca):.2f} €\n⚠️ Terás de pagar a diferença."
        except Exception:
            lbl_simulacao_resultado.value = "⚠️ Erro no cálculo."
        page.update()

    perfil_simulador_irs = ft.Column([
        ft.Text("🧮 Simulador de IRS", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
        ft.Row([txt_irs_rendimento, txt_irs_retencao]),
        ft.Row([txt_irs_deducoes, txt_irs_filhos]),
        ft.ElevatedButton("Calcular Simulação", icon=ft.Icons.CALCULATE, on_click=calcular_simulacao_irs),
        ft.Card(content=ft.Container(content=lbl_simulacao_resultado, padding=15))
    ])

    # =========================================================
    # HEADER & HERO SECTION (BOAS-VINDAS)
    # =========================================================
    header_hero = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER, size=28),
                    ft.Text("Bem-vindo de volta! 👋", size=22, weight=ft.FontWeight.BOLD),
                ]),
                lbl_frase,
                ft.Divider(color=ft.Colors.GREY_800),
                lbl_dica
            ]),
            padding=18,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_GREY_900, ft.Colors.BLACK]
            )
        )
    )

    # =========================================================
    # NAVEGAÇÃO PRINCIPAL (BOTÕES COM ESTILO)
    # =========================================================
    conteudo_principal = ft.Container(content=perfil_empresa, expand=True)

    def mudar_aba(e):
        idx = int(e.control.data)
        seccoes = [perfil_empresa, perfil_loja, perfil_particular, perfil_faturas, perfil_impostos, perfil_simulador_irs]
        conteudo_principal.content = seccoes[idx]
        page.update()

    botoes_navegacao = ft.Row(
        controls=[
            ft.ElevatedButton("🏢 Empresa", data=0, on_click=mudar_aba),
            ft.ElevatedButton("🏪 Loja & POS", data=1, on_click=mudar_aba),
            ft.ElevatedButton("👤 Particular", data=2, on_click=mudar_aba),
            ft.ElevatedButton("📑 Faturas/Recibos", data=3, on_click=mudar_aba),
            ft.ElevatedButton("🏛️ Impostos", data=4, on_click=mudar_aba),
            ft.ElevatedButton("🧮 IRS", data=5, on_click=mudar_aba),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # Montagem final
    page.add(
        header_hero,
        botoes_navegacao,
        ft.Divider(),
        conteudo_principal
    )

    atualizar_particular()
    atualizar_empresa()
    atualizar_loja()
    atualizar_faturas()
    atualizar_impostos()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)
