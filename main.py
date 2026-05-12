import tkinter as tk
from deps import ensure_dependencies

# Abhängigkeiten prüfen und laden, bevor GUI und Converter Module importiert werden,
# die litemapy/nbtlib benötigen
ensure_dependencies()

from gui import ConverterGUI
import sv_ttk
import threading
from updater import check_for_updates

if __name__ == "__main__":
    root = tk.Tk()
    
    # Modernes Theme aktivieren
    sv_ttk.set_theme("dark")
    
    # Update-Check im Hintergrund starten
    threading.Thread(target=check_for_updates, args=(root,), daemon=True).start()
    
    app = ConverterGUI(root)
    root.mainloop()
