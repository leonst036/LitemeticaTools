import urllib.request
import json
import os
import sys
from tkinter import messagebox
from packaging import version

CURRENT_VERSION = "1.1"
REPO_API_URL = "https://api.github.com/repos/leonst036/LitemeticaTools/releases/latest"

def check_for_updates(root):
    """
    Checks GitHub for the latest release and prompts the user to update if a newer version is available.
    """
    try:
        # User-Agent header is required by GitHub API
        req = urllib.request.Request(REPO_API_URL, headers={'User-Agent': 'LitemeticaTools-Updater'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            latest_tag = data['tag_name']
            # Remove 'v' prefix if present
            latest_version_str = latest_tag.replace('v', '')
            
            if version.parse(latest_version_str) > version.parse(CURRENT_VERSION):
                # Use root.after to show the messagebox in the main thread
                root.after(0, lambda: _prompt_update(root, data))
    except Exception as e:
        print(f"Update-Check fehlgeschlagen: {e}")

def _prompt_update(root, data):
    latest_tag = data['tag_name']
    if messagebox.askyesno("Update verfügbar", 
                           f"Eine neue Version ({latest_tag}) ist verfügbar. "
                           f"Aktuelle Version: {CURRENT_VERSION}\n\n"
                           "Möchtest du das Update (.exe) jetzt herunterladen?"):
        import threading
        threading.Thread(target=_download_update, args=(data['assets'],), daemon=True).start()

def _download_update(assets):
    """
    Searches for an .exe file in the release assets and downloads it.
    """
    exe_asset = None
    for asset in assets:
        if asset['name'].lower().endswith('.exe'):
            exe_asset = asset
            break
    
    if exe_asset:
        download_url = exe_asset['browser_download_url']
        file_name = exe_asset['name']
        
        try:
            # Note: Since this is now in a thread, we should use messagebox carefully or not at all 
            # for "starting download", but for a simple app it's often okay to show it before starting.
            # We already prompted the user.
            
            urllib.request.urlretrieve(download_url, file_name)
            
            messagebox.showinfo("Download abgeschlossen", 
                                f"Das Update wurde erfolgreich als '{file_name}' im aktuellen Ordner gespeichert.\n"
                                "Bitte starte die neue Version manuell.")
            # We can't use sys.exit() easily from a daemon thread to close the main window, 
            # but we can try to force it or just let the user close it.
            os._exit(0) 
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Download des Updates: {e}")
    else:
        messagebox.showwarning("Kein Executable gefunden", 
                               "In der neuesten Release wurde keine .exe Datei gefunden. "
                               "Bitte schaue manuell auf GitHub nach.")
