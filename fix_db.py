import sqlite3
import hashlib
from pathlib import Path

paths = [Path("duotech.db"), Path("data/duotech.db")]

for db_path in paths:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS unidades (
        codigo_unidad TEXT PRIMARY KEY,
        kilometraje INTEGER,
        horometro_bomba REAL,
        estado TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inspecciones_inmutables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_unidad TEXT,
        inspector_rut TEXT,
        inspector_nombre TEXT,
        kilometraje INTEGER,
        horometro_bomba REAL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hash_sha256 TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS solicitudes_atencion_urgente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_unidad TEXT,
        hallazgo TEXT,
        prioridad TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado TEXT
    )''')

    cursor.execute("INSERT OR REPLACE INTO unidades VALUES ('B-1', 45200, 312.5, 'EN_REVISION')")

    raw_payload = "B-1|12345678-9|45200|312.5"
    hash_val = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    cursor.execute("DELETE FROM inspecciones_inmutables")
    cursor.execute('''
    INSERT INTO inspecciones_inmutables (codigo_unidad, inspector_rut, inspector_nombre, kilometraje, horometro_bomba, hash_sha256)
    VALUES ('B-1', '12345678-9', 'Oficial de Guardia', 45200, 312.5, ?)
    ''', (hash_val,))

    cursor.execute("DELETE FROM solicitudes_atencion_urgente")
    cursor.execute('''
    INSERT INTO solicitudes_atencion_urgente (codigo_unidad, hallazgo, prioridad, estado)
    VALUES ('B-1', 'Fuga menor en valvula de descarga auxiliar', 'ALTA', 'PENDIENTE')
    ''')

    conn.commit()
    conn.close()

print("✅ Base de datos sincronizada correctamente en ambas rutas.")