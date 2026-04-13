import sqlite3

class CampusManager:
    def __init__(self, db_name='campuslands.db'):
        self.db_name = db_name

    def _get_connection(self):
        """Asegura que cada conexión tenga las llaves foráneas activas."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def registrar_camper(self, id_camper, nombre):
        if not nombre.strip(): return "Error: El nombre no puede estar vacío."
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT INTO campers (id, nombre) VALUES (?, ?)", (id_camper, nombre))
            return f"Camper '{nombre}' registrado con éxito."
        except sqlite3.IntegrityError:
            return "Error: El ID del Camper ya existe."

    def registrar_pc(self, serial, marca):
        if not serial.strip(): return "Error: El serial es obligatorio."
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT INTO computadores (serial, marca) VALUES (?, ?)", (serial, marca))
            return f"PC {serial} registrado con éxito."
        except sqlite3.IntegrityError:
            return "Error: El serial ya está registrado."

    def asignar_equipo(self, id_camper, serial_pc, cubiculo):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Validar existencia y estado del Camper
                cursor.execute("SELECT estado FROM campers WHERE id = ?", (id_camper,))
                camper = cursor.fetchone()
                if not camper: return "Error: El Camper no existe."
                if camper[0] == 'Bloqueado': return "Error: El Camper está bloqueado."

                # Validar existencia y estado del PC
                cursor.execute("SELECT estado_fisico, disponibilidad FROM computadores WHERE serial = ?", (serial_pc,))
                pc = cursor.fetchone()
                if not pc: return "Error: El PC no existe."
                if pc[0] == 'Dañado': return "Error: El PC está dañado."
                if pc[1] == 'Ocupado': return "Error: El PC ya está asignado a alguien más."

                # Validar si el camper ya tiene un equipo activo
                cursor.execute("SELECT id_asignacion FROM asignaciones WHERE id_camper = ? AND activo = 1", (id_camper,))
                if cursor.fetchone(): return "Error: El Camper ya tiene un equipo asignado."

                # TRANSACCIÓN ATÓMICA: O se hacen ambas o ninguna
                cursor.execute("INSERT INTO asignaciones (id_camper, serial_pc, cubiculo) VALUES (?, ?, ?)", 
                               (id_camper, serial_pc, cubiculo))
                cursor.execute("UPDATE computadores SET disponibilidad = 'Ocupado' WHERE serial = ?", (serial_pc,))
                
                return "Asignación procesada correctamente."
        except Exception as e:
            return f"Error crítico en la transacción: {e}"

    def liberar_equipo(self, serial_pc):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT activo FROM asignaciones WHERE serial_pc = ? AND activo = 1", (serial_pc,))
                if not cursor.fetchone(): return "Error: Este PC no tiene asignaciones activas."

                cursor.execute("UPDATE asignaciones SET activo = 0, fecha_fin = CURRENT_TIMESTAMP WHERE serial_pc = ? AND activo = 1", (serial_pc,))
                cursor.execute("UPDATE computadores SET disponibilidad = 'Disponible' WHERE serial = ?", (serial_pc,))
                return f"Equipo {serial_pc} liberado con éxito."
        except Exception as e:
            return f"Error al liberar: {e}"
        
        import sqlite3

class CampusManager:
    def __init__(self, db_name='campuslands.db'):
        self.db_name = db_name

    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # --- NUEVOS MÉTODOS DE CONSULTA (READ-ONLY) ---

    def obtener_pcs_disponibles(self):
        query = """SELECT serial, marca FROM computadores 
                   WHERE disponibilidad = 'Disponible' AND estado_fisico = 'Excelente'"""
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def obtener_asignaciones_activas(self):
        query = """
            SELECT c.nombre, a.serial_pc, a.cubiculo, a.fecha_inicio
            FROM asignaciones a
            JOIN campers c ON a.id_camper = c.id
            WHERE a.activo = 1
        """
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    # --- GESTIÓN DE ESTADOS (ADMIN ACTIONS) ---

    def gestionar_estado_camper(self, id_camper, nuevo_estado):
        """nuevo_estado debe ser 'Activo' o 'Bloqueado'"""
        try:
            with self._get_connection() as conn:
                res = conn.execute("UPDATE campers SET estado = ? WHERE id = ?", (nuevo_estado, id_camper))
                if res.rowcount == 0: return "Error: ID de Camper no encontrado."
                return f"Estado del camper actualizado a: {nuevo_estado}"
        except Exception as e:
            return f"Error: {e}"

    def reportar_daño_tecnico(self, serial_pc):
        """Cambia a dañado y libera al camper automáticamente si estaba en uso."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # 1. Verificar si el PC existe
                cursor.execute("SELECT serial FROM computadores WHERE serial = ?", (serial_pc,))
                if not cursor.fetchone(): return "Error: El serial del PC no existe."

                # 2. Si estaba asignado, cerrar la asignación
                cursor.execute("""UPDATE asignaciones SET activo = 0, fecha_fin = CURRENT_TIMESTAMP 
                                  WHERE serial_pc = ? AND activo = 1""", (serial_pc,))
                
                # 3. Marcar PC como Dañado y Bloqueado
                cursor.execute("""UPDATE computadores 
                                  SET estado_fisico = 'Dañado', disponibilidad = 'Bloqueado' 
                                  WHERE serial = ?""", (serial_pc,))
                
                return f"PC {serial_pc} marcado como DAÑADO. Se han liberado asignaciones previas."
        except Exception as e:
            return f"Error al procesar daño: {e}"

    # (Mantener los métodos anteriores de registrar_camper, registrar_pc, asignar_equipo y liberar_equipo)