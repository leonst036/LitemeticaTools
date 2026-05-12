import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from material_list import get_material_list, format_quantity

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class MaterialListWindow:
    def __init__(self, parent, file_path, file_format):
        self.window = tk.Toplevel(parent)
        self.window.title("Materialliste")
        self.window.geometry("850x650")
        # Fenster zentrieren oder über dem Hauptfenster platzieren
        self.window.transient(parent)
        
        self.file_path = file_path
        self.file_format = file_format
        self.materials = {}
        self.sort_reverse = {col: False for col in ("done", "material", "total", "shulkers")}
        
        # Filter Variablen
        self.filter_liquids = tk.BooleanVar(value=False)
        self.filter_helpers = tk.BooleanVar(value=False)
        
        self._create_widgets()
        
        # Materialien laden, am besten per after, damit GUI sich aufbaut
        self.window.after(100, self._load_materials)

    def _create_widgets(self):
        # Haupt-Container für besseres Padding
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Actions Frame (Top)
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", pady=(0, 15))

        # Filter-Bereich
        filter_frame = ttk.LabelFrame(actions_frame, text="Filter", padding=10)
        filter_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Checkbutton(filter_frame, text="Flüssigkeiten (Wasser/Lava) ignorieren", 
                        variable=self.filter_liquids, command=self._load_materials).pack(side="left", padx=5)
        ttk.Checkbutton(filter_frame, text="Hilfsblöcke (Dirt/Scaffolding) ignorieren", 
                        variable=self.filter_helpers, command=self._load_materials).pack(side="left", padx=5)

        # Export-Bereich
        export_frame = ttk.LabelFrame(actions_frame, text="Export", padding=10)
        export_frame.pack(side="right", fill="y")

        export_btn = ttk.Menubutton(export_frame, text="Exportieren...", style="Accent.TButton")
        export_btn.pack(padx=5, pady=2, fill="both", expand=True)
        
        export_menu = tk.Menu(export_btn, tearoff=0)
        export_menu.add_command(label="Als CSV (.csv)", command=self._export_csv)
        export_menu.add_command(label="Als Markdown (.md)", command=self._export_markdown)
        export_menu.add_command(label="Als PDF (.pdf)", command=self._export_pdf)
        export_btn["menu"] = export_menu

        # Info Label
        info_label = ttk.Label(main_frame, text="Doppelklick auf einen Eintrag, um ihn abzuhaken. Klick auf Spalten zum Sortieren.", font=("", 10, "italic"))
        info_label.pack(pady=(0, 10))

        # Frame für Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Spalten: Done, Material, Total, Shulkers
        columns = ("done", "material", "total", "shulkers")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("done", text="Status", command=lambda: self._sort_column("done"))
        self.tree.heading("material", text="Material (Block-ID)", command=lambda: self._sort_column("material"))
        self.tree.heading("total", text="Gesamtmenge", command=lambda: self._sort_column("total"))
        self.tree.heading("shulkers", text="Kisten / Stacks", command=lambda: self._sort_column("shulkers"))
        
        self.tree.column("done", width=70, anchor="center")
        self.tree.column("material", width=300, anchor="w")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("shulkers", width=250, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Doppelklick Event binden
        self.tree.bind("<Double-1>", self._toggle_done)
        
        # Tag für durchgestrichen/grau konfigurieren
        self.tree.tag_configure("done", foreground="#888888")
        
        # Statuszeile
        self.status_var = tk.StringVar()
        self.status_var.set("Lade Materialien... Bitte warten.")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief="sunken", anchor="w", padding=(10, 2))
        status_bar.pack(side="bottom", fill="x")

    def _load_materials(self):
        try:
            # Treeview leeren
            for item in self.tree.get_children():
                self.tree.delete(item)

            filters = {
                "ignore_liquids": self.filter_liquids.get(),
                "ignore_helpers": self.filter_helpers.get()
            }
            
            self.materials = get_material_list(self.file_path, self.file_format, filters)
            
            # Standardmäßig nach Häufigkeit absteigend sortieren
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

    def _sort_column(self, col):
        """Sortiert den Treeview nach einer Spalte."""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # Versuche numerische Sortierung für 'total'
        if col == "total":
            try:
                l.sort(key=lambda t: int(t[0]), reverse=self.sort_reverse[col])
            except (ValueError, TypeError):
                l.sort(reverse=self.sort_reverse[col])
        else:
            l.sort(reverse=self.sort_reverse[col])

        for index, (val, k) in enumerate(l):
            self.tree.move(k, "", index)

        # Richtung für das nächste Mal umkehren
        self.sort_reverse[col] = not self.sort_reverse[col]

    def _get_tree_data(self):
        """Extrahiert alle Daten aus dem Treeview."""
        data = []
        for item in self.tree.get_children():
            data.append(self.tree.item(item, "values"))
        return data

    def _export_csv(self):
        data = self._get_tree_data()
        if not data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv")],
            initialfile="Materialliste.csv"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Status", "Material", "Anzahl", "Kisten/Stacks"])
                writer.writerows(data)
            messagebox.showinfo("Export erfolgreich", f"Materialliste als CSV gespeichert unter:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Fehler", f"Fehler beim Speichern der CSV:\n{e}")

    def _export_markdown(self):
        data = self._get_tree_data()
        if not data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Dateien", "*.md")],
            initialfile="Materialliste.md"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Materialliste\n\n")
                f.write(f"Datei: `{os.path.basename(self.file_path)}`\n\n")
                f.write("| Status | Material | Anzahl | Kisten / Stacks |\n")
                f.write("| :---: | :--- | ---: | :--- |\n")
                for row in data:
                    f.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
            messagebox.showinfo("Export erfolgreich", f"Materialliste als Markdown gespeichert unter:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Fehler", f"Fehler beim Speichern der Markdown Datei:\n{e}")

    def _export_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Fehler", "ReportLab ist nicht installiert. PDF-Export nicht möglich.")
            return

        data = self._get_tree_data()
        if not data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dateien", "*.pdf")],
            initialfile="Materialliste.pdf"
        )
        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Titel
            elements.append(Paragraph(f"Materialliste: {os.path.basename(self.file_path)}", styles['Title']))
            elements.append(Spacer(1, 20))

            # Tabelle
            table_data = [["Status", "Material", "Anzahl", "Kisten / Stacks"]]
            for row in data:
                table_data.append(list(row))

            t = Table(table_data, colWidths=[50, 200, 80, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            
            doc.build(elements)
            messagebox.showinfo("Export erfolgreich", f"Materialliste als PDF gespeichert unter:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Fehler", f"Fehler beim Speichern der PDF:\n{e}")

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
