import flet as ft
import os
from chat_message import ChatMessage, Message
from gemini_handler import GeminiHandler

def main(page: ft.Page):
    page.title = "Elara AI"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.icon = "/Fotos Elara/Elara.png"
    page.window_height = 800
    page.window_center = True
    page.window_to_front = True
    page.window_width = 500
    page.window_full_screen = False
    
    # Custom color scheme
    primary_color = ft.colors.RED_ACCENT
    secondary_color = ft.colors.RED_200
    
    # Define custom theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=primary_color,
            secondary=secondary_color,
            surface_tint=ft.colors.SURFACE_VARIANT,
        )
    )

    gemini_handler = GeminiHandler()
    current_image_path = None

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update()

    chat_messages = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    new_message = ft.TextField(
        hint_text="Fale com a Elara...",
        border="none",
        bgcolor=ft.colors.TRANSPARENT,
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        focused_bgcolor=ft.colors.TRANSPARENT,
        border_radius=30,
        on_submit=lambda _: send_message(new_message),
    )

    image_preview = ft.Image(
        width=100,
        height=100,
        fit=ft.ImageFit.COVER,
        visible=False,
        border_radius=ft.border_radius.all(10),
    )

    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal current_image_path
        if e.files:
            current_image_path = e.files[0].path
            image_preview.src = current_image_path
            image_preview.visible = True
            delete_image_button.visible = True
            image_preview_container.visible = True
            page.update()

    def clear_image():
        nonlocal current_image_path
        current_image_path = None
        image_preview.src = None
        image_preview.visible = False
        delete_image_button.visible = False
        image_preview_container.visible = False
        page.update()

    pick_files_dialog = ft.FilePicker(on_result=on_file_picked)

    upload_file = ft.IconButton(
        icon=ft.icons.ATTACH_FILE,
        tooltip="Anexar imagem",
        on_click=lambda _: pick_files_dialog.pick_files(
            allow_multiple=False, 
            allowed_extensions=["jpg", "jpeg", "png", "gif"]
        )
    )

    delete_image_button = ft.IconButton(
        icon=ft.icons.DELETE,
        tooltip="Deletar imagem",
        on_click=clear_image,
        visible=False,
    )

    def send_message(e):
        nonlocal current_image_path
        user_message = new_message.value
        if user_message or current_image_path:
            if current_image_path:
                chat_messages.controls.append(ChatMessage(Message("Você", user_message, "user_message", current_image_path)))
                page.update()
            else:
                chat_messages.controls.append(ChatMessage(Message("Você", user_message, "user_message")))
                page.update()
            new_message.value = ""
            page.update()
            
            # Show "Elara está digitando..." message
            elara_digitando.visible = True
            page.update()
            
            responses = gemini_handler.analyze_input(user_message, current_image_path)
            
            # Hide "Elara está digitando..." message
            elara_digitando.visible = False
            
            for response in responses:
                chat_messages.controls.append(ChatMessage(Message("Elara", response, "bot_message")))
                page.update()
            clear_image()
            page.update()

    send_button = ft.IconButton(
        icon=ft.icons.SEND,
        tooltip="Enviar mensagem",
        on_click=lambda _: send_message(new_message),
    )

    image_preview_container = ft.Container(
        content=ft.Stack([
            image_preview,
            ft.Container(
                content=delete_image_button,
                alignment=ft.alignment.top_right,
            ),
        ]),
        visible=False,
    )

    chat_input = ft.Container(
        content=ft.Row(
            [
                upload_file,
                new_message,
                image_preview_container,
                send_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=10,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=ft.border_radius.all(20),
        margin=ft.margin.all(30)
    )
    
    elara_digitando = ft.Container(
        content=ft.Text("Elara está digitando...", color=ft.colors.SECONDARY),
        padding=ft.padding.only(left=70, bottom=-70),
        visible=False
    )

    chat_view = ft.Column(
        [
            ft.Container(
                content=chat_messages,
                expand=True,
                padding=5,
            ),
            elara_digitando,
            chat_input,
        ],
        expand=True,
    )

    def route_change(route):
        page.views.clear()
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        ft.AppBar(title=ft.Text("Configurações"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.DARK_MODE),
                                title=ft.Text("Modo Escuro"),
                                trailing=ft.Switch(value=page.theme_mode == ft.ThemeMode.DARK, on_change=toggle_theme),
                            ),
                            ft.ElevatedButton("Voltar", on_click=lambda _: page.go("/"), icon="ARROW_BACK_IOS")
                        ])
                    ],
                )
            )
        else:
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row(
                                    [
                                        ft.Text("   Elara AI", size=28, weight=ft.FontWeight.BOLD),
                                        ft.IconButton(ft.icons.SETTINGS, on_click=lambda _: page.go("/settings")),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [chat_view],
                                    expand=True,
                                    spacing=20,
                                ),
                            ]),
                            expand=True,
                        )
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.overlay.append(pick_files_dialog)
    page.go(page.route)

ft.app(target=main)