import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from converter import convert_litematica_to_schematica, convert_schematica_to_litematica
from material_gui import MaterialListWindow

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Litematica <-> Schematica Converter")
        self.root.geometry("550x260")
        self.root.resizable(False, False)

        self.loaded_file_path = None
        self.loaded_format = None

        self._create_widgets()

    def _create_widgets(self):
        # Haupt-Container für besseres Padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Frame für Datei-Infos
        info_frame = ttk.LabelFrame(main_frame, text="Datei Information", padding=(15, 15))
        info_frame.pack(fill="x", pady=(0, 15))

        self.file_label = ttk.Label(info_frame, text="Keine Datei geladen", foreground="#ff6b6b", font=("", 10, "bold"))
        self.file_label.pack(anchor="w", pady=(0, 5))

        self.format_label = ttk.Label(info_frame, text="Format: Unbekannt")
        self.format_label.pack(anchor="w")

        # Frame für Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")

        self.btn_load = ttk.Button(btn_frame, text="Datei laden", command=self.load_file)
        self.btn_load.pack(side="left")
        
        self.btn_materials = ttk.Button(btn_frame, text="Materialliste", state="disabled", command=self.show_materials)
        self.btn_materials.pack(side="left", padx=10)

        self.btn_convert = ttk.Button(btn_frame, text="Konvertieren", style="Accent.TButton", state="disabled", command=self.convert_and_save)
        self.btn_convert.pack(side="right")

        # Statuszeile
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(10, 2))
        status_bar.pack(side="bottom", fill="x")

    def show_materials(self):
        if self.loaded_file_path and self.loaded_format:
            MaterialListWindow(self.root, self.loaded_file_path, self.loaded_format)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Wähle eine Schematic oder Litematic Datei",
            filetypes=[
                ("Minecraft Schematics", "*.litematic *.schematic *.schem"),
                ("Litematica", "*.litematic"),
                ("Sponge/Schematica", "*.schematic *.schem"),
                ("Alle Dateien", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            self.loaded_file_path = file_path
            
            # Überprüfe Format anhand der Dateiendung
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".litematic":
                self.loaded_format = "litematica"
            elif ext in [".schematic", ".schem"]:
                self.loaded_format = "schematica"
            else:
                self.loaded_format = "unknown"
                messagebox.showwarning("Warnung", "Das Dateiformat konnte nicht sicher anhand der Endung identifiziert werden.")

            # Aktualisiere GUI
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Geladen: {filename}", foreground="green")
            self.format_label.config(text=f"Format: {self.loaded_format.capitalize()}")
            self.btn_convert.config(state="normal")
            self.btn_materials.config(state="normal")
            
            # Zeige Zielformat im Button an
            if self.loaded_format == "litematica":
                target = "Schematica (Sponge)"
            else:
                target = "Litematica"
                
            self.btn_convert.config(text=f"Konvertiere zu {target} & Speichern")
            self.status_var.set(f"Datei '{filename}' erfolgreich ausgewählt.")

        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Datei nicht verarbeiten:\n{e}")
            self.status_var.set("Fehler beim Verarbeiten der Datei.")

    def convert_and_save(self):
        if not self.loaded_file_path or not self.loaded_format:
            return

        if self.loaded_format == "litematica":
            target_ext = ".schem"
            target_format = "Sponge/Schematica"
            default_name = os.path.splitext(os.path.basename(self.loaded_file_path))[0] + ".schem"
        else:
            target_ext = ".litematic"
            target_format = "Litematica"
            default_name = os.path.splitext(os.path.basename(self.loaded_file_path))[0] + ".litematic"

        save_path = filedialog.asksaveasfilename(
            title=f"Speichern als {target_format}",
            defaultextension=target_ext,
            initialfile=default_name,
            filetypes=[(target_format, f"*{target_ext}")]
        )

        if not save_path:
            return

        try:
            self.status_var.set(f"Konvertiere zu {target_format}...")
            self.root.update()

            if self.loaded_format == "litematica":
                convert_litematica_to_schematica(self.loaded_file_path, save_path)
            else:
                convert_schematica_to_litematica(self.loaded_file_path, save_path)

            self.status_var.set("Konvertierung erfolgreich!")
            messagebox.showinfo("Erfolg", f"Datei erfolgreich konvertiert und gespeichert unter:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Konvertierungsfehler", f"Fehler bei der Konvertierung:\n{e}")
            self.status_var.set("Fehler bei der Konvertierung.")
