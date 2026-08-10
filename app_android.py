import flet as ft

def main(page: ft.Page):
    page.title = "Exemplo Flet - Ícones Corrigidos"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # Título
    page.add(
        ft.Text("Perfil do Utilizador", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD))
    )

    # Exemplo 1: Ícone individual (passando a string "person" sem 'name=')
    user_icon = ft.Icon("person", size=40, color="blue")

    # Exemplo 2: Botão com ícone
    profile_button = ft.ElevatedButton(
        text="Ver Perfil",
        icon="person",
        on_click=lambda e: print("Botão de perfil clicado!")
    )

    # Exemplo 3: Campo de texto com ícone
    username_input = ft.TextField(
        label="Nome de Utilizador",
        prefix_icon="person",
        width=300
    )

    # Adicionar componentes à página
    page.add(
        user_icon,
        username_input,
        profile_button
    )

    # Exemplo 4: Barra de navegação inferior
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon="home", label="Início"),
            ft.NavigationDestination(icon="person", label="Perfil"),
            ft.NavigationDestination(icon="settings", label="Definições"),
        ]
    )

    page.update()

if __name__ == "__main__":
    ft.app(target=main)
