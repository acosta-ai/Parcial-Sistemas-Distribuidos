# FASE 1: ANÁLISIS, MODELADO UML Y DISEÑO ARQUITECTÓNICO
**Proyecto:** Plataforma Distribuida de Interoperabilidad Clínica (FHIR, HSB, BD Distribuida)  
**Curso:** Sistemas Distribuidos – Parcial Final  
**Integrantes:** Carlos Andrés Acosta Herrera & Juan David Benítez Ruiz  
**Institución:** Corporación Universitaria Antonio José de Sucre  

---

## 1. Diagrama de Arquitectura Global del Sistema

```mermaid
flowchart TB
    subgraph Fuentes["Fuentes de Datos Legadas (3 Sedes)"]
        S1["Sede 1: Sincelejo\n(HL7 v2 ORU^R01 / Postgres 5433)"]
        S2["Sede 2: Cartagena\n(HL7 v2 ADT^A01 / Postgres 5434)"]
        S3["Sede 3: Corozal\n(CSV / JSON Legado / Postgres 5435)"]
    end

    subgraph Middleware["HSB - Health Service Bus (FastAPI :8000)"]
        Adapter["Adaptadores de Ingesta\n(HL7 Parser / CSV Reader)"]
        Validator["Motor de Validación Semántica\n(Documento, Sexo, Dx)"]
        Idempotency["Filtro de Idempotencia\n(SHA-256 Hash / Msg-ID Cache)"]
        Terminology["Servicio de Terminologías\n(ref_terminology: Local -> CIE-10 / LOINC)"]
        Normalizer["Normalizador FHIR R4\n(Bundle: Patient, Encounter, Obs, Cond)"]
        RetryQueue["Cola de Reintentos Exponenciales\n(Backoff: 1s, 2s, 4s...)"]
        DLQ["Dead Letter Queue (DLQ)\nMensajes Fallidos Incorregibles"]
    end

    subgraph Persistencia["Capa de Persistencia Distribuida"]
        CitusCoord["Coordinador Distribuido Citus (:5432)\nParticionado por patient_id"]
        CitusW1["Worker 1 (Sede 1 & 2 Shards)"]
        CitusW2["Worker 2 (Sede 3 Shard)"]
        HAPIFHIR["Servidor FHIR Canónico\n(HAPI FHIR JPA :8080)"]
        AuditLog["Registro de Auditoría Encadenado\n(SHA-256 Hash Chain Block)"]
    end

    subgraph Vistas["Capa de Presentación / Aplicación (:8000)"]
        VPaciente["Vista 1: Paciente\n(HC Unificada + Descarga Bundle FHIR)"]
        VAdmision["Vista 2: Admisionista\n(Búsqueda, Triage, Despacho HSB)"]
        VMedico["Vista 3: Médico\n(Consulta, Diagnóstico CIE-10, Sello)"]
        VReporte["Vista 4: Reporte HC / Monitoreo\n(Cobertura FHIR, Latencia, DLQ)"]
    end

    S1 --> Adapter
    S2 --> Adapter
    S3 --> Adapter

    Adapter --> Validator
    Validator -->|Inválido| DLQ
    Validator -->|Válido| Idempotency
    Idempotency -->|Duplicado| DLQ
    Idempotency -->|Único| Terminology
    Terminology --> Normalizer

    Normalizer --> CitusCoord
    Normalizer -->|Fallo Red / Down| RetryQueue
    RetryQueue -->|Reintento OK| HAPIFHIR
    RetryQueue -->|Max Reintentos Excedido| DLQ
    Normalizer -->|Transacción OK| HAPIFHIR
    Normalizer --> AuditLog

    CitusCoord --- CitusW1
    CitusCoord --- CitusW2

    Vistas --> CitusCoord
    Vistas --> HAPIFHIR
```

---

## 2. Los 4 Modelos UML Oficiales

### 2.1 Diagrama de Casos de Uso (UML)
Describe las interacciones de los cuatro roles con el sistema y el HSB.

```mermaid
flowchart LR
    subgraph Actores
        Adm["Admisionista"]
        Med["Médico"]
        Pac["Paciente"]
        Aud["Auditor / Reportero"]
        Sys["Sistemas Legados"]
    end

    subgraph Plataforma["Plataforma Distribuida de Interoperabilidad Clínica"]
        UC1["Ingerir Mensajes (HL7 v2 / CSV)"]
        UC2["Validar y Resolver Identidad"]
        UC3["Registrar Admisión y Triage"]
        UC4["Consultar Historia Clínica Unificada"]
        UC5["Registrar Diagnóstico CIE-10"]
        UC6["Generar y Descargar Bundle FHIR"]
        UC7["Monitorear Métricas y DLQ"]
        UC8["Verificar Cadena de Auditoría (Hash Chain)"]
    end

    Sys --> UC1
    Adm --> UC2
    Adm --> UC3
    Med --> UC4
    Med --> UC5
    Pac --> UC4
    Pac --> UC6
    Aud --> UC7
    Aud --> UC8
```

---

### 2.2 Diagrama de Secuencia (UML)
Muestra la interacción temporal, validación, idempotencia, normalización FHIR y persistencia distribuida.

```mermaid
sequenceDiagram
    autonumber
    actor Sede as Sistema Legado (Sede 2)
    participant HSB as HSB (FastAPI)
    participant Val as Validador & Idempotencia
    participant Term as ref_terminology
    participant Norm as Normalizador FHIR R4
    participant Citus as BD Distribuida (Citus)
    participant HAPI as HAPI FHIR Server
    participant Audit as Hash-Chain Audit

    Sede->>HSB: POST /api/ingest/hl7 (01_adt_a01_valido_sede2.hl7)
    HSB->>Val: Validar estructura y hash SHA-256
    alt Mensaje Duplicado
        Val-->>HSB: Estado: DUPLICADO (Deduplicación)
        HSB-->>Sede: 200 OK (Mensaje ignorado sin duplicar)
    else Mensaje Inválido
        Val-->>HSB: Rechazado (motivos explícitos)
        HSB->>Audit: Registrar rechazo en DLQ
        HSB-->>Sede: 422 Unprocessable Entity
    else Mensaje Válido y Único
        Val->>Term: Mapear 'J45.9' -> Asma (CIE-10)
        Term-->>Norm: Códigos normalizados
        Norm->>Norm: Construir Bundle FHIR R4 (Patient, Encounter, Condition)
        
        critical Transacción ACID Distribuida
            Norm->>Citus: INSERT INTO distributed_patient, encounter (patient_id=1007)
            Citus-->>Norm: 201 Created (Commit Confirmado)
        end

        Norm->>HAPI: POST /fhir/Bundle (Transaction)
        alt HAPI Disponible
            HAPI-->>Norm: 200 OK (Recursos instanciados)
        else HAPI Caído / Timeout
            Norm->>HSB: Encolar en RetryQueue (Backoff Exponencial)
        end

        Norm->>Audit: Registrar AuditEvent (Hash previo + Hash actual)
        HSB-->>Sede: 200 OK {status: "ENTREGADO", fhir_id: "bundle-1007"}
    end
```

---

### 2.3 Diagrama de Clases (UML - >= 10 Entidades)
Estructura de clases canónicas del sistema, recursos FHIR R4 y entidades de infraestructura del HSB.

```mermaid
classDiagram
    class Patient {
        +String id
        +String documento_id
        +String tipo_documento
        +String nombre_completo
        +Date fecha_nacimiento
        +String genero
        +String sede_origen
    }

    class Encounter {
        +String id
        +String patient_id
        +DateTime fecha_inicio
        +String estado
        +String motivo_consulta
        +Integer triage
        +String profesional_id
    }

    class Condition {
        +String id
        +String patient_id
        +String encounter_id
        +String cie10_code
        +String descripcion
        +DateTime fecha_registro
    }

    class Observation {
        +String id
        +String patient_id
        +String loinc_code
        +String nombre_prueba
        +Float valor_numerico
        +String unidad
        +String estado
    }

    class Sede {
        +String sede_id
        +String nombre
        +String ip_host
        +Integer puerto
        +String formato_predeterminado
        +Boolean activo
    }

    class HSBMessage {
        +String message_id
        +String content_hash
        +String formato_origen
        +String sede_origen
        +String payload_raw
        +String estado
        +DateTime fecha_ingesta
    }

    class RetryQueue {
        +String queue_id
        +String message_id
        +Integer intento_actual
        +Integer max_intentos
        +DateTime proximo_reintento
        +String ultimo_error
    }

    class DeadLetterQueue {
        +String dlq_id
        +String message_id
        +String razon_fallo
        +DateTime fecha_descarte
        +Boolean revisado
    }

    class TerminologyMap {
        +String codigo_local
        +String sistema_destino
        +String codigo_estandar
        +String descripcion_oficial
    }

    class AuditEventChain {
        +Integer block_index
        +String prev_hash
        +String data_hash
        +String current_hash
        +String accion
        +String usuario
        +DateTime timestamp
    }

    Patient "1" --> "0..*" Encounter : tiene
    Patient "1" --> "0..*" Condition : presenta
    Patient "1" --> "0..*" Observation : registra
    Encounter "1" --> "0..*" Condition : diagnosticada_en
    Sede "1" --> "0..*" Patient : custodia
    HSBMessage "1" --> "0..1" RetryQueue : reintentado_por
    HSBMessage "1" --> "0..1" DeadLetterQueue : descartado_en
    HSBMessage "0..*" --> "1" TerminologyMap : utiliza
    AuditEventChain "1" --> "1" HSBMessage : audita
```

---

### 2.4 Diagrama de Estados (Ciclo de Vida del Mensaje en el HSB)

```mermaid
stateDiagram-v2
    [*] --> RECIBIDO: Ingesta HL7 v2 / CSV
    
    RECIBIDO --> VALIDANDO: Verificar reglas sintácticas y unicidad
    
    VALIDANDO --> RECHAZADO: Faltan campos / Formato inválido
    RECHAZADO --> DLQ: Almacenar en Dead Letter Queue con motivo
    
    VALIDANDO --> DUPLICADO: Hash coincide con mensaje procesado
    DUPLICADO --> DESCARTADO_OK: Confirmar sin re-procesar (Idempotencia)
    
    VALIDANDO --> TRANSFORMANDO: Validación exitosa
    
    TRANSFORMANDO --> NORMALIZADO_FHIR: Mapeo terminológico (CIE-10 / LOINC)
    
    NORMALIZADO_FHIR --> PERSISTIENDO_CITUS: Escritura en Shards Distribuidos
    PERSISTIENDO_CITUS --> ENVIANDO_HAPI: POST /fhir/Bundle
    
    ENVIANDO_HAPI --> ENTREGADO: Respuesta 200 OK de Citus y HAPI
    
    ENVIANDO_HAPI --> REINTENTANDO: Fallo de red / HAPI caído
    REINTENTANDO --> ENVIANDO_HAPI: Backoff Exponencial (1s, 2s, 4s...)
    REINTENTANDO --> DLQ: Intentos >= MAX_RETRIES (3)
    
    ENTREGADO --> [*]
    DESCARTADO_OK --> [*]
    DLQ --> [*]
```

---

## 3. Tabla de Mapeo Semántico de Campos (>= 15 Campos)

| # | Campo Origen (HL7 / CSV Legado) | Segmento / Columna Origen | Recurso FHIR R4 Destino | Elemento FHIR R4 | Tipo de Dato | Terminología / Regla de Transformación |
|---|---|---|---|---|---|---|
| 1 | Identificador de Mensaje | MSH-10 | Bundle / MessageHeader | `Bundle.id` | id | Preserva ID único para idempotencia |
| 2 | Sede Emisora | MSH-4 | Provenance / ServiceRequest | `Provenance.agent.who` | Reference | Normaliza a Código Sede (SEDE1, SEDE2, SEDE3) |
| 3 | Fecha y Hora de Envío | MSH-7 | Bundle / MessageHeader | `Bundle.timestamp` | instant | Formato ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`) |
| 4 | Documento de Identidad | PID-3.1 / `documento` | Patient | `Patient.identifier.value` | string | Numérico >= 3 dígitos (Clave de partición) |
| 5 | Tipo de Identificador | PID-3.4 / Sistema HIS | Patient | `Patient.identifier.system` | uri | `urn:oid:co:ips:identificacion` |
| 6 | Apellidos del Paciente | PID-5.1 / `nombre` (split) | Patient | `Patient.name.family` | string | Normalización a mayúscula inicial |
| 7 | Nombres del Paciente | PID-5.2 / `nombre` (split) | Patient | `Patient.name.given` | string | Extrae nombres de pila |
| 8 | Fecha de Nacimiento | PID-7 / `nacimiento` | Patient | `Patient.birthDate` | date | Formato `YYYY-MM-DD` |
| 9 | Sexo / Género | PID-8 / `sexo` | Patient | `Patient.gender` | code | Mapeo obligatorio: M->male, F->female |
| 10 | Identificador del Encuentro | PV1-19 / Generado | Encounter | `Encounter.identifier.value` | string | Prefijo de sede: ej. `V-S2-0101` |
| 11 | Fecha de Atención | PV1-44 / `fecha` | Encounter | `Encounter.period.start` | dateTime | Formato ISO 8601 con zona horaria |
| 12 | Profesional a Cargo | PV1-7 / `profesional` | Encounter / Practitioner | `Encounter.participant.individual` | Reference | Código médico: ej. `MED-01` |
| 13 | Nivel de Triage | `triage` | Encounter | `Encounter.priority.coding.code` | code | Sistema Triage (1 Crítico a 5 No urgente) |
| 14 | Código de Diagnóstico | DG1-3.1 / `dx_local` | Condition | `Condition.code.coding.code` | code | Mapeo vía `ref_terminology` a CIE-10 |
| 15 | Descripción Diagnóstica | DG1-3.2 / Catálogo | Condition | `Condition.code.coding.display` | string | Catálogo oficial OMS / MinSalud |
| 16 | Código Prueba Laboratorio | OBR-4.1 / OBX-3.1 | Observation | `Observation.code.coding.code` | code | Normalización a LOINC (ej. `718-7`) |
| 17 | Nombre Prueba Laboratorio | OBR-4.2 / OBX-3.2 | Observation | `Observation.code.coding.display` | string | ej. Hemoglobina en sangre |
| 18 | Resultado Numérico | OBX-5 | Observation | `Observation.valueQuantity.value` | decimal | Valor numérico medido (ej. `13.8`) |
| 19 | Unidad de Medida | OBX-6 | Observation | `Observation.valueQuantity.unit` | string | Sistema UCUM (ej. `g/dL`) |
