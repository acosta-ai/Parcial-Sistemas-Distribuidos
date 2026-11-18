# EVIDENCIAS OFICIALES - FASE 2 COMPLETADA

## Resumen de Evidencias Capturadas:
1. **`evidencia_01_docker_compose_up.png`**: Servicios arriba (3 Sedes legadas + Clúster Citus + HAPI FHIR).
2. **`evidencia_02_explain_citus.png`**: `EXPLAIN SELECT * FROM distributed_patient WHERE patient_id = 1001;` -> Plan distribuido Citus Adaptive con `Task Count: 1` e `Index Scan` sobre shard específico.
3. **`evidencia_03_acid_rollback.png`**: Transacción distribuida con `BEGIN`, doble inserción atómica y `ROLLBACK` resultando en `(0 rows)` demostrando propiedades ACID.
4. **`evidencia_04_pruebas_unitarias_fhir.png`**: `Ran 5 tests in 0.001s ... OK` demostrando normalización canónica a FHIR R4, validación estricta de documentos, normalización de sexo y mapeo terminológico de diagnósticos locales a CIE-10 / LOINC.
