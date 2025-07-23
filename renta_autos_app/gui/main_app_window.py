import customtkinter as ctk
from gui.frames.vehicle_management import VehicleManagementFrame # Importamos el futuro panel


class MainAppWindow(ctk.CTk):

    def __init__(self, app_instance):
        super().__init__()

        self.app = app_instance # Referencia a la clase principal
        self.user_info = self.app.current_user_info
        self.auth_manager = self.app.auth_manager
        
        # Agrega el protocolo para el cierre de la ventana
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title(f"Renta Autos Secure - Panel ({self.user_info.get('rol').capitalize()})")
        self.geometry("1100x720")

        # --- Configurar el layout de la ventana con grid ---
        # 1 columna para el menú lateral, 1 columna para el contenido principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame del Menú Lateral ---
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Espacio para empujar logout hacia abajo

        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="Renta Secure",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Botones de Navegación ---
        self.btn_vehicles = ctk.CTkButton(
            self.sidebar_frame,
            text="Gestionar Vehículos",
            command=self.show_vehicle_frame
        )
        self.btn_vehicles.grid(row=1, column=0, padx=20, pady=10)

        self.btn_clients = ctk.CTkButton(
            self.sidebar_frame,
            text="Gestionar Clientes",
            # command=self.show_client_frame # Se agregará después
        )
        self.btn_clients.grid(row=2, column=0, padx=20, pady=10)
        self.btn_clients.configure(state="disabled") # Deshabilitado por ahora

        self.btn_rentals = ctk.CTkButton(
            self.sidebar_frame,
            text="Gestionar Alquileres",
            # command=self.show_rental_frame # Se agregará después
        )
        self.btn_rentals.grid(row=3, column=0, padx=20, pady=10)
        self.btn_rentals.configure(state="disabled") # Deshabilitado por ahora

        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Cerrar Sesión",
            command=self.logout
        )
        self.logout_button.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="s")

        # --- Frame Principal (donde se mostrará el contenido) ---
        self.main_view_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_view_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # --- Instancias de los frames de contenido ---
        # Solo se crea una instancia de cada frame para no consumir memoria innecesariamente
        self.vehicle_frame = VehicleManagementFrame(self.main_view_frame, self.app.db_manager) # Pasamos el contenedor
        # self.client_frame = ... # Se agregarán después
        
        # Mostrar el frame inicial por defecto
        self.show_vehicle_frame()

    def on_closing(self):
        """Maneja el evento de cierre de la ventana principal."""
        self.logout() # Llama a la función de logout para cerrar la sesión de BD
    def show_vehicle_frame(self):
        """Muestra el frame de gestión de vehículos."""
        print("Mostrando panel de vehículos...")
        # Empaquetar el frame en el contenedor principal, asegurándose de que llene el espacio
        self.vehicle_frame.pack(fill="both", expand=True)

    def logout(self):
        """Cierra la sesión y la ventana."""
        token = self.user_info.get('token')
        if token:
            self.auth_manager.logout(token)
        self.destroy()