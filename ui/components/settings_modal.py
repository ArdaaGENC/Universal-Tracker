import flet as ft
import shutil
import zipfile
import os
from core.themes import THEMES

class SettingsModalOverlay(ft.Stack):
    def __init__(self, state):
        super().__init__(expand=True, visible=False)
        self.state = state
        
        # Arayüzü inşa et ve merkezi değişim motoruna abone ol
        self._build_ui()
        self.state.subscribe(self._handle_state_update)

    def _handle_state_update(self, msg):
        if isinstance(msg, dict) and msg.get("action") == "DATA_CHANGED":
            self._update_texts()

    def open_modal(self):
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.color_drop.value = self.state.theme_name
        self.lang_drop.value = self.state.language
        self.visible = True
        self.update()

    def _close_modal(self, e=None):
        self.visible = False
        self.update()

    def _toggle_theme(self, e):
        new_mode = "dark" if e.control.value else "light"
        self.state.set_theme_mode(new_mode)
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.update()

    def _change_color(self, e):
        self.state.set_theme_name(e.control.value)
        self.color_drop.value = self.state.theme_name
        self.update()

    def _change_language(self, e):
        self.state.set_language(e.control.value)
        self.lang_drop.value = self.state.language
        self.update()

    def _show_snack(self, message):
        if self.page:
            self.page.snack_bar = ft.SnackBar(ft.Text(message))
            self.page.snack_bar.open = True
            self.page.update()

    def _trigger_export(self, e):
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            file_path = filedialog.asksaveasfilename(
                initialfile="UniversalTracker_Backup.zip",
                defaultextension=".zip",
                filetypes=[("ZIP Files", "*.zip")]
            )
            root.destroy()
            
            if file_path:
                base_name = file_path
                if base_name.endswith('.zip'):
                    base_name = base_name[:-4]
                shutil.make_archive(base_name, 'zip', 'data')
                self._show_snack(self.state.t("backup_success"))
        except Exception:
            self._show_snack(self.state.t("backup_error"))

    def _trigger_import(self, e):
        try:
            import tkinter as tk
            from tkinter import filedialog
            import tempfile
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            file_path = filedialog.askopenfilename(
                filetypes=[("ZIP Files", "*.zip")]
            )
            root.destroy()
            
            if file_path:
                # KÖKTEN ÇÖZÜM: Klasörü silmek yerine geçici belleğe açıp tek tek kopyalıyoruz.
                # Böylece Windows'un "Dosya o an kullanımda" kilitleme çıkmazını tamamen baypas ediyoruz.
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdir)
                    
                    os.makedirs("data", exist_ok=True)
                    
                    # Geçici klasördeki yeni verileri mevcut data klasörünün içine güvenle yediriyoruz
                    for root_dir, dirs, files in os.walk(tmpdir):
                        for file in files:
                            src_file = os.path.join(root_dir, file)
                            rel_path = os.path.relpath(src_file, tmpdir)
                            dest_file = os.path.join("data", rel_path)
                            
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            try:
                                shutil.copy2(src_file, dest_file)
                            except Exception:
                                # Eğer o an ekranda açık olan kilitli bir poster resmi varsa pas geç, uygulamayı dondurma
                                pass
                
                self._show_snack(self.state.t("import_success"))
                self.state.refresh_data() # Yeni veritabanını anında arayüze senkronize et
        except Exception:
            self._show_snack(self.state.t("backup_error"))

    def _update_texts(self):
        self.title_text.value = self.state.t("settings")
        self.appearance_text.value = self.state.t("appearance")
        self.theme_switch.label = self.state.t("dark_mode")
        self.color_drop.label = self.state.t("custom_theme")
        self.lang_drop.label = self.state.t("language")
        
        self.backup_text.value = self.state.t("backup_section")
        self.export_btn.text = self.state.t("export_backup")
        self.import_btn.text = self.state.t("import_backup")
        
        try:
            self.update()
        except Exception: 
            pass

    def _build_ui(self):
        self.theme_switch = ft.Switch(
            label=self.state.t("dark_mode"),
            value=(self.state.theme_mode == "dark"),
            on_change=self._toggle_theme
        )

        dropdown_options = []
        for key, value in THEMES.items():
            dropdown_options.append(ft.DropdownOption(key=key, text=value["name"]))

        self.color_drop = ft.Dropdown(
            label=self.state.t("custom_theme"),
            options=dropdown_options,
            width=250,
            on_select=self._change_color
        )

        lang_options = [
            ft.DropdownOption(key="en", text="English"),
            ft.DropdownOption(key="tr", text="Türkçe"),
            ft.DropdownOption(key="es", text="Español")
        ]
        
        self.lang_drop = ft.Dropdown(
            label=self.state.t("language"),
            options=lang_options,
            width=250,
            on_select=self._change_language
        )

        self.title_text = ft.Text(self.state.t("settings"), weight=ft.FontWeight.BOLD, size=18, color="primary")
        self.appearance_text = ft.Text(self.state.t("appearance"), weight=ft.FontWeight.BOLD, color="primary")
        self.backup_text = ft.Text(self.state.t("backup_section"), weight=ft.FontWeight.BOLD, color="primary")

        self.export_btn = ft.ElevatedButton(
            self.state.t("export_backup"),
            icon=ft.Icons.DOWNLOAD,
            on_click=self._trigger_export
        )
        
        self.import_btn = ft.ElevatedButton(
            self.state.t("import_backup"),
            icon=ft.Icons.UPLOAD,
            on_click=self._trigger_import
        )

        backup_row = ft.Row([self.export_btn, self.import_btn], alignment=ft.MainAxisAlignment.START, spacing=10)

        modal_header = ft.Row(
            controls=[
                self.title_text,
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=self._close_modal)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        settings_content = ft.Column(
            controls=[
                self.appearance_text,
                self.theme_switch,
                self.color_drop,
                self.lang_drop,
                ft.Divider(height=10, color="outlineVariant"),
                self.backup_text,
                backup_row
            ],
            spacing=15
        )

        self.modal_box = ft.Container(
            width=450,
            height=480,
            bgcolor="surface",
            border_radius=15,
            padding=20,
            content=ft.Column(
                controls=[
                    modal_header,
                    ft.Divider(height=1),
                    settings_content
                ],
                expand=True
            )
        )

        self.modal_overlay = ft.Container(
            content=self.modal_box,
            bgcolor="#8A000000",
            alignment=ft.Alignment(0, 0),
            expand=True
        )

        self.controls = [self.modal_overlay]