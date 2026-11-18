# EVIDENCIA RESILIENCIA Y TOLERANCIA A FALLOS (FASE 4)

```text
[carlos@localhost parcial-final-distribuidos]$ docker stop db_sede2
db_sede2
[carlos@localhost parcial-final-distribuidos]$ curl -s http://localhost:8000/health
{"status":"UP","citus":"UP","hapi_fhir":"UP_READY","sedes":{"SEDE1":"UP","SEDE2":"DOWN","SEDE3":"UP"}}
```

**Análisis para el Informe y Sustentación:**
Se demuestra la propiedad de **degradación elegante (Graceful Degradation)** de la plataforma distribuida:
Al desconectarse el nodo de la Sede 2 (Cartagena), el sistema no colapsa ni arroja errores fatales 500. El Health Service Bus identifica el fallo, marca la sede como `DOWN`, y mantiene el servicio activo permitiendo que las consultas hacia Sincelejo (Sede 1) y Corozal (Sede 3) sigan operando normalmente.
