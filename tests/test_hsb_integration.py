import requests
import time
import os

BASE_URL = "http://localhost:8000"

def run_tests():
    print("=== INICIANDO PRUEBAS OFICIALES DEL HSB ===")
    
    # 1. Health check
    print("\n1. Verificando /health...")
    r = requests.get(f"{BASE_URL}/health")
    print(r.json())
    
    # 2. Prueba 01_adt_a01_valido_sede2.hl7
    print("\n2. Ingesta HL7 v2 Válido Sede 2 (Andrea Rojas - Asma J45.9)...")
    with open("data/01_adt_a01_valido_sede2.hl7", "r") as f:
        payload = f.read()
    r = requests.post(f"{BASE_URL}/api/ingest/hl7", data=payload)
    print("Respuesta:", r.json())
    
    # 3. Idempotencia: Reenviar 01_adt_a01
    print("\n3. Probando Idempotencia (Reenviar mismo mensaje)...")
    r = requests.post(f"{BASE_URL}/api/ingest/hl7", data=payload)
    print("Respuesta (debe ser duplicado):", r.json())
    
    # 4. Ingesta HL7 v2 Inválido (03_adt_a01_invalido.hl7)
    print("\n4. Ingesta HL7 v2 Inválido (Debe ser rechazado con 3 motivos)...")
    with open("data/03_adt_a01_invalido.hl7", "r") as f:
        payload_inv = f.read()
    r = requests.post(f"{BASE_URL}/api/ingest/hl7", data=payload_inv)
    print("Respuesta:", r.json())

    # 5. Ingesta CSV Legado Sede 3 (04_sede3_legado.csv)
    print("\n5. Ingesta CSV Legado Sede 3 (3 entregados, 2 rechazados)...")
    with open("data/04_sede3_legado.csv", "r") as f:
        payload_csv = f.read()
    r = requests.post(f"{BASE_URL}/api/ingest/csv", data=payload_csv)
    print("Respuesta:", r.json())

    # 6. Consultar Métricas y DLQ
    print("\n6. Consultando Métricas del HSB (/metrics)...")
    r = requests.get(f"{BASE_URL}/metrics")
    print("Métricas:", r.json())

if __name__ == "__main__":
    run_tests()
