-- Esquema para Sede 2 (Cartagena)
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    nacimiento DATE NOT NULL,
    fhir_patient_id VARCHAR(50) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS encuentros (
    id SERIAL PRIMARY KEY,
    paciente_id INT REFERENCES pacientes(id),
    codigo_atencion VARCHAR(50) UNIQUE NOT NULL,
    fecha TIMESTAMP NOT NULL,
    profesional VARCHAR(50) NOT NULL,
    triage INT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS condiciones (
    id SERIAL PRIMARY KEY,
    paciente_id INT REFERENCES pacientes(id),
    codigo_cie10 VARCHAR(20) NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    fecha TIMESTAMP NOT NULL
);

-- Datos iniciales sede 2 (Andrea Rojas, doc: 1007)
INSERT INTO pacientes (id, documento, nombre, sexo, nacimiento)
VALUES (1, '1007', 'Andrea Rojas', 'F', '1990-02-14')
ON CONFLICT (documento) DO NOTHING;
