import flet as ft

def main(page: ft.Page):
    # Configurações gerais da página para simulação/dispositivo móvel
    page.title = "AURA 360"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.window_width = 390
    page.window_height = 844

    # ----------------------------------------------------
    # ESTADOS E DADOS
    # ----------------------------------------------------
    servicos_selecionados = []
    
    cat_servicos = {
        "Limpeza & Organização": [
            {"nome": "Limpeza Profunda", "preco": 45.0},
            {"nome": "Limpeza Pós-Obra", "preco": 80.0},
            {"nome": "Higienização de Sofás/Estofados", "preco": 35.0},
        ],
        "Manutenção & Obras": [
            {"nome": "Pintura Interiores (m²)", "preco": 15.0},
            {"nome": "Instalação Placa de Gesso / Teto Falso", "preco": 60.0},
            {"nome": "Piso Vinílico / Flutuante", "preco": 50.0},
            {"nome": "Pequenos Reparos / Marido de Aluguer", "preco": 25.0},
        ],
        "Especializados": [
            {"nome": "Inspeção Técnica / Avaliação", "preco": 30.0},
            {"nome": "Consultoria de Espaço & Layout", "preco": 40.0},
        ]
    }

    # ----------------------------------------------------
    # CONTROLO DE NAVEGAÇÃO
    # ----------------------------------------------------
    def navegar_para(e):
        index = e.control.selected_index
        if index == 0:
            content_area.content = build_view_inicio()
        elif index == 1:
            content_area.content = build_view_servicos()
        elif index == 2:
            content_area.content = build_view_orcamento()
        elif index == 3:
            content_area.content = build_view_contacto()
        page.update()

    # ----------------------------------------------------
    # VISTA 1: INÍCIO
    # ----------------------------------------------------
    def build_view_inicio():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.icons.AUTO_AWESOME, size=60, color=ft.colors.CYAN_400),
                                ft.Text("AURA 360", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text("Soluções Integradas para o seu Espaço", size=14, color=ft.colors.WHITE_70),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        padding=30,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=15,
                    ),
                    ft.Text("Destaques & Serviços", size=18, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.CLEANING_SERVICES, color=ft.colors.CYAN_400),
                            title=ft.Text("Limpeza & Manutenção"),
                            subtitle=ft.Text("Serviços rápidos e eficientes para residências e espaços de trabalho."),
                        )
                    ),
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.HOME_REPAIR_SERVICE, color=ft.colors.CYAN_400),
                            title=ft.Text("Remodelação & Reparos"),
                            subtitle=ft.Text("Pintura, teto falso, pavimento e pequenas reparações."),
                        )
                    ),
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.CALCULATOR, color=ft.colors.CYAN_400),
                            title=ft.Text("Orçamento Imediato"),
                            subtitle=ft.Text("Escolha os serviços e simule o valor estimado no momento."),
                        )
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ----------------------------------------------------
    # VISTA 2: CATÁLOGO DE SERVIÇOS
    # ----------------------------------------------------
    def toggle_servico(servico, checked):
        if checked and servico not in servicos_selecionados:
            servicos_selecionados.append(servico)
        elif not checked and servico in servicos_selecionados:
            servicos_selecionados.remove(servico)

    def build_view_servicos():
        elementos = [
            ft.Text("Serviços Disponíveis", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Selecione os serviços que deseja incluir no orçamento:", size=13, color=ft.colors.WHITE_60),
            ft.Divider()
        ]

        for cat, itens in cat_servicos.items():
            elementos.append(ft.Text(cat, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400))
            for s in itens:
                is_selected = s in servicos_selecionados
                cb = ft.Checkbox(
                    label=f"{s['nome']} — {s['preco']:.2f}€",
                    value=is_selected,
                    on_change=lambda e, serv=s: toggle_servico(serv, e.control.value)
                )
                elementos.append(cb)
            elementos.append(ft.Container(height=10))

        return ft.Container(
            content=ft.Column(controls=elementos, scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=20,
        )

    # ----------------------------------------------------
    # VISTA 3: SIMULADOR DE ORÇAMENTO
    # ----------------------------------------------------
    def build_view_orcamento():
        total = sum(s["preco"] for s in servicos_selecionados)

        itens_lista = []
        if not servicos_selecionados:
            itens_lista.append(ft.Text("Nenhum serviço selecionado no catálogo.", color=ft.colors.WHITE_50))
        else:
            for s in servicos_selecionados:
                itens_lista.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(s["nome"], size=14),
                            ft.Text(f"{s['preco']:.2f} €", weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400),
                        ]
                    )
                )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Resumo do Orçamento", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Serviços Escolhidos:", size=14, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=ft.Column(controls=itens_lista, spacing=8),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        padding=15,
                        border_radius=10,
                    ),
                    ft.Divider(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Estimativa Total:", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{total:.2f} €", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                        ]
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        text="Avançar para Pedido",
                        icon=ft.icons.SEND,
                        style=ft.ButtonStyle(bgcolor=ft.colors.CYAN_700, color=ft.colors.WHITE),
                        on_click=lambda _: set_tab(3)
                    )
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ----------------------------------------------------
    # VISTA 4: CONTACTO & PEDIDO
    # ----------------------------------------------------
    def submeter_pedido(e):
        if not txt_nome.value or not txt_contacto.value:
            snack = ft.SnackBar(ft.Text("Por favor, preencha o Nome e o Contacto!"), bgcolor=ft.colors.RED_700)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        snack = ft.SnackBar(
            ft.Text("Pedido enviado com sucesso! Entraremos em contacto brevemente."),
            bgcolor=ft.colors.GREEN_700
        )
        page.overlay.append(snack)
        snack.open = True
        
        # Limpar campos
        txt_nome.value = ""
        txt_contacto.value = ""
        txt_notas.value = ""
        page.update()

    txt_nome = ft.TextField(label="Nome / Entidade", prefix_icon=ft.icons.PERSON)
    txt_contacto = ft.TextField(label="Telefone / Email", prefix_icon=ft.icons.PHONE)
    txt_notas = ft.TextField(label="Observações / Detalhes do Local", multiline=True, min_lines=3)

    def build_view_contacto():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Finalizar Pedido de Contacto", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Indique os seus dados para podermos agendar ou validar o seu pedido:", size=13, color=ft.colors.WHITE_60),
                    txt_nome,
                    txt_contacto,
                    txt_notas,
                    ft.ElevatedButton(
                        text="Enviar Pedido",
                        icon=ft.icons.CHECK_CIRCLE,
                        style=ft.ButtonStyle(bgcolor=ft.colors.CYAN_700, color=ft.colors.WHITE),
                        on_click=submeter_pedido
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    def set_tab(index):
        nav_bar.selected_index = index
        if index == 0:
            content_area.content = build_view_inicio()
        elif index == 1:
            content_area.content = build_view_servicos()
        elif index == 2:
            content_area.content = build_view_orcamento()
        elif index == 3:
            content_area.content = build_view_contacto()
        page.update()

    # ----------------------------------------------------
    # ESTRUTURA PRINCIPAL (LAYOUT)
    # ----------------------------------------------------
    content_area = ft.Container(content=build_view_inicio(), expand=True)

    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=navegar_para,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME_OUTLINED, selected_icon=ft.icons.HOME, label="Início"),
            ft.NavigationDestination(icon=ft.icons.LIST_ALT_OUTLINED, selected_icon=ft.icons.LIST_ALT, label="Serviços"),
            ft.NavigationDestination(icon=ft.icons.CALCULATOR_OUTLINED, selected_icon=ft.icons.CALCULATOR, label="Orçamento"),
            ft.NavigationDestination(icon=ft.icons.CONTACT_MAIL_OUTLINED, selected_icon=ft.icons.CONTACT_MAIL, label="Contacto"),
        ],
    )

    page.appbar = ft.AppBar(
        title=ft.Text("AURA 360"),
        center_title=True,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )
    
    page.add(
        content_area,
        nav_bar
    )

ft.app(target=main)
