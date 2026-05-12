import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from converter import (
    convert_litematica_to_schematica, 
    convert_schematica_to_litematica,
    get_schematic_info
)
from material_gui import MaterialListWindow
from preview import export_3d_preview
from updater import CURRENT_VERSION

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Litematica <-> Schematica Converter v{CURRENT_VERSION}")
        self.root.geometry("650x420")
        self.root.resizable(False, False)

        self.loaded_file_path = None
        self.loaded_format = None
        self.block_mapping = {}

        self._create_widgets()

    def _create_widgets(self):
        # Haupt-Container für besseres Padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Oberer Bereich: Lade-Aktionen
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 15))
        
        self.btn_load = ttk.Button(top_frame, text="Datei laden", command=self.load_file)
        self.btn_load.pack(side="left", padx=(0, 10))
        
        self.btn_batch = ttk.Button(top_frame, text="Batch Ordner...", command=self.batch_convert)
        self.btn_batch.pack(side="left")

        # Frame für Datei-Infos
        info_frame = ttk.LabelFrame(main_frame, text="Datei Information", padding=(15, 10))
        info_frame.pack(fill="x", pady=(0, 15))

        self.file_label = ttk.Label(info_frame, text="Keine Datei geladen", foreground="#ff6b6b", font=("", 10, "bold"))
        self.file_label.pack(anchor="w", pady=(0, 10))

        details_frame = ttk.Frame(info_frame)
        details_frame.pack(fill="x")

        self.format_label = ttk.Label(details_frame, text="Format: Unbekannt")
        self.format_label.grid(row=0, column=0, sticky="w", padx=(0, 30), pady=(0, 5))

        self.regions_label = ttk.Label(details_frame, text="Regionen: -")
        self.regions_label.grid(row=0, column=1, sticky="w", padx=(0, 30), pady=(0, 5))

        self.dims_label = ttk.Label(details_frame, text="Größe: -")
        self.dims_label.grid(row=1, column=0, columnspan=2, sticky="w")

        # Frame für Werkzeuge
        tools_frame = ttk.LabelFrame(main_frame, text="Werkzeuge", padding=(15, 10))
        tools_frame.pack(fill="x", pady=(0, 15))

        self.btn_materials = ttk.Button(tools_frame, text="Materialliste", state="disabled", command=self.show_materials)
        self.btn_materials.pack(side="left", padx=(0, 10))

        self.btn_preview = ttk.Button(tools_frame, text="3D Vorschau", state="disabled", command=self.show_preview)
        self.btn_preview.pack(side="left", padx=(0, 10))
        
        self.btn_replace = ttk.Button(tools_frame, text="Blöcke Ersetzen", command=self.show_replace_dialog)
        self.btn_replace.pack(side="left")

        # Frame für Konvertieren Button (ganz unten, nimmt volle Breite)
        self.btn_convert = ttk.Button(main_frame, text="Konvertieren & Speichern", style="Accent.TButton", state="disabled", command=self.convert_and_save)
        self.btn_convert.pack(fill="x", pady=(10, 0))

        # Statuszeile
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(10, 2))
        status_bar.pack(side="bottom", fill="x")

    def show_materials(self):
        if self.loaded_file_path and self.loaded_format:
            MaterialListWindow(self.root, self.loaded_file_path, self.loaded_format)

    def show_preview(self):
        if not self.loaded_file_path or not self.loaded_format:
            return
            
        self.btn_preview.config(state="disabled")
        self.status_var.set("Generiere 3D Vorschau (dies kann einen Moment dauern)...")
        self.root.update()
        
        def run_export():
            try:
                export_3d_preview(self.loaded_file_path, self.loaded_format)
                self.root.after(0, lambda: self.status_var.set("3D Vorschau im Browser geöffnet."))
            except Exception as e:
                self.root.after(0, lambda err=e: messagebox.showerror("Vorschau Fehler", f"Fehler bei der 3D Vorschau:\n{err}"))
                self.root.after(0, lambda: self.status_var.set("Fehler bei der Vorschau."))
            finally:
                self.root.after(0, lambda: self.btn_preview.config(state="normal"))
                
        threading.Thread(target=run_export, daemon=True).start()

    def show_replace_dialog(self):
        """Öffnet ein Fenster zum Definieren von Block-Ersetzungen."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Suchen & Ersetzen")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        
        main_d = ttk.Frame(dialog, padding=15)
        main_d.pack(fill="both", expand=True)

        ttk.Label(main_d, text="Format: minecraft:old_block -> minecraft:new_block", font=("", 9, "italic")).pack(pady=(0, 10))
        
        txt_mapping = tk.Text(main_d, height=10, font=("Consolas", 10))
        txt_mapping.pack(fill="both", expand=True)
        
        # Aktuelles Mapping laden
        mapping_str = "\n".join([f"{k} -> {v}" for k, v in self.block_mapping.items()])
        txt_mapping.insert("1.0", mapping_str)
        
        def save_mapping():
            lines = txt_mapping.get("1.0", "end-1c").split("\n")
            new_mapping = {}
            for line in lines:
                if "->" in line:
                    parts = line.split("->")
                    if len(parts) == 2:
                        old = parts[0].strip()
                        new = parts[1].strip()
                        if old and new:
                            new_mapping[old] = new
            self.block_mapping = new_mapping
            self.status_var.set(f"{len(self.block_mapping)} Ersetzungen aktiv.")
            dialog.destroy()
            
        ttk.Button(main_d, text="Speichern", style="Accent.TButton", command=save_mapping).pack(pady=(15, 0))

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
            
            # Hole zusätzliche Infos
            regions, dims = get_schematic_info(file_path, self.loaded_format)
            self.regions_label.config(text=f"Regionen: {regions}")
            self.dims_label.config(text=f"Größe: {dims}")

            self.btn_convert.config(state="normal")
            self.btn_materials.config(state="normal")
            self.btn_preview.config(state="normal")
            
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

    def batch_convert(self):
        folder_path = filedialog.askdirectory(title="Ordner für Batch-Konvertierung auswählen")
        if not folder_path:
            return

        # Frage nach Zielformat
        if not messagebox.askyesno("Batch", "Sollen alle .litematic zu .schem UND alle .schem zu .litematic konvertiert werden?"):
            return

        files = [f for f in os.listdir(folder_path) if f.endswith((".litematic", ".schem", ".schematic"))]
        if not files:
            messagebox.showinfo("Batch", "Keine passenden Dateien im Ordner gefunden.")
            return

        success_count = 0
        error_count = 0
        
        self.status_var.set(f"Batch: Verarbeite {len(files)} Dateien...")
        self.root.update()

        for filename in files:
            input_path = os.path.join(folder_path, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            try:
                if ext == ".litematic":
                    output_path = os.path.join(folder_path, os.path.splitext(filename)[0] + ".schem")
                    convert_litematica_to_schematica(input_path, output_path, self.block_mapping)
                else:
                    output_path = os.path.join(folder_path, os.path.splitext(filename)[0] + ".litematic")
                    convert_schematica_to_litematica(input_path, output_path, self.block_mapping)
                success_count += 1
            except:
                error_count += 1

        self.status_var.set(f"Batch abgeschlossen. Erfolg: {success_count}, Fehler: {error_count}")
        messagebox.showinfo("Batch Erfolg", f"Batch-Konvertierung abgeschlossen.\n\nErfolgreich: {success_count}\nFehler: {error_count}")

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
                convert_litematica_to_schematica(self.loaded_file_path, save_path, self.block_mapping)
            else:
                convert_schematica_to_litematica(self.loaded_file_path, save_path, self.block_mapping)

            self.status_var.set("Konvertierung erfolgreich!")
            messagebox.showinfo("Erfolg", f"Datei erfolgreich konvertiert und gespeichert unter:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Konvertierungsfehler", f"Fehler bei der Konvertierung:\n{e}")
            self.status_var.set("Fehler bei der Konvertierung.")
