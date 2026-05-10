import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import gzip
import os

try:
    import nbtlib
    import litemapy
except ImportError:
    import subprocess
    import sys
    # Versuch, litemapy (und damit nbtlib) automatisch zu installieren, falls nicht vorhanden
    subprocess.check_call([sys.executable, "-m", "pip", "install", "litemapy", "nbtlib"])
    import nbtlib
    import litemapy

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Litematica <-> Schematica Converter")
        self.root.geometry("450x250")
        self.root.resizable(False, False)

        self.loaded_file_path = None
        self.loaded_format = None

        self._create_widgets()

    def _create_widgets(self):
        # Frame für Datei-Infos
        info_frame = ttk.LabelFrame(self.root, text="Datei Information", padding=(10, 10))
        info_frame.pack(fill="x", padx=10, pady=10)

        self.file_label = ttk.Label(info_frame, text="Keine Datei geladen", foreground="red")
        self.file_label.pack(anchor="w")

        self.format_label = ttk.Label(info_frame, text="Format: Unbekannt")
        self.format_label.pack(anchor="w")

        # Frame für Buttons
        btn_frame = ttk.Frame(self.root, padding=(10, 10))
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_load = ttk.Button(btn_frame, text="Datei laden", command=self.load_file)
        self.btn_load.pack(side="left", padx=5)

        self.btn_convert = ttk.Button(btn_frame, text="Konvertieren & Speichern", state="disabled", command=self.convert_and_save)
        self.btn_convert.pack(side="right", padx=5)

        # Statuszeile
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

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

        from litemapy import Schematic, Region

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
                # Konvertiere von Litematica zu Sponge Schematic
                sch = Schematic.load(self.loaded_file_path)
                if not sch.regions:
                    raise ValueError("Keine Regionen in der Litematica-Datei gefunden.")
                
                # Wir konvertieren aktuell nur die erste Region, 
                # da Sponge Schematics standardmäßig nicht multi-regionfähig sind.
                region_name = list(sch.regions.keys())[0]
                region = sch.regions[region_name]
                
                sponge_nbt = region.to_sponge_nbt()
                sponge_nbt.save(save_path, gzipped=True, byteorder="big")

            else:
                # Konvertiere von Sponge Schematic zu Litematica
                nbt_data = nbtlib.load(self.loaded_file_path)
                
                # from_sponge_nbt gibt ein Tuple (Region, version) zurück
                region, version = Region.from_sponge_nbt(nbt_data)
                
                sch_name = os.path.basename(save_path)
                # Erstelle ein Schematic-Objekt aus der Region
                sch = region.as_schematic(name=sch_name, author="ConverterGUI")
                sch.save(save_path)

            self.status_var.set("Konvertierung erfolgreich!")
            messagebox.showinfo("Erfolg", f"Datei erfolgreich konvertiert und gespeichert unter:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Konvertierungsfehler", f"Fehler bei der Konvertierung:\n{e}")
            self.status_var.set("Fehler bei der Konvertierung.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()
