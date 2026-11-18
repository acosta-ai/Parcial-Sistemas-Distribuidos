import requests
import json
import time

BASE = "http://localhost:8000"

def test_all():
    print("=== 1. TEST HEALTH ===")
    r = requests.get(f"{BASE}/health")
    print(r.json())

    print("\n=== 2. TEST HL7 VALIDO SEDE 2 (ANDREA ROJAS) ===")
    with open("data/01_adt_a01_valido_sede2.hl7") as f:
        data1 = f.read()
    r1 = requests.post(f"{BASE}/api/ingest/hl7", data=data1)
    print("Status:", r1.status_code, r1.json())

    print("\n=== 3. TEST IDEMPOTENCIA (REENVIO MENSAJE 1) ===")
    r2 = requests.post(f"{BASE}/api/ingest/hl7", data=data1)
    print("Status:", r2.status_code, r2.json())

    print("\n=== 4. TEST HL7 INVALIDO (RECHAZO ESPERADO CON MOTIVOS) ===")
    with open("data/03_adt_a01_invalido.hl7") as f:
        data3 = f.read()
    r3 = requests.post(f"{BASE}/api/ingest/hl7", data=data3)
    print("Status:", r3.status_code, r3.json())

    print("\n=== 5. TEST CSV SEDE 3 (3 ENTREGADOS, 2 RECHAZADOS) ===")
    with open("data/04_sede3_legado.csv") as f:
        data4 = f.read()
    r4 = requests.post(f"{BASE}/api/ingest/csv", data=data4)
    print("Status:", r4.status_code, r4.json())

    print("\n=== 6. TEST METRICAS Y DEAD LETTER QUEUE (DLQ) ===")
    r5 = requests.get(f"{BASE}/metrics")
    print("Metricas:", r5.json())

if __name__ == "__main__":
    test_all()
