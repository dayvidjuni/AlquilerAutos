import customtkinter as ctk

class LoginWindow(ctk.CTk):
    """
    Ventana de inicio de sesión. No abre la siguiente ventana,
    solo informa a la clase principal (App) si el login fue exitoso.
    """
    def __init__(self, app_instance):
        super().__init__()

        self.app = app_instance # Referencia a la instancia de la clase App
        self.auth_manager = self.app.auth_manager

        # --- Configuración de la ventana ---
        self.title("Renta Autos Secure - Inicio de Sesión")
        self.geometry("400x480")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Centrar
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # --- Widgets ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="Bienvenido", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Inicia sesión para continuar", font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.username_entry = ctk.CTkEntry(self.main_frame, width=250, height=40, placeholder_text="Nombre de usuario")
        self.username_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(self.main_frame, width=250, height=40, placeholder_text="Contraseña", show="*")
        self.password_entry.pack(pady=12, padx=10)
        self.password_entry.bind("<Return>", self.login_event)

        self.login_button = ctk.CTkButton(self.main_frame, text="Ingresar", width=250, height=40, command=self.login_event)
        self.login_button.pack(pady=30, padx=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=12), text_color="red")
        self.status_label.pack(pady=(0, 10))

    def login_event(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Por favor, ingresa usuario y contraseña.")
            return

        self.login_button.configure(state="disabled", text="Ingresando...")
        self.update_idletasks()

        login_result = self.auth_manager.login(username, password)

        if login_result['success']:
            # Guardamos la info del usuario en la instancia principal de la App
            self.app.current_user_info = login_result
            # Y cerramos la ventana
            self.destroy()
        else:
            self.status_label.configure(text=login_result['message'])
            self.login_button.configure(state="normal", text="Ingresar")

    def on_closing(self):
        # Asegura que si se cierra la ventana, la app termine
        self.destroy()