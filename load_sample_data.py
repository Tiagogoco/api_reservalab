from sistema_buap_api.models import Lab, Equipment

# Crear laboratorios
labs_data = [
    {"name": "Laboratorio de Cómputo 1", "building": "Edificio A", "floor": "1", "capacity": 30, "type": "COMPUTO", "status": "ACTIVE"},
    {"name": "Laboratorio de Electrónica", "building": "Edificio B", "floor": "2", "capacity": 25, "type": "ELECTRONICA", "status": "ACTIVE"},
    {"name": "Laboratorio de Cómputo 2", "building": "Edificio C", "floor": "1", "capacity": 35, "type": "COMPUTO", "status": "ACTIVE"},
    {"name": "Laboratorio de Redes", "building": "Edificio A", "floor": "3", "capacity": 20, "type": "REDES", "status": "ACTIVE"},
    {"name": "Laboratorio de Biología", "building": "Edificio B", "floor": "1", "capacity": 28, "type": "BIOLOGIA", "status": "MAINTENANCE"},
]

print("Creando laboratorios...")
labs = []
for data in labs_data:
    lab = Lab.objects.create(**data)
    labs.append(lab)
    print(f"✓ {lab.name}")

# Crear equipos
equipment_data = [
    {"name": "Computadora Dell OptiPlex", "description": "Computadora de escritorio Dell OptiPlex 7090", "inventory_number": "COMP-001", "total_quantity": 30, "available_quantity": 30, "status": "AVAILABLE", "lab": labs[0]},
    {"name": "Osciloscopio Digital", "description": "Osciloscopio digital Tektronix TBS2000", "inventory_number": "OSC-001", "total_quantity": 10, "available_quantity": 8, "status": "AVAILABLE", "lab": labs[1]},
    {"name": "Multímetro Digital", "description": "Multímetro digital Fluke 117", "inventory_number": "MULT-001", "total_quantity": 15, "available_quantity": 12, "status": "AVAILABLE", "lab": labs[1]},
    {"name": "Switch Cisco Catalyst", "description": "Switch de red Cisco Catalyst 2960", "inventory_number": "SW-001", "total_quantity": 8, "available_quantity": 8, "status": "AVAILABLE", "lab": labs[3]},
    {"name": "Proyector Epson", "description": "Proyector multimedia Epson PowerLite", "inventory_number": "PROY-001", "total_quantity": 5, "available_quantity": 3, "status": "AVAILABLE", "lab": labs[0]},
    {"name": "Arduino Uno R3", "description": "Placa de desarrollo Arduino Uno R3", "inventory_number": "ARD-001", "total_quantity": 20, "available_quantity": 15, "status": "AVAILABLE", "lab": labs[1]},
    {"name": "Raspberry Pi 4", "description": "Computadora de placa única Raspberry Pi 4 Model B", "inventory_number": "RPI-001", "total_quantity": 12, "available_quantity": 10, "status": "AVAILABLE", "lab": labs[3]},
    {"name": "Cable HDMI", "description": "Cable HDMI 2.0 de 2 metros", "inventory_number": "HDMI-001", "total_quantity": 25, "available_quantity": 20, "status": "AVAILABLE", "lab": None},
    {"name": "Fuente de Poder Variable", "description": "Fuente de poder DC variable 0-30V 0-5A", "inventory_number": "FP-001", "total_quantity": 8, "available_quantity": 6, "status": "AVAILABLE", "lab": labs[1]},
    {"name": "Kit de Herramientas", "description": "Kit de herramientas para electrónica", "inventory_number": "KIT-001", "total_quantity": 10, "available_quantity": 8, "status": "AVAILABLE", "lab": labs[1]},
]

print("\nCreando equipos...")
for data in equipment_data:
    equipment = Equipment.objects.create(**data)
    print(f"✓ {equipment.name}")

print(f"\n✅ Datos cargados exitosamente!")
print(f"   - {len(labs)} laboratorios")
print(f"   - {len(equipment_data)} equipos")
