import customtkinter as ctk
from database_manager import DatabaseManager

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
        
        self.title_label = ctk.CTkLabel(
            top_frame, text="Gestión de Flota de Vehículos", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        self.refresh_button = ctk.CTkButton(top_frame, text="Actualizar", command=self.load_vehicles)
        self.refresh_button.pack(side="right", padx=(0, 10))

        # --- Frame Desplazable para la Lista de Vehículos ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Listado de Vehículos")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_vehicles()

    def load_vehicles(self):
        """
        Carga los vehículos desde la base de datos y los muestra en el frame desplazable.
        """
        # Limpiar la lista actual antes de cargar nuevos datos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Consulta SQL para obtener todos los datos necesarios
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
            no_data_label = ctk.CTkLabel(self.scrollable_frame, text="No hay vehículos para mostrar.")
            no_data_label.pack(pady=20)
            return

        # Crear una "tarjeta" para cada vehículo
        for vehicle in vehicles:
            card = ctk.CTkFrame(self.scrollable_frame, border_width=2)
            card.pack(fill="x", padx=10, pady=5, expand=True)
            card.grid_columnconfigure(1, weight=1) # Permite que la columna del medio se expanda

            # --- Contenido de la tarjeta ---
            # Nombre del vehículo (Marca y Modelo)
            car_name = f"{vehicle['marca_nombre']} {vehicle['modelo_nombre']} ({vehicle['anio']})"
            name_label = ctk.CTkLabel(card, text=car_name, font=ctk.CTkFont(size=16, weight="bold"))
            name_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")
            
            # Detalles
            plate_label = ctk.CTkLabel(card, text=f"Placa: {vehicle['placa']}", font=ctk.CTkFont(size=12))
            plate_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
            
            km_label = ctk.CTkLabel(card, text=f"Kilometraje: {vehicle['kilometraje']:,} km", font=ctk.CTkFont(size=12))
            km_label.grid(row=2, column=0, padx=10, pady=(2,10), sticky="w")
            
            # Estado (con colores)
            status_colors = {
                'disponible': 'green',
                'alquilado': 'orange',
                'mantenimiento': 'red'
            }
            status_color = status_colors.get(vehicle['estado'], 'gray')
            
            status_label = ctk.CTkLabel(card, text=vehicle['estado'].upper(), font=ctk.CTkFont(size=14, weight="bold"), text_color=status_color)
            status_label.grid(row=1, column=1, rowspan=2, pady=5)
            
            # Precio
            price_label = ctk.CTkLabel(card, text=f"${vehicle['precio_diario']:.2f} / día", font=ctk.CTkFont(size=18, weight="bold"))
            price_label.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky="e")