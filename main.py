import flet as ft
import traceback
from core.database import init_db
from core.ui.generator_module import GeneratorModule
from core.ui.manual_codes_module import ManualCodesModule
from core.ui.table_module import TableModule


def main(page: ft.Page):
    try:
        page.window.width = 800
        page.window.height = 620
        page.window.min_width = 800
        page.window.min_height = 620
        page.title = "MCA"
        page.locale = "ru"
        page.scroll = "auto"

        init_db()

        generator_module = GeneratorModule(page)
        manual_module = ManualCodesModule(page)
        table_module = TableModule(page, tabs_ref=None, generator_module=generator_module)

        def on_tab_change(e):
            if tabs.selected_index == 2:
                table_module.refresh()

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=on_tab_change,
            tabs=[
                ft.Tab(text="Генератор", content=generator_module.build()),
                ft.Tab(text="Внешние коды", content=manual_module.build()),
                ft.Tab(text="Каталог", content=table_module.build()),
            ],
            expand=True
        )

        table_module.tabs_ref = tabs
        page.add(tabs)

    except Exception as e:
        error_text = f"КРИТИЧЕСКАЯ ОШИБКА:\n{str(e)}\n\nПОДРОБНОСТИ:\n{traceback.format_exc()}"
        page.add(
            ft.Container(
                content=ft.Text(error_text, color="red", size=12, selectable=True),
                padding=20,
                bgcolor="#ffeeee",
                border=ft.border.all(2, "red")
            )
        )


if __name__ == "__main__":
    ft.app(target=main)