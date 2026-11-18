import unittest
from fhir.normalizer import (
    normalize_gender,
    validate_document,
    map_diagnosis,
    build_fhir_bundle
)

class TestNormalizerFHIR(unittest.TestCase):

    def test_01_normalize_gender(self):
        self.assertEqual(normalize_gender("M"), "male")
        self.assertEqual(normalize_gender("F"), "female")
        self.assertEqual(normalize_gender("masculino"), "male")
        self.assertEqual(normalize_gender("FEMENINO"), "female")
        with self.assertRaises(ValueError):
            normalize_gender("X")

    def test_02_validate_document(self):
        self.assertEqual(validate_document("1007"), 1007)
        self.assertEqual(validate_document(1008), 1008)
        with self.assertRaises(ValueError):
            validate_document("ABC123")
        with self.assertRaises(ValueError):
            validate_document("12")

    def test_03_map_diagnosis(self):
        # Mapeo por catálogo
        res = map_diagnosis("ASMA")
        self.assertEqual(res["code"], "J45.9")
        self.assertEqual(res["display"], "Asma")

        # Formato HL7 estándar
        res2 = map_diagnosis("J45.9^Asma^I10")
        self.assertEqual(res2["code"], "J45.9")

        # Diagnóstico inválido
        with self.assertRaises(ValueError):
            map_diagnosis("DOLOR MISTERIOSO")

    def test_04_build_fhir_bundle_transaction(self):
        pat = {
            "documento": "1007",
            "nombre": "Andrea Rojas",
            "sexo": "F",
            "nacimiento": "1995-05-12"
        }
        enc = {
            "codigo_atencion": "V-001",
            "profesional": "MED-02^Ruiz^Mateo",
            "triage": 3
        }
        cond = {"dx": "ASMA"}

        bundle = build_fhir_bundle(pat, encounter_data=enc, condition_data=cond)
        
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "transaction")
        self.assertTrue(len(bundle["entry"]) >= 3)
        
        # Verificar request POST para HAPI
        for entry in bundle["entry"]:
            self.assertEqual(entry["request"]["method"], "POST")
            self.assertTrue(entry["fullUrl"].startswith("urn:uuid:"))

if __name__ == "__main__":
    unittest.main()
