import flet as ft
from core import config
from core.groups import get_group_names
from core.code_generator import build_full_code, get_code_url
from core.database import add_generated_item


def show_snack_bar(page: ft.Page, message: str, bgcolor: str = "red"):
    page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor)
    page.snack_bar.open = True
    page.update()


class GeneratorModule:
    def __init__(self, page: ft.Page):
        self.page = page
        self.code_type_dropdown = None
        self.group_dropdown = None
        self.name_field = None
        self.ean_field = None
        self.comment_field = None
        self.image_container = None
        self.full_code_display = None
        self.last_js_code = ""
        self.first_row_container = None
        self.copy_js_btn = None
        self.copy_adb_btn = None
        self.save_image_btn = None

    def build(self):
        self.code_type_dropdown = ft.Dropdown(
            label="Тип кода *",
            options=[
                ft.dropdown.Option("DataMatrix"),
                ft.dropdown.Option("EAN-13"),
                ft.dropdown.Option("EAN-8")
            ],
            value="DataMatrix",
            width=150,
            on_change=self.on_code_type_change
        )
        self.ean_field = ft.TextField(label="EAN (13 цифр) *", width=200)

        group_names = get_group_names()
        if not group_names:
            group_names = ["(нет групп в marking_groups.json)"]
        self.group_dropdown = ft.Dropdown(
            label="Группа маркировки *",
            options=[ft.dropdown.Option(name) for name in group_names],
            expand=True
        )

        self.name_field = ft.TextField(label="Название номенклатуры (опционально)", expand=True)
        self.comment_field = ft.TextField(label="Комментарий (опционально)", expand=True)

        button_height = 48

        generate_btn = ft.ElevatedButton(
            "Сгенерировать код",
            on_click=self.on_generate,
            height=100,
            width=float("inf")
        )

        self.save_image_btn = ft.ElevatedButton(
            "Сохранить изображение",
            on_click=self.on_save_image,
            disabled=True,
            height=button_height,
            expand=True
        )
        self.copy_js_btn = ft.ElevatedButton(
            "Скопировать код вызова",
            on_click=self.on_copy_js,
            disabled=True,
            height=button_height,
            expand=True
        )
        save_db_btn = ft.ElevatedButton(
            "Сохранить в БД",
            on_click=self.on_save,
            height=button_height,
            expand=True
        )
        self.copy_adb_btn = ft.ElevatedButton(
            "Скопировать ADB-команду",
            on_click=self.on_copy_adb,
            disabled=True,
            height=button_height,
            expand=True
        )

        buttons_col = ft.Column([
            generate_btn,
            ft.Row([self.save_image_btn, self.copy_js_btn], spacing=10),
            ft.Row([save_db_btn, self.copy_adb_btn], spacing=10)
        ], spacing=10)

        self.image_container = ft.Container(
            content=ft.Text("Код", color="grey"),
            alignment=ft.alignment.center,
            width=222,
            height=222,
            bgcolor="white",
            border=ft.border.all(1, "grey"),
            border_radius=5,
            padding=0
        )

        self.full_code_display = ft.TextField(
            label="Сгенерированный код",
            read_only=True,
            expand=True,
        )

        self.first_row_container = ft.Row(spacing=10)
        self._update_first_row()

        layout = ft.Column([
            ft.Row(
                [ft.Text(f"v{config.APP_VERSION}", size=8, weight="bold", color="grey")],
                alignment=ft.MainAxisAlignment.END
            ),
            self.first_row_container,
            self.name_field,
            self.comment_field,
            ft.Row([
                self.image_container,
                ft.Container(buttons_col, expand=True, padding=ft.padding.only(left=20))
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            self.full_code_display
        ], spacing=15, expand=True)

        return layout

    def _update_first_row(self):
        controls = [self.code_type_dropdown, self.ean_field]
        if self.code_type_dropdown.value == "DataMatrix":
            controls.append(self.group_dropdown)
        self.first_row_container.controls = controls
        self.page.update()

    def on_code_type_change(self, e):
        self._update_first_row()

    def on_generate(self, e):
        code_type = self.code_type_dropdown.value
        ean = self.ean_field.value.strip()

        if not code_type:
            show_snack_bar(self.page, "Выберите тип кода!")
            return
        if not ean:
            show_snack_bar(self.page, "Введите EAN!")
            return

        group = None
        if code_type == "DataMatrix":
            group = self.group_dropdown.value
            if not group or "(нет групп" in group:
                show_snack_bar(self.page, "Выберите группу маркировки для DataMatrix!")
                return

        try:
            full_code = build_full_code(code_type, ean, group)
            self.full_code_display.value = full_code
            self.last_js_code = f"requirejs(['browser!ManagerWorkplaceDevice/Manager/reader'], function(scannerLib){{scannerLib.Main._notify('onBarcodeScan', {{Code:'{full_code}'}}); }});"

            image_url = get_code_url(code_type, full_code)
            self.image_container.content = ft.Container(
                content=ft.Image(src=image_url, width=200, height=200, fit=ft.ImageFit.CONTAIN),
                alignment=ft.alignment.center,
                bgcolor="white"
            )

            self.copy_js_btn.disabled = False
            self.copy_adb_btn.disabled = False
            self.save_image_btn.disabled = False
            self.page.update()
        except Exception as ex:
            show_snack_bar(self.page, f"Ошибка генерации: {ex}")

    def on_copy_js(self, e):
        if not self.last_js_code:
            show_snack_bar(self.page, "Сначала сгенерируйте код!")
            return
        self.page.set_clipboard(self.last_js_code)
        show_snack_bar(self.page, "Код вызова скопирован в буфер обмена!", bgcolor="green")

    def on_copy_adb(self, e):
        adb_command = "adb shell input text 'ADB-КОМАНДА: НЕ РЕАЛИЗОВАНА'"
        self.page.set_clipboard(adb_command)
        show_snack_bar(self.page, "ADB-команда скопирована (заглушка)!", bgcolor="orange")

    def on_save_image(self, e):
        show_snack_bar(self.page, "Сохранение изображения — пока недоступно", bgcolor="orange")

    def on_save(self, e):
        name = self.name_field.value.strip()
        if not name:
            show_snack_bar(self.page, "Введите название для сохранения!")
            return

        comment = self.comment_field.value.strip() or ""
        ean = self.ean_field.value.strip()
        group = ""

        code_type = self.code_type_dropdown.value
        if code_type == "DataMatrix":
            group = self.group_dropdown.value
            if not group or "(нет групп" in group:
                show_snack_bar(self.page, "Выберите группу для сохранения DataMatrix!")
                return

        try:
            add_generated_item(
                name=name,
                marking_group=group,
                short_ean=ean,
                comment=comment
            )
            show_snack_bar(self.page, "Запись успешно сохранена!", bgcolor="green")
        except Exception as ex:
            show_snack_bar(self.page, f"Ошибка сохранения: {ex}")

    def fill_from_record(self, record):
        name, group, ean, saved_code, comment = record
        self.name_field.value = name or ""
        self.comment_field.value = comment or ""
        self.ean_field.value = ean or ""

        if group:
            self.code_type_dropdown.value = "DataMatrix"
            self.group_dropdown.value = group
        else:
            if ean and len(ean) == 8:
                self.code_type_dropdown.value = "EAN-8"
            else:
                self.code_type_dropdown.value = "EAN-13"
            self.group_dropdown.value = None

        self._update_first_row()
        self.page.update()