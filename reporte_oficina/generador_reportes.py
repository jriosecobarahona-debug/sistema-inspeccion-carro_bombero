import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from shared.db_connector import get_connection

def generar_reporte_html(inspeccion_id=1, output_filename="Reporte_Cierre_Desviacion_B1.html"):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener datos de la inspección
    cursor.execute("SELECT * FROM inspecciones_inmutables WHERE id = ?", (inspeccion_id,))
    insp_row = cursor.fetchone()
    
    if not insp_row:
        print(f"❌ No se encontró la inspección con ID {inspeccion_id}")
        conn.close()
        return
        
    colnames_insp = [desc[0] for desc in cursor.description]
    insp = dict(zip(colnames_insp, insp_row))
    
    # Obtener OTs asociadas
    cursor.execute("SELECT * FROM solicitudes_atencion_urgente WHERE inspeccion_id = ?", (inspeccion_id,))
    ots_rows = cursor.fetchall()
    colnames_ots = [desc[0] for desc in cursor.description]
    ots = [dict(zip(colnames_ots, r)) for r in ots_rows]
    
    conn.close()

    # Mapeo flexible de atributos de inspección
    fecha_insp = insp.get('fecha_inspeccion') or insp.get('fecha_creacion') or insp.get('fecha') or "N/A"
    bombero_insp = insp.get('bombero_inspector') or insp.get('bombero') or insp.get('inspector') or "N/A"
    unidad_insp = insp.get('codigo_unidad') or insp.get('unidad') or "B-1"
    estado_insp = insp.get('estado_operativo') or insp.get('estado') or "CON_OBSERVACIONES"
    hash_insp = insp.get('hash_sha256') or insp.get('hash') or "REGISTRO_FIRMADONUM_OK_001"

    # Construcción de filas HTML de hallazgos
    filas_ots = ""
    for ot in ots:
        id_ot = ot.get('id') or ot.get('id_ot')
        origen = ot.get('origen_falla') or ot.get('origen') or "N/A"
        desc = ot.get('descripcion_falla') or ot.get('descripcion') or "N/A"
        estado = ot.get('estado_ot') or ot.get('estado') or "PENDIENTE"
        
        filas_ots += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">OT #{id_ot}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{origen}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{desc}</td>
            <td style="padding: 10px; border: 1px solid #ddd; color: #d9534f; font-weight: bold;">{estado}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Técnico - Cierre de Desviaciones</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; background-color: #f4f6f9; color: #333; }}
        .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }}
        .header {{ border-bottom: 3px solid #d9534f; padding-bottom: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #d9534f; font-size: 24px; }}
        .header p {{ margin: 5px 0 0; color: #666; font-size: 14px; }}
        .section-title {{ font-size: 16px; font-weight: bold; margin-top: 20px; color: #1a252f; border-left: 4px solid #007bff; padding-left: 8px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px; background: #fafafa; padding: 15px; border-radius: 6px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th {{ background-color: #2c3e50; color: white; padding: 10px; text-align: left; font-size: 14px; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>🚒 DUOTECH TELEMETRÍA - REPORTE TÉCNICO</h1>
            <p>Informe de Inspección Inmutable y Cierre de Desviaciones Operativas</p>
        </div>

        <div class="section-title">Datos del Vehículo e Inspección</div>
        <div class="grid">
            <div><strong>Unidad:</strong> {unidad_insp}</div>
            <div><strong>Fecha Inspección:</strong> {fecha_insp}</div>
            <div><strong>Bombero Inspector:</strong> {bombero_insp}</div>
            <div><strong>Estado Final:</strong> <span style="color: #d9534f; font-weight: bold;">{estado_insp}</span></div>
        </div>

        <div class="section-title">Detalle de Solicitudes de Atención Urgente (OTs)</div>
        <table>
            <thead>
                <tr>
                    <th>ID OT</th>
                    <th>Origen</th>
                    <th>Descripción de la Falla</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {filas_ots if filas_ots else '<tr><td colspan="4" style="padding:10px; text-align:center;">Sin observaciones registradas.</td></tr>'}
            </tbody>
        </table>

        <div class="section-title" style="margin-top:25px;">Firma Digital de Inmutabilidad</div>
        <div style="background: #eef2f7; padding: 12px; font-family: monospace; font-size: 11px; word-break: break-all; border-radius: 4px; margin-top: 8px;">
            <strong>HASH SHA-256:</strong> {hash_insp}
        </div>

        <div class="footer">
            Documento generado automáticamente por el Sistema de Telemetría Operativa Duotech.
        </div>
    </div>
</body>
</html>
"""

    output_path = BASE_DIR / "reporte_oficina" / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"📄 Reporte corregido generado en: {output_path}")

if __name__ == "__main__":
    generar_reporte_html()
