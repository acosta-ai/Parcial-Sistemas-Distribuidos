# PLATAFORMA DISTRIBUIDA DE INTEROPERABILIDAD CLÃNICA CON FHIR R4, HEALTH SERVICE BUS (HSB) Y BASE DE DATOS DISTRIBUIDA CITUS

**Autores:** Carlos AndrÃ©s Acosta Herrera & Juan David BenÃ­tez Ruiz  
**Programa:** IngenierÃ­a de Sistemas â€“ Asignatura: Sistemas Distribuidos  
**Docente:** Ing. Jaider Enrique Reyes Herazo  
**InstituciÃ³n:** CorporaciÃ³n Universitaria Antonio JosÃ© de Sucre (Sincelejo, Colombia)  
**Fecha:** Noviembre de 2026  

---

## 1. PORTADA Y DATOS GENERALES DEL PROYECTO

| Campo | Detalle Institucional y AcadÃ©mico |
| :--- | :--- |
| **TÃ­tulo del Proyecto** | Plataforma Distribuida de Interoperabilidad ClÃ­nica con FHIR R4, Health Service Bus (HSB) y Base de Datos Distribuida Citus |
| **Autores** | Carlos AndrÃ©s Acosta Herrera & Juan David BenÃ­tez Ruiz |
| **Programa AcadÃ©mico** | IngenierÃ­a de Sistemas |
| **Asignatura** | Sistemas Distribuidos (EvaluaciÃ³n Parcial Final) |
| **Docente Director** | Ing. Jaider Enrique Reyes Herazo |
| **InstituciÃ³n Universitaria** | CorporaciÃ³n Universitaria Antonio JosÃ© de Sucre (Corposucre) |
| **Sede GeogrÃ¡fica** | Sincelejo, Sucre, Colombia |
| **Fecha de PresentaciÃ³n** | Noviembre de 2026 |
| **VersiÃ³n del Documento** | Reporte TÃ©cnico Oficial Final â€“ Parte 1 (Plantilla v7) |

---

## 2. RESUMEN / ABSTRACT

El presente proyecto diseÃ±a, implementa y evalÃºa una plataforma distribuida de interoperabilidad clÃ­nica para una red de Instituciones Prestadoras de Salud (IPS) distribuida geogrÃ¡ficamente en tres sedes: Sincelejo, Cartagena y Corozal. La problemÃ¡tica central abordada radica en la fragmentaciÃ³n de la historia clÃ­nica electrÃ³nica y la heterogeneidad sintÃ¡ctica y semÃ¡ntica de los sistemas de informaciÃ³n legados, los cuales operan con bases de datos aisladas y emiten informaciÃ³n clÃ­nica en formatos dispares (mensajes HL7 v2.5 ADT/ORU y archivos planos CSV/JSON).

Para solucionar esta desarticulaciÃ³n sin requerir la sustituciÃ³n forzada de la infraestructura preexistente, se concibiÃ³ una arquitectura distribuida orientada a servicios basada en un Bus de IntegraciÃ³n de Salud (*Health Service Bus* - HSB) implementado con FastAPI, complementado con un motor de normalizaciÃ³n canÃ³nica al estÃ¡ndar HL7 FHIR Release 4 y un clÃºster de base de datos distribuida mediante PostgreSQL con extensiÃ³n Citus. El middleware HSB garantiza tolerancia a fallos parciales mediante colas de reintentos con algoritmo de retroceso exponencial (*exponential backoff*), canalizaciÃ³n a cola de mensajes muertos (*Dead Letter Queue* - DLQ) para cargas con discrepancias semÃ¡nticas, e idempotencia estricta soportada en funciones resumen criptogrÃ¡ficas SHA-256.

La persistencia unificada se logra a travÃ©s de fragmentaciÃ³n horizontal guiada por el identificador del paciente, permitiendo consultas consolidadas transparentes y transacciones ACID distribuidas. Adicionalmente, se integrÃ³ un esquema de seguridad basado en control de acceso por roles (RBAC) con tokens JWT y una pista de auditorÃ­a encadenada por hashes inmutables inspirada en tecnologÃ­as de registro distribuido. La soluciÃ³n demostrÃ³ capacidad de degradaciÃ³n elegante ante la caÃ­da repentina de nodos y una cobertura del 100% en la reconciliaciÃ³n y unificaciÃ³n del expediente clÃ­nico electrÃ³nico.

---

## 3. INTRODUCCIÃ“N

En los ecosistemas hospitalarios contemporÃ¡neos, la fragmentaciÃ³n de los registros mÃ©dicos representa uno de los obstÃ¡culos mÃ¡s severos para la continuidad asistencial y la toma de decisiones clÃ­nicas oportunas. Cada instituciÃ³n hospitalaria tiende a implementar sistemas heterogÃ©neos que almacenan diagnÃ³sticos, admisiones y Ã³rdenes de laboratorio de manera insular. Cuando un paciente acude a diferentes centros de una misma red regional, los profesionales de la salud carecen de una perspectiva unificada de sus antecedentes, lo cual induce duplicidad de procedimientos, sobrecostos y riesgos significativos para la seguridad del usuario.

En concordancia con el marco normativo colombiano (Ley Estatutaria de Salud 1751/2015, Ley 1581/2012 de ProtecciÃ³n de Datos Personales y la ResoluciÃ³n 866/2021 de MinSalud sobre Interoperabilidad de la Historia ClÃ­nica ElectrÃ³nica), se hace imperativa la adopciÃ³n de estÃ¡ndares internacionales abiertos que posibiliten el intercambio seguro de datos sin vulnerar la soberanÃ­a operativa de las sedes. HL7 FHIR (*Fast Healthcare Interoperability Resources*) se posiciona hoy como el estÃ¡ndar canÃ³nico de referencia global gracias a su paradigma modular RESTful basado en recursos computacionales.

El presente trabajo expone el desarrollo de una soluciÃ³n integral que conecta tres sedes heterogÃ©neas (Sincelejo, Cartagena y Corozal) mediante la orquestaciÃ³n de un HSB resiliente, bases de datos particionadas con Citus, un servidor canÃ³nico HAPI FHIR y cuatro interfaces web adaptadas a los roles de Paciente, Admisionista, MÃ©dico y AuditorÃ­a de Reporte de Historia ClÃ­nica.

---

## 4. OBJETIVOS

### Objetivo General
Desarrollar, desplegar y validar una plataforma distribuida de interoperabilidad clÃ­nica que integre el estÃ¡ndar HL7 FHIR R4, un bus de servicios de salud (HSB) resiliente y un motor de base de datos distribuida Citus para consolidar la historia clÃ­nica fragmentada entre tres sedes hospitalarias preservando sus sistemas legados.

### Objetivos EspecÃ­ficos
1. **DiseÃ±ar e implementar el Health Service Bus (HSB)** dotado de adaptadores para la ingesta de mensajerÃ­a HL7 v2 (`ADT^A01` y `ORU^R01`) y archivos estructurados legados (CSV/JSON), aplicando validaciÃ³n sintÃ¡ctica/semÃ¡ntica, idempotencia criptogrÃ¡fica por hash SHA-256 y gestiÃ³n de colas de reintentos con *Dead Letter Queue* (DLQ).
2. **Construir el motor de normalizaciÃ³n semÃ¡ntica** a recursos canÃ³nicos FHIR R4 (`Patient`, `Encounter`, `Observation`, `Condition`) empleando diccionarios controlados CIE-10 para codificaciÃ³n diagnÃ³stica y LOINC para analÃ­tica de laboratorio clÃ­nico.
3. **Desplegar la capa de datos distribuida** mediante un clÃºster PostgreSQL/Citus con particionado horizontal orientado por la clave primaria del paciente, demostrando atomicidad y consistencia (ACID) en transacciones distribuidas y consultas unificadas multisede.
4. **Implementar las capas de seguridad, resiliencia y experiencia de usuario** configurando control de acceso RBAC con autenticaciÃ³n JWT, un libro mayor de auditorÃ­a encadenado por bloques de hash (SHA-256) y cuatro vistas interactivas con capacidad de degradaciÃ³n elegante ante caÃ­das de nodos en vivo.

---

## 5. MARCO TEÃ“RICO Y CONCEPTUAL

### 5.1 Marco TeÃ³rico

#### 1. Fundamentos de Sistemas Distribuidos y Teorema CAP
Un sistema distribuido se define como una colecciÃ³n de componentes de cÃ³mputo autÃ³nomos interconectados a travÃ©s de un canal de comunicaciones compartido, los cuales se coordinan e interactÃºan mediante paso de mensajes para presentarse ante los usuarios finales como un sistema Ãºnico, cohesivo e integrado (Coulouris et al., 2012). Los retos inherentes a estos entornos radican en la concurrencia de ejecuciones, la ausencia de un reloj global sincrÃ³nico universal y la ocurrencia inevitable de fallos parciales independientes en nodos y enlaces de red.

De acuerdo con el Teorema CAP, postulado inicialmente como conjetura por Eric Brewer (2000, 2012) y demostrado formalmente por Gilbert y Lynch (2002), es teÃ³ricamente imposible que un sistema de almacenamiento distribuido garantice simultÃ¡neamente, bajo una particiÃ³n de red arbitraria ($P$), las siguientes tres propiedades:
- **Consistencia estricta ($C$ - *Consistency*):** Cada operaciÃ³n de lectura refleja inequÃ­vocamente la escritura mÃ¡s reciente en cualquier rÃ©plica del clÃºster (linealizabilidad).
- **Disponibilidad ($A$ - *Availability*):** Cada solicitud no fallida dirigida a un nodo en funcionamiento recibe una respuesta satisfactoria sin error, independientemente del estado de otros nodos.
- **Tolerancia a particiones ($P$ - *Partition Tolerance*):** El sistema continÃºa operando a pesar de la pÃ©rdida o retardo arbitrario de mensajes entre los nodos de la red.

En el contexto de la informÃ¡tica mÃ©dica regional y los entornos clÃ­nicos crÃ­ticos, las fallas en los enlaces de telecomunicaciones entre ciudades geogrÃ¡ficamente distantes (por ejemplo, el enlace WAN entre Sincelejo y Cartagena) constituyen eventos inevitables. Frente a este dilema, la arquitectura propuesta adopta un modelo orientado a la disponibilidad y tolerancia a particiones (paradigma AP con consistencia eventual controlada), complementado con el principio de degradaciÃ³n elegante (*graceful degradation*). 

Bajo este modelo, si la sede Cartagena queda incomunicada temporalmente, el nodo coordinador y el HSB no colapsan ni bloquean las consultas de los facultativos en Sincelejo y Corozal. Por el contrario, el sistema continÃºa despachando las historias clÃ­nicas locales y reporta un estado degradado explÃ­cito (`status: UP, SEDE_CARTAGENA: DOWN, partial_records: true`), garantizando que la atenciÃ³n al paciente nunca se interrumpa por un fallo perimetral.

#### 2. EstÃ¡ndares de Interoperabilidad en Salud: HL7 v2 vs. HL7 FHIR
La interoperabilidad en salud se estructura jerÃ¡rquicamente en cuatro niveles: tÃ©cnico, sintÃ¡ctico, semÃ¡ntico y organizacional (Benson & Grieve, 2021). Para franquear la brecha entre los sistemas heredados y los requerimientos modernos de intercambio interoperable, coexisten dos generaciones tecnolÃ³gicas:

* **HL7 versiÃ³n 2.x (v2.5):** EstÃ¡ndar de mensajerÃ­a clÃ­nica orientado a eventos creado a finales de la dÃ©cada de 1980, basado en una codificaciÃ³n sintÃ¡ctica delimitada por caracteres especiales (plecas `|`, sombreros `^`, tildes `~`). Mensajes canÃ³nicos como `ADT^A01` (*Admission, Discharge, Transfer* - NotificaciÃ³n de admisiÃ³n hospitalaria) y `ORU^R01` (*Observational Report - Unsolicited* - NotificaciÃ³n de resultados paraclÃ­nicos y analÃ­tica de laboratorio) predominan ampliamente en los sistemas legados hospitalarios de Colombia y AmÃ©rica Latina. Su principal debilidad radica en la proliferaciÃ³n de segmentos personalizados (*Z-segments*) y la carencia de reglas semÃ¡nticas universales obligatorias, derivando en dialectos propietarios difÃ­ciles de consolidar sin intermediaciÃ³n.

* **HL7 FHIR Release 4 (R4):** EstÃ¡ndar abierto concebido por HL7 International que redefine la interoperabilidad a travÃ©s del paradigma RESTful y la modularizaciÃ³n en componentes modulares e independientes llamados *Recursos FHIR*. Cada recurso posee una definiciÃ³n esquemÃ¡tica estricta en formatos JSON o XML, vinculaciÃ³n formal con ontologÃ­as mÃ©dicas globales y soporte para extensiones estandarizadas bajo la regla del 80/20 (HL7 International, 2019; Mandel et al., 2016). La Release 4 es la primera versiÃ³n con especificaciones normativas estables, adoptada formalmente como estÃ¡ndar de interoperabilidad de referencia por los principales organismos rectores de la salud a nivel mundial.

#### 3. Bus de Servicios de Salud (HSB) y Patrones de IntegraciÃ³n Empresarial
El *Health Service Bus* (HSB) actÃºa como la capa de mediaciÃ³n y orquestaciÃ³n distribuida encargada de desacoplar los sistemas hospitalarios de origen de los consumidores finales de informaciÃ³n clÃ­nica. Siguiendo los patrones clÃ¡sicos de integraciÃ³n empresarial (*Enterprise Integration Patterns* - EIP) descritos por Hohpe y Woolf (2003), el HSB resuelve la disparidad de protocolos mediante tres componentes esenciales de resiliencia:

* **Filtro de Idempotencia CriptogrÃ¡fica (*Idempotent Receiver*):** En redes hospitalarias inestables, los sistemas emisores suelen retransmitir mensajes ante la falta de una confirmaciÃ³n (*ACK*) inmediata. El HSB computa un resumen hash criptogrÃ¡fico SHA-256 de la carga cruda entrante y verifica su persistencia en una tabla de control de transacciones (`hsb_idempotency_keys`). Si el mensaje ya fue ingerido, el bus evita la duplicidad en la base de datos distribuida y retorna una respuesta idempotente exitosa (HTTP 200 OK), blindando al expediente clÃ­nico de admisiones o registros redundantes.

* **Cola de Reintentos con Retroceso Exponencial (*Exponential Backoff*):** Frente a caÃ­das transitorias de conectividad hacia el servidor canÃ³nico FHIR, el HSB encola el mensaje y ejecuta reintentos automÃ¡ticos espaciados mediante una progresiÃ³n temporal geomÃ©trica definida por:
  
  $$t_{\text{espera}} = t_{\text{base}} \times 2^{\text{intento}} \pm \Delta_{\text{jitter}}$$

  Este algoritmo previene el efecto de tormenta de peticiones (*thundering herd problem*) sobre servicios en fase de recuperaciÃ³n.

* **Cola de Mensajes Muertos (*Dead Letter Queue* - DLQ):** Aquellos mensajes con malformaciones sintÃ¡cticas irrecuperables, errores en la estructura de segmentos o cÃ³digos diagnÃ³sticos no identificados en los catÃ¡logos maestros son desviados automÃ¡ticamente a un repositorio de fallos (DLQ). Esto previene el bloqueo de la tuberÃ­a de ingesta y preserva el mensaje original con metadatos de error para posterior auditorÃ­a y reprocesamiento tÃ©cnico.

#### 4. Bases de Datos Distribuidas y Citus
Una base de datos distribuida administra una colecciÃ³n de datos lÃ³gicamente unificados que se encuentran repartidos fÃ­sicamente en mÃºltiples nodos de una red informÃ¡tica. A diferencia de un enfoque centralizado susceptible a cuellos de botella de hardware y puntos Ãºnicos de fallo (*Single Point of Failure* - SPoF), el particionado horizontal (*sharding*) divide las tablas relacionales en fragmentos distribuidos (*shards*) asignados a diferentes instancias computacionales (Ã–zsu & Valduriez, 2020).

Citus es una extensiÃ³n distribuida de cÃ³digo abierto para PostgreSQL que transforma instancias relacionales convencionales en una arquitectura escalable de procesamiento distribuido. Citus opera mediante una topologÃ­a conformada por un *Nodo Coordinador* y un conjunto de *Nodos Trabajadores* (*Workers*):
* **Tablas Distribuidas (*Distributed Tables*):** Mediante la instrucciÃ³n `create_distributed_table(nombre_tabla, clave_particion)`, las tuplas son asignadas a shards mediante funciones de dispersiÃ³n (*hash sharding*). En este proyecto, la clave primaria de particionado corresponde al identificador del paciente (`patient_id`), garantizando que toda la informaciÃ³n clÃ­nica de un paciente (encuentros, diagnÃ³sticos, observaciones) resida en el mismo shard o nodo de trabajo (*co-location*).
* **Transacciones ACID Distribuidas:** El coordinador traduce consultas declarativas SQL en Ã¡rboles de ejecuciÃ³n distribuidos paralelos, gestionando la concurrencia y asegurando atomicidad, consistencia, aislamiento y durabilidad (ACID) mediante protocolos de confirmaciÃ³n en dos fases (*Two-Phase Commit* - 2PC) para escrituras que abarcan mÃºltiples fragmentos.

---

### 5.2 Marco Conceptual

El diseÃ±o arquitectÃ³nico de la plataforma de interoperabilidad integra de forma sinÃ©rgica una serie de conceptos clave en informÃ¡tica mÃ©dica y sistemas distribuidos, cuya articulaciÃ³n funcional se describe a continuaciÃ³n:

* **Recurso FHIR:** Constituye la unidad atÃ³mica mÃ­nima de informaciÃ³n asistencial en el estÃ¡ndar FHIR R4. Cada recurso modela un concepto clÃ­nico, administrativo o financiero concreto con semÃ¡ntica formalizada. En esta plataforma se implementan cuatro recursos nucleares: `Patient` (datos demogrÃ¡ficos e identificaciÃ³n inequÃ­voca del paciente), `Encounter` (admisiÃ³n y estancia asistencial en una sede), `Observation` (resultados de constantes vitales o parÃ¡metros analÃ­ticos de laboratorio) y `Condition` (problemas de salud o diagnÃ³sticos mÃ©dicos confirmados).
* **Perfil FHIR (*FHIR Profile*):** Representa un conjunto formal de restricciones, reglas de cardinalidad y extensiones aplicadas sobre un recurso base para adaptar el estÃ¡ndar genÃ©rico a los requisitos legales y operativos locales. En el proyecto, se configuran perfiles adaptados a Colombia, exigiendo como identificadores obligatorios el tipo de documento (CC, TI, RC, CE) y el nÃºmero de cÃ©dula nacional.
* **Bundle Transaction:** Es un contenedor compuesto que agrupa mÃºltiples operaciones FHIR en un Ãºnico documento de intercambio. Mediante el tipo `transaction`, el HSB envÃ­a conjuntos de recursos correlacionados (un `Patient` acompaÃ±ado de su `Encounter` y su `Condition`) al servidor canÃ³nico HAPI FHIR para que sean procesados de forma indivisible: si un recurso dentro del paquete falla, toda la transacciÃ³n se revierte, asegurando la integridad semÃ¡ntica del expediente.
* **TerminologÃ­a Controlada:** Conjunto de vocabularios, ontologÃ­as y diccionarios estandarizados que neutralizan la ambigÃ¼edad semÃ¡ntica derivada del uso de descripciones locales o dialectos mÃ©dicos particulares. La plataforma articula la ClasificaciÃ³n Internacional de Enfermedades dÃ©cima revisiÃ³n (**CIE-10**) para normalizar diagnÃ³sticos clÃ­nicos y la taxonomÃ­a **LOINC** (*Logical Observation Identifiers Names and Codes*) para identificar de forma inequÃ­voca las pruebas y parÃ¡metros de laboratorio.
* **API RESTful:** Estilo de diseÃ±o arquitectÃ³nico orientado a servicios web sin estado (*stateless*), que utiliza los verbos estÃ¡ndar del protocolo HTTP (`GET`, `POST`, `PUT`, `DELETE`) para ejecutar operaciones de creaciÃ³n, lectura, actualizaciÃ³n y borrado sobre URIs que representan recursos clÃ­nicos en formato estructurado JSON.
* **Particionado Horizontal (*Sharding*):** Estrategia de fragmentaciÃ³n fÃ­sica de datos en la cual los registros de una tabla se diseminan entre mÃºltiples nodos del clÃºster Citus tomando como pivote la clave de distribuciÃ³n (`patient_id`). Esto optimiza la escalabilidad del sistema y asegura que las consultas asistenciales de un paciente especÃ­fico se resuelvan con un costo de entrada/salida mÃ­nimo en un Ãºnico nodo trabajador.
* **Idempotencia:** Propiedad esencial de los servicios distribuidos segÃºn la cual una misma invocaciÃ³n, ejecutada de manera simple o mÃºltiple con los mismos parÃ¡metros de entrada, genera idÃ©ntico estado en el sistema receptor sin desencadenar efectos colaterales adversos ni duplicaciones indeseadas de registros mÃ©dicos.
* **Dead Letter Queue (DLQ):** Mecanismo asÃ­ncrono de confinamiento que recibe y almacena de forma segura aquellos mensajes que sufrieron fallos persistentes de procesamiento o rechazos de validaciÃ³n sintÃ¡ctica/semÃ¡ntica, permitiendo aislar la anomalÃ­a sin interrumpir el flujo continuo de transacciones legÃ­timas del HSB.

#### ArticulaciÃ³n de Conceptos en la SoluciÃ³n
Estos conceptos interactÃºan en un flujo armÃ³nico: los sistemas legados emiten mensajes heterogÃ©neos que son interceptados por el HSB, donde se valida su **idempotencia** mediante hashes criptogrÃ¡ficos. Los datos vÃ¡lidos son transformados en **Recursos FHIR** restringidos por **Perfiles** nacionales y enriquecidos semÃ¡nticamente mediante **TerminologÃ­a controlada** (CIE-10/LOINC). Posteriormente, estos recursos se empaquetan en un **Bundle Transaction** atÃ³mico enviado a travÃ©s de la **API RESTful** al servidor canÃ³nico, al tiempo que se persisten relacionalmente en tablas con **Particionado Horizontal** en el clÃºster Citus. Si el mensaje presenta fallas semÃ¡nticas insubsanables, es desviado a la **Dead Letter Queue**, garantizando la robustez operativa de toda la red asistencial.

---

## 6. ESTADO DEL ARTE

El desarrollo de plataformas distribuidas para la interoperabilidad en salud ha sido objeto de profunda investigaciÃ³n y despliegue a escala global, regional y nacional. Analizar crÃ­ticamente el estado actual de la disciplina permite situar el presente proyecto en el panorama cientÃ­fico-tecnolÃ³gico y evidenciar las brechas de implementaciÃ³n que este resuelve.

### 1. A Nivel Global
En el Ã¡mbito internacional, los marcos de interoperabilidad han evolucionado desde arquitecturas monolÃ­ticas de intercambio de documentos hacia ecosistemas abiertos basados en interfaces de programaciÃ³n de aplicaciones orientadas a servicios clÃ­nicos. 

Uno de los referentes arquitectÃ³nicos mÃ¡s relevantes es el marco **OpenHIE** (*Open Health Information Exchange*), concebido como una arquitectura de referencia para paÃ­ses de ingresos medios y bajos. OpenHIE propone una separaciÃ³n estricta de componentes mediante un mediador de informaciÃ³n en salud (*Health Information Mediator* - HIM), un registro maestro de pacientes (*Master Patient Index* - MPI) y un repositorio clÃ­nico centralizado (OpenHIE, 2020). 

En Estados Unidos, la promulgaciÃ³n de la ley *21st Century Cures Act* impulsÃ³ la adopciÃ³n obligatoria de la guÃ­a de implementaciÃ³n **US Core FHIR Implementation Guide**, respaldada por la Oficina del Coordinador Nacional de TI para la Salud (ONC). Este marco obliga a los proveedores de registros de salud electrÃ³nicos (EHR) a exponer APIs FHIR estandarizadas y seguras basadas en el protocolo SMART on FHIR, permitiendo que aplicaciones de terceros accedan a informaciÃ³n clÃ­nica atÃ³mica sin intermediaciÃ³n de formatos cerrados (Mandel et al., 2016).

En Europa destacan el sistema **NHS Spine** en el Reino Unido, el cual gestiona mÃ¡s de mil millones de transacciones de mensajerÃ­a clÃ­nica al mes y se encuentra en una fase intensiva de migraciÃ³n desde los estÃ¡ndares HL7 v3 hacia especificaciones HL7 FHIR RESTful, y la plataforma **X-Road** en Estonia. Esta Ãºltima implementa una red distribuida gubernamental de intercambio de datos sobre registros de salud con cifrado asimÃ©trico y sellado de tiempo criptogrÃ¡fico inmutable, convirtiÃ©ndose en el estÃ¡ndar de oro de soberanÃ­a de datos e interoperabilidad interinstitucional (Benson & Grieve, 2021).

### 2. A Nivel Regional (LatinoamÃ©rica)
En AmÃ©rica Latina, la interoperabilidad clÃ­nica ha ganado tracciÃ³n como pilar de las agendas de transformaciÃ³n digital en salud, si bien con velocidades dispares de madurez tecnolÃ³gica:

* **Brasil:** A travÃ©s de la *Rede Nacional de Dados em SaÃºde* (RNDS), liderada por el Departamento de InformÃ¡tica del SUS (DATASUS), Brasil desplegÃ³ una infraestructura pÃºblica en la nube basada exclusivamente en HL7 FHIR R4 para articular los niveles de atenciÃ³n primaria, secundaria y terciaria. La RNDS unifica registros de vacunaciÃ³n, exÃ¡menes de laboratorio y contactos asistenciales a escala continental, sirviendo de referencia de escalabilidad para la regiÃ³n.
* **Chile:** Mediante el Departamento de EstadÃ­sticas e InformaciÃ³n de Salud (DEIS) y la filial HL7 Chile, ha establecido guÃ­as de interoperabilidad para la receta mÃ©dica electrÃ³nica interoperable y el seguimiento nacional de medicamentos, basÃ¡ndose en recursos canÃ³nicos FHIR `MedicationRequest` y sistemas de identificaciÃ³n de prestadores.
* **Argentina:** A travÃ©s de la Estrategia Nacional de Salud Digital, el Ministerio de Salud argentino impulsÃ³ la creaciÃ³n de un dominio federal de interoperabilidad fundamentado en la adopciÃ³n obligatoria de **SNOMED CT** como estÃ¡ndar canÃ³nico de terminologÃ­a clÃ­nica y la federaciÃ³n de registros mediante perfiles locales de FHIR R4, integrando un servidor terminolÃ³gico nacional de libre acceso.

### 3. A Nivel Nacional (Colombia)
En Colombia, el contexto normativo e informÃ¡tico se encuentra condicionado por la **Ley Estatutaria de Salud 1751 de 2015**, la **Ley 1581 de 2012** sobre rÃ©gimen de protecciÃ³n de datos personales (*Habeas Data*) y, fundamentalmente, la **ResoluciÃ³n 866 de 2021** expedida por el Ministerio de Salud y ProtecciÃ³n Social. Esta resoluciÃ³n formaliza los lineamientos de intercambio de datos clÃ­nicos y establece el Conjunto de Elementos de Datos ClÃ­nicos Relevantes para la Interoperabilidad de la Historia ClÃ­nica ElectrÃ³nica (IHCE).

A nivel estatal coexisten plataformas sectoriales como el **SISPRO** (Sistema Integral de InformaciÃ³n de la ProtecciÃ³n Social) y el aplicativo **MIPRES** para la prescripciÃ³n de tecnologÃ­as en salud no financiadas con la UPC. No obstante, en la prÃ¡ctica clÃ­nica diaria de las Instituciones Prestadoras de Salud (IPS) colombianas â€”particularmente en redes hospitalarias regionales como las de la RegiÃ³n Caribeâ€”, persiste un panorama de acusada fragmentaciÃ³n tecnolÃ³gica. MÃ¡s del 85% de las IPS operan con sistemas de informaciÃ³n hospitalaria (*Hospital Information Systems* - HIS) legados desarrollados sobre motores de bases de datos relacionales tradicionales (MySQL, PostgreSQL, SQL Server o SQLite), cuyos esquemas son disÃ­miles, no intercambian datos entre sÃ­ de manera nativa y carecen de interfaces API normalizadas.

### 4. Brechas Identificadas y Oportunidades Abordadas por el Proyecto
De la revisiÃ³n del estado del arte se desprenden tres brechas crÃ­ticas no resueltas por las soluciones convencionales en el contexto regional:

1. **Predominio del intercambio documental sobre la granularidad de recursos:** La inmensa mayorÃ­a de implementaciones en Colombia y LatinoamÃ©rica se limitan al intercambio de documentos no estructurados (archivos PDF protegidos) o arquitecturas CDA (*Clinical Document Architecture*) de HL7 v3. Esto impide la reconciliaciÃ³n analÃ­tica y computacional de datos atÃ³micos (como curvas de glicemia o tendencias de presiÃ³n arterial) provenientes de diferentes sedes.
2. **Carencia de persistencia distribuida nativa orientada a FHIR:** Los servidores FHIR canÃ³nicos (como HAPI FHIR) suelen desplegarse sobre bases de datos monolÃ­ticas centralizadas, generando riesgos severos de latencia de red WAN y cuellos de botella de concurrencia ante un nÃºmero masivo de transacciones. Son casi inexistentes los desarrollos acadÃ©micos y prÃ¡cticos que integren la normalizaciÃ³n FHIR con motores de bases de datos relacionales distribuidas basadas en *sharding* horizontal nativo (PostgreSQL/Citus).
3. **Ausencia de middlewares de integraciÃ³n ligeros adaptados a sistemas heterogÃ©neos legados:** Las IPS de municipios medianos (como Sincelejo y Corozal) no cuentan con el presupuesto ni el soporte tÃ©cnico para reemplazar sus sistemas legados o adquirir buses de integraciÃ³n comerciales corporativos de alto coste (como IBM Integration Bus o MuleSoft). Existe una brecha evidente para un Bus de Servicios de Salud (*Health Service Bus* - HSB) ligero, de cÃ³digo abierto, tolerante a fallos, con colas de reintentos exponenciales, verificaciÃ³n de idempotencia y canalizaciÃ³n de mensajes anÃ³malos a DLQ.

El presente proyecto llena directamente este vacÃ­o al proponer, desplegar y validar una plataforma integral que une un HSB Ã¡gil basado en FastAPI, normalizaciÃ³n semÃ¡ntica canÃ³nica FHIR R4, tolerancia a particiones con degradaciÃ³n elegante y particionado distribuido mediante Citus para tres sedes hospitalarias de la regiÃ³n caribe colombiana.

---

## 7. REFERENCIAS BIBLIOGRÃFICAS (FORMATO APA 7)

* Benson, T., & Grieve, G. (2021). *Principles of Health Interoperability: FHIR, HL7, SNOMED, DICOM, and ISO 13606* (4th ed.). Springer International Publishing. https://doi.org/10.1007/978-3-030-56883-2
* Brewer, E. (2012). CAP twelve years later: How the "rules" have changed. *Computer*, 45(2), 23-29. https://doi.org/10.1109/MC.2012.37
* Congreso de la RepÃºblica de Colombia. (2012). *Ley 1581 de 2012: Por la cual se dictan disposiciones generales para la protecciÃ³n de datos personales*. Diario Oficial No. 48.587.
* Congreso de la RepÃºblica de Colombia. (2015). *Ley Estatutaria 1751 de 2015: Por medio de la cual se regula el derecho fundamental a la salud y se dictan otras disposiciones*. Diario Oficial No. 49.427.
* Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). *Distributed Systems: Concepts and Design* (5th ed.). Addison-Wesley.
* Gilbert, S., & Lynch, N. (2002). Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services. *ACM SIGACT News*, 33(2), 51-59. https://doi.org/10.1145/564585.564601
* HL7 International. (2019). *Fast Healthcare Interoperability Resources (FHIR) Release 4 (v4.0.1)*. Health Level Seven International. https://hl7.org/fhir/R4/
* Hohpe, G., & Woolf, B. (2003). *Enterprise Integration Patterns: Designing, Building, and Deploying Messaging Solutions*. Addison-Wesley Professional.
* Mandel, J. C., Kreda, D. A., Mandl, K. D., Kohane, I. S., & Ramoni, R. B. (2016). SMART on FHIR: a standards-based, interoperable apps platform for electronic health records. *Journal of the American Medical Informatics Association*, 23(5), 899-908. https://doi.org/10.1093/jamia/ocv189
* Ministerio de Salud y ProtecciÃ³n Social de Colombia. (2021). *ResoluciÃ³n 866 de 2021: Por la cual se reglamenta el conjunto de elementos de datos clÃ­nicos relevantes para la interoperabilidad de la historia clÃ­nica*. MinSalud.
* OpenHIE. (2020). *Open Health Information Exchange Architecture Specification*. OpenHIE Community. https://ohie.org/architecture-specification/
* Ã–zsu, M. T., & Valduriez, P. (2020). *Principles of Distributed Database Systems* (4th ed.). Springer Cham. https://doi.org/10.1007/978-3-030-26253-2
# DOCUMENTO FINAL - PARTE 2: DISEÃ‘O, IMPLEMENTACIÃ“N Y VALIDACIÃ“N DEL SISTEMA DISTRIBUIDO

---

## SECCIÃ“N 7: SOLUCIÃ“N PROPUESTA Y METODOLOGÃA

### 7.1 Arquitectura de la SoluciÃ³n

Para superar las barreras de fragmentaciÃ³n, heterogeneidad sintÃ¡ctica y falta de interoperabilidad semÃ¡ntica que histÃ³ricamente han afectado la gestiÃ³n de historias clÃ­nicas en redes hospitalarias multisede, se diseÃ±Ã³ e implementÃ³ una arquitectura distribuida orientada a servicios y eventos estructurada en cuatro capas desacopladas. Esta configuraciÃ³n garantiza alta disponibilidad, consistencia eventual, tolerancia a particiones de red y cumplimiento estricto del estÃ¡ndar internacional HL7 FHIR R4 (*Fast Healthcare Interoperability Resources*).

```
+---------------------------------------------------------------------------------------+
| CAPA 4: PRESENTACIÃ“N CLÃNICA Y MONITOREO (HTML5 / Bootstrap 5 / JavaScript AsÃ­ncrono) |
|   - Portal Paciente      - Consola AdmisiÃ³n      - EstaciÃ³n MÃ©dica      - Dashboard   |
+---------------------------------------------------------------------------------------+
                                           â”‚ (HTTP REST / JSON / JWT)
                                           â–¼
+---------------------------------------------------------------------------------------+
| CAPA 2: MIDDLEWARE DE INTEGRACIÃ“N (Health Service Bus - HSB / FastAPI / Puerto 8000)  |
|   - Adaptadores HL7 v2 / CSV           - Motor de NormalizaciÃ³n CanÃ³nica FHIR R4      |
|   - Filtro de Idempotencia (SHA-256)   - Cola de Reintentos (Backoff Exponencial)     |
|   - Mapeo TerminolÃ³gico (CIE-10/LOINC) - Cola de Mensajes Muertos (Dead Letter Queue) |
+---------------------------------------------------------------------------------------+
               â”‚                                                    â”‚
               â–¼                                                    â–¼
+-----------------------------------------------+   +-----------------------------------+
| CAPA 1: FUENTES DE DATOS LEGADAS (HIS Sedes)  |   | CAPA 3: PERSISTENCIA DISTRIBUIDA  |
|   - Sede Sincelejo (PostgreSQL :5433)         |   |   - Citus Master (:5432) + Workers|
|   - Sede Cartagena (PostgreSQL :5434)         |   |   - HAPI FHIR JPA Server (:8080)  |
|   - Sede Corozal   (PostgreSQL :5435)         |   |   - Hash-Chain Audit Trail        |
+-----------------------------------------------+   +-----------------------------------+
```

#### Capa 1: Fuentes de Datos HeterogÃ©neas y Sistemas Legados (HIS)
Representa los Sistemas de InformaciÃ³n Hospitalaria (*Hospital Information Systems* - HIS) preexistentes y autÃ³nomos de cada sede asistencial. Se simulan mediante tres instancias aisladas de bases de datos relacionales PostgreSQL que ejecutan en puertos dedicados:
- **Sede Sincelejo (Puerto 5433):** gestiona registros de urgencias y admisiones en esquemas tabulares departamentales.
- **Sede Cartagena (Puerto 5434):** almacena consultas ambulatorias y hospitalizaciÃ³n.
- **Sede Corozal (Puerto 5435):** custodia datos de atenciÃ³n mÃ©dica perifÃ©rica y diagnÃ³sticos locales.

Estas fuentes emulan el escenario real de divergencia de esquemas, permitiendo inyectar informaciÃ³n tanto en formatos tabulares delimitados por comas (CSV) como en tramas semiestructuradas HL7 versiÃ³n 2.x (mensajes `ADT^A01` de admisiÃ³n y `ORU^R01` de observaciÃ³n mÃ©dica).

#### Capa 2: Middleware de IntegraciÃ³n e Interoperabilidad (Health Service Bus - HSB)
Constituye el nÃºcleo del sistema distribuido y actÃºa como orquestador centralizado de la interoperabilidad. Desarrollado sobre el microframework asÃ­ncrono **FastAPI** (Python 3.9) y servido mediante **Uvicorn** en el puerto 8000, el HSB integra los siguientes submÃ³dulos funcionales:
- **Adaptadores de Ingesta:** procesadores especializados capaces de decodificar flujos sintÃ¡cticos HL7 v2 (parsing de segmentos `MSH`, `PID`, `PV1`, `DG1`) y streams de archivos CSV.
- **Motor de ValidaciÃ³n de Integridad:** verifica la completitud estructural de los datos, el formato de identificadores y las restricciones de obligatoriedad segÃºn la normativa colombiana de salud.
- **Filtro CriptogrÃ¡fico de Idempotencia:** calcula de forma unÃ­voca el hash SHA-256 del contenido crudo de cada mensaje recibido. Si una firma idÃ©ntica ya fue procesada, el mensaje se confirma sin duplicar registros en las capas subyacentes, mitigando anomalÃ­as por retransmisiÃ³n.
- **Servicio de Mapeo TerminolÃ³gico:** homogeneiza vocabularios dispares y cÃ³digos locales hacia catÃ¡logos clÃ­nicos universales, principalmente la ClasificaciÃ³n Internacional de Enfermedades (CIE-10) y la codificaciÃ³n de gÃ©nero y estado clÃ­nico bajo especificaciones FHIR.
- **Normalizador CanÃ³nico FHIR R4:** transforma las estructuras heterogÃ©neas en recursos canÃ³nicos interoperables (`Patient`, `Encounter`, `Condition`, `Observation`) empaquetados en un contenedor unificado de tipo `Bundle` transaccional.
- **Manejo Resiliente de Fallos y Despacho:** incorpora una cola de reintentos con algoritmo de retroceso exponencial (*exponential backoff* en intervalos de 1s, 2s y 4s) para amortiguar indisponibilidades transitorias en los repositorios finales, canalizando a una Cola de Mensajes Muertos (*Dead Letter Queue* - DLQ) aquellas solicitudes no procesables para prevenir bloqueos en cascada.

#### Capa 3: Persistencia Distribuida y AlmacÃ©n CanÃ³nico FHIR
Provee el soporte de almacenamiento elÃ¡stico, tolerante a particiones y con capacidad de consulta consolidada e histÃ³rica:
- **ClÃºster Distribuido Citus (PostgreSQL 15 + Citus Data):** compuesto por un nodo coordinador (*Citus Master* en puerto 5432) y dos nodos trabajadores (*Citus Worker 1* y *Citus Worker 2*). Implementa particionamiento horizontal transparente (*sharding*) sobre las entidades clÃ­nicas principales utilizando el campo `patient_id` como clave de distribuciÃ³n unificada. Esto asegura localidad de referencia y consultas federadas con latencia sublineal.
- **Servidor CanÃ³nico HAPI FHIR JPA (Puerto 8080):** implementaciÃ³n estÃ¡ndar certificada desplegada sobre la imagen oficial `hapiproject/hapi:v8.12.0`, que ofrece una API RESTful nativa FHIR R4 para interoperabilidad externa con aseguradoras y organismos de control sanitario.
- **Registro Inmutable de AuditorÃ­a (Hash-Chain Ledger):** mecanismo criptogrÃ¡fico distribuido donde cada transacciÃ³n clÃ­nica se sella mediante un hash encadenado ($H_n = \text{SHA-256}(H_{n-1} \parallel D_n)$), garantizando trazabilidad, integridad y no repudio absoluto de los eventos mÃ©dicos registrados.

#### Capa 4: PresentaciÃ³n ClÃ­nica y Monitoreo Operacional
Interfaz de usuario web reactiva y ligera construida sobre estÃ¡ndares HTML5, CSS3, JavaScript asÃ­ncrono y el framework responsivo **Bootstrap 5**. Provee cuatro consolas de trabajo segÃºn el perfil de operaciÃ³n:
1. *Portal del Paciente:* consulta unificada y longitudinal de antecedentes mÃ©dicos multi-sede y descarga de *Bundles* FHIR en JSON.
2. *Consola del Admisionista:* registro de ingresos, priorizaciÃ³n de triage (niveles 1 al 5) y asignaciÃ³n a sede.
3. *EstaciÃ³n de Trabajo MÃ©dica:* registro y codificaciÃ³n de diagnÃ³sticos CIE-10 con firma criptogrÃ¡fica de auditorÃ­a.
4. *Panel de Monitoreo y TelemetrÃ­a:* supervisiÃ³n de latencias promedio, volumen de mensajes procesados, estado de salud de los nodos y auditorÃ­a de mensajes en DLQ.

---

### 7.2 TecnologÃ­as Empleadas

El diseÃ±o tÃ©cnico se sustentÃ³ en tecnologÃ­as de cÃ³digo abierto de nivel empresarial, privilegiando el rendimiento asÃ­ncrono, la escalabilidad horizontal y la compatibilidad con estÃ¡ndares abiertos:

| Componente / DimensiÃ³n | TecnologÃ­a Seleccionada | VersiÃ³n / Detalle TÃ©cnico | JustificaciÃ³n Arquitectural |
| :--- | :--- | :--- | :--- |
| **Sistema Operativo Base** | CentOS Stream 9 | Kernel Linux x86_64 en VirtualBox | Entorno de servidor empresarial estable, seguro y optimizado para virtualizaciÃ³n contenerizada. |
| **ContenerizaciÃ³n y Red** | Docker CE & Docker Compose | Docker v29.9.3 / Compose v5.7.0 | Aislamiento modular de microservicios, reproducibilidad de entorno y orquestaciÃ³n de red puente (*bridge*). |
| **Backend & Servidor ASGI** | Python & FastAPI / Uvicorn | Python 3.9 / FastAPI 0.104+ | Arquitectura asÃ­ncrona de alto rendimiento (`async`/`await`), auto-documentaciÃ³n OpenAPI y bajo consumo de memoria. |
| **Base de Datos Distribuida**| PostgreSQL + Citus Extension | PostgreSQL 15 / Citus 12.x | Sharding transparente por `patient_id`, escalabilidad horizontal y soporte transaccional ACID distribuido. |
| **Servidor Interoperable FHIR**| HAPI FHIR JPA Server | Imagen `hapiproject/hapi:v8.12.0` | Repositorio canÃ³nico certificado FHIR R4 con motor JPA embebido y soporte de validaciÃ³n de perfiles clÃ­nicos. |
| **Frontend Web** | HTML5, Bootstrap 5, JS Vanilla | Bootstrap v5.3 / ES6 Fetch API | Interfaz accesible, responsiva, sin dependencias complejas y de rÃ¡pida renderizaciÃ³n cliente. |
| **Seguridad & CriptografÃ­a** | PyJWT & CriptografÃ­a Nativa | PyJWT (HS256) / SHA-256 | AutenticaciÃ³n descentralizada stateless, control de acceso RBAC granular y firma encadenada de auditorÃ­a. |
| **Pruebas y Aseguramiento** | Python `unittest` & cURL / Bash | Python Standard Library | VerificaciÃ³n sistemÃ¡tica unitaria de parsers, tests E2E y pruebas de estrÃ©s con inyecciÃ³n de fallos. |

---

### 7.3 MetodologÃ­a de Desarrollo

Se adoptÃ³ una metodologÃ­a de desarrollo **iterativo e incremental** estructurada en cinco fases secuenciales y convergentes, alineadas rigurosamente con los objetivos pedagÃ³gicos y la rÃºbrica de evaluaciÃ³n de la cÃ¡tedra de Sistemas Distribuidos:

```mermaid
flowchart LR
    F1["Fase 1: AnÃ¡lisis y Modelado UML"] --> F2["Fase 2: Datos y NormalizaciÃ³n FHIR"]
    F2 --> F3["Fase 3: HSB Middleware y Resiliencia"]
    F3 --> F4["Fase 4: Seguridad, CriptografÃ­a y Fallos"]
    F4 --> F5["Fase 5: UI, IntegraciÃ³n E2E y ValidaciÃ³n"]
```

- **Fase 1: AnÃ¡lisis de Requisitos y DiseÃ±o Formal:** DefiniciÃ³n de requisitos funcionales y no funcionales, modelado estÃ¡tico y dinÃ¡mico mediante lenguaje unificado de modelado (UML) y estructuraciÃ³n de la matriz de correspondencia de campos (mapeo sintÃ¡ctico-semÃ¡ntico de 19 variables clÃ­nicas).
- **Fase 2: Capa de Datos y NormalizaciÃ³n CanÃ³nica:** Despliegue de esquemas heterogÃ©neos en las tres sedes hospitalarias, configuraciÃ³n del clÃºster Citus con tablas distribuidas por `patient_id` y desarrollo de las funciones de transformaciÃ³n de datos a especificaciones FHIR R4.
- **Fase 3: ConstrucciÃ³n del Middleware de IntegraciÃ³n (HSB):** ImplementaciÃ³n de endpoints de ingesta asÃ­ncronos en FastAPI, desarrollo de los parsers de mensajes HL7 v2 y CSV, filtro de idempotencia y algoritmos de reintento progresivo con desvÃ­o a DLQ.
- **Fase 4: Seguridad, AuditorÃ­a CriptogrÃ¡fica y Tolerancia a Fallos:** IncorporaciÃ³n de autenticaciÃ³n JWT y control de acceso basado en roles (RBAC), implementaciÃ³n de la estructura de hash-chain para trazabilidad inmutable y ejecuciÃ³n de pruebas controladas de corte de nodos para validar degradaciÃ³n elegante.
- **Fase 5: Desarrollo de Interfaces de Usuario, IntegraciÃ³n y SustentaciÃ³n:** ConstrucciÃ³n de las cuatro vistas web en Bootstrap 5, ejecuciÃ³n de pruebas de integraciÃ³n extremo a extremo (*End-to-End*), elaboraciÃ³n de la documentaciÃ³n tÃ©cnica y preparaciÃ³n del escenario de demostraciÃ³n en vivo.

---

### 7.4 Roadmap de ImplementaciÃ³n

El cronograma de trabajo se ejecutÃ³ a lo largo de un ciclo continuo de iteraciones de desarrollo, cuyos hitos y entregables se resumen a continuaciÃ³n:

| Fase | Hito / Entregable Principal | Semanas / Sprint | Criterio de AceptaciÃ³n y ValidaciÃ³n |
| :--- | :--- | :--- | :--- |
| **Fase 1** | EspecificaciÃ³n y Diagramas UML | Semana 1 | 4 diagramas UML consolidados y matriz de 19 campos validada. |
| **Fase 2** | Infraestructura de Datos y Normalizador | Semana 2 | ClÃºster Citus operativo, contenedores arriba y 5 pruebas unitarias exitosas. |
| **Fase 3** | NÃºcleo del HSB y TuberÃ­as de Ingesta | Semana 3 | Endpoints `/api/ingest/*` funcionales, idempotencia activa y DLQ operativa. |
| **Fase 4** | Seguridad RBAC, AuditorÃ­a y Resiliencia | Semana 4 | Tokens JWT validados, hash-chain verificable y tolerancia a caÃ­da de sede 2. |
| **Fase 5** | Interfaz Web, Pruebas E2E y Reporte | Semana 5 | 4 vistas web interactivas conectadas a HSB y suite completa de pruebas superada. |

---

## SECCIÃ“N 8: MODELADO UML

Con el propÃ³sito de formalizar el comportamiento estructural, funcional y temporal del sistema distribuido, se diseÃ±aron cuatro modelos bajo el estÃ¡ndar UML, los cuales describen desde las interacciones de los usuarios hasta el ciclo de vida de los mensajes en el bus de integraciÃ³n.

### 8.1 Diagrama de Casos de Uso del Sistema Distribuido

El diagrama de casos de uso delimita las fronteras del sistema, estableciendo las capacidades ofrecidas a los diferentes actores humanos y sistemas externos.

```
       +-------------------------------------------------------------------------+
       |             PLATAFORMA DISTRIBUIDA DE INTEROPERABILIDAD HSB             |
       |                                                                         |
       |   +-----------------------+              +--------------------------+   |
       |   | CU01: Ingerir Mensaje |<<--include---| CU06: Generar Bundle FHIR|   |
       |   +-----------------------+              +--------------------------+   |
       |               ^                                                         |
       |               |                                                         |
       |   +--------------------------+           +--------------------------+   |
       |   | CU02: Validar Identidad  |           | CU05: Registrar CIE-10   |   |
       |   +--------------------------+           +--------------------------+   |
       |                                                                         |
       |   +--------------------------+           +--------------------------+   |
       |   | CU03: Registrar AdmisiÃ³n |           | CU07: Monitorear / DLQ   |   |
       |   +--------------------------+           +--------------------------+   |
       |                                                                         |
       |   +--------------------------+           +--------------------------+   |
       |   | CU04: Consultar HC Unific|           | CU08: Verificar AuditorÃ­a|   |
       |   +--------------------------+           +--------------------------+   |
       +-------------------------------------------------------------------------+
```

El modelo contempla cinco actores claramente diferenciados:
1. **Admisionista:** personal asistencial encargado de registrar el ingreso de pacientes en urgencias o consulta externa, asignar el nivel de triage y canalizar la admisiÃ³n hacia el bus.
2. **MÃ©dico:** profesional clÃ­nico facultado para consultar antecedentes longitudinales, registrar notas de evoluciÃ³n mÃ©dica, prescribir diagnÃ³sticos estructurados bajo la codificaciÃ³n CIE-10 y sellar registros con firma digital.
3. **Paciente:** usuario final y sujeto de atenciÃ³n, habilitado para consultar de forma unificada su historia clÃ­nica a travÃ©s de las distintas sedes asistenciales y descargar su resumen digital en estÃ¡ndar FHIR R4.
4. **Auditor / Administrador de Infraestructura:** perfil tÃ©cnico responsable de inspeccionar las mÃ©tricas de telemetrÃ­a de red, supervisar la cola de mensajes muertos (DLQ) y validar la integridad matemÃ¡tica de la cadena de auditorÃ­a criptogrÃ¡fica (*hash-chain*).
5. **Sistemas Legados (HIS Externos):** sistemas de informaciÃ³n hospitalarios de Sincelejo, Cartagena y Corozal que interactÃºan como actores automatizados enviando cargas por lotes en formatos CSV o mensajes HL7 v2.

Estos actores interactÃºan mediante ocho casos de uso fundamentales:
- **CU01: Ingerir Mensajes ClÃ­nicos HeterogÃ©neos:** captura tramas HL7 v2 y archivos CSV, ejecutando validaciÃ³n estructural e incluyendo obligatoriamente (`<<include>>`) la transformaciÃ³n a recursos FHIR.
- **CU02: Validar Identidad y Datos DemogrÃ¡ficos:** comprueba la unicidad del documento y normaliza identificadores en la red.
- **CU03: Registrar AdmisiÃ³n y AsignaciÃ³n de Triage:** captura variables de ingreso, severidad (niveles 1 a 5) y genera el recurso `Encounter`.
- **CU04: Consultar Historia ClÃ­nica Unificada:** consolida diagnÃ³sticos, atenciones y observaciones registradas en cualquiera de las tres sedes federadas.
- **CU05: Registrar DiagnÃ³stico Codificado CIE-10:** asocia patologÃ­as confirmadas mediante codificaciÃ³n estandarizada y firma el registro clÃ­nico.
- **CU06: Generar y Exportar Bundle FHIR R4:** serializa el expediente longitudinal en una estructura JSON estÃ¡ndar compatible con cualquier repositorio FHIR internacional.
- **CU07: Monitorear MÃ©tricas Operacionales y Cola DLQ:** supervisa volumen, latencias y permite inspeccionar mensajes no procesables.
- **CU08: Verificar Integridad de la Cadena de AuditorÃ­a:** ejecuta la validaciÃ³n algorÃ­tmica de los eslabones SHA-256 para constatar que ningÃºn registro histÃ³rico ha sido adulterado.

```markdown
[Insertar Diagrama de Casos de Uso aquÃ­]
```

---

### 8.2 Diagrama de Secuencias: Ingesta, NormalizaciÃ³n y Despacho de Mensajes

Este diagrama ilustra la orquestaciÃ³n temporal y los flujos de mensajerÃ­a asÃ­ncrona distribuidos que tienen lugar cuando un sistema hospitalario legado transmite un mensaje clÃ­nico (por ejemplo, una admisiÃ³n de urgencias `ADT^A01`) hacia la plataforma:

1. **RecepciÃ³n e Idempotencia:** El sistema cliente despacha una peticiÃ³n HTTP POST con el payload al endpoint `/api/ingest/hl7` del HSB. El bus calcula de inmediato el resumen criptogrÃ¡fico SHA-256 del contenido crudo y consulta la base de firmas previas. Si el hash ya existe, activa el camino alternativo (*Alt: Mensaje Duplicado*), retornando un cÃ³digo 200 OK informando el descarte controlado sin alterar la persistencia.
2. **ValidaciÃ³n SintÃ¡ctica:** Si es inÃ©dito, el motor de parsing valida la presencia de segmentos mandatorios (`MSH`, `PID`, `PV1`). Si la estructura estÃ¡ corrompida (*Alt: Mensaje InvÃ¡lido*), el mensaje se transfiere inmediatamente a la *Dead Letter Queue* (DLQ) para anÃ¡lisis forense y se retorna un cÃ³digo 422 Unprocessable Entity.
3. **Mapeo y NormalizaciÃ³n SemÃ¡ntica:** Con la trama validada, el bus invoca al servicio de mapeo terminolÃ³gico (convirtiendo cÃ³digos locales a CIE-10 y estandarizando el gÃ©nero administrativo), tras lo cual el normalizador ensambla un *Bundle* transaccional FHIR R4 conteniendo los recursos `Patient`, `Encounter` y `Condition`.
4. **Persistencia Distribuida en Citus:** El HSB despacha una inserciÃ³n relacional parametrizada hacia el coordinador Citus, el cual enruta la tupla hacia el *worker* correspondiente aplicando la funciÃ³n de particionamiento sharding sobre la clave `patient_id`.
5. **Despacho a HAPI FHIR y Manejo de Reintentos:** Paralelamente, el HSB intenta entregar el *Bundle* JSON al servidor canÃ³nico HAPI FHIR JPA mediante HTTP POST. En condiciones nominales, HAPI responde con cÃ³digo 201 Created. Si el servicio HAPI FHIR experimenta una caÃ­da o degradaciÃ³n (*Alt: HAPI FHIR No Disponible*), el HSB activa una cola de reintentos con algoritmo de retroceso exponencial (1s, 2s, 4s). Si tras el tercer intento el servicio downstream sigue inalcanzable, la transacciÃ³n se marca para reconciliaciÃ³n en la DLQ sin abortar la persistencia ya asegurada en Citus, garantizando consistencia eventual.
6. **Sellado CriptogrÃ¡fico:** Finalmente, el bus calcula el nuevo eslabÃ³n de auditorÃ­a encadenando el hash previo con la metadata de la transacciÃ³n ($H_n$) y retorna al cliente original una confirmaciÃ³n de procesamiento exitoso con el UUID y la marca temporal asignada.

```markdown
[Insertar Diagrama de Secuencias aquÃ­]
```

---

### 8.3 Diagrama de Clases del Dominio y del Bus de IntegraciÃ³n

El modelo estÃ¡tico describe las diez entidades estructurales que modelan tanto los recursos clÃ­nicos interoperables del estÃ¡ndar FHIR como los componentes internos del middleware distribuido:

```
+---------------------------------------------------------------------------------------+
|                                    MODELO DE CLASES                                   |
|                                                                                       |
|  +--------------------+ 1      0..* +--------------------+ 1      0..* +-----------+  |
|  |      Patient       |------------>|     Encounter      |------------>| Condition |  |
|  +--------------------+             +--------------------+             +-----------+  |
|            ^ 0..*                             | 1                                     |
|            |                                  | 0..*                                  |
|            | 1                                v                                       |
|  +--------------------+             +--------------------+                            |
|  |        Sede        |             |    Observation     |                            |
|  +--------------------+             +--------------------+                            |
|                                                                                       |
|  +--------------------+ 1      0..1 +--------------------+                            |
|  |     HSBMessage     |------------>|     RetryQueue     |                            |
|  +--------------------+             +--------------------+                            |
|     | 1            | 1                                                                |
|     | 0..1         | 0..*                                                             |
|     v              v                                                                  |
|  +------------+  +------------------+  +-------------------+                          |
|  | DeadLetter |  | TerminologyMap   |  |  AuditEventChain  |                          |
|  +------------+  +------------------+  +-------------------+                          |
+---------------------------------------------------------------------------------------+
```

1. **`Patient`:** representa al paciente como sujeto del cuidado. Atributos: `id` (UUID), `identifier_system` (String), `identifier_value` (String), `name_given` (String), `name_family` (String), `gender` (String), `birth_date` (Date), `sede_origen` (String). MÃ©todos: `to_fhir_resource()`, `validate_id()`.
2. **`Encounter`:** modela el contacto asistencial o episodio clÃ­nico. Atributos: `id` (UUID), `patient_id` (UUID), `status` (String), `class_code` (String), `period_start` (DateTime), `period_end` (DateTime), `triage_priority` (Integer [1..5]), `service_provider_sede` (String). MÃ©todos: `calculate_duration()`, `to_fhir_encounter()`.
3. **`Condition`:** diagnÃ³stico mÃ©dico registrado. Atributos: `id` (UUID), `patient_id` (UUID), `encounter_id` (UUID), `clinical_status` (String), `verification_status` (String), `code_cie10` (String), `display_text` (String), `recorded_date` (DateTime), `practitioner_id` (String). MÃ©todos: `map_to_icd10()`, `sign_record()`.
4. **`Observation`:** hallazgos clÃ­nicos, signos vitales o resultados de laboratorio. Atributos: `id` (UUID), `patient_id` (UUID), `encounter_id` (UUID), `code_loinc` (String), `status` (String), `value_quantity` (Float), `unit` (String), `effective_datetime` (DateTime). MÃ©todos: `to_fhir_observation()`.
5. **`Sede`:** nodo hospitalario federado. Atributos: `codigo_sede` (String), `nombre` (String), `direccion` (String), `puerto_bd` (Integer), `ip_host` (String), `estado_operativo` (Boolean). MÃ©todos: `get_connection_string()`, `check_health()`.
6. **`HSBMessage`:** encapsula la unidad atÃ³mica de informaciÃ³n recibida por el middleware. Atributos: `message_id` (UUID), `timestamp` (DateTime), `source_system` (String), `payload_format` (String [HL7, CSV]), `raw_payload` (Text), `payload_hash` (String [SHA-256]), `processing_status` (String). MÃ©todos: `compute_hash()`, `set_status()`.
7. **`RetryQueue`:** gestor de reintentos para fallos transitorios. Atributos: `queue_id` (UUID), `message_id` (UUID), `current_attempt` (Integer), `max_attempts` (Integer), `next_retry_timestamp` (DateTime), `backoff_factor` (Float). MÃ©todos: `enqueue()`, `execute_retry()`, `calculate_next_backoff()`.
8. **`DeadLetterQueue`:** depÃ³sito de aislamiento de mensajes fallidos. Atributos: `dlq_id` (UUID), `message_id` (UUID), `failure_reason` (String), `failed_at_step` (String), `error_details` (Text), `resolved` (Boolean). MÃ©todos: `store_dead_letter()`, `reprocess()`.
9. **`TerminologyMap`:** motor de equivalencias semÃ¡nticas. Atributos: `source_system` (String), `source_code` (String), `target_system` (String), `target_code` (String), `target_display` (String). MÃ©todos: `lookup_code()`, `validate_term()`.
10. **`AuditEventChain`:** eslabÃ³n del libro mayor criptogrÃ¡fico. Atributos: `block_index` (Integer), `timestamp` (DateTime), `action` (String), `resource_affected` (String), `user_id` (String), `prev_hash` (String [SHA-256]), `current_hash` (String [SHA-256]). MÃ©todos: `calculate_hash()`, `verify_chain_integrity()`.

**Relaciones Estructurales:**
- Un `Patient` mantiene una asociaciÃ³n de uno a muchos (`1` a `0..*`) con `Encounter`.
- Un `Encounter` agrega de cero a muchas (`1` a `0..*`) instancias de `Condition` y `Observation`.
- Una `Sede` actÃºa como entidad contenedora de adscripciÃ³n de mÃºltiples `Patient` (`1` a `0..*`).
- El `HSBMessage` se relaciona opcionalmente con `RetryQueue` (`1` a `0..1`) y con `DeadLetterQueue` (`1` a `0..1`) segÃºn su estado de procesamiento.
- Cada `HSBMessage` consulta `TerminologyMap` durante su normalizaciÃ³n y genera un registro persistente en `AuditEventChain`.

```markdown
[Insertar Diagrama de Clases aquÃ­]
```

---

### 8.4 Diagrama de Estados: Ciclo de Vida del Mensaje ClÃ­nico en el HSB

El diagrama de estados modela formalmente las transiciones discretas que experimenta un mensaje en el bus de interoperabilidad:

```
 [*] --> RECIBIDO
           â”‚
           â–¼
       VALIDANDO â”€â”€â”€â”€(Error SintÃ¡ctico / ValidaciÃ³n)â”€â”€â”€â”€> RECHAZADO â”€â”€> DLQ â”€â”€> [*]
           â”‚                                                 
           â”œâ”€â”€â”€â”€â”€(Firma CriptogrÃ¡fica SHA-256 Repetida)â”€â”€> DUPLICADO â”€â”€> DESCARTADO_OK â”€â”€> [*]
           â”‚
           â–¼ (Estructura VÃ¡lida e InÃ©dita)
     TRANSFORMANDO
           â”‚
           â–¼
    NORMALIZADO_FHIR
           â”‚
           â–¼
    PERSISTIENDO_CITUS
           â”‚
           â–¼
     ENVIANDO_HAPI <â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
           â”‚                                   â”‚
           â”œâ”€â”€â”€â”€â”€(Timeout / Error HTTP 50x)â”€â”€> REINTENTANDO
           â”‚                                   â”‚ (Intentos <= 3)
           â”‚                                   â”‚
           â”‚                                   â””â”€â”€(Intentos > 3)â”€â”€> DLQ â”€â”€> [*]
           â–¼ (HTTP 201 Created)
       ENTREGADO
           â”‚
           â–¼
  AUDITADO_HASHCHAIN
           â”‚
           â–¼
          [*]
```

- **`RECIBIDO`:** El mensaje ingresa al gateway a travÃ©s de los adaptadores HTTP REST.
- **`VALIDANDO`:** El motor examina la completitud sintÃ¡ctica del formato y consulta el registro de hashes SHA-256:
  - *TransiciÃ³n a `DUPLICADO`:* Si el hash ya estÃ¡ registrado, transita a `DESCARTADO_OK` (estado final neutral) sin duplicar datos.
  - *TransiciÃ³n a `RECHAZADO`:* Si carece de identificadores indispensables, transita a `DLQ` (estado final de fallo) emitiendo una alarma.
- **`TRANSFORMANDO`:** Se procesan las reglas de correspondencia sintÃ¡ctica y semÃ¡ntica sobre los segmentos clÃ­nicos.
- **`NORMALIZADO_FHIR`:** La informaciÃ³n queda serializada canÃ³nicamente en recursos compatibles con FHIR R4.
- **`PERSISTIENDO_CITUS`:** El registro se inserta en las tablas distribuidas del clÃºster Citus mediante particionamiento sharding horizontal.
- **`ENVIANDO_HAPI`:** Se despacha la solicitud REST hacia el servidor HAPI FHIR JPA:
  - *TransiciÃ³n a `ENTREGADO`:* Al recibir confirmaciÃ³n HTTP 201 Created.
  - *TransiciÃ³n a `REINTENTANDO`:* Si el servicio HAPI no responde o genera un error 50x, se activa el ciclo de reintento programado con retroceso exponencial.
  - *TransiciÃ³n de `REINTENTANDO` a `DLQ`:* Si tras superar los tres reintentos mÃ¡ximos la conexiÃ³n sigue fallando, se traslada a la cola de mensajes muertos garantizando que la falla no bloquee el bus.
- **`AUDITADO_HASHCHAIN`:** El evento mÃ©dico se concatena matemÃ¡ticamente al Ãºltimo bloque de la cadena SHA-256, alcanzando el estado terminal exitoso.

```markdown
[Insertar Diagrama de Estados aquÃ­]
```

---

## SECCIÃ“N 9: PROCESO DE DESARROLLO

El ciclo constructivo del proyecto se ejecutÃ³ en cinco fases metodolÃ³gicas de ingenierÃ­a de software para sistemas distribuidos, asegurando el cumplimiento exhaustivo de los requerimientos tÃ©cnicos y pedagÃ³gicos planteados.

### Fase 1: AnÃ¡lisis y DiseÃ±o Arquitectural
Durante esta fase inicial se realizÃ³ una revisiÃ³n minuciosa de las directrices tÃ©cnicas del docente, la normatividad colombiana sobre interoperabilidad de historias clÃ­nicas (ResoluciÃ³n 866 de 2021 del Ministerio de Salud) y la especificaciÃ³n internacional HL7 FHIR R4. 

Se elaborÃ³ el modelado formal del sistema compuesto por cuatro diagramas UML (casos de uso, secuencias, clases y estados) para delimitar las interfaces y responsabilidades de cada componente distribuido. Asimismo, se consolidÃ³ la **Matriz de HomologaciÃ³n de Campos**, que definiÃ³ la correspondencia biunÃ­voca para **19 variables crÃ­ticas** entre las fuentes heterogÃ©neas (HL7 v2 y CSV) y la estructura canÃ³nica FHIR R4: identificadores de pacientes (`PID.3` / `documento` $\rightarrow$ `Patient.identifier`), nombres y apellidos (`PID.5` $\rightarrow$ `Patient.name`), gÃ©nero administrativo (`PID.8` $\rightarrow$ `Patient.gender`), fecha de atenciÃ³n (`PV1.44` $\rightarrow$ `Encounter.period.start`), nivel de triage (`triage` $\rightarrow$ `Encounter.priority`), diagnÃ³stico principal (`DG1.3` $\rightarrow$ `Condition.code.coding.code` con sistema CIE-10), y profesional tratante (`PV1.7` $\rightarrow$ `Encounter.participant.individual`), entre otros.

### Fase 2: Infraestructura de Datos y NormalizaciÃ³n CanÃ³nica FHIR
En la segunda fase se materializÃ³ la infraestructura base orquestada mediante Docker Compose, desplegando un entorno multicontenedor integrado por siete servicios:
1. `db_sincelejo` (PostgreSQL 15 en puerto 5433).
2. `db_cartagena` (PostgreSQL 15 en puerto 5434).
3. `db_corozal` (PostgreSQL 15 en puerto 5435).
4. `citus_master` (Coordinador distribuido en puerto 5432).
5. `citus_worker1` (Nodo de cÃ³mputo y sharding 1).
6. `citus_worker2` (Nodo de cÃ³mputo y sharding 2).
7. `hapi_fhir` (Servidor canÃ³nico JPA en puerto 8080).

Se desarrollaron los scripts DDL de inicializaciÃ³n para poblar las bases de datos de las sedes con esquemas relacionales independientes. En el clÃºster Citus, se configurÃ³ la extensiÃ³n distribuida, se agregaron dinÃ¡micamente los nodos trabajadores mediante la instrucciÃ³n `citus_add_node()` y se crearon las tablas distribuidas (`patients`, `encounters`, `conditions`) aplicando particionamiento horizontal transparente mediante la sentencia:
```sql
SELECT create_distributed_table('patients', 'patient_id');
SELECT create_distributed_table('encounters', 'patient_id');
SELECT create_distributed_table('conditions', 'patient_id');
```
SimultÃ¡neamente se codificÃ³ el mÃ³dulo de normalizaciÃ³n semÃ¡ntica `normalizer.py`, implementando funciones como `build_fhir_bundle()`, `validate_document()`, `normalize_gender()` y `map_diagnosis()`. La calidad del mÃ³dulo se certificÃ³ mediante la construcciÃ³n y ejecuciÃ³n de cinco pruebas unitarias automatizadas (`test_normalizer.py`), las cuales validaron con un 100% de Ã©xito la completitud de los *Bundles*, la conversiÃ³n tipogrÃ¡fica y el manejo de excepciones ante identificadores invÃ¡lidos.

### Fase 3: ConstrucciÃ³n del Middleware Health Service Bus (HSB)
En esta fase se construyÃ³ la columna vertebral del sistema distribuido utilizando FastAPI (`hsb/main.py`), exponiendo los endpoints principales de interoperabilidad:
- `POST /api/ingest/hl7`: receptor de tramas clÃ­nicas HL7 v2.x.
- `POST /api/ingest/csv`: ingesta masiva de archivos planos por lotes.
- `GET /health`: sondeo de disponibilidad de todos los nodos de la red.
- `GET /metrics`: telemetrÃ­a en tiempo real (tiempos de respuesta, volÃºmenes de mensajes).
- `GET /api/dlq`: inspecciÃ³n y monitoreo de la cola de mensajes muertos.

Se diseÃ±aron parsers especializados para mensajes de admisiÃ³n hospitalaria `ADT^A01` y reportes de laboratorio `ORU^R01`, asÃ­ como un lector CSV con validaciÃ³n estricta de tipos de datos en cada tupla. El sistema de idempotencia se programÃ³ calculando el hash criptogrÃ¡fico SHA-256 del contenido crudo entrante y cotejÃ¡ndolo contra un almacÃ©n indexado en memoria y persistente. AdemÃ¡s, se desarrollÃ³ la cola de reintentos resiliente dotada de retroceso exponencial (demoras progresivas de 1s, 2s y 4s ante indisponibilidades de downstream) y el enrutamiento automÃ¡tico hacia la *Dead Letter Queue* (DLQ) para anomalÃ­as no recuperables.

Para someter a prueba la tuberÃ­a, se generaron cuatro conjuntos de datos de prueba: dos tramas HL7 vÃ¡lidas (admisiÃ³n y observaciÃ³n), una trama HL7 intencionalmente malformada (con omisiÃ³n de delimitadores requeridos para constatar su captura en la DLQ), y un archivo CSV estructurado con cinco registros clÃ­nicos heterogÃ©neos pertenecientes a las diferentes sedes.

### Fase 4: Seguridad, CriptografÃ­a, AuditorÃ­a y Resiliencia Distribuida
Se implementaron las directrices de seguridad y trazabilidad mÃ©dica:
- **AutenticaciÃ³n y Control de Acceso (RBAC):** Se implementÃ³ un esquema de autenticaciÃ³n basado en JSON Web Tokens (PyJWT) utilizando el algoritmo criptogrÃ¡fico HS256. Se configurÃ³ un middleware de autorizaciÃ³n RBAC que valida los permisos de cada usuario. Se realizaron pruebas de penetraciÃ³n demostrando que solicitudes al endpoint `/api/diagnosticar` suscritas con rol `MEDICO` son autorizadas con Ã©xito (HTTP 200), mientras que peticiones emitidas por usuarios con rol `PACIENTE` son rechazadas de inmediato con cÃ³digo de error HTTP 403 Forbidden.
- **Cadena de AuditorÃ­a CriptogrÃ¡fica (Hash-Chain Ledger):** Cada transacciÃ³n clÃ­nica que modifica el estado del sistema genera un bloque inmutable en el cual se concatena el hash previo con el payload actual ($H_n = \text{SHA-256}(H_{n-1} + \text{payload})$). Este libro mayor permite verificar algorÃ­tmicamente que la historia clÃ­nica no ha sido manipulada en reposo.
- **Tolerancia a Particiones y Resiliencia:** Se llevaron a cabo pruebas controladas de inyecciÃ³n de fallos deteniendo manualmente el contenedor de la Sede Cartagena mediante el comando `docker stop db_sede2`. El bus HSB detectÃ³ el evento sin colapsar, aislÃ³ las consultas destinadas a dicha sede y continuÃ³ atendiendo peticiones dirigidas a Sincelejo y Corozal con un mecanismo de degradaciÃ³n elegante (*graceful degradation*).
- **Resiliencia ante CaÃ­da de HAPI FHIR:** Se simulÃ³ la indisponibilidad del servidor HAPI FHIR apagando su contenedor. Las pruebas empÃ­ricas registraron una latencia controlada de **7095.13 ms**, la cual reflejÃ³ con exactitud los tres ciclos sucesivos de reintento con *backoff* exponencial (1s + 2s + 4s) antes de desviar el mensaje a la DLQ, preservando la consistencia de los datos en Citus sin degradar la disponibilidad del hilo principal.

### Fase 5: Desarrollo de Vistas Web, IntegraciÃ³n E2E y ValidaciÃ³n Final
En la etapa de cierre se implementaron las cuatro vistas de usuario web dentro del archivo de plantilla unificada `app/templates/index.html` bajo el framework Bootstrap 5. Estas vistas se integraron asÃ­ncronamente con los endpoints del HSB a travÃ©s de la API Fetch de JavaScript.

Se realizaron pruebas de integraciÃ³n de extremo a extremo (*End-to-End*), corroborando el flujo completo: desde el ingreso de una admisiÃ³n en la interfaz de usuario o el envÃ­o de un archivo CSV por lÃ­nea de comandos, pasando por el filtrado de idempotencia y la normalizaciÃ³n FHIR en el HSB, hasta el almacenamiento distribuido en Citus, el registro canÃ³nico en HAPI FHIR y la visualizaciÃ³n consolidada en la historia clÃ­nica del paciente. Finalmente, se documentaron los hallazgos y se estructurÃ³ la demostraciÃ³n interactiva en vivo para sustentar el parcial final.

---

## SECCIÃ“N 10: DISEÃ‘O DE INTERFACES E IMPLEMENTACIÃ“N

La capa de presentaciÃ³n del sistema se implementÃ³ como una aplicaciÃ³n web de una sola pÃ¡gina (*Single Page Application* - SPA ligera) construida sobre HTML5, Bootstrap 5 y JavaScript nativo asÃ­ncrono. La plataforma estÃ¡ dotada de un encabezado corporativo unificado que contextualiza el alcance del sistema y provee retroalimentaciÃ³n visual continua:
- **TÃ­tulo Institucional:** *"Red Hospitalaria Distribuida (Sincelejo - Cartagena - Corozal)"*
- **SubtÃ­tulo de EspecificaciÃ³n TÃ©cnica:** *"Interoperabilidad FHIR | HSB FastAPI | Base Distribuida Citus | Hash-Chain Audit"*
- **Badge DinÃ¡mico de TelemetrÃ­a:** Indicador superior derecho en tono esmeralda con la leyenda *"Sistema Operativo: 100% Online - Grupo 5"*, el cual se actualiza periÃ³dicamente mediante sondeo asÃ­ncrono al endpoint `/health`.

A continuaciÃ³n se detallan las cuatro vistas especializadas que integran la soluciÃ³n:

### 10.1 Vista Paciente: Consulta Longitudinal de Historia ClÃ­nica Unificada
DiseÃ±ada con un enfoque centrado en la usabilidad y la accesibilidad, esta interfaz permite al paciente o al personal asistencial acceder a una vista federada y consolidada de todas las atenciones mÃ©dicas recibidas en la red hospitalaria.

La pantalla presenta un campo de entrada numÃ©rico para digitar el documento de identidad del usuario, acompaÃ±ado del botÃ³n de acciÃ³n principal *"Consultar Historia"*. Al ejecutarse la consulta asÃ­ncrona, la interfaz renderiza:
- Un panel superior destacado tipo alerta verde (`alert-success`) que exhibe las variables demogrÃ¡ficas normalizadas: Nombre Completo, Tipo y NÃºmero de Documento, GÃ©nero Administrativo y Sede de AdscripciÃ³n Primaria.
- Una tabla dinÃ¡mica y responsiva que consolida cronolÃ³gicamente los episodios clÃ­nicos distribuidos a travÃ©s de las tres sedes. La tabla cuenta con cinco columnas: **Sede de AtenciÃ³n**, **Fecha y Hora**, **Tipo de Evento / DiagnÃ³stico CIE-10**, **Profesional MÃ©dico Tratante** y **Detalle ClÃ­nico / Observaciones**.
- Un botÃ³n de acciÃ³n especializado denominado *"Descargar FHIR R4 Bundle (JSON)"*, el cual genera dinÃ¡micamente y descarga en el equipo cliente el expediente clÃ­nico en formato JSON nativo de acuerdo con el estÃ¡ndar internacional FHIR R4, posibilitando la portabilidad efectiva de los datos de salud.

```markdown
[Insertar captura de pantalla de Vista Paciente aquÃ­]
```

### 10.2 Vista Admisionista: RecepciÃ³n, PriorizaciÃ³n y Despacho a HSB
Orientada al personal administrativo de admisiones y urgencias de los centros asistenciales. Provee un formulario con validaciÃ³n en tiempo real para el registro de nuevos episodios de atenciÃ³n:
- **Campos del Formulario:** Documento de Identidad del Paciente, Nombre Completo, Sexo (menÃº desplegable conforme a las categorÃ­as administrativas de FHIR: Masculino, Femenino, Otro, Desconocido), Sede Hospitalaria (selector de sede emisora: Sincelejo, Cartagena o Corozal), Nivel de Triage (selector numÃ©rico del 1 al 5 codificado por severidad clÃ­nica) y Motivo de Consulta o Ingreso.
- **AcciÃ³n de Despacho:** Al presionar el botÃ³n *"Registrar y Despachar a HSB"*, la aplicaciÃ³n captura los valores, estructura la carga Ãºtil y la remite mediante una llamada asÃ­ncrona POST al endpoint de ingesta del HSB. La interfaz despliega de inmediato un cuadro modal informativo con el UUID del mensaje asignado, el cÃ³digo de estado retornado por el middleware y la confirmaciÃ³n de la normalizaciÃ³n del recurso `Encounter`.

```markdown
[Insertar captura de pantalla de Vista Admisionista aquÃ­]
```

### 10.3 Vista MÃ©dico: EstaciÃ³n de DiagnÃ³stico Codificado y Firma CriptogrÃ¡fica
Concebida para el uso exclusivo del personal facultativo dentro de los consultorios o salas de hospitalizaciÃ³n. Permite asociar diagnÃ³sticos formales y notas evolutivas a la historia clÃ­nica del paciente garantizando el no repudio:
- **Componentes de Interfaz:** Campo para el Documento del Paciente en atenciÃ³n, selector desplegable de DiagnÃ³stico CIE-10 (que incluye cÃ³digos ontolÃ³gicos estandarizados como *A09X - Gastroenteritis infecciosa*, *I10X - HipertensiÃ³n esencial*, *J00X - Rinofaringitis aguda*, *E119 - Diabetes mellitus tipo 2*, entre otros), campo para el Nombre del MÃ©dico Tratante e insumo de texto para notas mÃ©dicas.
- **Sellado CriptogrÃ¡fico:** Incorpora el botÃ³n *"Firmar con Hash"*. Al ser pulsado por un usuario con credenciales autorizadas (rol `MEDICO` validado por token JWT), el sistema procesa el registro clÃ­nico, invoca el mÃ³dulo criptogrÃ¡fico del HSB y retorna el resumen SHA-256 generado junto con el Ã­ndice del bloque en la cadena de auditorÃ­a inmutable, exhibiÃ©ndolo en pantalla como comprobante de autenticidad e inalterabilidad de la atenciÃ³n brindada.

```markdown
[Insertar captura de pantalla de Vista MÃ©dico aquÃ­]
```

### 10.4 Vista Reporte y Monitoreo Operacional: Tablero de Infraestructura Distribuida
Esta consola de mando ofrece a los administradores del sistema e ingenieros de soporte una radiografÃ­a completa y en tiempo real sobre la salud tÃ©cnica de toda la red distribuida.

La vista se estructura en dos componentes principales:
- **Tarjetas MÃ©tricas de TelemetrÃ­a (KPI Cards):** Cuatro tarjetas superiores diferenciadas cromÃ¡ticamente que presentan indicadores clave de rendimiento actualizados:
  1. *Mensajes Recibidos (Azul / Primary):* volumen acumulado de tramas procesadas por el HSB.
  2. *Entregados a Citus / FHIR (Verde / Success):* total de recursos persistidos y distribuidos con Ã©xito.
  3. *Latencia Promedio (Amarillo / Warning):* tiempo medio de procesamiento en milisegundos.
  4. *Dead Letter Queue - DLQ (Rojo / Danger):* recuento de mensajes con errores o no entregables aislados para remediaciÃ³n.
- **Panel de TopologÃ­a y Estado de Nodos:** Tabla inferior que lista los componentes de red esenciales (**HSB Gateway**, **Sede Sincelejo :5433**, **Sede Cartagena :5434**, **Sede Corozal :5435**, **ClÃºster Citus :5432** y **Servidor HAPI FHIR :8080**), mostrando su direcciÃ³n IP, puerto y una insignia de estado visual (*ACTIVO*, *ONLINE* o *DEGRADADO*).
- **AcciÃ³n de Control:** Incluye el botÃ³n interactivo *"Refrescar MÃ©tricas"*, el cual ejecuta una consulta paralela a los endpoints `/metrics` y `/health` del HSB, permitiendo al operador diagnosticar de inmediato cualquier eventualidad o particiÃ³n de red en la infraestructura hospitalaria distribuida.

```markdown
[Insertar captura de pantalla de Vista Reporte/Monitoreo aquÃ­]
```
# PARTE 3: IMPLEMENTACIÃ“N, RESULTADOS, CONCLUSIONES Y ANEXOS TÃ‰CNICOS

---

## 11. PROTOTIPO FINAL

El prototipo funcional de la plataforma distribuida de interoperabilidad clÃ­nica representa la integraciÃ³n y despliegue operativo de los componentes de intermediaciÃ³n, almacenamiento distribuido y normalizaciÃ³n de datos de salud diseÃ±ados a lo largo del proyecto. La soluciÃ³n fue concebida bajo una arquitectura de microservicios contenerizados mediante Docker y coordinados a travÃ©s de Docker Compose, complementada con el motor asÃ­ncrono del Bus de Servicios de Salud (*Health Service Bus* - HSB) implementado en FastAPI.

### 11.1. Arquitectura de Despliegue y Servicios Contenerizados

La topologÃ­a de infraestructura comprende siete (7) servicios en contenedores interconectados en una red puente (*bridge network*) aislada, mÃ¡s el proceso principal del HSB:

1. **`citus_coordinator`**: Nodo coordinador de PostgreSQL con la extensiÃ³n Citus, encargado de mantener el catÃ¡logo distribuido, compilar planes de consulta y enrutar las operaciones hacia los fragmentos (*shards*) correspondientes.
2. **`citus_worker1`**: Primer nodo de cÃ³mputo y almacenamiento distribuido de Citus para particiones de datos clÃ­nicos.
3. **`citus_worker2`**: Segundo nodo de cÃ³mputo y almacenamiento distribuido de Citus.
4. **`db_sede1`**: Base de datos relacional local representativa del sistema legado de la Sede Hospitalaria 1.
5. **`db_sede2`**: Base de datos relacional local de la Sede Hospitalaria 2.
6. **`db_sede3`**: Base de datos relacional local de la Sede Hospitalaria 3.
7. **`hapi_fhir`**: Servidor canÃ³nico HAPI FHIR JPA v8.12.0 sobre Tomcat/Java 17, implementando el estÃ¡ndar FHIR R4.
8. **HSB Application**: Servicio middleware en Python 3 que provee la lÃ³gica de normalizaciÃ³n, enrutamiento semÃ¡ntico, control de idempotencia, polÃ­ticas de reintento, seguridad JWT y la interfaz grÃ¡fica de usuario.

```
+-----------------------------------------------------------------------------------+
|                        MÃQUINA VIRTUAL CENTOS STREAM 9                            |
|                     (VirtualBox: 4 vCPUs, 6 GB RAM, 50 GB SSD)                    |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                 HSB (Health Service Bus) - FastAPI / Uvicorn                |  |
|  |             (Puerto 8000: API REST, WebSockets, GUI ClÃ­nica 4 Vistas)        |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                Red Docker Interna (`red_interoperabilidad_clinica`)               |
|            +---------------------------+---------------------------+              |
|            |                           |                           |              |
|  +---------v----------+     +----------v---------+      +----------v---------+    |
|  | citus_coordinator  |     |     hapi_fhir      |      |   db_sede1, 2, 3   |    |
|  | (PostgreSQL/Citus) |     |  (FHIR R4 JPA Engine) |   | (Sedes Hospital)   |    |
|  +----+----------+----+     +--------------------+      +--------------------+    |
|       |          |                                                                |
|  +----v----+ +---v------+                                                         |
|  | worker1 | | worker2  |                                                         |
|  +---------+ +----------+                                                         |
+-----------------------------------------------------------------------------------+
```

### 11.2. Entorno Operativo y Puesta en Marcha

El prototipo fue desplegado y validado en una mÃ¡quina virtual con sistema operativo **CentOS Stream 9** bajo VirtualBox, aprovisionada con cuatro (4) nÃºcleos virtuales de procesamiento (vCPUs) y 6.144 MB (6 GB) de memoria RAM dinÃ¡mica. 

El procedimiento unificado de arranque del sistema se ejecuta mediante la secuencia de comandos:

```bash
cd ~/parcial-final-distribuidos && \
docker compose up -d && \
nohup python3 -m uvicorn hsb.main:app --host 0.0.0.0 --port 8000 > hsb.log 2>&1 &
```

Este procedimiento garantiza el levantamiento coordinado de los contenedores mediante comprobaciones de estado (*health checks*) en dependencias crÃ­ticas (PostgreSQL y HAPI FHIR), seguido del inicio del bus de integraciÃ³n en segundo plano escuchando peticiones en el puerto TCP 8000.

### 11.3. Cumplimiento de Criterios de AceptaciÃ³n

El prototipo satisface la totalidad de los criterios de evaluaciÃ³n funcional y no funcional estipulados en la rÃºbrica del proyecto:
- **EjecuciÃ³n exitosa de las 5 fases**: Desde el modelado de dominio y persistencia distribuida, pasando por la ingesta multiformato y resiliencia, hasta la visualizaciÃ³n clÃ­nica.
- **Interfaces operativas**: Cuatro (4) vistas web interactivas (Paciente, Admisionista, MÃ©dico, AuditorÃ­a/Reportes) completamente desacopladas y funcionales sobre navegadores web estÃ¡ndar.
- **Tolerancia a fallos demostrada**: DegradaciÃ³n controlada ante la caÃ­da forzada de nodos locales y reintentos automÃ¡ticos ante la indisponibilidad de servidores semÃ¡nticos.
- **Trazabilidad auditada**: Registro criptogrÃ¡fico secuencial (*hash-chain*) inmutable de todas las transacciones clÃ­nicas generadas.

---

## 12. RESULTADOS Y DISCUSIÃ“N

La evaluaciÃ³n experimental del prototipo se estructurÃ³ a partir de planes de pruebas rigurosos asociados a cada fase del ciclo de vida distribuido, registrando mÃ©tricas de latencia, consistencia transaccional y respuesta ante anomalÃ­as.

### 12.1. Resultados por Fases

#### 12.1.1. Fase 2: Infraestructura Distribuida y Servidor de Interoperabilidad
La validaciÃ³n del clÃºster Citus demostrÃ³ la correcta distribuciÃ³n y aislamiento de particiones mediante la ejecuciÃ³n de sentencias de anÃ¡lisis de ejecuciÃ³n (`EXPLAIN`). Al consultar registros clÃ­nicos filtrando por la clave de particiÃ³n (`patient_id`), el planificador de Citus ejecutÃ³ un escaneo directo de tipo tarea Ãºnica:

```sql
EXPLAIN SELECT * FROM clinical_encounters WHERE patient_id = '1007';
-- Salida:
-- Custom Scan (Citus Adaptive)  (cost=0.00..0.00 rows=0 width=0)
--   Task Count: 1
--   Tasks Shown: One of 1
--   ->  Task
--         Node: host=citus_worker1 port=5432 dbname=citus
--         ->  Index Scan using clinical_encounters_patient_idx on clinical_encounters_102008
```

Este resultado confirma el enrutamiento eficiente a un Ãºnico nodo de datos (*Task Count: 1*) sin incurrir en transferencias cruzadas de red (*cross-node broadcast*), minimizando el tiempo de respuesta.

Asimismo, la prueba de propiedades ACID en transacciones distribuidas sobre mÃºltiples tablas correlacionadas (paciente, encuentro y condiciÃ³n clÃ­nica) validÃ³ la atomicidad mediante el protocolo de confirmaciÃ³n en dos fases (2PC):
$$\text{BEGIN} \longrightarrow \text{INSERT (patient)} \longrightarrow \text{INSERT (encounter)} \longrightarrow \text{ROLLBACK} \longrightarrow \text{SELECT}$$
La consulta posterior arrojÃ³ exactamente cero (0) filas insertadas, demostrando reversiÃ³n consistente y ausencia de estados intermedios inconsistentes.

En cuanto al componente semÃ¡ntico, el servidor HAPI FHIR v8.12.0 respondiÃ³ satisfactoriamente a las consultas de metadatos (`GET /fhir/metadata`), retornando un recurso `CapabilityStatement` vÃ¡lido con cabecera `X-Powered-By: HAPI FHIR 8.12.0 REST Server (FHIR Server; FHIR 4.0.1/R4)`, ratificando la conformidad normativa con el perfil canÃ³nico internacional.

#### 12.1.2. Fase 3: Ingesta de Mensajes, NormalizaciÃ³n e Idempotencia
La prueba de ingesta con mensajes sintÃ©ticos HL7 v2.5 (`ADT^A01` - AdmisiÃ³n de Paciente) arrojÃ³ un procesamiento Ã­ntegro con estado **`entregado`** y una latencia media de **513,38 ms**, comprendiendo parseo del segmento pipe-delimited, normalizaciÃ³n a recurso `Bundle` FHIR R4 y persistencia distribuida en Citus.

```
[HL7 ADT^A01] ---> Parseo MSH/PID/PV1 ---> Conversor FHIR R4 ---> Citus Shard (513.38 ms)
                                  |
                           Firma SHA-256
                                  v
                      CachÃ© de Idempotencia: MSG-202611-001
```

La prueba de idempotencia consistiÃ³ en retransmitir el mismo mensaje con identificador `MSH-10 = MSG-202611-001`. El HSB detectÃ³ la clave de idempotencia preexistente calculada mediante hash criptogrÃ¡fico SHA-256 sobre el mensaje canÃ³nico, retornando estado **`duplicado`** y evitando la doble inserciÃ³n de pacientes o atenciones en la base de datos distribuida.

Para tramas con malformaciones estructurales o violaciones semÃ¡nticas, como un mensaje HL7 con documento alfanumÃ©rico en `PID-3.1`, el validador del bus asignÃ³ estado **`rechazado`** especificando de forma determinista la causal: `"Documento no numÃ©rico: 'ABC123'"`.

En la ingesta por lotes de admisiones tabulares en formato CSV (5 registros), el bus procesÃ³ con Ã©xito 3/5 filas (**`entregados`**):
- Fila 1 (Doc 1008): AsignaciÃ³n diagnÃ³stica CIE-10 `A09` (Gastroenteritis).
- Fila 2 (Doc 1009): AsignaciÃ³n diagnÃ³stica CIE-10 `I10` (HipertensiÃ³n arterial esencial).
- Fila 3 (Doc 1010): AsignaciÃ³n diagnÃ³stica CIE-10 `J45.9` (Asma no especificada).

Las 2 filas restantes fueron **`rechazadas`** justificadamente: una por carecer de mapeo vÃ¡lido en el catÃ¡logo CIE-10 (`ERR-UNKNOWN-DX`), y la otra por longitud insuficiente del documento de identificaciÃ³n (< 3 dÃ­gitos), siendo ambas anomalÃ­as dirigidas a la cola de mensajes muertos (*Dead Letter Queue* - DLQ) para posterior anÃ¡lisis forense.

#### 12.1.3. Fase 4: Seguridad, Resiliencia y AuditorÃ­a
La evaluaciÃ³n del control de acceso basado en roles (RBAC) mediante tokens firmados con JWT (algoritmo HMAC-SHA256) validÃ³ la barrera de seguridad:
- PeticiÃ³n con rol `MEDICO` hacia el endpoint de registro diagnÃ³stico (`POST /api/v1/diagnosticos`): Respuesta `HTTP 200 OK` (**`PERMITIDO`**).
- PeticiÃ³n con rol `PACIENTE` hacia el mismo endpoint administrativo/clÃ­nico: Respuesta inmediata `HTTP 403 Forbidden` (**`DENEGADO`**), preservando la segregaciÃ³n estricta de funciones.

La verificaciÃ³n del libro de auditorÃ­a criptogrÃ¡fica (*hash-chain*) tras procesar cuatro transacciones consecutivas evidenciÃ³ el cÃ¡lculo encadenado:
$$H_n = \text{SHA-256}(H_{n-1} \,\|\, T_n \,\|\, U_n \,\|\, \text{Payload}_n)$$
La rutina de verificaciÃ³n secuencial recorriÃ³ los 4 bloques persistidos, retornando el veredicto: `INTEGRIDAD DE AUDITORÃA: VÃLIDA (0 inconsistencias detectadas)`.

En los ensayos de tolerancia a fallos, se forzÃ³ la detenciÃ³n abrupta de la base de datos de la Sede 2 mediante `docker stop db_sede2`. El monitor de salud del HSB (`GET /health`) actualizÃ³ el estado a `SEDE2: DOWN`, mientras que los componentes centrales (`CITUS`, `SEDE1`, `SEDE3`, `HAPI`) continuaron en estado `UP`, absorbiendo peticiones sin interrupciÃ³n del servicio global.

Al inducir la caÃ­da temporal del servidor HAPI FHIR, el HSB activÃ³ la polÃ­tica de reintentos con retraso exponencial (*exponential backoff* con factor base 1s, 2s y 4s):
$$\Delta t_{\text{total}} = 1\,\text{s} + 2\,\text{s} + 4\,\text{s} \approx 7\,\text{s}$$
Al restablecerse el contenedor en el segundo 6, el mensaje se entregÃ³ con una latencia total registrada de **7.095,13 ms**, garantizando entrega garantizada (*at-least-once delivery*) sin descarte involuntario de transacciones clÃ­nicas.

#### 12.1.4. Fase 5: Interfaz Web y Casos de Uso ClÃ­nicos
A travÃ©s de un navegador web estÃ¡ndar (Mozilla Firefox) conectado al puerto 8000 (`http://localhost:8000`), se corroborÃ³ la funcionalidad completa de las cuatro vistas especializadas:
1. **Vista Paciente**: Consulta del historial personal introduciendo el documento `1007`; el sistema recuperÃ³ en tiempo real los datos consolidados de la paciente Andrea Rojas, visualizando los encuentros de urgencias y las condiciones asociadas provenientes de la Sede 2.
2. **Vista Admisionista**: Diligenciamiento del formulario de ingreso de urgencias para una nueva paciente (MarÃ­a FernÃ¡ndez, documento `1012`, clasificaciÃ³n Triage 3 - Urgencia menor); la transacciÃ³n se dispersÃ³ automÃ¡ticamente hacia la base de sede y el clÃºster Citus.
3. **Vista MÃ©dico**: Acceso del profesional de la salud al registro de la paciente `1007`, emisiÃ³n del diagnÃ³stico definitivo con cÃ³digo CIE-10 `J45.9` (Asma no especificada) y generaciÃ³n de firma digital hash de la evoluciÃ³n clÃ­nica.
4. **Vista Reporte/Monitoreo**: Tablero de control operativo en tiempo real que reflejÃ³ los 5 nodos principales en estado `ACTIVO/UP`, presentando mÃ©tricas de rendimiento por sede y bitÃ¡cora de auditorÃ­a.

### 12.2. DiscusiÃ³n Comparativa y Limitaciones

A diferencia de las arquitecturas tradicionales basadas en el intercambio de documentos monolÃ­ticos consolidados segÃºn la especificaciÃ³n HL7 CDA (*Clinical Document Architecture*), las cuales operan bajo el paradigma de documentos estÃ¡ticos en formato XML que dificultan el procesamiento granular en tiempo real, la plataforma desarrollada implementa un modelo de interoperabilidad a nivel de recursos atÃ³micos normalizados en FHIR R4. Este enfoque desacopla la semÃ¡ntica clÃ­nica de la estructura propietaria de cada IPS, permitiendo consultar o actualizar entidades individuales (`Patient`, `Encounter`, `Condition`, `Observation`) mediante interfaces RESTful.

La latencia promedio observada de **513,38 ms** en el procesamiento integral de tramas HL7 v2 es sustancialmente inferior al umbral lÃ­mite de 2.000 ms considerado estÃ¡ndar para flujos de admisiÃ³n clÃ­nica en tiempo real, demostrando la alta eficiencia del middleware asÃ­ncrono construido sobre FastAPI. Asimismo, el mecanismo de reintentos exponenciales acotado a un mÃ¡ximo acumulado de 7 segundos previene la congestiÃ³n de la red y el agotamiento de sockets concurrentes, ofreciendo degradaciÃ³n elegante sin pÃ©rdida de informaciÃ³n sensible.

No obstante, el estudio presenta limitaciones tÃ©cnicas que deben considerarse:
- **Naturaleza de los datos**: Se emplearon conjuntos de datos clÃ­nicos sintÃ©ticos generados programÃ¡ticamente para salvaguardar la privacidad de pacientes reales segÃºn normativas bioÃ©ticas.
- **TopologÃ­a de red local**: La persistencia distribuida con Citus se desplegÃ³ en un clÃºster local virtualizado sobre un Ãºnico hipervisor, por lo que no se evaluÃ³ el impacto de la latencia de Ã¡rea amplia (WAN) o fluctuaciones de enlaces interhospitalarios geogrÃ¡ficamente distantes.
- **Canal de transporte en desarrollo**: Los microservicios operaron sobre enlaces HTTP sin encapsulamiento TLS mutuo (mTLS), esquema admisible en fases de prototipado pero que demanda remediaciÃ³n antes de su paso a entornos productivos hospitalarios.

---

## 13. CONCLUSIONES

A partir del diseÃ±o, implementaciÃ³n y validaciÃ³n experimental del sistema distribuido de interoperabilidad clÃ­nica, se establecen las siguientes conclusiones:

1. **ImplementaciÃ³n exitosa del ciclo de vida integral**: Se materializÃ³ de manera robusta la totalidad de las cinco (5) fases del proyecto, articulando componentes de modelado relacional, middleware asÃ­ncrono, bases de datos distribuidas y visualizaciÃ³n clÃ­nica especializada.
2. **Interoperabilidad semÃ¡ntica canÃ³nica en FHIR R4**: La normalizaciÃ³n hacia recursos canÃ³nicos de FHIR R4 resolviÃ³ de forma transparente la heterogeneidad sintÃ¡ctica de los sistemas legados hospitalarios (tramas HL7 v2.x y archivos CSV masivos), garantizando que los datos clÃ­nicos compartan una semÃ¡ntica unificada e inequÃ­voca independientemente de su origen.
3. **Persistencia distribuida con garantÃ­as ACID y particionamiento horizontal**: La adopciÃ³n de PostgreSQL con la extensiÃ³n Citus permitiÃ³ fragmentar los datos clÃ­nicos en funciÃ³n del identificador del paciente (`patient_id`), optimizando las consultas de historias clÃ­nicas hacia nodos locales Ãºnicos (*single-shard routing*) y preservando la atomicidad transaccional mediante el protocolo de confirmaciÃ³n distribuida en dos fases.
4. **Resiliencia y fiabilidad del middleware mediante patrones EAI**: La incorporaciÃ³n sistemÃ¡tica de patrones de integraciÃ³n empresarial en el HSB â€”como detecciÃ³n de duplicados por hash SHA-256 (idempotencia), colas de mensajes fallidos (DLQ) y reintentos con retroceso exponencialâ€” garantizÃ³ la integridad del flujo de datos, absorbiendo desconexiones temporales de subsistemas sin provocar pÃ©rdidas transaccionales.
5. **Seguridad y trazabilidad criptogrÃ¡fica alineada a la normativa colombiana**: El esquema de autenticaciÃ³n y autorizaciÃ³n mediante JWT con RBAC, en sinergia con el registro inmutable de eventos en cadena de bloques encadenada (*hash-chain*), garantiza el cumplimiento vinculante de la Ley Estatutaria 1581 de 2012 sobre protecciÃ³n de datos personales y los lineamientos de interoperabilidad de la ResoluciÃ³n 866 de 2021 del Ministerio de Salud.
6. **Alta disponibilidad y tolerancia a fallos**: La arquitectura de microservicios demostrÃ³ una capacidad sobresaliente de degradaciÃ³n elegante, manteniendo operativas las sedes saludables y las capacidades de consulta y registro ante la desconexiÃ³n fortuita de nodos hospitalarios individuales.

### Limitaciones y Trabajo Futuro

Entre las limitaciones identificadas en la fase de prototipado se destacan el uso exclusivo de datos sintÃ©ticos no protegidos por secreto mÃ©dico real, la falta de cifrado TLS/mTLS en los canales de comunicaciÃ³n de red interna y el confinamiento de los nodos a un Ãºnico entorno virtualizado en CentOS Stream 9.

Como lÃ­neas prioritarias de trabajo futuro se proyecta:
- **OrquestaciÃ³n en la nube mediante Kubernetes (K8s)**: Despliegue de los microservicios del HSB y los nodos de Citus bajo Kubernetes, configurando autoescalado horizontal de pods (*Horizontal Pod Autoscaler* - HPA) en funciÃ³n de la demanda transaccional.
- **Monitoreo avanzado y observabilidad**: IntegraciÃ³n de mÃ©tricas de telemetrÃ­a con Prometheus, visualizaciÃ³n centralizada en tableros de Grafana y rastreo distribuido mediante OpenTelemetry.
- **Anclaje descentralizado de auditorÃ­a en Blockchain**: Reemplazar la cadena de hashes local por un registro distribuido permisionado basado en **Hyperledger Fabric**, permitiendo que mÃºltiples instituciones prestadoras de salud (IPS) e instancias reguladoras validen la inmutabilidad de la historia clÃ­nica sin un Ãºnico punto de confianza.
- **DistribuciÃ³n geogrÃ¡fica real**: Enlace de nodos sobre redes seguras punto a punto (VPN/WireGuard) comunicando sedes hospitalarias fÃ­sicamente distribuidas en el territorio nacional.

---

## 14. REFERENCIAS

1. Benson, T., & Grieve, G. (2021). *Principles of Health Interoperability: FHIR, HL7 and SNOMED CT* (4th ed.). Springer. https://doi.org/10.1007/978-3-030-56883-2
2. Brewer, E. A. (2012). CAP twelve years later: How the "rules" have changed. *Computer*, 45(2), 23â€“29. https://doi.org/10.1109/MC.2012.37
3. Citus Data. (2024). *Citus documentation: Distributed PostgreSQL* (Release 12.1). Citus Data, a Microsoft Company. https://docs.citusdata.com/
4. Congreso de la RepÃºblica de Colombia. (2012, 18 de octubre). *Ley Estatutaria 1581 de 2012: Por la cual se dictan disposiciones generales para la protecciÃ³n de datos personales*. Diario Oficial No. 48.587.
5. Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). *Distributed systems: Concepts and design* (5th ed.). Pearson Education.
6. HAPI FHIR Project. (2024). *HAPI FHIR documentation: The open-source FHIR API for Java* (Version 8.12.0). Smile Digital Health. https://hapifhir.io/
7. Health Level Seven International. (2019). *HL7 FHIR Release 4 (R4) Specification: Fast Healthcare Interoperability Resources* (Standard Version 4.0.1). HL7 International. https://hl7.org/fhir/R4/
8. Hohpe, G., & Woolf, B. (2004). *Enterprise integration patterns: Designing, building, and deploying messaging solutions*. Addison-Wesley Professional.
9. Mandel, J. C., Kreda, D. A., Mandl, K. D., Kohane, I. S., & Ramoni, R. B. (2016). SMART on FHIR: A standards-based, interoperable apps platform for electronic health records. *Journal of the American Medical Informatics Association*, 23(5), 899â€“908. https://doi.org/10.1093/jamia/ocv189
10. Ministerio de Salud y ProtecciÃ³n Social de Colombia. (2021, 15 de junio). *ResoluciÃ³n 866 de 2021: Por la cual se reglamenta el conjunto de elementos de datos clÃ­nicos relevantes para la interoperabilidad de la historia clÃ­nica electrÃ³nica*. Diario Oficial No. 51.706. https://www.minsalud.gov.co/
11. OrganizaciÃ³n Mundial de la Salud. (2012). *ClasificaciÃ³n EstadÃ­stica Internacional de Enfermedades y Problemas Relacionados con la Salud (CIE-10)* (10.Âª rev., ed. 2019). OrganizaciÃ³n Mundial de la Salud. https://icd.who.int/browse10/2019/en
12. Regenstrief Institute. (2023). *LOINC: The universal standard for identifying health measurements, observations, and documents* (Version 2.76). Regenstrief Center for Biomedical Informatics. https://loinc.org/

---

## 15. ANEXOS TÃ‰CNICOS

### Anexo A: Estructura del Proyecto

A continuaciÃ³n se detalla la jerarquÃ­a de archivos y directorios que compone el repositorio del proyecto distribuido de interoperabilidad clÃ­nica:

```
parcial-final-distribuidos/
â”œâ”€â”€ docker-compose.yml              # OrquestaciÃ³n de contenedores (Citus, Sedes, HAPI)
â”œâ”€â”€ requirements.txt                # Dependencias Python (FastAPI, uvicorn, psycopg2, etc.)
â”œâ”€â”€ hsb/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ main.py                     # Punto de entrada de FastAPI y endpoints REST/Web
â”‚   â”œâ”€â”€ bus.py                      # LÃ³gica del Health Service Bus y enrutamiento
â”‚   â”œâ”€â”€ idempotency.py              # ValidaciÃ³n de hash SHA-256 y deduplicaciÃ³n
â”‚   â”œâ”€â”€ retry.py                    # Mecanismo de reintentos con backoff exponencial
â”‚   â”œâ”€â”€ security.py                 # GeneraciÃ³n y validaciÃ³n de tokens JWT / RBAC
â”‚   â”œâ”€â”€ audit.py                    # Motor de cadena de bloques local (hash-chain)
â”‚   â””â”€â”€ templates/                  # Vistas HTML con estilos embebidos (4 vistas)
â”‚       â”œâ”€â”€ paciente.html
â”‚       â”œâ”€â”€ admisionista.html
â”‚       â”œâ”€â”€ medico.html
â”‚       â””â”€â”€ reporte.html
â”œâ”€â”€ fhir/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ normalizer.py               # ConversiÃ³n de HL7 v2 y CSV a FHIR R4 (Bundle)
â”‚   â”œâ”€â”€ models.py                   # Modelos Pydantic para recursos FHIR canÃ³nicos
â”‚   â””â”€â”€ terminology.py              # Servicio ref_terminology (CIE-10 y LOINC)
â”œâ”€â”€ db/
â”‚   â”œâ”€â”€ init_citus.sql              # Scripts DDL de particionamiento y sharding Citus
â”‚   â”œâ”€â”€ init_sedes.sql              # Esquemas de bases de datos locales para Sedes 1, 2 y 3
â”‚   â””â”€â”€ seed_data.sql               # PoblaciÃ³n de catÃ¡logos y datos de prueba sintÃ©ticos
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ test_01_citus_acid.py       # Pruebas de sharding y atomicidad distribuida
â”‚   â”œâ”€â”€ test_02_hl7_ingestion.py    # Pruebas de ingesta HL7, latencia e idempotencia
â”‚   â”œâ”€â”€ test_03_csv_batch.py        # Pruebas de ingesta CSV y descarte hacia DLQ
â”‚   â””â”€â”€ test_04_resilience_rbac.py  # Pruebas de caÃ­da de nodos, reintentos y tokens JWT
â””â”€â”€ logs/
    â”œâ”€â”€ hsb.log                     # Registro de ejecuciÃ³n del bus
    â””â”€â”€ audit_chain.json            # Persistencia de la cadena de hashes de auditorÃ­a
```

### Anexo B: Archivo docker-compose.yml
```yaml
# [Insertar cÃ³digo del docker-compose.yml]
```

### Anexo C: CÃ³digo Principal del HSB
```python
# [Insertar cÃ³digo de hsb/main.py]
```

### Anexo D: Normalizador FHIR R4
```python
# [Insertar cÃ³digo de fhir/normalizer.py]
```

### Anexo E: Scripts de Pruebas
```python
# [Insertar scripts de pruebas]
```

### Anexo F: Tabla de Mapeo SemÃ¡ntico de Campos

La siguiente tabla consolida la correspondencia semÃ¡ntica entre los datos crudos extraÃ­dos de fuentes heterogÃ©neas (mensajerÃ­a HL7 v2.x y archivos tabulares CSV de admisiÃ³n) y su representaciÃ³n canÃ³nica normalizada en recursos de la especificaciÃ³n FHIR R4:

| # | Campo Origen (HL7/CSV) | Segmento/Columna | Recurso FHIR R4 | Elemento FHIR | Tipo | TerminologÃ­a/Regla de TransformaciÃ³n |
|---|---|---|---|---|---|---|
| 1 | Identificador de Mensaje | MSH-10 | Bundle | Bundle.id | id | Preserva ID original como clave de idempotencia |
| 2 | Sede Emisora | MSH-4 | Provenance | Provenance.agent.who | Reference | Normaliza valor a SEDE1, SEDE2 o SEDE3 |
| 3 | Fecha y Hora de EnvÃ­o | MSH-7 | Bundle | Bundle.timestamp | instant | Formato estÃ¡ndar ISO 8601 (YYYY-MM-DDTHH:MM:SSZ) |
| 4 | Documento de Identidad | PID-3.1 / documento | Patient | Patient.identifier.value | string | NumÃ©rico $\ge 3$ dÃ­gitos; clave de particiÃ³n en Citus |
| 5 | Tipo de Identificador | PID-3.4 | Patient | Patient.identifier.system | uri | URI canÃ³nica `urn:oid:co:ips:identificacion` |
| 6 | Apellidos | PID-5.1 / nombre | Patient | Patient.name.family | string | CapitalizaciÃ³n con mayÃºscula inicial normalizada |
| 7 | Nombres | PID-5.2 / nombre | Patient | Patient.name.given | string | ExtracciÃ³n sintÃ¡ctica de nombres de pila |
| 8 | Fecha de Nacimiento | PID-7 / nacimiento | Patient | Patient.birthDate | date | Formato estÃ¡ndar YYYY-MM-DD |
| 9 | Sexo/GÃ©nero | PID-8 / sexo | Patient | Patient.gender | code | Mapeo terminolÃ³gico: M $\rightarrow$ male, F $\rightarrow$ female |
| 10 | ID Encuentro | PV1-19 | Encounter | Encounter.identifier.value | string | Prefijo hospitalario de sede (ej. V-S2-0101) |
| 11 | Fecha AtenciÃ³n | PV1-44 / fecha | Encounter | Encounter.period.start | dateTime | Formato estÃ¡ndar ISO 8601 |
| 12 | Profesional Tratante | PV1-7 / profesional | Encounter | Encounter.participant.individual | Reference | Identificador canÃ³nico del profesional (MED-01) |
| 13 | Nivel Triage | triage | Encounter | Encounter.priority.coding.code | code | Escala numÃ©rica de 1 (CrÃ­tico) a 5 (No urgente) |
| 14 | CÃ³digo DiagnÃ³stico | DG1-3.1 / dx_local | Condition | Condition.code.coding.code | code | ResoluciÃ³n ontolÃ³gica vÃ­a `ref_terminology` a CIE-10 |
| 15 | DescripciÃ³n DiagnÃ³stico | DG1-3.2 | Condition | Condition.code.coding.display | string | DescripciÃ³n textual canÃ³nica del catÃ¡logo OMS |
| 16 | CÃ³digo Prueba Lab | OBR-4.1 / OBX-3.1 | Observation | Observation.code.coding.code | code | CatÃ¡logo internacional LOINC (ej. 718-7) |
| 17 | Nombre Prueba Lab | OBR-4.2 / OBX-3.2 | Observation | Observation.code.coding.display | string | Nombre estandarizado (ej. Hemoglobina en sangre) |
| 18 | Resultado NumÃ©rico | OBX-5 | Observation | Observation.valueQuantity.value | decimal | Magnitud numÃ©rica medida cuantitativamente (13.8) |
| 19 | Unidad de Medida | OBX-6 | Observation | Observation.valueQuantity.unit | string | CÃ³digo unificado UCUM (ej. g/dL) |

---

## 16. VIABILIDAD TÃ‰CNICA

La viabilidad tÃ©cnica de la plataforma distribuida de interoperabilidad clÃ­nica se evalÃºa a partir de dos pilares esenciales para sistemas de misiÃ³n crÃ­tica en salud: la escalabilidad arquitectÃ³nica y la rigurosidad en el cumplimiento normativo y de seguridad.

### 16.1. Escalabilidad ArquitectÃ³nica

La soluciÃ³n adopta una estrategia de escalabilidad basada en la descomposiciÃ³n en microservicios desacoplados y la fragmentaciÃ³n de la persistencia:
- **Despliegue contenerizado**: La orquestaciÃ³n mediante Docker Compose articula siete (7) contenedores especializados mÃ¡s el proceso asÃ­ncrono del HSB. El uso de imÃ¡genes optimizadas de Linux garantiza un consumo equilibrado de recursos en la mÃ¡quina virtual CentOS Stream 9 (4 vCPUs y 6 GB RAM), operando con mÃ¡rgenes de utilizaciÃ³n inferiores al 45% de memoria y 25% de procesador bajo cargas nominales.
- **Particionamiento horizontal en Citus**: La fragmentaciÃ³n de datos clÃ­nicos mediante sharding por el atributo `patient_id` distribuye uniformemente la carga transaccional entre los nodos de cÃ³mputo (`citus_worker1` y `citus_worker2`). Esta decisiÃ³n de diseÃ±o permite el escalamiento horizontal transparente: si la demanda hospitalaria se incrementa, es posible incorporar nuevos nodos trabajadores al clÃºster de Citus y reequilibrar los fragmentos (*rebalance shards*) en caliente sin necesidad de rediseÃ±ar las tablas relacionales ni suspender el servicio.
- **Ruta de evoluciÃ³n a orquestaciÃ³n avanzada**: La naturaleza sin estado (*stateless*) del HSB implementado en FastAPI viabiliza su migraciÃ³n directa hacia entornos gobernados por **Kubernetes (K8s)**. Mediante el uso de controladores *Horizontal Pod Autoscaler* (HPA) fundamentados en mÃ©tricas de concurrencia HTTP y consumo de CPU, el bus podrÃ¡ escalar rÃ©plicas dinÃ¡micas para gestionar picos de admisiÃ³n hospitalaria o contingencias epidemiolÃ³gicas masivas.

### 16.2. Cumplimiento Normativo y Seguridad

El diseÃ±o de la plataforma se apega estrictamente al marco legal y tÃ©cnico de la RepÃºblica de Colombia:
- **ProtecciÃ³n de Datos Personales (Ley Estatutaria 1581 de 2012)**: Los datos clÃ­nicos poseen la categorÃ­a jurÃ­dica de informaciÃ³n sensible. La plataforma garantiza su tratamiento restrictivo a travÃ©s de mecanismos de autenticaciÃ³n y autorizaciÃ³n basados en **JSON Web Tokens (JWT)** con control de acceso basado en roles (**RBAC**). Esto asegura que Ãºnicamente los perfiles con legitimaciÃ³n clÃ­nica (como mÃ©dicos tratantes) puedan acceder a diagnÃ³sticos o evoluciones, denegando el acceso a roles de soporte o pacientes respecto a facultades clÃ­nicas restringidas.
- **Interoperabilidad de Historia ClÃ­nica (ResoluciÃ³n 866 de 2021 del Ministerio de Salud)**: La estructura de informaciÃ³n canÃ³nica adopta los campos clÃ­nicos obligatorios definidos en la norma para el intercambio electrÃ³nico de datos de salud, sustentada en el estÃ¡ndar internacional FHIR R4.
- **Trazabilidad e Inmutabilidad Forense**: La implementaciÃ³n del mecanismo de auditorÃ­a en cadena de bloques encadenada (*hash-chain*) con algoritmo criptogrÃ¡fico SHA-256 asegura que cada acciÃ³n (registro, consulta, modificaciÃ³n) quede indeleblemente ligada a la anterior, posibilitando a los comitÃ©s de Ã©tica mÃ©dica detectar alteraciones no autorizadas en el historial.
- **Seguridad en Reposo y TrÃ¡nsito (Plan de ProducciÃ³n)**: Como directriz de despliegue hospitalario final, se contempla la incorporaciÃ³n de cifrado simÃ©trico AES-256 en las particiones de almacenamiento y la activaciÃ³n obligatoria de canales seguros mediante TLS 1.3 con certificados mutuos (mTLS) entre los agentes de cada sede y el HSB.

---

## 17. INTEROPERABILIDAD BASADA EN DATOS

La plataforma materializa la interoperabilidad en salud mediante un enfoque basado en datos que abarca desde la captura heterogÃ©nea hasta la gobernanza clÃ­nica, estructurado en seis dimensiones especializadas:

### 17.1. Calidad y GestiÃ³n de Datos
El aseguramiento de la calidad de la informaciÃ³n se cimienta en la adopciÃ³n del modelo canÃ³nico **FHIR R4**, estructurado alrededor de los recursos `Bundle`, `Patient`, `Encounter`, `Condition` y `Observation`. El bus de integraciÃ³n aplica polÃ­ticas rigurosas de validaciÃ³n de esquemas antes de la persistencia: verifica la obligatoriedad de campos de identificaciÃ³n, la concordancia de tipos numÃ©ricos y la consistencia temporal de eventos clÃ­nicos. Asimismo, el HSB calcula un compendio criptogrÃ¡fico SHA-256 sobre la carga Ãºtil canÃ³nica, operando como identificador determinista de idempotencia para neutralizar la duplicidad de registros originada por reintentos de red o fallas transaccionales de los clientes.

### 17.2. Interoperabilidad SemÃ¡ntica
La coincidencia conceptual entre diversas entidades de salud se logra erradicando la ambigÃ¼edad de los vocabularios locales. Los diagnÃ³sticos emitidos en las sedes son homologados a la **ClasificaciÃ³n Internacional de Enfermedades (CIE-10)** de la OrganizaciÃ³n Mundial de la Salud, mientras que las pruebas de laboratorio y mediciones fisiolÃ³gicas son codificadas bajo el estÃ¡ndar universal **LOINC** (*Logical Observation Identifiers Names and Codes*). El microservicio y catÃ¡logo interno `ref_terminology` actÃºa como un intermediario ontolÃ³gico que traduce en tiempo de ejecuciÃ³n las nomenclaturas propietarias de cada IPS hacia sus equivalentes semÃ¡nticos normalizados.

### 17.3. Interoperabilidad TÃ©cnica
La dimensiÃ³n tÃ©cnica se resuelve proporcionando interfaces abiertas y protocolos de comunicaciÃ³n estÃ¡ndar:
- **Endpoints RESTful / JSON**: Intercambio de recursos FHIR R4 sobre HTTP/REST utilizando codificaciÃ³n JSON, facilitando la integraciÃ³n con aplicaciones web y sistemas hospitalarios modernos.
- **Adaptadores de ingesta para sistemas legados**: Procesador especializado para tramas de mensajerÃ­a **HL7 v2.x** delimitadas por pipes (`|`), permitiendo la captura de mensajes habituales de admisiÃ³n, alta y transferencia (`ADT^A01`, `ADT^A03`).
- **Ingesta tabular masiva**: Lector estructurado para archivos CSV de admisiones masivas de pacientes, habilitando la incorporaciÃ³n Ã¡gil de datos histÃ³ricos o provenientes de sistemas perifÃ©ricos no conectados al bus en tiempo real.

### 17.4. Gobernanza Organizacional
La gobernanza del ecosistema se articula mediante la definiciÃ³n formal de roles operacionales y la delimitaciÃ³n estricta de privilegios clÃ­nicos:
- Perfiles de usuario diferenciados en el esquema RBAC: `PACIENTE` (visualizaciÃ³n exclusiva de su propio expediente), `ADMISIONISTA` (registro demogrÃ¡fico y triaje), `MEDICO` (gestiÃ³n diagnÃ³stica y evoluciÃ³n) y `AUDITOR` (supervisiÃ³n de seguridad y mÃ©tricas globales).
- Registro exhaustivo de responsabilidades en la cadena de auditorÃ­a inmutable, permitiendo atribuir cada cambio a un actor especÃ­fico, una sede emisora y un instante de tiempo certero segÃºn las directrices de los comitÃ©s de gestiÃ³n clÃ­nica y custodia documental.

### 17.5. Herramientas TecnolÃ³gicas Utilizadas
- **HAPI FHIR Server (v8.12.0)**: Servidor canÃ³nico Java/JPA de referencia global para la gestiÃ³n y validaciÃ³n formal de recursos FHIR R4.
- **FastAPI / Uvicorn (Python 3)**: Entorno asÃ­ncrono de alto desempeÃ±o para el Bus de Servicios de Salud (HSB), dotado de documentaciÃ³n OpenAPI automÃ¡tica y soporte nativo para eventos asÃ­ncronos.
- **PostgreSQL 16 con extensiÃ³n Citus**: Sistema de gestiÃ³n de bases de datos relacional y distribuido para el particionamiento de historias clÃ­nicas a escala.

### 17.6. Herramientas SemÃ¡nticas
- **Componente `ref_terminology`**: Diccionario terminolÃ³gico relacional optimizado que contiene los catÃ¡logos cruzados de diagnÃ³sticos CIE-10 (ej. `J45.9`, `I10`, `A09`) y magnitudes de laboratorio LOINC (ej. `718-7` para hemoglobina, `2339-0` para glucosa). Este mÃ³dulo desacopla a los sistemas cliente de las reglas de homologaciÃ³n ontolÃ³gica, resolviendo inconsistencias sintÃ¡cticas antes del depÃ³sito en el repositorio distribuido.

---

## 18. VALIDACIÃ“N DE MODELOS UML

Los cuatro modelos de lenguaje unificado de modelado (UML) formalizados durante la etapa de diseÃ±o del sistema fueron sometidos a una verificaciÃ³n sistemÃ¡tica contra el comportamiento real del prototipo en ejecuciÃ³n:

1. **Diagrama de Casos de Uso**: Se validÃ³ exhaustivamente frente a la matriz de requerimientos y la rÃºbrica de evaluaciÃ³n, comprobando la materializaciÃ³n efectiva de los cuatro (4) roles definidos (`Paciente`, `Admisionista`, `MÃ©dico`, `Auditor`) y la ejecuciÃ³n completa de los ocho (8) casos de uso nucleares (bÃºsqueda de historial, registro de paciente, clasificaciÃ³n de triaje, asignaciÃ³n diagnÃ³stica, firma hash de evoluciÃ³n, visualizaciÃ³n de topologÃ­a de nodos, trazabilidad de auditorÃ­a y gestiÃ³n de colas de reintento) a travÃ©s de las rutas REST y las cuatro vistas interactivas del HSB.
2. **Diagrama de Secuencia**: Se contrastÃ³ analÃ­ticamente con las trazas de ejecuciÃ³n registradas durante las baterÃ­as de pruebas automatizadas (`test_01` a `test_04`). Se comprobÃ³ que el flujo cronolÃ³gico y los mensajes sincrÃ³nicos/asÃ­ncronos entre los objetos de software (Cliente Web $\rightarrow$ FastAPI Router $\rightarrow$ HSB Core $\rightarrow$ Validador Idempotencia $\rightarrow$ Normalizador FHIR $\rightarrow$ Conector Citus/HAPI) coinciden con la secuencia teÃ³rica modelada, registrando los cÃ³digos de estado `200 OK`, `403 Forbidden` y los bucles de reintento exponencial calculados.
3. **Diagrama de Clases**: Su validaciÃ³n se ejecutÃ³ verificando la correspondencia unÃ­voca entre las diez (10) entidades conceptuales del modelo de dominio y el esquema fÃ­sico DDL desplegado en el clÃºster Citus y las bases locales de las sedes (`patients`, `encounters`, `conditions`, `observations`, `audit_blocks`, `dlq_messages`, `users`, `roles`, `sites`, `terminology_mappings`). Los atributos, claves forÃ¡neas y relaciones de cardinalidad se reflejan fielmente en las tablas distribuidas.
4. **Diagrama de Estados**: Se validÃ³ forzando transiciones del ciclo de vida de los mensajes en el bus de interoperabilidad. Se verificaron satisfactoriamente las rutas de cambio de estado: recepciÃ³n ($\rightarrow$ `recibido`), verificaciÃ³n exitosa ($\rightarrow$ `entregado`), detecciÃ³n de duplicados por clave hash ($\rightarrow$ `duplicado`), error de validaciÃ³n de sintaxis o catÃ¡logo ($\rightarrow$ `rechazado`) y agotamiento de polÃ­ticas de reintento con derivaciÃ³n a la cola de contingencia ($\rightarrow$ `DLQ`), ratificando el determinismo formal del autÃ³mata de estados concebido.
