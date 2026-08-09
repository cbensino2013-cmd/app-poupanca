import flet as ft
import os

def main(page: ft.Page):
    page.title = "Plataforma de Gestão: Empresa, Loja, Particular, Impostos & Simulador IRS"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    # ---------------------------------------------------------
    # ESTRUTURA DE DADOS EM MEMÓRIA
    # ---------------------------------------------------------
    despesas_pessoais = []
    clientes_empresa = []
    
    # Loja & POS
    caixa_inicio_dia = 0.0
    vendas_dia = []
    stock_fifo = []

    # Impostos
    impostos_lista = [
        {"nome": "IUC (Carro)", "tipo": "Particular", "mes": "Mês da Matrícula", "estado": "Pendente"},
        {"nome": "IMI (1ª Prestação)", "tipo": "Particular", "mes": "Maio", "estado": "Pendente"},
        {"nome": "IRS (Entrega)", "tipo": "Particular", "mes": "Abril - Junho", "estado": "Pendente"},
        {"nome": "IVA (Trimestral)", "tipo": "Empresa", "mes": "Fevereiro / Maio / Agosto / Novembro", "estado": "Pendente"},
        {"nome": "IRC / Pag. por Conta", "tipo": "Empresa", "mes": "Julho / Setembro / Dezembro", "estado": "Pendente"},
        {"nome": "Segurança Social (TSU)", "tipo": "Empresa", "mes": "Mensal (Dia 20)", "estado": "Pendente"},
    ]

    # =========================================================
    # 🟢 PERFIL PARTICULAR
    # =========================================================
    txt_rendimento_p = ft.TextField(label="Rendimento / Saldo (€)", value="1500", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())
    txt_meta_p = ft.TextField(label="Meta Poupança (€)", value="300", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())

    txt_nome_p = ft.TextField(label="Nome da Despesa", expand=True)
    txt_valor_p = ft.TextField(label="Valor (€)", keyboard_type=ft.KeyboardType.NUMBER, width=120)
    dd_cat_p = ft.Dropdown(
        label="Categoria", width=150, value="Essencial",
        options=[ft.dropdown.Option("Essencial"), ft.dropdown.Option("Alimentação"), ft.dropdown.Option("Lazer"), ft.dropdown.Option("Transportes"), ft.dropdown.Option("Outros")]
    )

    luz_p = ft.Container(width=18, height=18, border_radius=9, bgcolor=ft.Colors.GREEN)
    lbl_luz_p = ft.Text("Situação Controlada", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    
    alerta_p = ft.Container(
        content=ft.Text("⚠️ ALERTA: Estás a gastar mais de 80% do teu rendimento!", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.RED_800, padding=10, border_radius=6, visible=False
    )

    lbl_diag_p = ft.Text("Regista gastos para teres conselhos personalizados.", size=13)
    lista_desp_p = ft.Column()
    lbl_tot_gastos_p = ft.Text("Gastos: 0.00 €", weight=ft.FontWeight.BOLD)
    lbl_saldo_p = ft.Text("Saldo: 0.00 €", weight=ft.FontWeight.BOLD)

    def add_despesa_p(e):
        if txt_nome_p.value and txt_valor_p.value:
            try:
                despesas_pessoais.append({"nome": txt_nome_p.value, "valor": float(txt_valor_p.value), "cat": dd_cat_p.value})
                txt_nome_p.value = ""
                txt_valor_p.value = ""
                atualizar_particular()
            except ValueError: pass

    def atualizar_particular():
        try: rend = float(txt_rendimento_p.value or 0); meta = float(txt_meta_p.value or 0)
        except ValueError: rend = meta = 0

        tot = sum(d["valor"] for d in despesas_pessoais)
        saldo = rend - tot

        lbl_tot_gastos_p.value = f"Total Gastos: {tot:.2f} €"
        lbl_saldo_p.value = f"Saldo Atual: {saldo:.2f} €"

        alerta_p.visible = (rend > 0 and (tot / rend) >= 0.8)

        if saldo >= meta:
            luz_p.bgcolor = ft.Colors.GREEN; lbl_luz_p.value = "🟢 Poupança Saudável"; lbl_luz_p.color = ft.Colors.GREEN
        elif saldo > 0:
            luz_p.bgcolor = ft.Colors.YELLOW_600; lbl_luz_p.value = "🟡 Atenção à Meta"; lbl_luz_p.color = ft.Colors.YELLOW_600
        else:
            luz_p.bgcolor = ft.Colors.RED; lbl_luz_p.value = "🔴 Orçamento Ultrapassado"; lbl_luz_p.color = ft.Colors.RED

        lista_desp_p.controls.clear()
        for d in despesas_pessoais:
            lista_desp_p.controls.append(ft.ListTile(title=ft.Text(f"{d['nome']} ({d['cat']})"), trailing=ft.Text(f"-{d['valor']:.2f} €", color=ft.Colors.RED_400)))
        page.update()

    perfil_particular = ft.Column([
        ft.Text("👤 Perfil Particular (Gestão Doméstica)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
        alerta_p,
        ft.Row([txt_rendimento_p, txt_meta_p]),
        ft.Card(content=ft.Container(content=ft.Column([ft.Row([luz_p, lbl_luz_p]), lbl_diag_p]), padding=12)),
        ft.Row([txt_nome_p, txt_valor_p, dd_cat_p]),
        ft.ElevatedButton("Adicionar Gastos", icon=ft.Icons.ADD, on_click=add_despesa_p),
        ft.Divider(),
        ft.Row([lbl_tot_gastos_p, lbl_saldo_p], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        lista_desp_p
    ])

    # =========================================================
    # 🏢 PERFIL EMPRESA & CRM
    # =========================================================
    txt_cli_nome = ft.TextField(label="Nome do Contacto / Empresa", expand=True)
    txt_cli_contacto = ft.TextField(label="Telefone / Email", width=180)
    dd_cli_papel = ft.Dropdown(
        label="Papel / Função", width=180, value="Comprador Potencial",
        options=[
            ft.dropdown.Option("Comprador Potencial"),
            ft.dropdown.Option("Comprador Confirmado"),
            ft.dropdown.Option("Parceiro / Divulgador"),
            ft.dropdown.Option("Fornecedor")
        ]
    )
    lista_clientes = ft.Column()

    def add_cliente(e):
        if txt_cli_nome.value:
            clientes_empresa.append({"nome": txt_cli_nome.value, "contacto": txt_cli_contacto.value, "papel": dd_cli_papel.value})
            txt_cli_nome.value = ""; txt_cli_contacto.value = ""
            atualizar_empresa()

    txt_emp_fat = ft.TextField(label="Faturação Prevista (€)", value="5000", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    txt_emp_gastos = ft.TextField(label="Gastos / Custos (€)", value="2200", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    lbl_emp_lucro = ft.Text("Lucro Previsto: 0.00 €", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300)

    txt_orc_cliente = ft.TextField(label="Nome do Cliente", expand=True)
    txt_orc_servico = ft.TextField(label="Descrição do Serviço / Obra", expand=True)
    txt_orc_valor_base = ft.TextField(label="Mão de Obra (€)", value="1200", width=140)
    txt_orc_materiais = ft.TextField(label="Materiais (€)", value="500", width=130)
    dd_orc_iva = ft.Dropdown(label="IVA", width=110, value="23%", options=[ft.dropdown.Option("6%"), ft.dropdown.Option("13%"), ft.dropdown.Option("23%")])
    lbl_orc_resultado = ft.Text("Preenche os dados para gerar o orçamento visual.", size=13)

    def gerar_orcamento_empresa(e):
        try:
            base = float(txt_orc_valor_base.value or 0)
            mat = float(txt_orc_materiais.value or 0)
            subtotal = base + mat
            taxa = float(dd_orc_iva.value.replace("%", "")) / 100.0
            iva = subtotal * taxa
            total = subtotal + iva

            lbl_orc_resultado.value = (
                f"📄 **PROPOSTA DE ORÇAMENTO COMERCIAL**\n"
                f"👤 **Cliente:** {txt_orc_cliente.value or 'Cliente'}\n"
                f"🛠️ **Serviço:** {txt_orc_servico.value or 'Serviço Técnico'}\n"
                f"----------------------------------------\n"
                f"• Mão de Obra: {base:.2f} €\n"
                f"• Materiais: {mat:.2f} €\n"
                f"• Subtotal Liquido: {subtotal:.2f} €\n"
                f"• IVA ({dd_orc_iva.value}): {iva:.2f} €\n"
                f"💰 **TOTAL COM IVA: {total:.2f} €**\n"
                f"----------------------------------------\n"
                f"📌 *Orçamento válido por 30 dias.*"
            )
        except Exception:
            lbl_orc_resultado.value = "⚠️ Erro ao calcular orçamento."
        page.update()

    def atualizar_empresa():
        try:
            fat = float(txt_emp_fat.value or 0)
            gastos = float(txt_emp_gastos.value or 0)
            lucro = fat - gastos
            lbl_emp_lucro.value = f"📈 Lucro Previsto: {lucro:.2f} €"
        except ValueError: pass

        lista_clientes.controls.clear()
        for c in clientes_empresa:
            icone = ft.Icons.RECORD_VOICE_OVER if "Divulgador" in c['papel'] else ft.Icons.SHOPPING_BAG
            lista_clientes.controls.append(
                ft.ListTile(
                    leading=ft.Icon(icone, color=ft.Colors.AMBER),
                    title=ft.Text(f"{c['nome']} ({c['contacto']})"),
                    subtitle=ft.Text(f"Função: {c['papel']}")
                )
            )
        page.update()

    perfil_empresa = ft.Column([
        ft.Text("🏢 Gestão de Negócio & Clientes", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Previsão Financeira Geral", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([txt_emp_fat, txt_emp_gastos]),
                    lbl_emp_lucro
                ]), padding=12
            )
        ),
        ft.Text("👥 Redes de Contactos (Compradores & Divulgadores)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_cli_nome, txt_cli_contacto, dd_cli_papel]),
        ft.ElevatedButton("Registar Contacto", icon=ft.Icons.PERSON_ADD, on_click=add_cliente),
        lista_clientes,
        ft.Divider(),
        ft.Text("📄 Orçamentos Rápidos", size=16, weight=ft.FontWeight.BOLD),
        txt_orc_cliente,
        txt_orc_servico,
        ft.Row([txt_orc_valor_base, txt_orc_materiais, dd_orc_iva]),
        ft.ElevatedButton("Gerar Orçamento", icon=ft.Icons.RECEIPT, on_click=gerar_orcamento_empresa),
        ft.Card(content=ft.Container(content=lbl_orc_resultado, padding=15)),
    ])

    # =========================================================
    # 🏪 MÓDULO DE LOJA, CAIXA & STOCK FIFO
    # =========================================================
    txt_fundo_caixa = ft.TextField(label="Fundo de Maneio / Início do Dia (€)", value="100.00", width=220)
    lbl_status_caixa = ft.Text("Caixa Aberta com 100.00 €", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)

    txt_prod_nome = ft.TextField(label="Produto / Item", expand=True)
    txt_prod_qtd = ft.TextField(label="Qtd Lote", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    txt_prod_custo = ft.TextField(label="Custo Un. (€)", width=110, keyboard_type=ft.KeyboardType.NUMBER)
    lista_stock_fifo = ft.Column()

    txt_venda_item = ft.TextField(label="Item a Vender", expand=True)
    txt_venda_valor = ft.TextField(label="Valor Venda (€)", width=130, keyboard_type=ft.KeyboardType.NUMBER)
    lista_vendas_dia = ft.Column()
    lbl_tot_vendas_dia = ft.Text("Total Vendas do Dia: 0.00 €", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
    lbl_fecho_resumo = ft.Text("Faz o fecho do dia para veres o balanço final da caixa.", size=13)

    def iniciar_caixa(e):
        try:
            global caixa_inicio_dia
            caixa_inicio_dia = float(txt_fundo_caixa.value or 0)
            lbl_status_caixa.value = f"🟢 Caixa Aberta! Fundo Inicial: {caixa_inicio_dia:.2f} €"
        except ValueError: pass
        page.update()

    def dar_entrada_fifo(e):
        if txt_prod_nome.value and txt_prod_qtd.value and txt_prod_custo.value:
            try:
                lote_id = len(stock_fifo) + 1
                stock_fifo.append({
                    "lote": lote_id,
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
                val = float(txt_venda_valor.value)
                item_nome = txt_venda_item.value
                
                for lote in stock_fifo:
                    if lote["item"].lower() == item_nome.lower() and lote["qtd"] > 0:
                        lote["qtd"] -= 1
                        break

                vendas_dia.append({"item": item_nome, "valor": val})
                txt_venda_item.value = ""; txt_venda_valor.value = ""
                atualizar_loja()
            except ValueError: pass

    def realizar_fecho_dia(e):
        tot_vendas = sum(v["valor"] for v in vendas_dia)
        total_em_caixa = caixa_inicio_dia + tot_vendas
        lbl_fecho_resumo.value = (
            f"🔒 **FECHO DE DIA CONCLUÍDO**\n"
            f"• Fundo Inicial de Caixa: {caixa_inicio_dia:.2f} €\n"
            f"• Total de Vendas Registadas: {tot_vendas:.2f} €\n"
            f"💰 **VALOR TOTAL ESPERADO EM CAIXA: {total_em_caixa:.2f} €**\n"
            f"✅ *Relatório do dia guardado.*"
        )
        page.update()

    def atualizar_loja():
        tot_vendas = sum(v["valor"] for v in vendas_dia)
        lbl_tot_vendas_dia.value = f"Total Vendas Hoje: {tot_vendas:.2f} €"

        lista_stock_fifo.controls.clear()
        for s in stock_fifo:
            lista_stock_fifo.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2),
                    title=ft.Text(f"{s['item']} (Lote #{s['lote']})"),
                    subtitle=ft.Text(f"Qtd Restante: {s['qtd']} | Custo Un: {s['custo']:.2f} €")
                )
            )

        lista_vendas_dia.controls.clear()
        for v in vendas_dia:
            lista_vendas_dia.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.POINT_OF_SALE, color=ft.Colors.GREEN),
                    title=ft.Text(v["item"]),
                    trailing=ft.Text(f"+{v['valor']:.2f} €", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)
                )
            )
        page.update()

    perfil_loja = ft.Column([
        ft.Text("🏪 Gestão de Loja, POS & Stock (FIFO)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_200),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🌅 Início do Dia / Fundo de Caixa", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([txt_fundo_caixa, ft.ElevatedButton("Abrir Caixa", icon=ft.Icons.LOCK_OPEN, on_click=iniciar_caixa)]),
                    lbl_status_caixa
                ]), padding=12
            )
        ),
        ft.Text("📦 Entrada de Produto no Stock (Lotes FIFO)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_prod_nome, txt_prod_qtd, txt_prod_custo]),
        ft.ElevatedButton("Registar Entrada no Stock", icon=ft.Icons.ADD_BOX, on_click=dar_entrada_fifo),
        lista_stock_fifo,
        ft.Divider(),
        ft.Text("🛒 Ponto de Venda (Saída Rápida)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([txt_venda_item, txt_venda_valor]),
        ft.ElevatedButton("Registar Venda", icon=ft.Icons.SHOPPING_CART, on_click=registar_venda),
        lbl_tot_vendas_dia,
        lista_vendas_dia,
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🌙 Fecho do Dia", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300),
                    ft.ElevatedButton("Calcular & Fechar Dia", icon=ft.Icons.LOCK, on_click=realizar_fecho_dia),
                    lbl_fecho_resumo
                ]), padding=12
            )
        )
    ])

    # =========================================================
    # 🏛️ ALERTAS DE IMPOSTOS
    # =========================================================
    lista_impostos_ui = ft.Column()

    def alternar_imposto(imp):
        imp["estado"] = "Pago ✅" if imp["estado"] == "Pendente" else "Pendente"
        atualizar_impostos()

    def atualizar_impostos():
        lista_impostos_ui.controls.clear()
        for imp in impostos_lista:
            cor = ft.Colors.GREEN_400 if imp["estado"] == "Pago ✅" else ft.Colors.RED_400
            lista_impostos_ui.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE, color=cor),
                    title=ft.Text(f"{imp['nome']} [{imp['tipo']}]", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Prazo de Pagamento: {imp['mes']}"),
                    trailing=ft.OutlinedButton(imp["estado"], on_click=lambda e, i=imp: alternar_imposto(i))
                )
            )
        page.update()

    perfil_impostos = ft.Column([
        ft.Text("🏛️ Calendário & Alertas de Impostos (Portugal)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300),
        ft.Text("Acompanha os prazos para evitar coimas da Autoridade Tributária:"),
        lista_impostos_ui,
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("💡 Dica Fiscal Importante:", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_200),
                    ft.Text("• **IUC:** Pago no mês da matrícula do veículo."),
                    ft.Text("• **IMI:** Pode ser pago em até 3 prestações (Maio, Agosto, Novembro)."),
                    ft.Text("• **IVA:** Guarda a percentagem de IVA faturada para a liquidação trimestral/mensal.")
                ]), padding=12
            )
        )
    ])

    # =========================================================
    # 🧮 SIMULADOR DE IRS
    # =========================================================
    txt_irs_rendimento = ft.TextField(label="Rendimento Anual Bruto (€)", value="18000", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_irs_retencao = ft.TextField(label="Retenção na Fonte Já Paga (€)", value="2100", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_irs_deducoes = ft.TextField(label="Deduções à Coleta / e-Fatura (€)", value="600", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    dd_irs_estado = ft.Dropdown(
        label="Estado Civil", value="Solteiro / Não Casado", width=220,
        options=[ft.dropdown.Option("Solteiro / Não Casado"), ft.dropdown.Option("Casado / União de Facto (1 Titular)"), ft.dropdown.Option("Casado / União de Facto (2 Titulares)")]
    )
    txt_irs_filhos = ft.TextField(label="Nº de Dependentes", value="0", width=140, keyboard_type=ft.KeyboardType.NUMBER)

    lbl_simulacao_resultado = ft.Text("Preenche os dados acima e clica em 'Simular IRS'.", size=14)

    def calcular_simulacao_irs(e):
        try:
            rend_bruto = float(txt_irs_rendimento.value or 0)
            retencao = float(txt_irs_retencao.value or 0)
            deducoes = float(txt_irs_deducoes.value or 0)
            num_filhos = int(txt_irs_filhos.value or 0)

            # Dedução específica base do IRS (~4.104€)
            materia_coletavel = max(0.0, rend_bruto - 4104.0)

            # Estimativa simplificada de taxa média efetiva por escalões
            if materia_coletavel <= 7703:
                taxa = 0.13
            elif materia_coletavel <= 11623:
                taxa = 0.165
            elif materia_coletavel <= 16472:
                taxa = 0.22
            elif materia_coletavel <= 21321:
                taxa = 0.25
            elif materia_coletavel <= 27146:
                taxa = 0.32
            else:
                taxa = 0.38

            imposto_bruto = materia_coletavel * taxa
            
            # Bonificação por dependente (~600€ por filho)
            deducao_filhos = num_filhos * 600.0
            imposto_liquido = max(0.0, imposto_bruto - deducoes - deducao_filhos)

            # Balanço final entre Retenção efetuada e Imposto Líquido devido
            diferenca = retencao - imposto_liquido

            if diferenca >= 0:
                resultado_texto = (
                    f"🟢 **REEMBOLSO ESTIMADO:** +{diferenca:.2f} €\n\n"
                    f"🎉 Vais receber reembolso da Autoridade Tributária!\n"
                    f"• Imposto Total Calculado: {imposto_liquido:.2f} €\n"
                    f"• Retenção que já pagaste: {retencao:.2f} €"
                )
            else:
                resultado_texto = (
                    f"🔴 **IMPOSTO A PAGAR ESTIMADO:** {abs(diferenca):.2f} €\n\n"
                    f"⚠️ Terás de pagar a diferença às Finanças.\n"
                    f"• Imposto Total Calculado: {imposto_liquido:.2f} €\n"
                    f"• Retenção que já pagaste: {retencao:.2f} €"
                )

            lbl_simulacao_resultado.value = resultado_texto
        except Exception:
            lbl_simulacao_resultado.value = "⚠️ Erro ao calcular a simulação. Verifica os números inseridos."
        page.update()

    perfil_simulador_irs = ft.Column([
        ft.Text("🧮 Simulador de IRS (Estimativa Anual)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
        ft.Text("Calcula quanto podes receber ou pagar no acerto anual de IRS em Portugal:"),
        
        ft.Row([txt_irs_rendimento, txt_irs_retencao]),
        ft.Row([txt_irs_deducoes, dd_irs_estado, txt_irs_filhos]),
        
        ft.ElevatedButton("Calcular Simulação de IRS", icon=ft.Icons.CALCULATE, on_click=calcular_simulacao_irs),
        
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    lbl_simulacao_resultado
                ]), padding=15
            )
        ),
        
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("ℹ️ Nota Informativa:", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_200),
                    ft.Text("Esta simulação utiliza tabelas e deduções médias padrão. O valor exato final depende da validação oficial das faturas no e-Fatura da Autoridade Tributária.")
                ]), padding=12
            )
        )
    ])

    # =========================================================
    # NAVEGAÇÃO PRINCIPAL (5 ABAS)
    # =========================================================
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="🏢 Empresa", icon=ft.Icons.BUSINESS, content=perfil_empresa),
            ft.Tab(text="🏪 Loja & POS", icon=ft.Icons.STORE, content=perfil_loja),
            ft.Tab(text="👤 Particular", icon=ft.Icons.PERSON, content=perfil_particular),
            ft.Tab(text="🏛️ Impostos", icon=ft.Icons.RECEIPT_LONG, content=perfil_impostos),
            ft.Tab(text="🧮 Simulador IRS", icon=ft.Icons.CALCULATE, content=perfil_simulador_irs),
        ],
        expand=True
    )

    page.add(tabs)
    atualizar_particular()
    atualizar_empresa()
    atualizar_loja()
    atualizar_impostos()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)
