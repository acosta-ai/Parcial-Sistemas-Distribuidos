# PLATAFORMA DISTRIBUIDA DE INTEROPERABILIDAD CLÍNICA CON FHIR R4, HEALTH SERVICE BUS (HSB) Y BASE DE DATOS DISTRIBUIDA CITUS

**Autores:** Carlos Andrés Acosta Herrera & Juan David Benítez Ruiz  
**Programa:** Ingeniería de Sistemas – Asignatura: Sistemas Distribuidos  
**Docente:** Ing. Jaider Enrique Reyes Herazo  
**Institución:** Corporación Universitaria Antonio José de Sucre (Sincelejo, Colombia)  
**Fecha:** Noviembre de 2026  

---

## RESUMEN / ABSTRACT
El presente proyecto diseña, implementa y evalúa una plataforma distribuida de interoperabilidad clínica para una red de Instituciones Prestadoras de Salud (IPS) distribuida geográficamente en tres sedes: Sincelejo, Cartagena y Corozal. La problemática central abordada radica en la fragmentación de la historia clínica electrónica y la heterogeneidad sintáctica y semántica de los sistemas de información legados, los cuales operan con bases de datos aisladas y emiten información clínica en formatos dispares (mensajes HL7 v2.5 ADT/ORU y archivos planos CSV/JSON). 

Para solucionar esta desarticulación sin requerir la sustitución forzada de la infraestructura preexistente, se concibió una arquitectura distribuida orientada a servicios basada en un Bus de Integración de Salud (*Health Service Bus* - HSB) implementado con FastAPI, complementado con un motor de normalización canónica al estándar HL7 FHIR Release 4 y un clúster de base de datos distribuida mediante PostgreSQL con extensión Citus. El middleware HSB garantiza tolerancia a fallos parciales mediante colas de reintentos con algoritmo de retroceso exponencial (*exponential backoff*), canalización a cola de mensajes muertos (*Dead Letter Queue* - DLQ) para cargas con discrepancias semánticas, e idempotencia estricta soportada en funciones resumen criptográficas SHA-256. 

La persistencia unificada se logra a través de fragmentación horizontal guiada por el identificador del paciente, permitiendo consultas consolidadas transparentes y transacciones ACID distribuidas. Adicionalmente, se integró un esquema de seguridad basado en control de acceso por roles (RBAC) con tokens JWT y una pista de auditoría encadenada por hashes inmutables inspirada en tecnologías de registro distribuido. La solución demostró capacidad de degradación elegante ante la caída repentina de nodos y una cobertura del 100% en la reconciliación y unificación del expediente clínico electrónico.

---

## INTRODUCCIÓN
En los ecosistemas hospitalarios contemporáneos, la fragmentación de los registros médicos representa uno de los obstáculos más severos para la continuidad asistencial y la toma de decisiones clínicas oportunas. Cada institución hospitalaria tiende a implementar sistemas heterogéneos que almacenan diagnósticos, admisiones y órdenes de laboratorio de manera insular. Cuando un paciente acude a diferentes centros de una misma red regional, los profesionales de la salud carecen de una perspectiva unificada de sus antecedentes, lo cual induce duplicidad de procedimientos, sobrecostos y riesgos significativos para la seguridad del usuario.

En concordancia con el marco normativo colombiano (Ley Estatutaria de Salud 1751/2015, Ley 1581/2012 de Protección de Datos Personales y la Resolución 866/2021 de MinSalud sobre Interoperabilidad de la Historia Clínica Electrónica), se hace imperativa la adopción de estándares internacionales abiertos que posibiliten el intercambio seguro de datos sin vulnerar la soberanía operativa de las sedes. HL7 FHIR (*Fast Healthcare Interoperability Resources*) se posiciona hoy como el estándar canónico de referencia global gracias a su paradigma modular RESTful basado en recursos computacionales.

El presente trabajo expone el desarrollo de una solución integral que conecta tres sedes heterogéneas (Sincelejo, Cartagena y Corozal) mediante la orquestación de un HSB resiliente, bases de datos particionadas con Citus, un servidor canónico HAPI FHIR y cuatro interfaces web adaptadas a los roles de Paciente, Admisionista, Médico y Auditoría de Reporte de Historia Clínica.

---

## OBJETIVOS

### Objetivo General
Desarrollar, desplegar y validar una plataforma distribuida de interoperabilidad clínica que integre el estándar HL7 FHIR R4, un bus de servicios de salud (HSB) resiliente y un motor de base de datos distribuida Citus para consolidar la historia clínica fragmentada entre tres sedes hospitalarias preservando sus sistemas legados.

### Objetivos Específicos
1. **Diseñar e implementar el Health Service Bus (HSB)** dotado de adaptadores para la ingesta de mensajería HL7 v2 (ADT^A01 y ORU^R01) y archivos estructurados legados (CSV/JSON), aplicando validación sintáctica/semántica, idempotencia criptográfica por hash SHA-256 y gestión de colas de reintentos con *Dead Letter Queue*.
2. **Construir el motor de normalización semántica** a recursos canónicos FHIR R4 (`Patient`, `Encounter`, `Observation`, `Condition`) empleando diccionarios controlados CIE-10 para codificación diagnóstica y LOINC para analítica de laboratorio clínico.
3. **Desplegar la capa de datos distribuida** mediante un clúster PostgreSQL/Citus con particionado horizontal orientado por la clave primaria del paciente, demostrando atomicidad y consistencia (ACID) en transacciones distribuidas y consultas unificadas multisede.
4. **Implementar las capas de seguridad, resiliencia y experiencia de usuario** configurando control de acceso RBAC con autenticación JWT, un libro mayor de auditoría encadenado por bloques de hash (SHA-256) y cuatro vistas interactivas con capacidad de degradación elegante ante caídas de nodos en vivo.

---

## MARCO TEÓRICO Y CONCEPTUAL

### 1. Fundamentos de Sistemas Distribuidos y Teorema CAP
Un sistema distribuido es un conjunto de entidades computacionales independientes que se comunican a través de una red compartida y se presentan ante el usuario como un único sistema coordinado (Coulouris et al., 2012). De acuerdo con el Teorema CAP formulado por Eric Brewer, ningún sistema de datos distribuido puede garantizar simultáneamente Consistencia estricta (C), Alta Disponibilidad (A) y Tolerancia a Particiones de red (P). 

En el ámbito de la salud crítica, la disponibilidad y la tolerancia a particiones son indispensables: si el enlace hacia una sede regional (por ejemplo, Cartagena) experimenta una interrupción transitoria, el sistema unificado en Sincelejo debe continuar prestando servicio con degradación elegante (*graceful degradation*), informando de forma explícita al facultativo que la sede remota se encuentra temporalmente inaccesible sin bloquear la consulta de los registros locales disponibles (Consistencia Eventual controlada).

### 2. Estándares de Interoperabilidad en Salud: HL7 v2 vs. HL7 FHIR
- **HL7 versión 2.x:** Estándar de mensajería clínica orientado a eventos basado en delimitadores de caracteres (`|`, `^`, `~`). Mensajes como ADT^A01 (Admisión/Alta de Pacientes) y ORU^R01 (Observaciones y Reportes de Laboratorio) continúan siendo predominantes en sistemas legados hospitalarios por su ligereza y madurez histórica.
- **HL7 FHIR R4:** Estándar de interoperabilidad de última generación desarrollado por HL7 International. Modela la información médica en componentes discretos denominados *Recursos* (`Patient`, `Encounter`, `Observation`, `Condition`, `Bundle`), accesibles a través de especificaciones RESTful en formato JSON/XML y enriquecidos con extensiones semánticas rigurosas.

### 3. Bus de Servicios de Salud (HSB) y Patrones de Integración
El HSB (*Health Service Bus*) constituye la capa de mediación que desacopla a los emisores de los receptores clínicos. Implementa patrones fundamentales de integración empresarial (EIP):
- **Idempotencia:** Capacidad de una operación de ejecutarse múltiples veces consecutivas produciendo exactamente el mismo efecto que una única invocación. En el HSB, se computa una huella SHA-256 del contenido crudo; transmisiones duplicadas son detectadas y confirmadas con código 200 OK sin generar registros espurios en la base de datos.
- **Cola de Reintentos con Retroceso Exponencial:** Frente a fallos transitorios en el servidor FHIR de destino, el mensaje es encolado y reexpedido en intervalos crecientes ($t = base \cdot 2^{intento}$).
- **Dead Letter Queue (DLQ):** Repositorio de mensajes descartados donde se confinan aquellas cargas cuya estructura sintáctica es anómala o cuyos diagnósticos locales carecen de correspondencia en el catálogo maestro.

### 4. Bases de Datos Distribuidas y Citus
Citus es una extensión de código abierto para PostgreSQL que transforma a una instancia individual en una base de datos relacional distribuida. Utiliza el particionado basado en tablas distribuidas (*distributed tables*), donde una clave de partición uniforme (en este proyecto, `patient_id` / `documento_id`) distribuye los registros entre los nodos de trabajo (*workers*). El nodo coordinador traduce las consultas SQL estándar en planes de ejecución distribuidos paralelos, asegurando cumplimiento de propiedades ACID completas en transacciones locales al shard.
