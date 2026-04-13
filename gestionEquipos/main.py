import os
from core.database import init_db
from core.manager import CampusManager

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_tabla(headers, data):
    if not data:
        print("\n[ No hay registros para mostrar ]")
        return
    # Formato simple de columnas
    header_line = " | ".join(f"{h:<15}" for h in headers)
    print("\n" + header_line)
    print("-" * len(header_line))
    for row in data:
        print(" | ".join(f"{str(item):<15}" for item in row))

def menu_principal():
    init_db()
    manager = CampusManager()

    while True:
        print("\n" + "╔" + "═"*35 + "╗")
        print("║   SISTEMA DE GESTIÓN CAMPUSLANDS  ║")
        print("╚" + "═"*35 + "╝")
        print("1. [REGISTRO] Nuevo Camper o PC")
        print("2. [ASIGNAR] Vincular PC a Camper")
        print("3. [RETORNAR] Liberar Equipo")
        print("4. [ADMIN] Gestionar Estados (Bloqueos/Daños)")
        print("5. [REPORTES] Consultar Disponibilidad/Uso")
        print("6. SALIR")
        
        opc = input("\nSeleccione una categoría: ")

        try:
            if opc == "1":
                sub = input("¿Registrar (1)Camper o (2)PC?: ")
                if sub == "1":
                    id_c = int(input("ID: ")); nom = input("Nombre: ")
                    print(f"\n>> {manager.registrar_camper(id_c, nom)}")
                else:
                    ser = input("Serial: "); mar = input("Marca: ")
                    print(f"\n>> {manager.registrar_pc(ser, mar)}")

            elif opc == "2":
                print("\n--- PCs DISPONIBLES ---")
                mostrar_tabla(["SERIAL", "MARCA"], manager.obtener_pcs_disponibles())
                id_c = int(input("\nID del Camper: "))
                ser = input("Serial del PC: ")
                cub = int(input("Cubículo: "))
                print(f"\n>> {manager.asignar_equipo(id_c, ser, cub)}")

            elif opc == "3":
                ser = input("Serial del PC a liberar: ")
                print(f"\n>> {manager.liberar_equipo(ser)}")

            elif opc == "4":
                print("\n1. Bloquear/Desbloquear Camper\n2. Reportar PC Dañado")
                sub = input("Opción: ")
                if sub == "1":
                    id_c = int(input("ID Camper: "))
                    est = input("Nuevo estado (Activo/Bloqueado): ").capitalize()
                    print(f"\n>> {manager.gestionar_estado_camper(id_c, est)}")
                elif sub == "2":
                    ser = input("Serial del PC dañado: ")
                    print(f"\n>> {manager.reportar_daño_tecnico(ser)}")

            elif opc == "5":
                print("\n--- ASIGNACIONES ACTUALES ---")
                mostrar_tabla(["CAMPER", "SERIAL PC", "CUBÍCULO", "DESDE"], manager.obtener_asignaciones_activas())

            elif opc == "6":
                break
            
            input("\nPresione Enter para volver al menú...")
            limpiar_pantalla()

        except ValueError:
            print("\n[!] Error: Ingrese un dato numérico válido.")
        except Exception as e:
            print(f"\n[!] Error inesperado: {e}")

if __name__ == "__main__":
    menu_principal()