import customtkinter as ctk
# Importamos los paneles que usaremos
from gui.frames.vehicle_management import VehicleManagementFrame
from gui.frames.user_management import UserManagementFrame

class MainAppWindow(ctk.CTk):
    """
    Ventana principal de la aplicación con navegación lateral.
    Gestiona qué panel se muestra en el área de contenido.
    """
    def __init__(self, app_instance):
        super().__init__()

        self.app = app_instance
        self.user_info = self.app.current_user_info
        self.auth_manager = self.app.auth_manager
        
        self.title(f"Renta Autos Secure - Panel ({self.user_info.get('rol').capitalize()})")
        self.geometry("1100x720")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Configurar el layout principal ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame del Menú Lateral ---
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Renta Secure", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Botones de Navegación ---
        self.btn_vehicles = ctk.CTkButton(
            self.sidebar_frame, text="Gestionar Vehículos", command=self.show_vehicle_frame
        )
        self.btn_vehicles.grid(row=1, column=0, padx=20, pady=10)

        self.btn_users = ctk.CTkButton(
            self.sidebar_frame, text="Gestionar Usuarios", command=self.show_user_frame
        )
        self.btn_users.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_rentals = ctk.CTkButton(self.sidebar_frame, text="Gestionar Alquileres")
        self.btn_rentals.grid(row=3, column=0, padx=20, pady=10)
        self.btn_rentals.configure(state="disabled")

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Cerrar Sesión", command=self.logout)
        self.logout_button.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="s")

        # --- Frame Principal (donde se mostrará el contenido) ---
        self.main_view_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_view_frame.grid_rowconfigure(0, weight=1)
        self.main_view_frame.grid_columnconfigure(0, weight=1)

        # --- Instancias de los frames de contenido ---
        # Se crea una única instancia de cada panel.
        self.vehicle_frame = VehicleManagementFrame(self.main_view_frame, self.app.db_manager)
        self.user_frame = UserManagementFrame(self.main_view_frame, self.app.db_manager, self.app.auth_manager)
        # Aquí irían los otros frames...

        # Mostrar el frame inicial por defecto
        self.show_vehicle_frame()

    # --- Funciones de Navegación ---
    def show_vehicle_frame(self):
        """Muestra el panel de vehículos y oculta los demás."""
        self.user_frame.grid_forget() # Oculta el panel de usuarios
        # Aquí ocultaríamos otros frames si los hubiera

        # Muestra el panel de vehículos, asegurando que ocupe todo el espacio
        self.vehicle_frame.grid(row=0, column=0, sticky="nsew")

    def show_user_frame(self):
        """Muestra el panel de usuarios y oculta los demás."""
        self.vehicle_frame.grid_forget() # Oculta el panel de vehículos
        # Aquí ocultaríamos otros frames si los hubiera

        # Muestra el panel de usuarios, asegurando que ocupe todo el espacio
        self.user_frame.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        token = self.user_info.get('token')
        if token:
            self.auth_manager.logout(token)
        self.destroy()

    def on_closing(self):
        self.logout()