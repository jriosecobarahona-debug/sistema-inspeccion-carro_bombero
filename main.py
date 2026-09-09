import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "duotech.db"

app = FastAPI(title="Duotech Telemetria - Sistema Final")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

class InspeccionInCompleta(BaseModel):
    codigo_unidad: str
    inspector_rut: str
    inspector_nombre: str
    turno_compania: str
    kilometraje: int
    horometro_bomba: float
    psi_neumaticos: str
    chk_respuestas: dict
    evidencias_items: dict
    foto_frontal: str = ""
    foto_lat_izq: str = ""
    foto_lat_der: str = ""
    foto_posterior: str = ""
    firma_digital: str = ""

@app.get("/nueva-inspeccion", response_class=HTMLResponse)
async def form_inspeccion_movil():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checklist Móvil de Terreno - Duotech</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 15px; max-width: 650px; margin: 0 auto; line-height: 1.4; }
        h2, h3 { color: #f87171; text-align: center; margin-top: 10px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
        .badge-alert { background: #7f1d1d; color: #fca5a5; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; display: block; text-align: center; margin-top: 8px; }
        .badge-ok { background: #064e3b; color: #34d399; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; display: block; text-align: center; margin-top: 8px; }
        .form-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: bold; font-size: 13px; color: #8b949e; }
        input, select, textarea { width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white; box-sizing: border-box; font-size: 14px; }
        .chk-item { background: #0d1117; padding: 10px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 8px; }
        .chk-title { font-weight: bold; color: #f0f6fc; font-size: 14px; margin-bottom: 3px; }
        .chk-desc { font-size: 11px; color: #8b949e; margin-bottom: 6px; }
        .evidencia-box { display: none; background: #161b22; border: 1px dashed #f87171; border-radius: 6px; padding: 10px; margin-top: 8px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        canvas { background: #ffffff; border-radius: 6px; border: 1px solid #30363d; width: 100%; height: 120px; touch-action: none; cursor: crosshair; }
        button.btn-submit { width: 100%; background: #238636; color: white; padding: 14px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 15px; }
        button.btn-submit:hover { background: #2ea043; }
        .section-header { background: #21262d; padding: 8px 12px; border-radius: 6px; font-weight: bold; color: #58a6ff; margin: 15px 0 10px 0; border-left: 4px solid #1f6beb; }
    </style>
</head>
<body>
    <h2>App de Inspección en Terreno</h2>
    
    <div class="card" id="card-status">
        <h3 style="margin:0; color:#58a6ff;">Carro Bomba B-1</h3>
        <p style="margin:5px 0 0 0; font-size:12px; text-align:center;">Spartan Metro Star / Crimson</p>
        <div id="mantencion-info" style="font-size:12px; margin-top:10px; text-align:center;">Cargando pauta de mantenimiento...</div>
    </div>

    <form id="chkForm">
        <div class="card">
            <div class="section-header">1. Datos Generales de Control</div>
            <div class="grid-2">
                <div class="form-group">
                    <label>Inspector / Conductor:</label>
                    <input type="text" id="inspector_nombre" value="Juan Pérez" required>
                </div>
                <div class="form-group">
                    <label>RUT Inspector:</label>
                    <input type="text" id="inspector_rut" value="12345678-9" required>
                </div>
            </div>
            <div class="form-group">
                <label>Turno / Compañía:</label>
                <input type="text" id="turno_compania" value="Guardia Nocturna - 1ª Compañía" required>
            </div>
            <div class="grid-2">
                <div class="form-group">
                    <label>Kilometraje Actual:</label>
                    <input type="number" id="kilometraje" value="45210" required>
                </div>
                <div class="form-group">
                    <label>Horómetro Bomba (hrs):</label>
                    <input type="number" step="0.1" id="horometro_bomba" value="1280.0" required>
                </div>
            </div>
            <div class="form-group">
                <label>Presión Neumáticos Ejes (PSI):</label>
                <input type="text" id="psi_neumaticos" value="Delanteros: 110 PSI | Traseros: 120 PSI" required>
            </div>
        </div>

        <div class="card">
            <div class="section-header">2. Registro Fotográfico de Perímetro</div>
            <div class="grid-2">
                <div class="form-group"><label>Foto Frontal:</label><input type="file" id="f_frontal" accept="image/*" capture="environment"></div>
                <div class="form-group"><label>Foto Lateral Izq:</label><input type="file" id="f_lat_izq" accept="image/*" capture="environment"></div>
                <div class="form-group"><label>Foto Lateral Der:</label><input type="file" id="f_lat_der" accept="image/*" capture="environment"></div>
                <div class="form-group"><label>Foto Posterior:</label><input type="file" id="f_posterior" accept="image/*" capture="environment"></div>
            </div>
        </div>

        <div class="card">
            <div class="section-header">3. Checklist de Inspección (Con Evidencia Dinámica)</div>
            <div id="checklist-container">Cargando ítems...</div>
        </div>

        <div class="card">
            <div class="section-header">4. Firma Digital del Inspector</div>
            <div class="form-group">
                <label>Dibujar Firma en Pantalla:</label>
                <canvas id="signature-pad"></canvas>
                <button type="button" onclick="limpiarFirma()" style="background:#30363d; color:white; border:none; padding:4px 8px; border-radius:4px; font-size:11px; margin-top:4px;">Limpiar Firma</button>
            </div>
        </div>

        <button type="submit" class="btn-submit">Firmar y Registrar con SHA-256</button>
    </form>

    <script>
        const items = [
            {id:'MOT-01', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Nivel de Aceite de Motor', desc:'Entre marcas MIN y MAX de la varilla; sin evidencias de contaminación'},
            {id:'MOT-02', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Refrigerante de Radiador', desc:'Nivel correcto en vaso de expansión; sin fugas visibles ni depósitos'},
            {id:'MOT-03', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Líquido de Dirección Asistida', desc:'Nivel adecuado; depósito limpio y mangueras sin humedad'},
            {id:'MOT-04', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Líquido de Limpiaparabrisas', desc:'Depósito lleno; eyectores despejados y funcionales'},
            {id:'MOT-05', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Correa', desc:'Tensión correcta, sin grietas, deshilachados ni desgastes'},
            {id:'MOT-06', cat:'SISTEMA DE MOTOR Y FLUIDOS', name:'Fugas de Lubricantes / Fluidos', desc:'Verificación visual bajo el chasis (aceite, combustible, refrigerante)'},
            
            {id:'ELE-01', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Estado de Baterías', desc:'Bornes limpios, apretados, sin sulfato; fijación de soporte segura'},
            {id:'ELE-02', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Voltímetro / Carga', desc:'Lectura de carga en panel dentro del rango nominal (24V - 28V)'},
            {id:'ELE-03', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Sirena Electrónica y Air Horn', desc:'Prueba de tonos (Wail, Yelp, Hi-Lo) y claxon de aire operativo'},
            {id:'ELE-04', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Micrófono de Perifoneo', desc:'Funcionamiento claro de megafonía externa'},
            {id:'ELE-05', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Barra de Luces (Balizas) y Estrobos', desc:'Todas las luces perimetrales y destellantes operativas al 100%'},
            {id:'ELE-06', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Luces de Escena y Perímetro', desc:'Focos de trabajo de alto poder funcionales sin ampolletas quemadas'},
            {id:'ELE-07', cat:'SISTEMA ELÉCTRICO Y ADVERTENCIA', name:'Luces de Tránsito', desc:'Verificación de luces altas, bajas, viraje, freno y retroceso'},

            {id:'CHS-01', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Presión y Estado de Neumáticos', desc:'Presión según manual (PSI); dibujo >4mm; sin cortes ni deformaciones'},
            {id:'CHS-02', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Tuercas y Pernos de Rueda', desc:'Indicadores de torque alineados; sin pernos sueltos o faltantes'},
            {id:'CHS-03', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Sistema de Frenos de Aire', desc:'Presión en tanques >90 PSI; purga de condensado; sin fugas auditivas'},
            {id:'CHS-04', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Freno de Estacionamiento', desc:'Anclaje seguro y retención efectiva del vehículo'},
            {id:'CHS-05', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Espejos y Vidrios', desc:'Límpios, ajustados, sin fisuras ni impedimentos visuales'},
            {id:'CHS-06', cat:'CHASIS, NEUMÁTICOS Y FRENOS', name:'Puertas y Cierres de Persianas', desc:'Apertura/cierre suave, seguros operativos y alarmas de puerta abierta'},

            {id:'BMB-01', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Nivel de Aceite de la Bomba', desc:'Nivel correcto en ojo de buey / varilla de transmisión de bomba'},
            {id:'BMB-02', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Sistema de Cebado (Primer)', desc:'Creación de vacío efectiva (<30 seg) y sellado de sistema'},
            {id:'BMB-03', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Válvulas de Entrada y Descarga', desc:'Movimiento suave de manivelas/palancas; sellos y empaquetaduras OK'},
            {id:'BMB-04', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Manómetros y Vacuómetros', desc:'Instrumentos intactos, carátula legible y marcación correcta'},
            {id:'BMB-05', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Nivel de Estanque de Agua', desc:'Sensor de nivel operativo; comprobación física de llenado'},
            {id:'BMB-06', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Sistema de Espuma (AFFF / CAFS)', desc:'Nivel de concentrado; dosificador y válvulas de espuma operativas'},
            {id:'BMB-07', cat:'BOMBA DE AGUA Y SISTEMA DE EXTINCIÓN', name:'Acoples y Tapas de Descarga', desc:'Hilos e hiper-acoples limpios, con gomas de sello y cadenas'},

            {id:'EQP-01', cat:'EQUIPAMIENTO Y CABINA', name:'Generador / Motobomba Auxiliar', desc:'Nivel de combustible, aceite y prueba de arranque en vacío'},
            {id:'EQP-02', cat:'EQUIPAMIENTO Y CABINA', name:'Cinturones de Seguridad', desc:'Hebillas y retractores en cabina probados y operativos'},
            {id:'EQP-03', cat:'EQUIPAMIENTO Y CABINA', name:'Soportes de ERA en Cabina', desc:'Trabas mecánicas/neumáticas de equipos autónomos fijas'},
            {id:'EQP-04', cat:'EQUIPAMIENTO Y CABINA', name:'Radio de Comunicaciones', desc:'Prueba de transmisión/recepción en canal de guardia'}
        ];

        async function init() {
            const res = await fetch('/api/unidad/B-1');
            const data = await res.json();
            const divInfo = document.getElementById('mantencion-info');
            
            let statusHtml = <strong>Próxima Mantención:</strong>  km /  hrs<br>;
            if (data.alerta_mantencion) {
                statusHtml += <span class="badge-alert">MANTENCIÓN PROGRAMADA REQUERIDA (Margen:  km /  hrs)</span>;
            } else {
                statusHtml += <span class="badge-ok">PAUTA AL DÍA (Margen:  km /  hrs)</span>;
            }
            divInfo.innerHTML = statusHtml;

            const container = document.getElementById('checklist-container');
            let html = '';
            let currentCat = '';
            
            items.forEach(it => {
                if (it.cat !== currentCat) {
                    currentCat = it.cat;
                    html += <div style="font-weight:bold; color:#f87171; margin:15px 0 8px 0; font-size:12px; border-bottom:1px solid #30363d; padding-bottom:3px;"></div>;
                }
                html += 
                <div class="chk-item">
                    <div class="chk-title">[] </div>
                    <div class="chk-desc"></div>
                    <select id="chk_" onchange="toggleEvidencia('')">
                        <option value="Conforme">Conforme</option>
                        <option value="No Conforme">No Conforme</option>
                    </select>
                    <div class="evidencia-box" id="ev_box_">
                        <label style="color:#f87171;">📷 Fotografiar Evidencia de Falla:</label>
                        <input type="file" id="ev_file_" accept="image/*" capture="environment">
                        <label style="color:#f87171; margin-top:6px;">💬 Breve Comentario de la Anomalía:</label>
                        <textarea id="ev_text_" placeholder="Describa la falla encontrada en este ítem..."></textarea>
                    </div>
                </div>;
            });
            container.innerHTML = html;
        }

        function toggleEvidencia(id) {
            const val = document.getElementById(chk_).value;
            const box = document.getElementById(ev_box_);
            if (val === 'No Conforme') {
                box.style.display = 'block';
            } else {
                box.style.display = 'none';
            }
        }

        // Canvas de firma
        const canvas = document.getElementById('signature-pad');
        const ctx = canvas.getContext('2d');
        let drawing = false;

        function getPos(e) {
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return { x: clientX - rect.left, y: clientY - rect.top };
        }

        canvas.addEventListener('mousedown', (e) => { drawing = true; const p = getPos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); });
        canvas.addEventListener('mousemove', (e) => { if(drawing) { const p = getPos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); } });
        canvas.addEventListener('mouseup', () => drawing = false);
        canvas.addEventListener('touchstart', (e) => { drawing = true; const p = getPos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); e.preventDefault(); });
        canvas.addEventListener('touchmove', (e) => { if(drawing) { const p = getPos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); e.preventDefault(); } });
        canvas.addEventListener('touchend', () => drawing = false);

        function limpiarFirma() { ctx.clearRect(0, 0, canvas.width, canvas.height); }

        function fileToBase64(fileInput) {
            return new Promise((resolve) => {
                if (!fileInput || !fileInput.files[0]) return resolve("");
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(fileInput.files[0]);
            });
        }

        document.getElementById('chkForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const chkRespuestas = {};
            const evidenciasItems = {};

            for (const it of items) {
                const val = document.getElementById(chk_).value;
                chkRespuestas[it.id] = val;
                if (val === 'No Conforme') {
                    const fileInput = document.getElementById(ev_file_);
                    const textInput = document.getElementById(ev_text_);
                    evidenciasItems[it.id] = {
                        foto: await fileToBase64(fileInput),
                        comentario: textInput.value
                    };
                }
            }

            const payload = {
                codigo_unidad: 'B-1',
                inspector_rut: document.getElementById('inspector_rut').value,
                inspector_nombre: document.getElementById('inspector_nombre').value,
                turno_compania: document.getElementById('turno_compania').value,
                kilometraje: parseInt(document.getElementById('kilometraje').value),
                horometro_bomba: parseFloat(document.getElementById('horometro_bomba').value),
                psi_neumaticos: document.getElementById('psi_neumaticos').value,
                chk_respuestas: chkRespuestas,
                evidencias_items: evidenciasItems,
                foto_frontal: await fileToBase64(document.getElementById('f_frontal')),
                foto_lat_izq: await fileToBase64(document.getElementById('f_lat_izq')),
                foto_lat_der: await fileToBase64(document.getElementById('f_lat_der')),
                foto_posterior: await fileToBase64(document.getElementById('f_posterior')),
                firma_digital: canvas.toDataURL()
            };

            const res = await fetch('/api/guardar-inspeccion-completa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert('Inspección guardada y asociada con evidencia fotográfica por ítem.');
                window.location.href = '/';
            } else {
                alert('Error al guardar registro.');
            }
        });

        init();
    </script>
</body>
</html>"""

@app.post("/api/guardar-inspeccion-completa")
async def guardar_inspeccion_completa(data: InspeccionInCompleta):
    str_chk = json.dumps(data.chk_respuestas, sort_keys=True)
    str_evidencias = json.dumps(data.evidencias_items)
    raw_payload = f"{data.codigo_unidad}|{data.inspector_rut}|{data.kilometraje}|{data.horometro_bomba}|{str_chk}|{data.firma_digital[:50]}"
    hash_val = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO inspecciones_inmutables 
        (codigo_unidad, inspector_rut, inspector_nombre, kilometraje, horometro_bomba, json_checklist, foto_frontal, foto_lateral_izq, foto_lateral_der, foto_posterior, foto_evidencia_falla, firma_digital, hash_sha256)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.codigo_unidad, data.inspector_rut, data.inspector_nombre, data.kilometraje, 
        data.horometro_bomba, str_chk, data.foto_frontal, data.foto_lat_izq, 
        data.foto_lat_der, data.foto_posterior, str_evidencias, data.firma_digital, hash_val
    ))
    
    cursor.execute("UPDATE unidades SET kilometraje_actual = ?, horometro_actual = ? WHERE codigo = ?", 
                   (data.kilometraje, data.horometro_bomba, data.codigo_unidad))
    
    no_conformes = [k for k, v in data.chk_respuestas.items() if v == "No Conforme"]
    if no_conformes:
        txt_ot = f"Desviaciones registradas en ítems: {', '.join(no_conformes)}. Revisa reporte ordenado por ítem."
        cursor.execute('''
            INSERT INTO solicitudes_atencion_urgente (codigo_unidad, hallazgo, prioridad, estado)
            VALUES (?, ?, 'ALTA', 'PENDIENTE')
        ''', (data.codigo_unidad, txt_ot))
        
    conn.commit()
    conn.close()
    return {"status": "ok", "hash": hash_val}

@app.get("/api/unidad/{codigo}")
async def get_unidad_info(codigo: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM unidades WHERE codigo = ?", (codigo,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    u = dict(row)
    prox_mant_km = u['ultimo_mantenimiento_km'] + u['pauta_km_intervalo']
    prox_mant_hrs = u['ultimo_mantenimiento_hrs'] + u['pauta_hrs_intervalo']
    
    restante_km = prox_mant_km - u['kilometraje_actual']
    restante_hrs = prox_mant_hrs - u['horometro_actual']
    
    return {
        "codigo": u['codigo'],
        "nombre_modelo": u['nombre_modelo'],
        "kilometraje_actual": u['kilometraje_actual'],
        "horometro_actual": u['horometro_actual'],
        "proxima_mantencion_km": prox_mant_km,
        "proxima_mantencion_hrs": prox_mant_hrs,
        "restante_km": restante_km,
        "restante_hrs": restante_hrs,
        "alerta_mantencion": restante_km <= 0 or restante_hrs <= 0
    }

@app.get("/", response_class=HTMLResponse)
async def status():
    return "<html><body style='font-family:sans-serif; background:#0d1117; color:#c9d1d9; padding:30px;'><h2>Modulo 2: Formulario Movil con Evidencias por Item Listo</h2><p><a href='/nueva-inspeccion' style='background:#238636; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;'>Ir al Formulario Movil Terreno</a></p></body></html>"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8085, reload=False)