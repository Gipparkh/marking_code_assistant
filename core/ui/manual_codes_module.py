import flet as ft
from core import config
from core.database import add_manual_item
from core.random_generator import generate_random_string
from core.groups import get_group_names


def show_snack_bar(page: ft.Page, message: str, bgcolor: str = "red"):
    page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor)
    page.snack_bar.open = True
    page.update()


class ManualCodesModule:
    def __init__(self, page: ft.Page):
        self.page = page
        self.name_field = None
        self.group_dropdown = None
        self.full_code_field = None
        self.comment_field = None

    def build(self):
        self.name_field = ft.TextField(label="Название *", expand=True)
        self.group_dropdown = ft.Dropdown(
            label="Группа маркировки (опционально)",
            options=[ft.dropdown.Option(g) for g in get_group_names()],
            expand=True
        )
        self.full_code_field = ft.TextField(
            label="Полный код маркировки *",
            multiline=True,
            min_lines=3,
            max_lines=6,
            expand=True
        )
        self.comment_field = ft.TextField(label="Комментарий (опционально)", expand=True)

        save_btn = ft.ElevatedButton(
            "Сохранить внешний код",
            on_click=self.on_save,
            height=48,
            width=float("inf")
        )

        helper_buttons = ft.Row([
            ft.TextButton(
                "Скопировать <GS>",
                on_click=self.on_copy_gs,
                style=ft.ButtonStyle(color="blue")
            ),
            ft.TextButton(
                "Сгенерировать 4 символа",
                on_click=self.on_4random,
                style=ft.ButtonStyle(color="blue")
            ),
            ft.TextButton(
                "Сгенерировать 6 символов",
                on_click=self.on_6random,
                style=ft.ButtonStyle(color="blue")
            ),
            ft.TextButton(
                "Сгенерировать 8 символов",
                on_click=self.on_8random,
                style=ft.ButtonStyle(color="blue")
            )
        ], spacing=10)

        layout = ft.Column([
            ft.Row(
                [ft.Text(f"v{config.APP_VERSION}", size=8, weight="bold", color="grey")],
                alignment=ft.MainAxisAlignment.END
            ),
            self.name_field,
            self.full_code_field,
            self.group_dropdown,
            self.comment_field,
            save_btn,
            helper_buttons
        ], spacing=15)

        return layout

    def on_save(self, e):
        name = self.name_field.value.strip()
        full_code = self.full_code_field.value.strip()
        marking_group = self.group_dropdown.value

        if not name:
            show_snack_bar(self.page, "Введите название!")
            return
        if not full_code:
            show_snack_bar(self.page, "Введите полный код маркировки!")
            return

        try:
            add_manual_item(
                name=name,
                full_code=full_code,
                marking_group=marking_group,
                comment=self.comment_field.value.strip() or ""
            )
            show_snack_bar(self.page, "Внешний код успешно сохранён!", bgcolor="green")

            self.name_field.value = ""
            self.group_dropdown.value = None
            self.full_code_field.value = ""
            self.comment_field.value = ""
            self.page.update()
        except Exception as ex:
            show_snack_bar(self.page, f"Ошибка сохранения: {ex}")

    def on_copy_gs(self, e):
        self.page.set_clipboard("\x1D")
        show_snack_bar(self.page, "Символ <GS> скопирован!", bgcolor="green")

    def on_4random(self, e):
        random_str = generate_random_string(4)
        self.page.set_clipboard(random_str)
        show_snack_bar(self.page, f"Сгенерировано: {random_str}", bgcolor="green")

    def on_6random(self, e):
        random_str = generate_random_string(6)
        self.page.set_clipboard(random_str)
        show_snack_bar(self.page, f"Сгенерировано: {random_str}", bgcolor="green")

    def on_8random(self, e):
        random_str = generate_random_string(8)
        self.page.set_clipboard(random_str)
        show_snack_bar(self.page, f"Сгенерировано: {random_str}", bgcolor="green")