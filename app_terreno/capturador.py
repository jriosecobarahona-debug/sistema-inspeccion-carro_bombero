import os
import sys
from pathlib import Path

# Agregar directorio raíz al path para importar shared
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from shared.db_connector import get_connection

# Plantilla de los 30 Ítems del Checklist Operacional de Bomberos
ITEMS_CHECKLIST_BASE = [
    # Subsistema 1: Motor y Transmisión
    (1, "Motor", "Nivel de aceite de motor"),
    (2, "Motor", "Nivel de refrigerante / anticongelante"),
    (3, "Motor", "Correas de accesorios y tensión"),
    (4, "Motor", "Filtro y purga de agua en combustible"),
    (5, "Motor", "Estado y fugas en sistema de escape"),
    (6, "Motor", "Fugas visibles de aceite o fluidos hidráulicos"),
    
    # Subsistema 2: Sistema Eléctrico y Iluminación
    (7, "Eléctrico", "Estado y carga de baterías"),
    (8, "Eléctrico", "Luces de emergencia y destelladores (Balizas)"),
    (9, "Eléctrico", "Sirena y claxon de aire (Air Horn)"),
    (10, "Eléctrico", "Luces de navegación (Altas, Bajas, Viraje, Cero)"),
    (11, "Eléctrico", "Focos de escena y torres de iluminación"),
    (12, "Eléctrico", "Sistema de perifoneo / Radio Comunicaciones VHF"),

    # Subsistema 3: Chasis, Frenos y Suspensión
    (13, "Chasis", "Presión y estado de frenos de aire (Compresor/Purga)"),
    (14, "Chasis", "Freno de estacionamiento (Maxi-Brake)"),
    (15, "Chasis", "Suspensión delantera y trasera (Ballestas/Pulmones)"),
    (16, "Chasis", "Dirección y terminales de acople"),
    (17, "Chasis", "Espejos retrovisores y cámaras de retroceso"),
    (18, "Chasis", "Estructura de carrocería y cortinas de compartimento"),

    # Subsistema 4: Bomba de Agua y Sistema Contra Incendio
    (19, "Bomba", "Nivel de aceite en caja de transferencia de bomba"),
    (20, "Bomba", "Emptador de cebado y empaque de prensaestopa"),
    (21, "Bomba", "Válvulas de admisión / succión (Apertura y Cierre)"),
    (22, "Bomba", "Válvulas de descarga e impulsión"),
    (23, "Bomba", "Manómetros y vacuómetro de panel de bomba"),
    (24, "Bomba", "Estanque de agua / espuma (Niveles y fugas)"),

    # Subsistema 5: Material Mayor y Equipamiento Vehicular
    (25, "Material", "Estado de escalas y soportes de sujeción"),
    (26, "Material", "Polipasto / Winche y cable de acero"),
    (27, "Material", "Generador eléctrico auxiliar del carro"),
    (28, "Material", "Trabas de seguridad de gavetas y cajoneras"),
    (29, "Material", "Cintas de amarre y calzos de rueda"),
    (30, "Material", "Extintores portátiles de la unidad (Carga y vencimiento)")
]

POSICIONES_NEUMATICOS = [
    "Delantero Izquierdo",
    "Delantero Derecho",
    "Trasero Exterior Izquierdo",
    "Trasero Interior Izquierdo",
    "Trasero Interior Derecho",
    "Trasero Exterior Derecho"
]

def registrar_inspeccion_terreno(
    codigo_unidad: str,
    kilometraje: float,
    horometro_bomba: float,
    inspector_nombre: str,
    inspector_rut: str,
    fotos_perimetrales: dict,  # {'frontal': 'path', 'trasera': 'path', 'lat_izq': 'path', 'lat_der': 'path'}
    firma_digital_path: str,
    mediciones_neumaticos: list, # [{'posicion': str, 'psi': float, 'mm': float, 'estado': 'OK'/'NOK', 'foto_desviacion': str}]
    evaluaciones_checklist: list  # [{'item_num': int, 'estado': 'OK'/'NOK', 'obs': str, 'foto_desviacion': str}]
):
    """
    Registra la inspección asegurando validación estricta de fotos ante hallazgos NOK,
    garantiza inmutabilidad y genera Solicitudes de Atención Urgente (OT).
    """
    
    # 1. Validación de Fotos Perimetrales y Firma Digital
    required_fotos = ['frontal', 'trasera', 'lat_izq', 'lat_der']
    for foto in required_fotos:
        if not fotos_perimetrales.get(foto):
            raise ValueError(f"ERROR DE VALIDACIÓN: Falta la foto perimetral obligatorio: '{foto}'.")

    if not firma_digital_path:
        raise ValueError("ERROR DE VALIDACIÓN: La firma digital manuscrita es OBLIGATORIA para sellar el informe.")

    desviaciones_detectadas = []

    # 2. Validación de Neumáticos
    if len(mediciones_neumaticos) != 6:
        raise ValueError("ERROR DE VALIDACIÓN: Debe registrar el control de los 6 neumáticos.")

    for neum in mediciones_neumaticos:
        if neum['estado'] == 'NOK':
            if not neum.get('foto_desviacion'):
                raise ValueError(f"ERROR REGLA DE NEGOCIO: El neumático '{neum['posicion']}' está en NOK pero NO tiene foto de evidencia.")
            desviaciones_detectadas.append({
                'origen': f"Neumático {neum['posicion']}",
                'descripcion': f"Presión: {neum['psi']} PSI | Profundidad: {neum['mm']} mm",
                'foto': neum['foto_desviacion']
            })

    # 3. Validación de Checklist (30 Ítems)
    if len(evaluaciones_checklist) != 30:
        raise ValueError("ERROR DE VALIDACIÓN: Debe evaluar los 30 ítems del checklist operacional.")

    for item_eval in evaluaciones_checklist:
        if item_eval['estado'] == 'NOK':
            if not item_eval.get('foto_desviacion'):
                raise ValueError(f"ERROR REGLA DE NEGOCIO: El ítem #{item_eval['item_num']} está en NOK pero NO tiene foto de evidencia.")
            
            desc_item = next((it[2] for it in ITEMS_CHECKLIST_BASE if it[0] == item_eval['item_num']), "Ítem desconocido")
            desviaciones_detectadas.append({
                'origen': f"Checklist Ítem #{item_eval['item_num']} - {desc_item}",
                'descripcion': item_eval.get('obs', 'Sin observación detallada'),
                'foto': item_eval['foto_desviacion']
            })

    # 4. Determinar Estado de la Unidad
    if len(desviaciones_detectadas) == 0:
        estado_final = "APROBADO"
        estado_unidad = "DISPONIBLE"
    elif len(desviaciones_detectadas) <= 2:
        estado_final = "CON_OBSERVACIONES"
        estado_unidad = "CON_OBSERVACIONES"
    else:
        estado_final = "FUERA_DE_SERVICIO"
        estado_unidad = "FUERA_DE_SERVICIO"

    # 5. Guardar en Base de Datos
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # A. Insertar Encabezado Inmutable
        cursor.execute("""
        INSERT INTO inspecciones_inmutables (
            codigo_unidad, modelo, kilometraje, horometro_bomba,
            inspector_nombre, inspector_rut,
            foto_frontal, foto_trasera, foto_lat_izq, foto_lat_der,
            firma_digital, estado_final
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            codigo_unidad, "Modelo Registrado", kilometraje, horometro_bomba,
            inspector_nombre, inspector_rut,
            fotos_perimetrales['frontal'], fotos_perimetrales['trasera'],
            fotos_perimetrales['lat_izq'], fotos_perimetrales['lat_der'],
            firma_digital_path, estado_final
        ))
        
        inspeccion_id = cursor.lastrowid

        # B. Insertar Control Neumáticos
        for neum in mediciones_neumaticos:
            cursor.execute("""
            INSERT INTO control_neumaticos (
                inspeccion_id, posicion, presion_psi, profundidad_mm, estado, foto_desviacion
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                inspeccion_id, neum['posicion'], neum['psi'], neum['mm'], neum['estado'], neum.get('foto_desviacion')
            ))

        # C. Insertar Checklist Operacional
        for item_eval in evaluaciones_checklist:
            info_base = next((it for it in ITEMS_CHECKLIST_BASE if it[0] == item_eval['item_num']), (0, "General", "Desconocido"))
            cursor.execute("""
            INSERT INTO detalle_checklist (
                inspeccion_id, item_numero, subsistema, item_descripcion, estado, observacion, foto_desviacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                inspeccion_id, item_eval['item_num'], info_base[1], info_base[2],
                item_eval['estado'], item_eval.get('obs', ''), item_eval.get('foto_desviacion')
            ))

        # D. Generar Solicitudes de Atención Urgente (OT) por cada Desviación
        for dev in desviaciones_detectadas:
            cursor.execute("""
            INSERT INTO solicitudes_atencion_urgente (
                codigo_unidad, inspeccion_id, origen_falla, descripcion_falla, foto_evidencia_falla, estado_ot
            ) VALUES (?, ?, ?, ?, ?, 'PENDIENTE')
            """, (
                codigo_unidad, inspeccion_id, dev['origen'], dev['descripcion'], dev['foto']
            ))

        # E. Actualizar Timers y Estado Operativo de la Unidad
        cursor.execute("""
        UPDATE unidades 
        SET kilometraje_actual = ?, horometro_bomba_actual = ?, estado_operativo = ?
        WHERE codigo_unidad = ?
        """, (kilometraje, horometro_bomba, estado_unidad, codigo_unidad))

        conn.commit()
        print(f"✅ INSPECCIÓN #{inspeccion_id} GUARDADA EXITOSAMENTE.")
        print(f"   📌 Estado Final: {estado_final}")
        print(f"   🛠 OTs de Atención Urgente Generadas: {len(desviaciones_detectadas)}")
        return inspeccion_id

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR AL GUARDAR EN BASE DE DATOS: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    print("Módulo capturador.py cargado correctamente con validaciones de desviaciones.")
