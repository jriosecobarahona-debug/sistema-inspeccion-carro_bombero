import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "storage" / "duotech_telemetria.db"

def get_connection():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Registro de Unidades de Bomberos y Timers de Mantención Periódica
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_unidad TEXT UNIQUE NOT NULL, -- Ej: B-1, R-1
        modelo TEXT NOT NULL,
        kilometraje_actual REAL DEFAULT 0,
        horometro_bomba_actual REAL DEFAULT 0,
        intervalo_km_mantencion REAL DEFAULT 5000,
        intervalo_hrs_mantencion REAL DEFAULT 250,
        ultimo_km_mantencion REAL DEFAULT 0,
        ultimo_hrs_mantencion REAL DEFAULT 0,
        estado_operativo TEXT DEFAULT 'DISPONIBLE' CHECK (estado_operativo IN ('DISPONIBLE', 'CON_OBSERVACIONES', 'FUERA_DE_SERVICIO'))
    );
    """)

    # 2. Encabezado Inmutable de Inspección (Con Fotos 360° y Firma)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspecciones_inmutables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_unidad TEXT NOT NULL,
        modelo TEXT,
        kilometraje REAL NOT NULL,
        horometro_bomba REAL NOT NULL,
        inspector_nombre TEXT NOT NULL,
        inspector_rut TEXT NOT NULL,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        foto_frontal TEXT NOT NULL,
        foto_trasera TEXT NOT NULL,
        foto_lat_izq TEXT NOT NULL,
        foto_lat_der TEXT NOT NULL,
        firma_digital TEXT NOT NULL,
        estado_final TEXT NOT NULL CHECK (estado_final IN ('APROBADO', 'CON_OBSERVACIONES', 'FUERA_DE_SERVICIO')),
        FOREIGN KEY (codigo_unidad) REFERENCES unidades (codigo_unidad)
    );
    """)

    # 3. Control Neumáticos (6 Posiciones PSI/Profundidad + Foto de Desviación si NOK)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS control_neumaticos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspeccion_id INTEGER NOT NULL,
        posicion TEXT NOT NULL, -- Ej: Delantero Izquierdo, Trasero Ext. Izq, etc.
        presion_psi REAL NOT NULL,
        profundidad_mm REAL NOT NULL,
        estado TEXT CHECK (estado IN ('OK', 'NOK')),
        foto_desviacion TEXT, -- OBLIGATORIA si estado es NOK
        FOREIGN KEY (inspeccion_id) REFERENCES inspecciones_inmutables (id)
    );
    """)

    # 4. Checklist Operacional (30 Ítems + Foto de Desviación si NOK)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspeccion_id INTEGER NOT NULL,
        item_numero INTEGER NOT NULL,
        subsistema TEXT NOT NULL, -- Motor, Eléctrico, Chasis, Bomba, Material
        item_descripcion TEXT NOT NULL,
        estado TEXT CHECK (estado IN ('OK', 'NOK')),
        observacion TEXT,
        foto_desviacion TEXT, -- OBLIGATORIA si estado es NOK
        FOREIGN KEY (inspeccion_id) REFERENCES inspecciones_inmutables (id)
    );
    """)

    # 5. Solicitudes de Atención Urgente (OT Automática por Desviación)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes_atencion_urgente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_unidad TEXT NOT NULL,
        inspeccion_id INTEGER NOT NULL,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        origen_falla TEXT NOT NULL, -- Neumático o Ítem del Checklist
        descripcion_falla TEXT NOT NULL,
        foto_evidencia_falla TEXT NOT NULL,
        estado_ot TEXT DEFAULT 'PENDIENTE' CHECK (estado_ot IN ('PENDIENTE', 'EN_PROCESO', 'RESUELTO')),
        FOREIGN KEY (inspeccion_id) REFERENCES inspecciones_inmutables (id)
    );
    """)

    # 6. Documentos de Cierre de Desviación (Acta de Reparación - No modifica el reporte original)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documentos_cierre_desviacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        solicitud_ot_id INTEGER NOT NULL,
        codigo_unidad TEXT NOT NULL,
        fecha_cierre DATETIME DEFAULT CURRENT_TIMESTAMP,
        tecnico_responsable TEXT NOT NULL,
        trabajo_realizado TEXT NOT NULL,
        foto_evidencia_reparacion TEXT NOT NULL, -- OBLIGATORIA
        firma_tecnico TEXT NOT NULL,
        FOREIGN KEY (solicitud_ot_id) REFERENCES solicitudes_atencion_urgente (id)
    );
    """)

    # Carga de unidad de prueba (Carro B-1)
    cursor.execute("""
    INSERT OR IGNORE INTO unidades (codigo_unidad, modelo, kilometraje_actual, horometro_bomba_actual, ultimo_km_mantencion, ultimo_hrs_mantencion)
    VALUES ('B-1', 'Spartan Metro Star / Crimson', 45210.0, 1280.0, 45000.0, 1200.0);
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
