# GUÍA RÁPIDA DE SUSTENTACIÓN INDIVIDUAL - PARCIAL FINAL (GRUPO 5)
**Estudiantes:** Carlos Andrés Acosta Herrera & Juan David Benítez Ruiz  
**Asignatura:** Sistemas Distribuidos | **Profesor:** Ing. Jaider Enrique Reyes Herazo  

---

## 1. Guión de Sustentación en Vivo (15 Minutos)

El profesor pide arrancar la sustentación con:
```bash
docker compose down -v && docker compose up -d
```
Luego se inicia el HSB:
```bash
nohup python3 -m uvicorn hsb.main:app --host 0.0.0.0 --port 8000 > hsb.log 2>&1 &
```

Y se abre en el navegador: `http://localhost:8000`

---

## 2. Preguntas Típicas del Profesor y Respuestas Exactas

### Pregunta 1: "¿Por qué eligieron 'patient_id' como clave de distribución en Citus?"
> **Respuesta:**  
> "Porque el patrón de acceso dominante en sistemas hospitalarios es centrado en el paciente (*Patient-centric access pattern*). Al distribuir por `patient_id` (o documento), todas las tablas relacionadas (`distributed_encounter`, `distributed_condition`, `distributed_observation`) quedan colocalizadas (*colocated tables*) en el mismo shard del worker. Esto garantiza que las consultas de historia clínica y las transacciones ACID se resuelvan localmente en un solo nodo con latencia mínima, evitando 'shuffles' o transferencias masivas de datos por red entre nodos."

### Pregunta 2: "¿Cómo garantiza el HSB la idempotencia si una sede reenvía el mismo mensaje 2 veces?"
> **Respuesta:**  
> "Calculamos una función resumen criptográfica SHA-256 del cuerpo crudo del mensaje. El HSB mantiene un registro de hashes procesados. Si entra un mensaje idéntico, el bus lo identifica como colisión, responde de inmediato con HTTP 200 `{'status': 'duplicado'}` y descarta la operación sin volver a insertar registros duplicados en Citus ni en HAPI FHIR."

### Pregunta 3: "¿Cómo se evidencia el Teorema CAP y la degradación elegante ante la caída de una sede?"
> **Respuesta:**  
> "Priorizamos Disponibilidad y Tolerancia a Particiones (AP) sobre consistencia estricta global inmediata. Cuando apagamos la base de datos de la Sede 2 en caliente con `docker stop db_sede2`, el endpoint `/health` del HSB y la vista unificada no colapsan con un error 500. El bus marca la sede como `DOWN`, continúa sirviendo las consultas de las Sedes 1 y 3 disponibles, y reintenta el envío de mensajes mediante colas con retroceso exponencial (*exponential backoff*), protegiendo la continuidad asistencial del paciente."

### Pregunta 4: "¿Cómo funciona la cadena de auditoría (Hash-Chain)?"
> **Respuesta:**  
> "Funciona bajo el principio de encadenamiento de bloques: cada registro de acceso o inserción clínica guarda `current_hash = SHA-256(prev_hash + data)`. Si alguien entra directamente a la base de datos distribuida a modificar un diagnóstico o borrar una atención, el hash del bloque cambia y la cadena se rompe, lo cual es detectado al instante por nuestro script de verificación de integridad."
