import flet as ft

from core import config
from core.database import search_items, delete_item_by_id
from core.groups import get_group_names
from core.code_generator import get_code_url


class TableModule:
    def __init__(self, page: ft.Page, tabs_ref=None, generator_module=None):
        self.page = page
        self.tabs_ref = tabs_ref
        self.generator_module = generator_module
        self.search_field = None
        self.group_filter = None
        self.type_filter = None
        self.content_column = None

    def build(self):
        group_names = get_group_names()
        group_options = [ft.dropdown.Option("Все")] + [
            ft.dropdown.Option(name) for name in group_names
        ]

        self.type_filter = ft.Dropdown(
            label="Тип записи",
            options=[
                ft.dropdown.Option("Все"),
                ft.dropdown.Option("Сгенерированные"),
                ft.dropdown.Option("Внешние")
            ],
            value="Все",
            width=180,
            on_change=self.on_filter_change
        )

        self.group_filter = ft.Dropdown(
            label="Группа маркировки",
            options=group_options,
            value="Все",
            width=180,
            on_change=self.on_filter_change
        )

        self.search_field = ft.TextField(
            label="Поиск по названию",
            expand=True,
            on_change=self.on_search
        )

        self.content_column = ft.Column(
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        table_container = ft.Container(
            content=self.content_column,
            padding=0,
            border=ft.border.all(1, "grey"),
            border_radius=5,
            expand=True,
        )

        layout = ft.Column([
            ft.Row(
                [ft.Text(f"v{config.APP_VERSION}", size=8, weight="bold", color="grey")],
                alignment=ft.MainAxisAlignment.END
            ),
            ft.Row(
                controls=[
                    self.type_filter,
                    self.group_filter,
                    ft.Container(self.search_field, expand=True)
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                expand=False
            ),
            table_container
        ], expand=True)

        return layout

    def refresh(self):
        type_value = self.type_filter.value
        if type_value == "Сгенерированные":
            item_type = "generated"
        elif type_value == "Внешние":
            item_type = "manual"
        else:
            item_type = None

        group_filter = None
        if item_type != "manual":
            group_filter = None if self.group_filter.value == "Все" else self.group_filter.value

        search_query = self.search_field.value.strip()
        records = search_items(item_type=item_type, group_filter=group_filter, name_query=search_query)
        self._update_content(records)

    def on_filter_change(self, e):
        self.refresh()

    def on_search(self, e):
        self.refresh()

    def _get_manual_code_url(self, full_code: str) -> str:
        if not full_code:
            return ""
        if full_code.isdigit():
            if len(full_code) == 8:
                return get_code_url("EAN-8", full_code)
            elif len(full_code) == 13:
                return get_code_url("EAN-13", full_code)
        from core.code_generator import DATAMATRIX_URL_TEMPLATE
        import urllib.parse
        encoded = urllib.parse.quote(full_code, safe='')
        return DATAMATRIX_URL_TEMPLATE.format(full_code=encoded)

    def _preview_manual_code(self, full_code: str):
        image_url = self._get_manual_code_url(full_code)
        if not image_url:
            self.page.snack_bar = ft.SnackBar(ft.Text("Не удалось сгенерировать изображение"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return

        img = ft.Image(src=image_url, width=250, height=250, fit=ft.ImageFit.CONTAIN)
        dlg = ft.AlertDialog(
            title=ft.Text("Предпросмотр кода"),
            content=ft.Column([img, ft.Text(f"Код: {full_code[:50]}{'...' if len(full_code) > 50 else ''}")], tight=True),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: self.page.close(dlg))]
        )
        self.page.open(dlg)

    def _build_js_code(self, record):
        item_id, name, item_type, marking_group, short_ean, full_code, comment = record
        if item_type == "manual":
            code = full_code
        else:
            if len(short_ean) in (8, 13) and short_ean.isdigit():
                code = short_ean
            else:
                try:
                    from core.code_generator import build_full_code
                    code = build_full_code("DataMatrix", short_ean, marking_group)
                except:
                    code = "[ошибка]"
        return f"requirejs(['browser!ManagerWorkplaceDevice/Manager/reader'], function(scannerLib){{scannerLib.Main._notify('onBarcodeScan', {{Code:'{code}'}}); }});"

    def _update_content(self, records):
        self.content_column.controls.clear()

        if not records:
            self.content_column.scroll = None
            self.content_column.expand = True
            self.content_column.controls.append(
                ft.Container(
                    content=ft.Text("В локальной базе данных нет записей", italic=True, color="grey", size=16),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            self.content_column.scroll = ft.ScrollMode.AUTO
            self.content_column.expand = True

            header = ft.Container(
                ft.Row([
                    ft.Container(ft.Text("Название"), expand=True, alignment=ft.alignment.center),
                    ft.Container(ft.Text("Тип"), width=100, alignment=ft.alignment.center),
                    ft.Container(ft.Text("Группа / Код"), expand=True, alignment=ft.alignment.center),
                    ft.Container(ft.Text("Комментарий"), expand=True, alignment=ft.alignment.center),
                    ft.Container(ft.Text("Действия"), width=140, alignment=ft.alignment.center),
                ], spacing=10),
                padding=ft.padding.only(left=5, right=5, top=8, bottom=8),
                border=ft.border.only(bottom=ft.border.BorderSide(1, "grey"))
            )
            self.content_column.controls.append(header)

            for i, record in enumerate(records):
                item_id = record[0]
                name = record[1] or ""
                item_type = record[2] or ""
                marking_group = record[3] or ""
                short_ean = record[4] or ""
                full_code = record[5] or ""
                comment = record[6] or ""

                if item_type == "generated":
                    group_or_code_text = f"{marking_group} (EAN: {short_ean})"
                else:
                    group_or_code_text = full_code

                buttons = []

                if item_type == "generated":
                    buttons.append(
                        ft.IconButton(
                            icon="arrow_upward",
                            icon_color="green",
                            tooltip="Заполнить в генераторе",
                            on_click=lambda e, r=(name, marking_group, short_ean, "", comment): self._on_fill(r),
                            icon_size=18
                        )
                    )
                else:
                    buttons.append(
                        ft.IconButton(
                            icon="visibility",
                            icon_color="purple",
                            tooltip="Предпросмотр кода",
                            on_click=lambda e, c=full_code: self._preview_manual_code(c),
                            icon_size=18
                        )
                    )

                js_code = self._build_js_code(record)
                buttons.extend([
                    ft.IconButton(
                        icon="content_copy",
                        icon_color="blue",
                        tooltip="Скопировать код вызова",
                        on_click=lambda e, c=js_code: self._copy_js(c),
                        icon_size=18
                    ),
                    ft.IconButton(
                        icon="delete",
                        icon_color="red",
                        tooltip="Удалить запись",
                        on_click=lambda e, rid=item_id: self._on_delete(rid),
                        icon_size=18
                    )
                ])

                row = ft.Container(
                    ft.Row([
                        ft.Container(ft.Text(name), expand=True, alignment=ft.alignment.center),
                        ft.Container(ft.Text("Gen" if item_type == "generated" else "Save"), width=100,
                                     alignment=ft.alignment.center),
                        ft.Container(ft.Text(group_or_code_text), expand=True, alignment=ft.alignment.center),
                        ft.Container(ft.Text(comment), expand=True, alignment=ft.alignment.center),
                        ft.Container(ft.Row(buttons, spacing=4), width=140, alignment=ft.alignment.center),
                    ], spacing=10),
                    padding=ft.padding.only(left=5, right=5, top=8, bottom=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "grey")) if i < len(records) - 1 else None
                )
                self.content_column.controls.append(row)

        self.page.update()

    def _copy_js(self, js_code):
        self.page.set_clipboard(js_code)
        self.page.snack_bar = ft.SnackBar(ft.Text("Код вызова скопирован!"), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()

    def _on_fill(self, record):
        if not self.generator_module or not record:
            return
        if self.tabs_ref:
            self.tabs_ref.selected_index = 0
            self.page.update()
        self.generator_module.fill_from_record(record)

    def _on_delete(self, item_id: int):
        try:
            success = delete_item_by_id(item_id)
            if success:
                self.refresh()
                self.page.snack_bar = ft.SnackBar(ft.Text("Запись удалена"), bgcolor="green")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Запись не найдена"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка удаления: {ex}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()