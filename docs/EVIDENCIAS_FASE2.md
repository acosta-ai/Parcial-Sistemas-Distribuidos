# EVIDENCIAS OFICIALES - FASE 2: DATOS DISTRIBUIDOS Y FHIR

## 1. Evidencia EXPLAIN Consulta Distribuida (Citus)
```text
Custom Scan (Citus Adaptive)  (cost=0.00..0.00 rows=0 width=0)
  Task Count: 1
  Tasks Shown: All
  -> Task
       Node: host=citus_master port=5432 dbname=citus_clinical_cdr
       -> Index Scan using distributed_patient_pkey_102032 on distributed_patient_102032 distributed_patient
          Index Cond: (patient_id = 1001)
```
**Análisis Técnico para el Informe:**
El optimizador distribuido de Citus determina en tiempo de compilación de la consulta que el predicado `WHERE patient_id = 1001` aplica directamente sobre la clave de distribución de la tabla `distributed_patient`. Esto reduce el espacio de búsqueda a una única tarea (`Task Count: 1`) ejecutando un `Index Scan` sobre el shard correspondiente (`distributed_patient_102032`), eliminando la necesidad de realizar un broadcast o full scan en todos los nodos del clúster.

## 2. Evidencia Prueba Transaccional ACID (Atomicidad y Rollback)
```sql
BEGIN;
INSERT INTO distributed_patient (patient_id, documento, nombre, sexo, nacimiento, sede_origen, fhir_id)
VALUES (9999, '9999', 'Prueba Fallida', 'male', '2000-01-01', 'SEDE1', 'pat-9999');
INSERT INTO distributed_encounter (patient_id, codigo_atencion, fecha, triage, profesional, sede)
VALUES (9999, 'V-FAIL-01', NOW(), 3, 'MED-01', 'SEDE1');
ROLLBACK;
SELECT * FROM distributed_patient WHERE patient_id = 9999;
-- Resultado: (0 rows)
```
