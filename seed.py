import sqlite3
import hashlib
from pathlib import Path

db_path = Path("duotech.db")
if not db_path.exists():
    db_path = Path("data/duotech.db")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 1. Crear tablas si no existen
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

# 2. Insertar Unidad de prueba
cursor.execute("INSERT OR REPLACE INTO unidades VALUES ('B-1', 45200, 312.5, 'EN_REVISION')")

# 3. Insertar Inspección con Hash SHA-256 inmutable
raw_payload = "B-1|12345678-9|45200|312.5"
hash_val = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

cursor.execute('''
INSERT INTO inspecciones_inmutables (codigo_unidad, inspector_rut, inspector_nombre, kilometraje, horometro_bomba, hash_sha256)
VALUES ('B-1', '12345678-9', 'Oficial de Guardia', 45200, 312.5, ?)
''', (hash_val,))

# 4. Insertar OT urgente pendiente
cursor.execute('''
INSERT INTO solicitudes_atencion_urgente (codigo_unidad, hallazgo, prioridad, estado)
VALUES ('B-1', 'Fuga menor en válvula de descarga auxiliar', 'ALTA', 'PENDIENTE')
''')

conn.commit()
conn.close()
print("✅ Base de datos poblada con éxito.")