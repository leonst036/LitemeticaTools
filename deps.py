import subprocess
import sys

def ensure_dependencies():
    try:
        import nbtlib
        import litemapy
        import sv_ttk
        import packaging
    except ImportError:
        # Versuch, Bibliotheken automatisch zu installieren, falls nicht vorhanden
        subprocess.check_call([sys.executable, "-m", "pip", "install", "litemapy", "nbtlib", "sv-ttk", "packaging"])
