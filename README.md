# Plataforma Distribuida de Interoperabilidad Clínica

Proyecto final para la asignatura **Sistemas Distribuidos** de la **Corporación Universitaria Antonio José de Sucre (Corposucre)**.
- **Autores:** Carlos Andrés Acosta Herrera & Juan David Benítez Ruiz
- **Docente:** Ing. Jaider Enrique Reyes Herazo
- **Versión:** `v1.0` (Tag oficial de entrega)

---

## 🚀 Arquitectura y Tecnologías
- **Health Service Bus (HSB):** FastAPI en Python 3.9 con mediación de mensajería HL7 v2 (ADT^A01, ORU^R01) y archivos CSV legados.
- **Normalizador Canónico:** HL7 FHIR Release 4 en formato `transaction` (`Patient`, `Encounter`, `Condition`, `Observation`).
- **Base de Datos Distribuida:** Clúster Citus (PostgreSQL 12.1) particionado horizontalmente por `patient_id`.
- **Servidor Canónico:** HAPI FHIR JPA v8.12.0.
- **Seguridad y Resiliencia:** Control de acceso granular RBAC con JWT, cadena de auditoría inmutable basada en bloques de hash SHA-256, deduplicación e idempotencia.

---

## 📦 Arranque con Comando Único desde Cero

Para levantar el 100% de la plataforma (las 3 bases de datos legadas, el clúster Citus autoconfigurado, el servidor HAPI y el HSB con las interfaces web):

```bash
docker compose down -v
docker compose up --build -d
```

### Servicios Expuestos:
- **Portal Web y Cuatro Vistas:** `http://localhost:8000`
- **Servidor HAPI FHIR:** `http://localhost:8080/fhir`
- **Citus Coordinator:** `localhost:5432`
- **Sede 1 (Sincelejo):** `localhost:5433`
- **Sede 2 (Cartagena):** `localhost:5434`
- **Sede 3 (Corozal):** `localhost:5435`

---

## 🧪 Ejecución de Pruebas Oficiales

Una vez levantado el clúster, ejecute la batería de pruebas:

```bash
# 1. Pruebas unitarias del normalizador FHIR (5 pruebas)
python3 -m unittest tests/test_normalizer.py

# 2. Pruebas oficiales de integración del HSB (HL7, Idempotencia, DLQ y CSV)
python3 tests/run_official_tests.py

# 3. Pruebas de Seguridad RBAC y Verificación de Cadena de Auditoría
python3 tests/test_fase4_security.py
```

---

## 👥 Usuarios de Prueba (Roles RBAC)
- **Rol Médico:** Acceso total a consulta unificada, formulación y registro de diagnósticos CIE-10 firmados por Hash.
- **Rol Admisionista:** Registro de pacientes, asignación de triage y despacho hacia el HSB.
- **Rol Paciente:** Consulta de su propia historia clínica unificada y descarga del Bundle FHIR R4.
- **Rol Auditor:** Monitoreo del estado de nodos en vivo, métricas de latencia y verificación de la cadena de bloques.
