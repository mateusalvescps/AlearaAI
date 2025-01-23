import flet as ft
import os

class Message:
    def __init__(self, user_name: str, text: str = None, message_type: str = None, file_path: str = None):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.file_path = file_path

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START

        # Create message content column
        message_content = ft.Column(tight=True, spacing=5)

        # Add text if it exists and is a text message
        if message.text:
            message_content.controls.append(ft.Text(message.user_name, weight="bold"))
            if message.user_name == "Você":
                message_content.controls.append(ft.Text(message.text, selectable=True))
            else:
                # For Elara's responses, use Markdown to properly format links and styling
                markdown_content = ft.Markdown(
                    value=message.text,
                    selectable=True,
                    extension_set="gitHubWeb",
                    on_tap_link=lambda e: self.handle_link_tap(e.data),
                )
                message_content.controls.append(markdown_content)

        # Add image if it exists
        if message.file_path and os.path.exists(message.file_path):
            message_content.controls.append(ft.Image(src=message.file_path, width=200, height=200, fit=ft.ImageFit.CONTAIN))

        # Define message container style
        message_container = ft.Container(
            content=message_content,
            width=400,
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE) if message.user_name == "Você" else ft.colors.with_opacity(0.1, ft.colors.PRIMARY),
        )

        # Create avatar
        avatar = ft.CircleAvatar(
            content=ft.Text(self.get_initials(message.user_name)),
            color=ft.colors.ON_PRIMARY,
            bgcolor=ft.colors.PRIMARY if message.user_name == "Você" else ft.colors.SECONDARY,
        )

        # Set message alignment
        if message.user_name == "Você":
            self.alignment = ft.MainAxisAlignment.END
            self.controls = [message_container, avatar]
        else:
            self.alignment = ft.MainAxisAlignment.START
            self.controls = [avatar, message_container]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    def handle_link_tap(self, url: str):
        self.page.launch_url(url)