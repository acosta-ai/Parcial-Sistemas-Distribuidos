#!/bin/bash
set -e

echo "=== INICIANDO SCRIPT DE AUTOCONFIGURACIÓN DEL CLÚSTER CITUS ==="

# Esperar a que el coordinador y workers estén accesibles
echo "Esperando que citus_master esté disponible..."
until pg_isready -h citus_master -p 5432 -U postgres; do
  sleep 1
done

echo "Esperando que citus_worker1 esté disponible..."
until pg_isready -h citus_worker1 -p 5432 -U postgres; do
  sleep 1
done

echo "Esperando que citus_worker2 esté disponible..."
until pg_isready -h citus_worker2 -p 5432 -U postgres; do
  sleep 1
done

echo "Todos los nodos están listos. Registrando coordinador y workers..."

# Configurar contraseña para conexiones internas
export PGPASSWORD=postgrespassword

# 1. Registrar coordinador y workers en Citus
psql -h citus_master -p 5432 -U postgres -d citus_clinical_cdr << 'EOSQL'
SELECT citus_set_coordinator_host('citus_master', 5432);

-- Registrar workers (ignorando si ya existen)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM citus_get_active_worker_nodes() WHERE node_name = 'citus_worker1') THEN
        PERFORM citus_add_node('citus_worker1', 5432);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM citus_get_active_worker_nodes() WHERE node_name = 'citus_worker2') THEN
        PERFORM citus_add_node('citus_worker2', 5432);
    END IF;
END $$;

EOSQL

# 2. Ejecutar esquema completo de tablas distribuidas y auditoría
echo "Creando tablas distribuidas y de auditoría..."
psql -h citus_master -p 5432 -U postgres -d citus_clinical_cdr -f /scripts/init-citus.sql

echo "=== CLÚSTER CITUS INICIALIZADO Y LISTO AL 100% ==="
