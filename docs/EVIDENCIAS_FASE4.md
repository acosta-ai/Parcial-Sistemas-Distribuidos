# EVIDENCIAS OFICIALES - FASE 4: SEGURIDAD, RESILIENCIA Y OBSERVABILIDAD

## 1. Evidencia Control de Acceso Basado en Roles (RBAC con JWT)
```text
=== 1. GENERACIÓN Y VALIDACIÓN DE TOKENS JWT (RBAC) ===
Token Médico (Rol MEDICO): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...
Acceso a /api/diagnosticar con Rol MEDICO: PERMITIDO (200 OK)
Acceso a /api/diagnosticar con Rol PACIENTE: DENEGADO (403 Forbidden)
```
**Análisis Técnico:**
Se implementa autenticación basada en JSON Web Tokens (JWT) firmados criptográficamente. El middleware HSB valida las firmas y los claims del payload, autorizando al personal médico el registro de encuentros y diagnósticos clínicos mientras restringe y deniega (HTTP 403 Forbidden) a usuarios con rol Paciente, en estricto cumplimiento de la Ley 1581/2012 de Protección de Datos Personales.

## 2. Evidencia Integridad de Auditoría (Hash-Chain Inmutable)
```text
=== 2. VERIFICACIÓN DE CADENA DE AUDITORÍA (HASH CHAIN) ===
Total bloques en la cadena de auditoría: 4
INTEGRIDAD DE AUDITORÍA: VÁLIDA (Cadena de Hash inmutable verificada al 100%)
```
**Análisis Técnico:**
Cada transacción de ingestión y acceso a datos clínicos genera un bloque de auditoría donde `current_hash = SHA-256(prev_hash + data)`. El script de verificación recorre la secuencia desde el bloque génesis; cualquier alteración de registros en las tablas distribuidas rompería el encadenamiento de manera inmediata e irreversible, garantizando no repudio y trazabilidad clínica.
