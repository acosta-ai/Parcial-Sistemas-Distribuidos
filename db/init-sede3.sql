-- Esquema para Sede 3 (Corozal - Legado CSV)
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    nacimiento DATE NOT NULL,
    fhir_patient_id VARCHAR(50) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS atenciones_legadas (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    nacimiento DATE NOT NULL,
    dx_local VARCHAR(50) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    triage INT DEFAULT NULL,
    profesional VARCHAR(50) NOT NULL
);
