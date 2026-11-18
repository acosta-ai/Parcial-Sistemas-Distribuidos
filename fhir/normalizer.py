import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

TERMINOLOGY_MAP = {
    "DIARREA": ("A09", "Diarrea y gastroenteritis"),
    "HIPERTENSION": ("I10", "Hipertensión esencial"),
    "DIABETES": ("E11.9", "Diabetes mellitus tipo 2"),
    "ASMA": ("J45.9", "Asma"),
    "INFECCION URINARIA": ("N39.0", "Infección de vías urinarias"),
    "LUMBAGO": ("M54.5", "Lumbago"),
    "NEUMONIA": ("J18.9", "Neumonía"),
    "CEFALEA": ("R51", "Cefalea")
}

def normalize_gender(sex: str) -> str:
    s = str(sex).strip().upper()
    if s in ["M", "MASCULINO", "MALE"]:
        return "male"
    elif s in ["F", "FEMENINO", "FEMALE"]:
        return "female"
    raise ValueError(f"Sexo no válido: '{sex}'")

def validate_document(doc: str) -> int:
    d_str = str(doc).strip()
    if not d_str.isdigit():
        raise ValueError(f"Documento no numérico: '{doc}'")
    if len(d_str) < 3:
        raise ValueError(f"Documento inválido (longitud < 3 dígitos): '{doc}'")
    return int(d_str)

def map_diagnosis(dx: str) -> Dict[str, str]:
    cleaned = str(dx).strip()
    # Si viene en formato HL7: CODIGO^DESCRIPCION^SISTEMA
    if "^" in cleaned:
        parts = cleaned.split("^")
        code_part = parts[0].strip().upper()
        display_part = parts[1].strip() if len(parts) > 1 else ""
        system_part = parts[2].strip() if len(parts) > 2 else ""
        
        # Si el sistema es 'L' (Local) o no es estándar CIE-10, debe validarse en la tabla
        if system_part == "L" or code_part not in ["A09", "I10", "E11.9", "J45.9", "N39.0", "M54.5", "J18.9", "R51"]:
            if code_part in TERMINOLOGY_MAP:
                c, d = TERMINOLOGY_MAP[code_part]
                return {"code": c, "display": display_part or d}
            else:
                raise ValueError(f"Diagnóstico local '{parts[0]}' sin mapeo a CIE-10")
        
        return {"code": code_part, "display": display_part or "Diagnóstico"}

    code_upper = cleaned.upper()
    if code_upper in TERMINOLOGY_MAP:
        code, display = TERMINOLOGY_MAP[code_upper]
        return {"code": code, "display": display}
    
    # Si ya es un código CIE-10 reconocido
    valid_cie10 = {v[0]: v[1] for v in TERMINOLOGY_MAP.values()}
    if code_upper in valid_cie10:
        return {"code": code_upper, "display": valid_cie10[code_upper]}

    raise ValueError(f"Diagnóstico local '{dx}' sin mapeo a CIE-10")

def build_fhir_bundle(
    patient_data: Dict[str, Any],
    encounter_data: Optional[Dict[str, Any]] = None,
    observation_data: Optional[Dict[str, Any]] = None,
    condition_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    doc_id = validate_document(patient_data["documento"])
    gender = normalize_gender(patient_data["sexo"])
    
    # Generar UUIDs válidos para transacciones FHIR R4
    pat_uuid = str(uuid.uuid4())
    pat_full_url = f"urn:uuid:{pat_uuid}"
    
    patient_resource = {
        "fullUrl": pat_full_url,
        "resource": {
            "resourceType": "Patient",
            "id": pat_uuid,
            "identifier": [
                {
                    "system": "urn:oid:co:ips:identificacion",
                    "value": str(doc_id)
                }
            ],
            "name": [
                {
                    "use": "official",
                    "text": patient_data["nombre"]
                }
            ],
            "gender": gender,
            "birthDate": patient_data.get("nacimiento", "1990-01-01")
        },
        "request": {
            "method": "POST",
            "url": "Patient"
        }
    }
    
    entries = [patient_resource]
    
    if encounter_data:
        enc_uuid = str(uuid.uuid4())
        enc_full_url = f"urn:uuid:{enc_uuid}"
        
        # Extraer profesional separado
        prof_raw = encounter_data.get("profesional", "MED-01")
        prof_parts = prof_raw.split("^")
        prof_code = prof_parts[0]
        prof_display = f"{prof_parts[1]} {prof_parts[2]}" if len(prof_parts) > 2 else prof_code
        
        enc_resource = {
            "fullUrl": enc_full_url,
            "resource": {
                "resourceType": "Encounter",
                "id": enc_uuid,
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": {
                    "reference": pat_full_url
                },
                "participant": [
                    {
                        "individual": {
                            "identifier": {
                                "value": prof_code
                            },
                            "display": prof_display
                        }
                    }
                ],
                "period": {
                    "start": encounter_data.get("fecha", datetime.now(timezone.utc).isoformat())
                }
            },
            "request": {
                "method": "POST",
                "url": "Encounter"
            }
        }
        if encounter_data.get("triage"):
            enc_resource["resource"]["priority"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/encounter-priority",
                        "code": str(encounter_data["triage"])
                    }
                ]
            }
        entries.append(enc_resource)
        
    if condition_data:
        dx_mapped = map_diagnosis(condition_data["dx"])
        cond_uuid = str(uuid.uuid4())
        cond_full_url = f"urn:uuid:{cond_uuid}"
        
        cond_resource = {
            "fullUrl": cond_full_url,
            "resource": {
                "resourceType": "Condition",
                "id": cond_uuid,
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }
                    ]
                },
                "subject": {
                    "reference": pat_full_url
                },
                "code": {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/sid/icd-10",
                            "code": dx_mapped["code"],
                            "display": dx_mapped["display"]
                        }
                    ]
                }
            },
            "request": {
                "method": "POST",
                "url": "Condition"
            }
        }
        entries.append(cond_resource)

    if observation_data:
        obs_uuid = str(uuid.uuid4())
        obs_full_url = f"urn:uuid:{obs_uuid}"
        
        obs_resource = {
            "fullUrl": obs_full_url,
            "resource": {
                "resourceType": "Observation",
                "id": obs_uuid,
                "status": "final",
                "subject": {
                    "reference": pat_full_url
                },
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": observation_data.get("loinc", "718-7"),
                            "display": observation_data.get("nombre_prueba", "Hemoglobina en sangre")
                        }
                    ]
                },
                "valueQuantity": {
                    "value": float(observation_data.get("valor", 0.0)),
                    "unit": observation_data.get("unidad", "g/dL"),
                    "system": "http://unitsofmeasure.org",
                    "code": observation_data.get("unidad", "g/dL")
                }
            },
            "request": {
                "method": "POST",
                "url": "Observation"
            }
        }
        entries.append(obs_resource)
        
    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": entries
    }
    return bundle
