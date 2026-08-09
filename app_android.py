import flet as ft
import os
import random

def main(page: ft.Page):
    # ---------------------------------------------------------
    # CONFIGURAÇÕES DE TEMA & PÁGINA
    # ---------------------------------------------------------
    page.title = "AURA 360 | Gestão Financeira & Otimização B2B/B2C"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ---------------------------------------------------------
    # ESTRUTURA DE DADOS
    # ---------------------------------------------------------
    faturas = [
        {"num": "FT 2026/089", "entidade": "Supermercado Continente", "cat": "🛒 Despesas Gerais", "valor": 124.50, "pago": True, "tipo": "Pessoal"},
        {"num": "FT 2026/102", "entidade": "Farmácia Central", "cat": "🏥 Saúde", "valor": 45.20, "pago": True, "tipo": "Pessoal"},
        {"num": "FT 2026/115", "entidade": "Combustíveis Galp", "cat": "🚗 Deslocações & Empresa", "valor": 65.00, "pago": False, "tipo": "Empresa"},
    ]

    deducoes_irs = [
        {"cat": "🛒 Despesas Gerais", "atual": 240.0, "max": 350.0, "cor": "#3B82F6", "dica": "Faltam 110€ para atingir o teto máximo de dedução!"},
        {"cat": "🏥 Saúde & Bem-Estar", "atual": 112.5, "max": 1000.0, "cor": "#10B981", "dica": "Guarde todas as faturas com receita médica a 23%."},
        {"cat": "🎓 Educação & Formação", "atual": 450.0, "max": 800.0, "cor": "#F59E0B", "dica": "Propinas e manuais escolares conferem até 30% de dedução."},
        {"cat": "🏠 Habitação & Rendas", "atual": 320.0, "max": 502.0, "cor": "#8B5CF6", "dica": "Recibos de renda declarados entram diretamente no e-Fatura."},
        {"cat": "🚗 Restauração & Lazer", "atual": 135.0, "max": 250.0, "cor": "#EC4899", "dica": "15% do IVA suportado em restaurantes volta para si no IRS."},
    ]

    # ---------------------------------------------------------
    # COMPONENTES VISUAIS (CARDS & MÉTRICAS)
    # ---------------------------------------------------------
    def criar_card_metrica(titulo, valor, subtexto, icone, cor_icone, cor_fundo="#FFFFFF"):
        return ft.Container(
            expand=True,
            bgcolor=cor_fundo,
            padding=20,
            border_radius=16,
            border=ft.Border.all(1, "#E2E8F0"),
            shadow=ft.BoxShadow(blur_radius=10, color="#0D000000"),
            content=ft.Column([
                ft.Row([
                    ft.Text(titulo, size=13, weight=ft.FontWeight.W_600, color="#64748B"),
                    ft.Container(
                        content=ft.Icon(icone, color=cor_icone, size=20),
                        bgcolor="#1F" + cor_icone.lstrip("#"),
                        padding=8,
                        border_radius=10
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color="#0F172A"),
                ft.Text(subtexto, size=12, color="#10B981" if "+" in subtexto or "🟢" in subtexto else "#64748B", weight=ft.FontWeight.W_500)
            ])
        )

    # ---------------------------------------------------------
    # ABA 1: DASHBOARD EXECUTIVO & INTELIGÊNCIA FISCAL
    # ---------------------------------------------------------
    card_saldo = criar_card_metrica("Património / Saldo Líquido", "12.450,00 €", "🟢 +8.4% este mês", ft.Icons.ACCOUNT_BALANCE_WALLET, "#10B981")
    card_irs = criar_card_metrica("Retorno Estimado IRS", "1.257,50 €", "💡 82% do teto máximo atingido", ft.Icons.ACCOUNT_BALANCE, "#3B82F6")
    card_empresa = criar_card_metrica("Reembolsos Empresa (B2B)", "185,00 €", "⏳ 1 fatura pendente de aprovação", ft.Icons.BUSINESS_CENTER, "#8B5CF6")

    coluna_deducoes = ft.Column()
    for d in deducoes_irs:
        perc = min(d["atual"] / d["max"], 1.0)
        coluna_deducoes.controls.append(
            ft.Container(
                bgcolor="#FFFFFF", padding=16, border_radius=12, border=ft.Border.all(1, "#E2E8F0"),
                content=ft.Column([
                    ft.Row([
                        ft.Text(d["cat"], weight=ft.FontWeight.BOLD, size=14, color="#0F172A"),
                        ft.Text(f"{d['atual']:.2f} € / {d['max']:.2f} €", weight=ft.FontWeight.BOLD, size=13, color=d["cor"])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=perc, color=d["cor"], bgcolor="#F1F5F9", height=8),
                    ft.Text(f"💡 {d['dica']}", size=12, color="#64748B", italic=True)
                ])
            )
        )

    view_dashboard = ft.Column([
        ft.Text("📊 Resumo Executivo & Otimização Fiscal", size=20, weight=ft.FontWeight.BOLD, color="#0F172A"),
        ft.Row([card_saldo, card_irs, card_empresa]),
        ft.Container(height=10),
        ft.Text("🏛️ Otimizador do e-Fatura & Deduções IRS", size=18, weight=ft.FontWeight.BOLD, color="#0F172A"),
        coluna_deducoes
    ])

    # ---------------------------------------------------------
    # ABA 2: SCANNER IA & REPOSITÓRIO INTELIGENTE
    # ---------------------------------------------------------
    coluna_faturas_list = ft.Column()
    status_scan = ft.Text("", size=13, color="#10B981", weight=ft.FontWeight.BOLD)

    def atualizar_faturas_ui():
        coluna_faturas_list.controls.clear()
        for f in faturas:
            status_cor = "#10B981" if f["pago"] else "#F59E0B"
            status_txt = "VALIDADA" if f["pago"] else "EM ANÁLISE"
            badge_b2b = "#8B5CF6" if f.get("tipo") == "Empresa" else "#3B82F6"
            
            coluna_faturas_list.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF", padding=16, border_radius=12, border=ft.Border.all(1, "#E2E8F0"),
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT_LONG, color=badge_b2b, size=24),
                            bgcolor="#F1F5F9", padding=10, border_radius=10
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(f"{f['num']} — {f['entidade']}", weight=ft.FontWeight.BOLD, size=15, color="#0F172A"),
                                ft.Container(content=ft.Text(f.get("tipo", "Pessoal"), size=10, color="white", weight=ft.FontWeight.BOLD), bgcolor=badge_b2b, padding=4, border_radius=4)
                            ]),
                            ft.Text(f"Categoria: {f['cat']}", size=12, color="#64748B")
                        ], expand=True),
                        ft.Text(f"{f['valor']:.2f} €", weight=ft.FontWeight.BOLD, size=16, color="#0F172A"),
                        ft.Container(
                            content=ft.Text(status_txt, size=10, weight=ft.FontWeight.BOLD, color="white"),
                            bgcolor=status_cor, padding=6, border_radius=6
                        )
                    ])
                )
            )
        page.update()

    def simular_scan_ia(e):
        status_scan.value = "⚡ A processar documento com Inteligência Artificial..."
        page.update()
        
        # Simulação de OCR instantâneo
        faturas.append({
            "num": f"FT 2026/{random.randint(120, 999)}",
            "entidade": "Restaurante Executivo Lisboa",
            "cat": "🚗 Restauração & Lazer",
            "valor": round(random.uniform(25.0, 95.0), 2),
            "pago": True,
            "tipo": "Empresa"
        })
        status_scan.value = "✅ Fatura lida com sucesso! Categoria, NIF e IVA extraídos automaticamente."
        atualizar_faturas_ui()

    view_scanner = ft.Column([
        ft.Text("📷 Scanner Inteligente & Digitalização OCR", size=20, weight=ft.FontWeight.BOLD, color="#0F172A"),
        ft.Container(
            bgcolor="#FFFFFF", padding=24, border_radius=16, border=ft.Border.all(1, "#CBD5E1"),
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD, size=48, color="#3B82F6"),
                ft.Text("Arraste o PDF da Fatura ou Carregue uma Foto do Recibo", size=15, weight=ft.FontWeight.BOLD, color="#0F172A"),
                ft.Text("A nossa IA extrai automaticamente os dados para o e-Fatura e para a contabilidade.", size=12, color="#64748B"),
                ft.ElevatedButton("Simular Leitura de Fatura por IA", icon=ft.Icons.AUTO_AWESOME, bgcolor="#3B82F6", color="white", on_click=simular_scan_ia),
                status_scan
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ),
        ft.Container(height=10),
        ft.Text("📑 Faturas Processadas", size=18, weight=ft.FontWeight.BOLD, color="#0F172A"),
        coluna_faturas_list
    ])

    # ---------------------------------------------------------
    # ABA 3: MÓDULO EMPRESARIAL B2B & RELATÓRIOS
    # ---------------------------------------------------------
    txt_notificacao_export = ft.Text("", size=13, color="#10B981", weight=ft.FontWeight.BOLD)

    def exportar_relatorio(e):
        txt_notificacao_export.value = "📄 Relatório PDF/Excel gerado e enviado com sucesso para o Contabilista!"
        page.update()

    view_b2b = ft.Column([
        ft.Text("🏢 Módulo B2B & Ligação à Contabilidade", size=20, weight=ft.FontWeight.BOLD, color="#0F172A"),
        ft.Text("Solução integrada para empresas, trabalhadores independentes e gabinetes de contabilidade.", size=13, color="#64748B"),
        ft.Container(height=10),
        ft.Container(
            bgcolor="#FFFFFF", padding=20, border_radius=16, border=ft.Border.all(1, "#E2E8F0"),
            content=ft.Column([
                ft.Text("📤 Exportação Pronta para Contabilista (SAF-T / Excel / PDF)", weight=ft.FontWeight.BOLD, size=16, color="#0F172A"),
                ft.Text("Gerador automático de relatórios mensais de despesas de representação e ajudas de custo.", size=12, color="#64748B"),
                ft.Row([
                    ft.ElevatedButton("Exportar Relatório Mensal", icon=ft.Icons.PICTURE_AS_PDF, bgcolor="#8B5CF6", color="white", on_click=exportar_relatorio),
                    ft.OutlinedButton("Sincronizar com e-Fatura (AT)", icon=ft.Icons.SYNC, border_color="#8B5CF6")
                ]),
                txt_notificacao_export
            ])
        ),
        ft.Container(height=10),
        ft.Container(
            bgcolor="#EFF6FF", padding=20, border_radius=16, border=ft.Border.all(1, "#BFDBFE"),
            content=ft.Column([
                ft.Text("💼 Por que as Empresas Compram a AURA 360?", weight=ft.FontWeight.BOLD, size=15, color="#1E40AF"),
                ft.Text("• Redução de 80% no tempo manual de validação de despesas dos colaboradores.", size=13, color="#1E3A8A"),
                ft.Text("• Conformidade fiscal garantida sem erros de classificação no e-Fatura.", size=13, color="#1E3A8A"),
                ft.Text("• Integração simples via API com software de gestão e faturação.", size=13, color="#1E3A8A"),
            ])
        )
    ])

    # ---------------------------------------------------------
    # CABEÇALHO & NAVEGAÇÃO
    # ---------------------------------------------------------
    frases = [
        "✨ «O controlo financeiro de hoje constrói a liberdade de amanhã.»",
        "💎 «Saber exatamente onde está o seu dinheiro é o primeiro passo para o multiplicar.»",
        "⚡ «Pequenas otimizações no IRS geram grandes retornos no final do ano.»"
    ]

    header = ft.Container(
        bgcolor="#0F172A", padding=24, border_radius=20,
        content=ft.Row([
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DIAMOND, color="#38BDF8", size=28),
                    ft.Text("AURA 360", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ]),
                ft.Text(random.choice(frases), size=13, color="#94A3B8", italic=True)
            ], expand=True),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.VERIFIED_USER, color="#10B981", size=18),
                    ft.Text("Plano Pro / B2B", color="white", size=12, weight=ft.FontWeight.BOLD)
                ]),
                bgcolor="#1E293B", padding=10, border_radius=12
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    area_conteudo = ft.Container(content=view_dashboard, expand=True, padding=ft.Padding.only(top=10))

    def mudar_tab(e):
        idx = int(e.control.data)
        views = [view_dashboard, view_scanner, view_b2b]
        area_conteudo.content = views[idx]
        page.update()

    nav_bar = ft.Row([
        ft.ElevatedButton("📊 Otimização IRS 360", data=0, on_click=mudar_tab, bgcolor="#0F172A", color="white"),
        ft.ElevatedButton("📷 Scanner IA de Faturas", data=1, on_click=mudar_tab, bgcolor="#3B82F6", color="white"),
        ft.ElevatedButton("🏢 Módulo B2B / Empresas", data=2, on_click=mudar_tab, bgcolor="#8B5CF6", color="white"),
    ], scroll=ft.ScrollMode.AUTO)

    # MONTAGEM FINAL
    page.add(
        header,
        ft.Container(height=5),
        nav_bar,
        ft.Divider(color="#E2E8F0"),
        area_conteudo
    )

    atualizar_faturas_ui()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)
