import customtkinter as ctk
from database_manager import DatabaseManager
from auth_manager import AuthManager
from gui.login_window import LoginWindow
from gui.main_app_window import MainAppWindow

# --- Configuración de la apariencia ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self):
        # 1. Inicializar los gestores
        self.db_manager = DatabaseManager()
        if not self.db_manager.pool:
            print("Error fatal: No se pudo conectar a la base de datos.")
            return

        self.auth_manager = AuthManager(self.db_manager)
        self.current_user_info = None # Guardará la info del usuario logueado

        # 2. Iniciar el ciclo de la aplicación
        self.run()

    def run(self):
        # 3. Mostrar la ventana de login y esperar a que se cierre
        login_win = LoginWindow(self) # Le pasamos la instancia de App
        login_win.mainloop()

        # 4. Una vez cerrada la ventana de login, comprobar si el login fue exitoso
        if self.current_user_info:
            # 5. Si fue exitoso, mostrar la ventana principal
            main_app = MainAppWindow(self)
            main_app.mainloop()

if __name__ == "__main__":
    app = App()
    print("\nLa aplicación ha finalizado.")