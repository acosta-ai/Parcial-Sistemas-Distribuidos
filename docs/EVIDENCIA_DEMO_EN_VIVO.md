# EVIDENCIA DEMO EN VIVO: APAGADO DE HAPI FHIR Y SEDE 2

```text
[carlos@localhost parcial-final-distribuidos]$ docker stop db_sede2
db_sede2
[carlos@localhost parcial-final-distribuidos]$ docker stop hapi_fhir
hapi_fhir
[carlos@localhost parcial-final-distribuidos]$ curl -X POST http://localhost:8000/api/ingest/hl7 --data-binary @data/01_adt_a01_valido_sede2.hl7
{"status":"entregado","sede":"SEDE2","documento":"1007","latency_ms":7095.13}
```

**Análisis de la Evidencia Técnica:**
1. Se detiene el servidor FHIR (`hapi_fhir`) y la base de la Sede 2 (`db_sede2`).
2. Se envía un mensaje clínico HL7 v2.
3. El HSB ejecuta su algoritmo de **retroceso exponencial** (1s + 2s + 4s = ~7 segundos totales de latencia: `7095.13 ms`).
4. Al no estar HAPI disponible, el bus asegura la persistencia en el clúster distribuido Citus sin perder el mensaje ni arrojar error al cliente emisor, y confina el evento a la cola de reintentos / DLQ.
