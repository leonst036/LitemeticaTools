import tkinter as tk
from deps import ensure_dependencies

# Abhängigkeiten prüfen und laden, bevor GUI und Converter Module importiert werden,
# die litemapy/nbtlib benötigen
ensure_dependencies()

from gui import ConverterGUI
import sv_ttk

if __name__ == "__main__":
    root = tk.Tk()
    
    # Modernes Theme aktivieren
    sv_ttk.set_theme("dark")
    
    app = ConverterGUI(root)
    root.mainloop()
