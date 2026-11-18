# EVIDENCIAS OFICIALES - FASE 3 COMPLETADA AL 100%

## 1. Prueba Ingesta HL7 v2 Válida (Sede 2 - Andrea Rojas)
```json
{
  "status": "entregado",
  "sede": "SEDE2",
  "documento": "1007",
  "latency_ms": 513.38
}
```
**Análisis:** El mensaje ADT^A01 es procesado, validado, transformado a Bundle FHIR R4 e insertado atómicamente en el clúster Citus y en la base legada de la Sede 2 en 513 ms.

## 2. Prueba de Idempotencia (Reenvío de Mensaje 1)
```json
{
  "status": "duplicado",
  "motivo": "Mensaje ya procesado (idempotencia)"
}
```
**Análisis:** Al reenviar el mismo mensaje, el HSB calcula la huella SHA-256 del contenido, detecta la colisión en su registro y descarta la duplicación sin generar registros redundantes en la base distribuida.

## 3. Prueba Ingesta HL7 v2 Inválida (Rechazo Sintáctico/Semántico)
```json
{
  "status": "rechazado",
  "motivo": "Documento no numérico: 'ABC123'"
}
```
**Análisis:** El mensaje 03 es interceptado por el motor de validación del HSB antes de persistir, evitando corrupción de datos y registrando el incidente en la Dead Letter Queue (DLQ).

## 4. Prueba Ingesta CSV Legado Sede 3 (Corozal)
```json
{
  "entregados": [
    {"documento": "1008", "nombre": "Camila Suarez Pineda", "cie10": "A09"},
    {"documento": "1009", "nombre": "Ricardo Mendoza Lara", "cie10": "I10"},
    {"documento": "1010", "nombre": "Sofia Blanco Mesa", "cie10": "J45.9"}
  ],
  "rechazados": [
    {"documento": "1011", "motivos": ["Diagnóstico local 'DOLOR MISTERIOSO' sin mapeo a CIE-10"]},
    {"documento": "12", "motivos": ["Documento inválido (longitud < 3 dígitos): '12'"]}
  ]
}
```
**Análisis:** De las 5 filas procesadas, exactamente las 3 válidas fueron normalizadas con sus códigos CIE-10 (`A09`, `I10`, `J45.9`), y las 2 erróneas fueron rechazadas con motivos específicos.
