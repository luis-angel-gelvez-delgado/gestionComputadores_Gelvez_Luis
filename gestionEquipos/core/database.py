import sqlite3

def init_db():
    conn = sqlite3.connect('campuslands.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campers (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            estado TEXT DEFAULT 'Activo'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS computadores (
            serial TEXT PRIMARY KEY,
            marca TEXT NOT NULL,
            estado_fisico TEXT DEFAULT 'Excelente',
            disponibilidad TEXT DEFAULT 'Disponible'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asignaciones (
            id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_camper INTEGER,
            serial_pc TEXT,
            cubiculo INTEGER NOT NULL,
            fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_fin TIMESTAMP,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_camper) REFERENCES campers(id),
            FOREIGN KEY (serial_pc) REFERENCES computadores(serial)
        )
    ''')

    conn.commit()
    conn.close()