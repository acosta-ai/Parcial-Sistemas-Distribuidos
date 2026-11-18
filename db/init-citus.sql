-- Esquema de Tablas Distribuidas y de Integración para Citus
CREATE EXTENSION IF NOT EXISTS citus;

-- 1. Tabla de Mensajes del Bus (Persistencia de Idempotencia y Estado)
CREATE TABLE IF NOT EXISTS mensaje_bus (
    message_id VARCHAR(100) PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,
    sede_origen VARCHAR(20) NOT NULL,
    formato VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL, -- recibido, reintentando, entregado, muerto
    intentos INT DEFAULT 0,
    payload_raw TEXT,
    fecha_ingesta TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de Dead Letter Queue (DLQ) Persistente
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    dlq_id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(100) NOT NULL,
    motivos TEXT NOT NULL,
    fecha_descarte TIMESTAMP DEFAULT NOW()
);

-- 3. Tabla de Referencia Terminológica (Replicada en todos los nodos)
CREATE TABLE IF NOT EXISTS ref_terminology (
    dx_local VARCHAR(50) PRIMARY KEY,
    cie10 VARCHAR(20) NOT NULL,
    descripcion VARCHAR(200) NOT NULL
);
SELECT create_reference_table('ref_terminology');

INSERT INTO ref_terminology (dx_local, cie10, descripcion) VALUES
('DIARREA', 'A09', 'Diarrea y gastroenteritis'),
('HIPERTENSION', 'I10', 'Hipertensión esencial'),
('DIABETES', 'E11.9', 'Diabetes mellitus tipo 2'),
('ASMA', 'J45.9', 'Asma'),
('INFECCION URINARIA', 'N39.0', 'Infección de vías urinarias'),
('LUMBAGO', 'M54.5', 'Lumbago'),
('NEUMONIA', 'J18.9', 'Neumonía'),
('CEFALEA', 'R51', 'Cefalea')
ON CONFLICT (dx_local) DO NOTHING;

-- 4. Tablas Distribuidas Clínicas (Particionadas por patient_id)
CREATE TABLE IF NOT EXISTS distributed_patient (
    patient_id BIGINT NOT NULL,
    documento VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    nacimiento DATE NOT NULL,
    sede_origen VARCHAR(20) NOT NULL,
    fhir_id VARCHAR(50),
    PRIMARY KEY (patient_id)
);
SELECT create_distributed_table('distributed_patient', 'patient_id');

CREATE TABLE IF NOT EXISTS distributed_encounter (
    encounter_id BIGSERIAL,
    patient_id BIGINT NOT NULL,
    codigo_atencion VARCHAR(50) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    triage INT,
    profesional VARCHAR(100),
    sede VARCHAR(20) NOT NULL,
    PRIMARY KEY (patient_id, encounter_id),
    CONSTRAINT uq_patient_encounter UNIQUE (patient_id, codigo_atencion)
);
SELECT create_distributed_table('distributed_encounter', 'patient_id');

CREATE TABLE IF NOT EXISTS distributed_condition (
    condition_id BIGSERIAL,
    patient_id BIGINT NOT NULL,
    cie10_code VARCHAR(20) NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    sede VARCHAR(20) NOT NULL,
    PRIMARY KEY (patient_id, condition_id)
);
SELECT create_distributed_table('distributed_condition', 'patient_id');

CREATE TABLE IF NOT EXISTS distributed_observation (
    observation_id BIGSERIAL,
    patient_id BIGINT NOT NULL,
    loinc_code VARCHAR(20) NOT NULL,
    nombre_prueba VARCHAR(100) NOT NULL,
    valor_numerico DECIMAL,
    unidad VARCHAR(20),
    fecha TIMESTAMP NOT NULL,
    sede VARCHAR(20) NOT NULL,
    PRIMARY KEY (patient_id, observation_id)
);
SELECT create_distributed_table('distributed_observation', 'patient_id');

-- 5. Tabla de Auditoría Inmutable (Hash Chain)
CREATE TABLE IF NOT EXISTS audit_event_chain (
    block_index BIGSERIAL PRIMARY KEY,
    prev_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    patient_id BIGINT,
    data_payload TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Bloque Génesis si no existe
INSERT INTO audit_event_chain (block_index, prev_hash, current_hash, action, user_id, role, patient_id, data_payload)
SELECT 0, '0000000000000000000000000000000000000000000000000000000000000000', 
       'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
       'GENESIS', 'SYSTEM', 'SYSTEM', 0, 'GENESIS_BLOCK'
WHERE NOT EXISTS (SELECT 1 FROM audit_event_chain WHERE block_index = 0);
