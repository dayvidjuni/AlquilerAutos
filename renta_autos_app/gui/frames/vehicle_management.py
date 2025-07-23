import customtkinter as ctk
from database_manager import DatabaseManager
from gui.add_vehicle_window import AddVehicleWindow

class VehicleManagementFrame(ctk.CTkFrame):
    """
    Frame para mostrar y gestionar los vehículos de la flota.
    """
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master, fg_color="transparent")
        self.db_manager = db_manager

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Frame Superior (Título y Botones) ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1) # El título empuja a los botones
        
        self.title_label = ctk.CTkLabel(
            top_frame, text="Gestión de Flota de Vehículos", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.add_button = ctk.CTkButton(top_frame, text="Añadir Vehículo", command=self.open_add_vehicle_window)
        self.add_button.grid(row=0, column=1, padx=(10, 5))

        self.refresh_button = ctk.CTkButton(top_frame, text="Actualizar", command=self.load_vehicles, width=100)
        self.refresh_button.grid(row=0, column=2, padx=(0, 5))

        # --- Frame Desplazable para la Lista de Vehículos ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Listado de Vehículos")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_vehicles()

    def open_add_vehicle_window(self):
        """Abre la ventana para añadir un nuevo vehículo."""
        # Si ya hay una ventana abierta, no abrir otra
        if hasattr(self, 'add_window') and self.add_window.winfo_exists():
            self.add_window.focus()
            return
            
        self.add_window = AddVehicleWindow(
            master=self.winfo_toplevel(), 
            db_manager=self.db_manager,
            on_close_callback=self.load_vehicles # Pasamos la función de refresco
        )

    def load_vehicles(self):
        """
        Carga los vehículos desde la base de datos y los muestra en el frame desplazable.
        """
        # Limpiar la lista actual antes de cargar nuevos datos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = """
            SELECT 
                v.placa, v.anio, v.color, v.kilometraje, v.precio_diario, v.estado,
                m.nombre AS modelo_nombre,
                b.nombre AS marca_nombre
            FROM vehiculos v
            JOIN modelos m ON v.id_modelo = m.id_modelo
            JOIN marcas b ON m.id_marca = b.id_marca
            ORDER BY b.nombre, m.nombre;
        """
        vehicles = self.db_manager.execute_query(query)

        if not vehicles:
            ctk.CTkLabel(self.scrollable_frame, text="No hay vehículos para mostrar.").pack(pady=20)
            return

        for vehicle in vehicles:
            card = ctk.CTkFrame(self.scrollable_frame, border_width=2)
            card.pack(fill="x", padx=10, pady=5, expand=True)
            card.grid_columnconfigure(1, weight=1)

            car_name = f"{vehicle['marca_nombre']} {vehicle['modelo_nombre']} ({vehicle['anio']})"
            ctk.CTkLabel(card, text=car_name, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")
            
            ctk.CTkLabel(card, text=f"Placa: {vehicle['placa']}", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(card, text=f"Kilometraje: {vehicle['kilometraje']:,} km", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=10, pady=(2,10), sticky="w")
            
            status_colors = {'disponible': 'green', 'alquilado': 'orange', 'mantenimiento': 'red'}
            status_color = status_colors.get(vehicle['estado'], 'gray')
            ctk.CTkLabel(card, text=vehicle['estado'].upper(), font=ctk.CTkFont(size=14, weight="bold"), text_color=status_color).grid(row=1, column=1, rowspan=2, pady=5)
            
            ctk.CTkLabel(card, text=f"${vehicle['precio_diario']:.2f} / día", font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky="e")