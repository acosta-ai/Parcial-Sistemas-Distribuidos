-- Esquema para Sede 1 (Sincelejo)
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
    motivo VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS observaciones (
    id SERIAL PRIMARY KEY,
    paciente_id INT REFERENCES pacientes(id),
    codigo_prueba VARCHAR(50) NOT NULL,
    nombre_prueba VARCHAR(100) NOT NULL,
    valor_numerico NUMERIC(6,2) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    fecha TIMESTAMP NOT NULL
);

-- Datos iniciales sede 1 (Carlos Perez, doc: 1001)
INSERT INTO pacientes (id, documento, nombre, sexo, nacimiento)
VALUES (1, '1001', 'Carlos Perez', 'M', '1980-04-12')
ON CONFLICT (documento) DO NOTHING;
