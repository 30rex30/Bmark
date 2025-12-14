# main.py
# (Código idêntico ao anterior)
import customtkinter as ctk
import platform
from bmark_ui import BMarkApp


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("AVISO: Muitos tweaks de sistema (Regedit, Debloat) são exclusivos para Windows.")
    try:
        from datetime import datetime
    except ImportError:
        print("Erro: O módulo 'datetime' está faltando.")
        exit()

    app = BMarkApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()