# REPORTE OFICIAL DEL PROYECTO FINAL - SISTEMAS DISTRIBUIDOS
## PLATAFORMA DISTRIBUIDA DE INTEROPERABILIDAD CLÍNICA CON FHIR R4, HEALTH SERVICE BUS (HSB) Y BASE DISTRIBUIDA CITUS

**Autores:** Carlos Andrés Acosta Herrera & Juan David Benítez Ruiz  
**Asignatura:** Sistemas Distribuidos | **Docente:** Ing. Jaider Enrique Reyes Herazo  
**Corporación Universitaria Antonio José de Sucre (Sincelejo, Colombia)**  
**Versión:** Plantilla v7 Completa | Noviembre 2026  

---

### ÍNDICE DE EVIDENCIAS Y CAPTURAS PARA EL INFORME WORD v7

| # Evidencia | Nombre de Archivo | Fase Evaluada | Descripción Técnica en la Solución |
|---|---|---|---|
| **📸 Evidencia 1** | `evidencia_01_docker_compose_up.png` | **Fase 2 (1.0 pt)** | Despliegue de los 7 contenedores en Docker Compose (3 Sedes legadas + Clúster Citus + HAPI FHIR) en estado `Up`. |
| **📸 Evidencia 2** | `evidencia_02_explain_citus.png` | **Fase 2 (1.0 pt)** | Plan de ejecución distribuido `EXPLAIN` con `Custom Scan (Citus Adaptive)`, `Task Count: 1` e `Index Scan` por `patient_id`. |
| **📸 Evidencia 3** | `evidencia_03_acid_rollback.png` | **Fase 2 (1.0 pt)** | Demostración transaccional ACID: inserción atómica en 2 tablas distribuidas con `ROLLBACK` y resultado `(0 rows)`. |
| **📸 Evidencia 4** | `evidencia_04_pruebas_unitarias_fhir.png` | **Fase 2 (1.0 pt)** | `Ran 5 tests in 0.001s ... OK`: normalización canónica a FHIR R4, validación estricta de documentos, sexo y mapeo CIE-10/LOINC. |
| **📸 Evidencia 5** | `evidencia_05_hsb_pruebas_completas.png` | **Fase 3 (1.25 pts)** | Contrato oficial HSB: Ingesta HL7 válida, rechazo sintáctico/semántico, idempotencia SHA-256 (duplicado) y CSV legado (3 entregados, 2 rechazados). |
| **📸 Evidencia 6** | `evidencia_06_seguridad_auditoria.png` | **Fase 4 (1.0 pt)** | Control de acceso RBAC con JWT (Médico 200 OK vs Paciente 403 Forbidden) y verificación de integridad de auditoría Hash-Chain (4 bloques inmutables). |
| **📸 Evidencia 7** | `evidencia_07_tolerancia_fallos_sede_down.png` | **Fase 4 (1.0 pt)** | Degradación elegante: caída en vivo de `db_sede2`, el sistema responde `status: UP`, `SEDE2: DOWN` sin colapsar. |
| **📸 Evidencia 8** | `evidencia_08_vista_paciente.png` | **Fase 5 (1.0 pt)** | **Vista 1 (Paciente):** Consulta unificada multisede y botón de descarga de Bundle FHIR R4 en JSON. |
| **📸 Evidencia 9** | `evidencia_09_vista_admisionista.png` | **Fase 5 (1.0 pt)** | **Vista 2 (Admisionista):** Admisión, triage (1 al 5), enrutamiento por sede y sincronización con Citus. |
| **📸 Evidencia 10** | `evidencia_10_vista_medico.png` | **Fase 5 (1.0 pt)** | **Vista 3 (Médico):** Diagnóstico codificado en CIE-10 y firmado en la cadena de auditoría por Hash. |
| **📸 Evidencia 11** | `evidencia_11_vista_reporte_monitoreo.png` | **Fase 5 (1.0 pt)** | **Vista 4 (Reporte/Monitoreo):** Tablero con mensajes entregados, latencia promedio, DLQ y estado de los 5 nodos. |
