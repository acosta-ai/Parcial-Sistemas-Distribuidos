import hashlib
import time
import requests
import psycopg2
import jwt
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fhir.normalizer import validate_document, normalize_gender

app = FastAPI(title="Plataforma de Interoperabilidad Clínica Distribuida", version="3.0.0")

JWT_SECRET = "supersecreto_clinico_nacional_2026_mfa_jwt_key_secure"
CITUS_CONN_PARAMS = {
    "host": os.getenv("CITUS_HOST", "localhost"),
    "port": int(os.getenv("CITUS_PORT", 5432)),
    "dbname": os.getenv("CITUS_DB", "citus_clinical_cdr"),
    "user": "postgres",
    "password": "postgrespassword",
    "connect_timeout": 2
}

SEDE_PORTS = { "SEDE1": 5433, "SEDE2": 5434, "SEDE3": 5435 }
PENDING_DISPATCH_QUEUE = []

DOCTORES_REGISTRADOS = [
    {"codigo": "MED-01", "nombre": "Dra. Laura Vega", "especialidad": "Medicina General / Urgencias", "sede": "SEDE1"},
    {"codigo": "MED-02", "nombre": "Dr. Mateo Ruiz", "especialidad": "Neumología / Pediatría", "sede": "SEDE2"},
    {"codigo": "MED-03", "nombre": "Dr. Andrés Gómez", "especialidad": "Medicina Interna", "sede": "SEDE3"},
    {"codigo": "MED-04", "nombre": "Dra. Camila Morales", "especialidad": "Cardiología", "sede": "SEDE1"}
]

USUARIOS = {
    "medico": {"pass": "medico123", "rol": "MEDICO", "nombre": "Dr. Mateo Ruiz (Neumología)", "otp": "784912"},
    "admision": {"pass": "admin123", "rol": "ADMISIONISTA", "nombre": "Laura Vega (Admisiones)", "otp": "123456"},
    "auditor": {"pass": "audit123", "rol": "AUDITOR", "nombre": "Dr. Carlos Herrera (Director Auditor)", "otp": "999888"},
    "paciente": {"pass": "paciente123", "rol": "PACIENTE", "nombre": "Andrea Rojas (Paciente)", "otp": "111222"}
}

def get_citus_connection():
    return psycopg2.connect(**CITUS_CONN_PARAMS)

def get_sede_connection(sede: str):
    port = SEDE_PORTS.get(sede.upper(), 5433)
    host = os.getenv(f"{sede.upper()}_HOST", "localhost")
    return psycopg2.connect(
        host=host, port=port,
        dbname=f"historia_clinica_{sede.lower()}",
        user="postgres", password="postgrespassword",
        connect_timeout=2
    )

def calculate_sha256(content: str) -> str:
    return hashlib.sha256(content.strip().encode('utf-8')).hexdigest()

def intentar_entrega_sede(sede_preferida: str, payload: dict) -> dict:
    sedes_prioridad = [sede_preferida] + [s for s in ["SEDE1", "SEDE2", "SEDE3"] if s != sede_preferida]
    for s in sedes_prioridad:
        try:
            conn = get_sede_connection(s)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pacientes (documento, nombre, sexo, fecha_nacimiento, fhir_patient_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (documento) DO NOTHING;
            """, (str(payload["documento"]), payload["nombre"], payload["sexo"][:1].upper(), payload.get("nacimiento", "1990-01-01"), f"pat-{payload['documento']}"))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "ENTREGADO", "sede_efectiva": s, "modo": "DIRECTO" if s == sede_preferida else "FAILOVER"}
        except Exception:
            continue

    PENDING_DISPATCH_QUEUE.append({"payload": payload, "sede_origen": sede_preferida, "timestamp": time.time()})
    return {"status": "ENCOLADO_CONTINGENCIA", "sede_efectiva": "NINGUNA (3 SEDES CAÍDAS)", "modo": "STORE_AND_FORWARD_PENDIENTE"}

def sincronizar_mensajes_pendientes():
    global PENDING_DISPATCH_QUEUE
    if not PENDING_DISPATCH_QUEUE:
        return
    pendientes = list(PENDING_DISPATCH_QUEUE)
    PENDING_DISPATCH_QUEUE = []
    for item in pendientes:
        res = intentar_entrega_sede(item["sede_origen"], item["payload"])
        if res["status"] != "ENTREGADO":
            PENDING_DISPATCH_QUEUE.append(item)

class LoginRequest(BaseModel):
    usuario: str
    password: str
    codigo_2fa: str

@app.post("/api/auth/login")
def login_2fa(req: LoginRequest):
    u = req.usuario.lower().strip()
    if u not in USUARIOS or USUARIOS[u]["pass"] != req.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if req.codigo_2fa != USUARIOS[u]["otp"]:
        raise HTTPException(status_code=403, detail="Código 2FA / OTP incorrecto")

    token = jwt.encode({
        "sub": u, "rol": USUARIOS[u]["rol"], "nombre": USUARIOS[u]["nombre"], "exp": time.time() + 3600
    }, JWT_SECRET, algorithm="HS256")

    return {"status": "OK", "token": token, "usuario": USUARIOS[u]["nombre"], "rol": USUARIOS[u]["rol"]}

@app.get("/api/doctores")
def listar_doctores():
    return DOCTORES_REGISTRADOS

class DoctorRequest(BaseModel):
    nombre: str
    especialidad: str
    sede: str

@app.post("/api/doctores")
def agregar_doctor(doc: DoctorRequest):
    nuevo = {"codigo": f"MED-0{len(DOCTORES_REGISTRADOS)+1}", "nombre": doc.nombre, "especialidad": doc.especialidad, "sede": doc.sede}
    DOCTORES_REGISTRADOS.append(nuevo)
    return {"status": "Doctor registrado", "doctor": nuevo}

class PacienteRequest(BaseModel):
    documento: str
    nombre: str
    sexo: str
    nacimiento: str
    sede: str
    triage: int
    motivo: str
    medico: Optional[str] = "MED-01"

@app.post("/api/admision")
def registrar_paciente_admision(pac: PacienteRequest, bg_tasks: BackgroundTasks):
    doc_id = validate_document(pac.documento)
    gen = normalize_gender(pac.sexo)
    
    try:
        conn = get_citus_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO distributed_patient (patient_id, documento, nombre, sexo, nacimiento, sede_origen, fhir_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (patient_id) DO UPDATE SET nombre = EXCLUDED.nombre;
        """, (doc_id, str(doc_id), pac.nombre, gen, pac.nacimiento, pac.sede, f"pat-{doc_id}"))
        
        cur.execute("""
            INSERT INTO distributed_encounter (patient_id, codigo_atencion, fecha, triage, profesional, sede)
            VALUES (%s, %s, NOW(), %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (doc_id, f"V-{pac.sede}-{int(time.time())}", pac.triage, pac.medico, pac.sede))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[CITUS] {e}")

    res_sede = intentar_entrega_sede(pac.sede, {"documento": doc_id, "nombre": pac.nombre, "sexo": gen, "nacimiento": pac.nacimiento})
    bg_tasks.add_task(sincronizar_mensajes_pendientes)

    return {"status": "PROCESADO", "documento": str(doc_id), "resiliencia": res_sede, "cola_pendientes_total": len(PENDING_DISPATCH_QUEUE)}

class DiagnosticoRequest(BaseModel):
    documento: str
    cie10: str
    medico: str

@app.post("/api/diagnostico")
def firmar_diagnostico(diag: DiagnosticoRequest):
    doc_id = validate_document(diag.documento)
    try:
        conn = get_citus_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO distributed_condition (patient_id, cie10_code, descripcion, fecha, sede)
            VALUES (%s, %s, %s, NOW(), 'SEDE1');
        """, (doc_id, diag.cie10, f"Diagnóstico confirmado por {diag.medico}"))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "FIRMADO_HASH_CHAIN", "hash": calculate_sha256(f"{doc_id}|{diag.cie10}|{time.time()}")}
    except Exception as e:
        return {"status": "OFFLINE_FIRMADO_LOCAL", "error": str(e)}

@app.get("/api/paciente/{doc}")
def consultar_historia(doc: str):
    try:
        conn = get_citus_connection()
        cur = conn.cursor()
        cur.execute("SELECT patient_id, documento, nombre, sexo, nacimiento, sede_origen FROM distributed_patient WHERE documento = %s;", (doc,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Paciente no encontrado en el clúster")

        p_id = row[0]
        cur.execute("SELECT codigo_atencion, fecha, triage, profesional, sede FROM distributed_encounter WHERE patient_id = %s ORDER BY fecha DESC;", (p_id,))
        encounters = cur.fetchall()
        cur.execute("SELECT cie10_code, descripcion, fecha, sede FROM distributed_condition WHERE patient_id = %s ORDER BY fecha DESC;", (p_id,))
        conditions = cur.fetchall()
        cur.close()
        conn.close()

        atenciones = []
        for e in encounters:
            atenciones.append({"sede": e[4], "fecha": str(e[1]), "codigo": e[0], "descripcion": f"Triage {e[2]}", "profesional": e[3], "detalle": "Consulta Externa / Urgencias"})
        for c in conditions:
            atenciones.append({"sede": c[3], "fecha": str(c[2]), "codigo": c[0], "descripcion": c[1], "profesional": "Especialista Asignado", "detalle": "Diagnóstico CIE-10 Confirmado"})

        return {
            "paciente": {"patient_id": row[0], "documento": row[1], "nombre": row[2], "sexo": row[3], "nacimiento": str(row[4]), "sede_origen": row[5]},
            "atenciones": atenciones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando clúster: {str(e)}")

@app.get("/health")
def health_check():
    status = {"status": "UP", "citus": "UP", "sedes": {}, "cola_contingencia_pendientes": len(PENDING_DISPATCH_QUEUE)}
    for s in ["SEDE1", "SEDE2", "SEDE3"]:
        try:
            c = get_sede_connection(s)
            c.close()
            status["sedes"][s] = "UP"
        except Exception:
            status["sedes"][s] = "DOWN"
    return status

@app.get("/", response_class=HTMLResponse)
def serve_index():
    path_html = os.path.join(os.path.dirname(__file__), "..", "app", "templates", "index.html")
    with open(path_html, "r", encoding="utf-8") as f:
        return f.read()
