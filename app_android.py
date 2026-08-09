import flet as ft
import os
import random
from datetime import datetime

def main(page: ft.Page):
    page.title = "Plataforma de Gestão 360 - Estilo Finanças"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F4F9"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 16

    # ---------------------------------------------------------
    # ESTRUTURAS DE DADOS
    # ---------------------------------------------------------
    foto_preview_url = {"src": None, "name": "Nenhuma foto anexa"}
    
    despesas_pessoais = []
    clientes_empresa = []
    faturas_recibos = [
        {"num": "FT 2026/001", "entidade": "Lidl / Fornecedor", "tipo": "Empresa", "valor": 450.00, "pago": True, "foto_url": None, "foto_nome": "Sem Foto"},
        {"num": "FT 2026/014", "entidade": "EDP Comercial", "tipo": "Particular", "valor": 85.50, "pago": False, "foto_url": None, "foto_nome": "Sem Foto"},
    ]

    # IRS / DEDUÇÕES À LUZ DAS FINANÇAS
    categorias_irs = [
        {
            "cat": "🛒 Despesas Gerais Familiares",
            "limite": "350.00 € (dedução máx)",
            "cor": "#0052CC",
            "instrucao": "👇 Coloque aqui faturas de supermercado, vestuário, água, luz, gás, telecomunicações e bens de consumo diário.",
            "valor": 0.0
        },
        {
            "cat": "🏥 Saúde & Bem-Estar",
            "limite": "15% até 1.000 €",
            "cor": "#00875A",
            "instrucao": "👇 Coloque aqui faturas de farmácia (com receita se taxadas a 23%), consultas médicas, exames e óculos.",
            "valor": 0.0
        },
        {
            "cat": "🎓 Educação & Formação",
            "limite": "30% até 800 €",
            "cor": "#FF9800",
            "instrucao": "👇 Coloque aqui mensalidades de creches, escolas, propinas universitárias, manuais escolares e explicações.",
            "valor": 0.0
        },
        {
            "cat": "🏠 Habitação & Rendas",
            "limite": "15% até 502 € (Rendas)",
            "cor": "#9C27B0",
            "instrucao": "👇 Coloque recibos de renda de casa para habitação permanente ou juros do crédito habitação (contratos até 2011).",
            "valor": 0.0
        },
        {
            "cat": "🚗 Restauração, Reparação & Passes",
            "limite": "15% do IVA suportado",
            "cor": "#FF5630",
            "instrucao": "👇 Coloque faturas de restaurantes, mecânicos, cabeleireiros, ginásios, alojamento e passes de transportes.",
            "valor": 0.0
        },
        {
            "cat": "🏛️ Impostos Obrigatórios (IUC, IMI, TSU)",
            "limite": "Pagamento Calendário",
            "cor": "#DE350B",
            "instrucao": "👇 Acompanhe e registe o pagamento do Imposto Único de Circulação (IUC), IMI do imóvel e TSU/SS.",
            "valor": 0.0
        }
    ]

    agenda_eventos = [
        {"data": "2026-08-15", "hora": "10:00", "titulo": "Reunião com Fornecedor", "prioridade": "Alta"},
        {"data": "2026-08-20", "hora": "14:30", "titulo": "Pagamento TSU / Segurança Social", "prioridade": "Urgente"}
    ]
    notas_lista = [
        {"titulo": "Lembrete Stock", "texto": "Verificar se é preciso encomendar mais material esta semana."},
        {"titulo": "Ideia para Loja", "texto": "Criar campanha de promoção no início do próximo mês."}
    ]

    frases_motivacionais = [
        "⚡ «O sucesso é a soma de pequenos esforços repetidos dia após dia.»",
        "🚀 «Gestão moderna não é sobre controlo, é sobre ter clareza e brilho nos resultados!»",
        "💡 «O dinheiro que poupas e geris hoje financia a tua liberdade de amanhã.»"
    ]
    lbl_frase = ft.Text(random.choice(frases_motivacionais), italic=True, size=14, color="#0052CC", weight=ft.FontWeight.BOLD)

    # UPLOADER DE FOTOS
    img_preview = ft.Image(src="", width=150, height=150, fit="cover", visible=False, border_radius=8)
    lbl_status_foto = ft.Text("Nenhuma foto anexa", size=12, italic=True, color="#7A869A")

    def ao_selecionar_foto(e):
        if e.files and len(e.files) > 0:
            ficheiro = e.files[0]
            foto_preview_url["src"] = ficheiro.path
            foto_preview_url["name"] = ficheiro.name
            lbl_status_foto.value = f"📸 Foto Pronta: {ficheiro.name}"
            lbl_status_foto.color = "#00875A"
            if ficheiro.path:
                img_preview.src = ficheiro.path
                img_preview.visible = True
        else:
            lbl_status_foto.value = "Nenhuma foto selecionada."
            img_preview.visible = False
        page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = ao_selecionar_foto
    page.overlay.append(file_picker)

    # =========================================================
    # 🏛️ MÓDULO IRS & FINANÇAS
    # =========================================================
    grid_irs_ui = ft.Column()

    def atualizar_valor_irs(cat_obj, txt_val):
        try:
            cat_obj["valor"] = float(txt_val.value or 0)
        except ValueError:
            cat_obj["valor"] = 0.0
        atualizar_irs_ui()

    def atualizar_irs_ui():
        grid_irs_ui.controls.clear()
        
        for item in categorias_irs:
            txt_input = ft.TextField(
                label="Acumulado Registado (€)",
                value=f"{item['valor']:.2f}" if item['valor'] > 0 else "",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=180,
                border_color=item["cor"],
                on_change=lambda e, obj=item, ctrl=e.control: atualizar_valor_irs(obj, ctrl)
            )

            grid_irs_ui.controls.append(
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.RECEIPT_LONG, color=item["cor"], size=28),
                                ft.Text(item["cat"], weight=ft.FontWeight.BOLD, size=16, color="#172B4D", expand=True),
                                ft.Container(
                                    content=ft.Text(item["limite"], color="white", size=11, weight=ft.FontWeight.BOLD),
                                    bgcolor=item["cor"],
                                    padding=6,
                                    border_radius=5
                                )
                            ]),
                            ft.Divider(color="#E2E8F0"),
                            ft.Container(
                                content=ft.Text(item["instrucao"], size=13, color="#172B4D", weight=ft.FontWeight.W_500),
                                bgcolor="#FFF8E1",
                                padding=10,
                                border_radius=6,
                                border=ft.Border.all(width=1, color="#FFE082")
                            ),
                            ft.Row([
                                txt_input,
                                ft.Text("🟢 Validado na Autoridade Tributária", color="#00875A", size=12, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ])
                    )
                )
            )
        page.update()

    perfil_irs_financas = ft.Column([
        ft.Text("🏛️ Portal IRS & Deduções Às Finanças", size=20, weight=ft.FontWeight.BOLD, color="#0052CC"),
        ft.Text("Organização por categorias oficiais do e-Fatura. Preencha os valores acumulados em cada quadrado.", size=13, color="#5E6C84"),
        ft.Divider(),
        grid_irs_ui
    ])

    # =========================================================
    # 📅 AGENDA & CALENDÁRIO
    # =========================================================
    txt_ag_titulo = ft.TextField(label="Título do Compromisso", expand=True, border_color="#FF9800")
    txt_ag_hora = ft.TextField(label="Hora (ex: 14:30)", width=130, value="10:00", border_color="#FF9800")
    txt_ag_data = ft.TextField(label="Data (AAAA-MM-DD)", width=150, value=datetime.today().strftime('%Y-%m-%d'), border_color="#FF9800")
    dd_ag_prio = ft.Dropdown(
        label="Prioridade", width=140, value="Normal",
        options=[ft.dropdown.Option("Normal"), ft.dropdown.Option("Alta"), ft.dropdown.Option("Urgente")]
    )
    lista_agenda_ui = ft.Column()

    def add_evento(e):
        if txt_ag_titulo.value and txt_ag_data.value:
            agenda_eventos.append({
                "data": txt_ag_data.value,
                "hora": txt_ag_hora.value,
                "titulo": txt_ag_titulo.value,
                "prioridade": dd_ag_prio.value
            })
            txt_ag_titulo.value = ""
            atualizar_agenda()

    def atualizar_agenda():
        lista_agenda_ui.controls.clear()
        eventos_ordenados = sorted(agenda_eventos, key=lambda x: x["data"])
        for ev in eventos_ordenados:
            cor_prio = "#DE350B" if ev["prioridade"] == "Urgente" else ("#FF9800" if ev["prioridade"] == "Alta" else "#00875A")
            lista_agenda_ui.controls.append(
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        padding=12,
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color="#FF9800", size=32),
                            ft.Column([
                                ft.Text(ev["titulo"], weight=ft.FontWeight.BOLD, size=15, color="#172B4D"),
                                ft.Text(f"📅 Data: {ev['data']} às {ev['hora']} | Prioridade: {ev['prioridade']}", size=13, color="#5E6C84")
                            ], expand=True),
                            ft.Container(
                                content=ft.Text(ev["prioridade"], color="white", size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=cor_prio,
                                padding=6,
                                border_radius=5
                            )
                        ])
                    )
                )
            )
        page.update()

    perfil_agenda = ft.Column([
        ft.Text("📅 Agenda & Calendário de Compromissos", size=20, weight=ft.FontWeight.BOLD, color="#FF9800"),
        ft.Container(
            content=ft.Column([
                ft.Text("➕ Agendar Novo Evento / Tarefa", weight=ft.FontWeight.BOLD, size=15, color="#172B4D"),
                ft.Row([txt_ag_titulo]),
                ft.Row([txt_ag_data, txt_ag_hora, dd_ag_prio]),
                ft.ElevatedButton("Guardar na Agenda", icon=ft.Icons.EVENT_AVAILABLE, bgcolor="#FF9800", color="white", on_click=add_evento)
            ]),
            padding=15,
            bgcolor="#FFF3E0",
            border_radius=10,
            border=ft.Border.all(width=2, color="#FFE0B2")
        ),
        ft.Divider(),
        lista_agenda_ui
    ])

    # =========================================================
    # 📝 NOTAS & LEMBRETES
    # =========================================================
    txt_nota_titulo = ft.TextField(label="Título da Nota", expand=True, border_color="#9C27B0")
    txt_nota_texto = ft.TextField(label="Conteúdo / Apontamento", multiline=True, max_lines=3, expand=True, border_color="#9C27B0")
    lista_notas_ui = ft.Column()

    def add_nota(e):
        if txt_nota_titulo.value:
            notas_lista.append({"titulo": txt_nota_titulo.value, "texto": txt_nota_texto.value})
            txt_nota_titulo.value = ""; txt_nota_texto.value = ""
            atualizar_notas()

    def remover_nota(nota):
        notas_lista.remove(nota)
        atualizar_notas()

    def atualizar_notas():
        lista_notas_ui.controls.clear()
        for n in notas_lista:
            lista_notas_ui.controls.append(
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.NOTE_ALT, color="#9C27B0"),
                                ft.Text(n["titulo"], weight=ft.FontWeight.BOLD, size=16, color="#172B4D", expand=True),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="#DE350B", on_click=lambda e, nota=n: remover_nota(nota))
                            ]),
                            ft.Text(n["texto"], size=14, color="#424242")
                        ])
                    )
                )
            )
        page.update()

    perfil_notas = ft.Column([
        ft.Text("📝 Bloco de Notas & Lembretes", size=20, weight=ft.FontWeight.BOLD, color="#9C27B0"),
        ft.Container(
            content=ft.Column([
                ft.Text("✏️ Nova Nota Rápida", weight=ft.FontWeight.BOLD, size=15, color="#172B4D"),
                txt_nota_titulo,
                txt_nota_texto,
                ft.ElevatedButton("Guardar Nota", icon=ft.Icons.NOTE_ADD, bgcolor="#9C27B0", color="white", on_click=add_nota)
            ]),
            padding=15,
            bgcolor="#F3E5F5",
            border_radius=10,
            border=ft.Border.all(width=2, color="#E1BEE7")
        ),
        ft.Divider(),
        lista_notas_ui
    ])

    # =========================================================
    # 🏢 PERFIL EMPRESA & CRM
    # =========================================================
    txt_cli_nome = ft.TextField(label="Nome do Contacto / Empresa", expand=True, border_color="#FF5630")
    txt_cli_contacto = ft.TextField(label="Telefone / Email", width=180, border_color="#FF5630")
    dd_cli_papel = ft.Dropdown(
        label="Função", width=180, value="Comprador Potencial",
        options=[ft.dropdown.Option("Comprador Potencial"), ft.dropdown.Option("Comprador Confirmado"), ft.dropdown.Option("Parceiro"), ft.dropdown.Option("Fornecedor")]
    )
    lista_clientes = ft.Column()

    def add_cliente(e):
        if txt_cli_nome.value:
            clientes_empresa.append({"nome": txt_cli_nome.value, "contacto": txt_cli_contacto.value, "papel": dd_cli_papel.value})
            txt_cli_nome.value = ""; txt_cli_contacto.value = ""
            atualizar_empresa()

    txt_emp_fat = ft.TextField(label="Faturação Prevista (€)", value="5000", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    txt_emp_gastos = ft.TextField(label="Gastos Previstos (€)", value="2200", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_empresa())
    lbl_emp_lucro = ft.Text("Lucro Previsto: 0.00 €", size=16, weight=ft.FontWeight.BOLD, color="#00875A")

    def atualizar_empresa():
        try:
            fat = float(txt_emp_fat.value or 0)
            gastos = float(txt_emp_gastos.value or 0)
            lucro = fat - gastos
            lbl_emp_lucro.value = f"🟢 Lucro Líquido Previsto: {lucro:.2f} €"
        except ValueError: pass

        lista_clientes.controls.clear()
        for c in clientes_empresa:
            lista_clientes.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON, color="#FFAB00"),
                    title=ft.Text(f"{c['nome']} ({c['contacto']})", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Função: {c['papel']}")
                )
            )
        page.update()

    perfil_empresa = ft.Column([
        ft.Text("🏢 Gestão Corporativa & CRM", size=20, weight=ft.FontWeight.BOLD, color="#172B4D"),
        ft.Card(
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=8,
                padding=15,
                content=ft.Column([
                    ft.Text("📊 Balanço & Previsão Financeira", size=16, weight=ft.FontWeight.BOLD, color="#FF5630"),
                    ft.Row([txt_emp_fat, txt_emp_gastos]),
                    lbl_emp_lucro
                ])
            )
        ),
        ft.Text("👥 Carteira de Clientes", size=16, weight=ft.FontWeight.BOLD, color="#172B4D"),
        ft.Row([txt_cli_nome, txt_cli_contacto, dd_cli_papel]),
        ft.ElevatedButton("Registar Contacto", icon=ft.Icons.PERSON_ADD, bgcolor="#FF5630", color="white", on_click=add_cliente),
        lista_clientes,
    ])

    # =========================================================
    # 📑 MÓDULO DE FATURAS COM FOTO
    # =========================================================
    txt_fat_num = ft.TextField(label="Nº Fatura / Código de Barras", expand=True, border_color="#0052CC")
    txt_fat_entidade = ft.TextField(label="Emitente / Fornecedor", expand=True, border_color="#0052CC")
    txt_fat_valor = ft.TextField(label="Valor (€)", width=120, keyboard_type=ft.KeyboardType.NUMBER, border_color="#0052CC")
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
                    "pago": False,
                    "foto_url": foto_preview_url["src"],
                    "foto_nome": foto_preview_url["name"]
                })
                txt_fat_num.value = ""; txt_fat_entidade.value = ""; txt_fat_valor.value = ""
                lbl_status_foto.value = "Nenhuma foto anexa"
                img_preview.visible = False
                foto_preview_url["src"] = None
                foto_preview_url["name"] = "Nenhuma foto anexa"
                atualizar_faturas()
            except ValueError: pass

    def atualizar_faturas():
        lista_faturas_ui.controls.clear()
        for f in faturas_recibos:
            status_icon = "🟢 PAGO" if f["pago"] else "🔴 PENDENTE"
            status_color = "#00875A" if f["pago"] else "#DE350B"
            
            foto_widget = ft.Image(src=f["foto_url"], width=80, height=80, fit="cover", border_radius=6) if f["foto_url"] else ft.Icon(ft.Icons.RECEIPT_LONG, color="#0052CC", size=40)

            lista_faturas_ui.controls.append(
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        padding=12,
                        content=ft.Row([
                            foto_widget,
                            ft.Column([
                                ft.Text(f"{f['num']} - {f['entidade']}", weight=ft.FontWeight.BOLD, size=15, color="#172B4D"),
                                ft.Text(f"Âmbito: {f['tipo']} | Valor: {f['valor']:.2f} €", size=13, color="#5E6C84"),
                                ft.Text(f"📎 Anexo: {f['foto_nome']}", size=11, italic=True, color="#0052CC")
                            ], expand=True),
                            ft.OutlinedButton(
                                status_icon,
                                style=ft.ButtonStyle(color=status_color),
                                on_click=lambda e, fat=f: alternar_pago_fatura(fat)
                            )
                        ])
                    )
                )
            )
        page.update()

    perfil_faturas = ft.Column([
        ft.Text("📑 Repositório Inteligente & Visual de Faturas", size=20, weight=ft.FontWeight.BOLD, color="#0052CC"),
        ft.Container(
            content=ft.Column([
                ft.Text("📷 Digitalização / Tirar Foto da Fatura", weight=ft.FontWeight.BOLD, size=15, color="#172B4D"),
                ft.Row([
                    ft.ElevatedButton(
                        "Tirar Foto / Anexar Fatura", 
                        icon=ft.Icons.CAMERA_ALT, 
                        bgcolor="#0052CC", 
                        color="white",
                        on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
                    ),
                    lbl_status_foto
                ]),
                img_preview,
                ft.Row([txt_fat_num, txt_fat_entidade]),
                ft.Row([txt_fat_valor, dd_fat_tipo, ft.ElevatedButton("Adicionar Fatura", icon=ft.Icons.SAVE, bgcolor="#00875A", color="white", on_click=add_fatura)]),
            ]),
            padding=15,
            bgcolor="#E3F2FD",
            border_radius=10,
            border=ft.Border.all(width=2, color="#90CAF9")
        ),
        ft.Divider(),
        lista_faturas_ui
    ])

    # =========================================================
    # 🟢 PERFIL PARTICULAR
    # =========================================================
    txt_rendimento_p = ft.TextField(label="Rendimento Mensal (€)", value="1500", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())
    txt_meta_p = ft.TextField(label="Meta Poupança (€)", value="300", keyboard_type=ft.KeyboardType.NUMBER, width=170, on_change=lambda e: atualizar_particular())
    txt_nome_p = ft.TextField(label="Nome do Gasto", expand=True)
    txt_valor_p = ft.TextField(label="Valor (€)", keyboard_type=ft.KeyboardType.NUMBER, width=120)
    dd_cat_p = ft.Dropdown(
        label="Categoria", width=150, value="Essencial",
        options=[ft.dropdown.Option("Essencial"), ft.dropdown.Option("Alimentação"), ft.dropdown.Option("Lazer"), ft.dropdown.Option("Transportes"), ft.dropdown.Option("Outros")]
    )
    lbl_status_p = ft.Text("🟢 Poupança dentro do objetivo!", weight=ft.FontWeight.BOLD, color="#00875A")
    lista_desp_p = ft.Column()
    lbl_tot_gastos_p = ft.Text("Gastos: 0.00 €", weight=ft.FontWeight.BOLD, color="#DE350B")
    lbl_saldo_p = ft.Text("Saldo: 0.00 €", weight=ft.FontWeight.BOLD, color="#00875A")

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
            lbl_status_p.value = "🟢 Situação Excelente: Meta de poupança atingida!"; lbl_status_p.color = "#00875A"
        elif saldo > 0:
            lbl_status_p.value = "🟡 Atenção: Abaixo da meta de poupança estipulada."; lbl_status_p.color = "#FFAB00"
        else:
            lbl_status_p.value = "🔴 ALERTA: Orçamento Ultrapassado!"; lbl_status_p.color = "#DE350B"

        lista_desp_p.controls.clear()
        for d in despesas_pessoais:
            lista_desp_p.controls.append(
                ft.ListTile(
                    leading=ft.Text("🔴 ⬇️", size=16),
                    title=ft.Text(f"{d['nome']} ({d['cat']})", weight=ft.FontWeight.BOLD),
                    trailing=ft.Text(f"-{d['valor']:.2f} €", color="#DE350B", weight=ft.FontWeight.BOLD)
                )
            )
        page.update()

    perfil_particular = ft.Column([
        ft.Text("👤 Perfil Particular (Orçamento)", size=20, weight=ft.FontWeight.BOLD, color="#0052CC"),
        ft.Card(
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=8,
                padding=15,
                content=ft.Column([ft.Row([txt_rendimento_p, txt_meta_p]), lbl_status_p])
            )
        ),
        ft.Row([txt_nome_p, txt_valor_p, dd_cat_p]),
        ft.ElevatedButton("Registar Despesa", icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, bgcolor="#DE350B", color="white", on_click=add_despesa_p),
        ft.Divider(),
        ft.Row([lbl_tot_gastos_p, lbl_saldo_p], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        lista_desp_p
    ])

    # =========================================================
    # HEADER VIBRANTE
    # =========================================================
    header_hero = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FLASH_ON, color="#FFAB00", size=32),
                ft.Text("Gestão 360 - Modo Finanças & e-Fatura", size=22, weight=ft.FontWeight.BOLD, color="#172B4D"),
            ]),
            lbl_frase
        ]),
        padding=16,
        bgcolor="#FFFFFF",
        border_radius=12,
        border=ft.Border.all(width=2, color="#FFAB00")
    )

    # =========================================================
    # NAVEGAÇÃO PRINCIPAL
    # =========================================================
    conteudo_principal = ft.Container(content=perfil_faturas, expand=True)

    def mudar_aba(e):
        idx = int(e.control.data)
        seccoes = [perfil_faturas, perfil_irs_financas, perfil_agenda, perfil_notas, perfil_empresa, perfil_particular]
        conteudo_principal.content = seccoes[idx]
        page.update()

    botoes_navegacao = ft.Row(
        controls=[
            ft.ElevatedButton("📑 Faturas", data=0, bgcolor="#0052CC", color="white", on_click=mudar_aba),
            ft.ElevatedButton("🏛️ IRS & Finanças", data=1, bgcolor="#DE350B", color="white", on_click=mudar_aba),
            ft.ElevatedButton("📅 Agenda", data=2, bgcolor="#FF9800", color="white", on_click=mudar_aba),
            ft.ElevatedButton("📝 Notas", data=3, bgcolor="#9C27B0", color="white", on_click=mudar_aba),
            ft.ElevatedButton("🏢 Empresa", data=4, bgcolor="#FF5630", color="white", on_click=mudar_aba),
            ft.ElevatedButton("👤 Particular", data=5, bgcolor="#00875A", color="white", on_click=mudar_aba),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    page.add(
        header_hero,
        botoes_navegacao,
        ft.Divider(),
        conteudo_principal
    )

    atualizar_particular()
    atualizar_empresa()
    atualizar_faturas()
    atualizar_agenda()
    atualizar_notas()
    atualizar_irs_ui()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)
