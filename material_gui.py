import tkinter as tk
from tkinter import ttk, messagebox
from material_list import get_material_list, format_quantity

class MaterialListWindow:
    def __init__(self, parent, file_path, file_format):
        self.window = tk.Toplevel(parent)
        self.window.title("Materialliste")
        self.window.geometry("750x550")
        # Fenster zentrieren oder über dem Hauptfenster platzieren
        self.window.transient(parent)
        
        self.file_path = file_path
        self.file_format = file_format
        self.materials = {}
        
        self._create_widgets()
        
        # Materialien laden, am besten per after, damit GUI sich aufbaut
        self.window.after(100, self._load_materials)

    def _create_widgets(self):
        # Haupt-Container für besseres Padding
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Info Label
        info_label = ttk.Label(main_frame, text="Doppelklick auf einen Eintrag, um ihn abzuhaken.", font=("", 10, "italic"))
        info_label.pack(pady=(0, 15))

        # Frame für Treeview
        frame = ttk.Frame(main_frame)
        frame.pack(fill="both", expand=True)
        
        # Spalten: Done, Material, Total, Shulkers
        columns = ("done", "material", "total", "shulkers")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("done", text="Status")
        self.tree.heading("material", text="Material (Block-ID)")
        self.tree.heading("total", text="Gesamtmenge")
        self.tree.heading("shulkers", text="Kisten / Stacks")
        
        self.tree.column("done", width=70, anchor="center")
        self.tree.column("material", width=250, anchor="w")
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("shulkers", width=200, anchor="e")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Doppelklick Event binden
        self.tree.bind("<Double-1>", self._toggle_done)
        
        # Tag für durchgestrichen/grau konfigurieren
        self.tree.tag_configure("done", foreground="#555555")
        
        # Statuszeile
        self.status_var = tk.StringVar()
        self.status_var.set("Lade Materialien... Bitte warten.")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief="sunken", anchor="w", padding=(10, 2))
        status_bar.pack(side="bottom", fill="x")

    def _load_materials(self):
        try:
            self.materials = get_material_list(self.file_path, self.file_format)
            
            # Nach Häufigkeit absteigend sortieren
            sorted_materials = sorted(self.materials.items(), key=lambda item: item[1], reverse=True)
            
            for name, count in sorted_materials:
                formatted_qty = format_quantity(count)
                display_name = name.replace("minecraft:", "")
                
                # Checkbox wird durch [ ] simuliert
                self.tree.insert("", "end", values=("[ ]", display_name, count, formatted_qty))
                
            self.status_var.set(f"{len(self.materials)} verschiedene Blöcke gefunden.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Materialliste nicht laden:\n{e}", parent=self.window)
            self.status_var.set("Fehler beim Laden.")
            self.window.destroy()

    def _toggle_done(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = selected[0]
        values = self.tree.item(item, "values")
        
        if values[0] == "[ ]":
            new_values = ("[X]", values[1], values[2], values[3])
            self.tree.item(item, values=new_values, tags=("done",))
        else:
            new_values = ("[ ]", values[1], values[2], values[3])
            self.tree.item(item, values=new_values, tags=("",))
