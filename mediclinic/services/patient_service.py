"""
Servicio para la gestión integral de pacientes en MediClinic.
Maneja el registro, búsqueda, actualización y consulta de pacientes.
"""

from typing import List, Optional, Dict, Any
from mediclinic.database import Database
from mediclinic.models.patient import Patient
from mediclinic.utils.validators import validate_email, validate_phone, validate_dni


class PatientService:
    """Provee métodos de negocio para operar sobre la tabla de pacientes."""

    def __init__(self, db: Database):
        self.db = db

    def seed_initial_patients(self) -> None:
        """Inserta pacientes de prueba si la base de datos está vacía."""
        count_res = self.db.safe_query("SELECT COUNT(*) as count FROM patients")
        if count_res and count_res[0]["count"] > 0:
            return

        sample_patients = [
            ("1712345678", "María", "López Morales", "maria.lopez@example.com", "0991234567", "1990-05-14", "O+", "SaludPlus"),
            ("0923456789", "Juan", "Pérez Gómez", "juan.perez@example.com", "0987654321", "1985-11-23", "A+", "Aseguradora del Sur"),
            ("1104567890", "Elena", "Torres Romero", "elena.torres@example.com", "0971122334", "1998-03-02", "B+", "NINGUNO"),
            ("0105678901", "Roberto", "Castillo Ortiz", "roberto.castillo@example.com", "0969988776", "1975-08-30", "O-", "BMI Seguros"),
        ]

        for dni, fn, ln, em, ph, bd, bt, ip in sample_patients:
            self.db.safe_execute(
                """
                INSERT INTO patients (dni, first_name, last_name, email, phone, birth_date, blood_type, insurance_provider)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (dni, fn, ln, em, ph, bd, bt, ip)
            )

    def register_patient(
        self,
        dni: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        birth_date: str,
        blood_type: str = "O+",
        insurance_provider: str = "NINGUNO"
    ) -> Patient:
        """Registra un nuevo paciente validando previamente los campos requeridos."""
        if not validate_dni(dni):
            raise ValueError(f"DNI/Cédula inválida: '{dni}'. Debe contener 10 dígitos numéricos.")
        if not validate_email(email):
            raise ValueError(f"Correo electrónico inválido: '{email}'.")
        if not validate_phone(phone):
            raise ValueError(f"Número de teléfono inválido: '{phone}'. Debe contener entre 7 y 15 dígitos.")

        existing = self.db.safe_query("SELECT id FROM patients WHERE dni = ?", (dni,))
        if existing:
            raise ValueError(f"Ya existe un paciente registrado con el DNI '{dni}'.")

        patient_id = self.db.safe_execute(
            """
            INSERT INTO patients (dni, first_name, last_name, email, phone, birth_date, blood_type, insurance_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (dni.strip(), first_name.strip(), last_name.strip(), email.strip(), phone.strip(), birth_date, blood_type, insurance_provider)
        )

        return Patient(
            id=patient_id,
            dni=dni,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            birth_date=birth_date,
            blood_type=blood_type,
            insurance_provider=insurance_provider
        )

    def get_all_patients(self) -> List[Patient]:
        """Recupera la lista completa de pacientes ordenados por apellido."""
        rows = self.db.safe_query("SELECT * FROM patients ORDER BY last_name ASC")
        return [self._map_row(r) for r in rows]

    def find_by_dni(self, dni: str) -> Optional[Patient]:
        """Busca un paciente de forma segura por su número de cédula."""
        rows = self.db.safe_query("SELECT * FROM patients WHERE dni = ?", (dni.strip(),))
        if rows:
            return self._map_row(rows[0])
        return None

    def search_patients_unsafe(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Búsqueda por nombre utilizando el método vulnerable a inyección SQL.
        Hallazgo didáctico para herramientas de análisis estático (Bandit / SonarQube).
        """
        return self.db.unsafe_raw_search("patients", "last_name", query_text)

    def _map_row(self, row: Dict[str, Any]) -> Patient:
        """Mapea una fila de base de datos a un objeto de dominio Patient."""
        return Patient(
            id=row["id"],
            dni=row["dni"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            birth_date=row["birth_date"],
            blood_type=row["blood_type"],
            insurance_provider=row["insurance_provider"],
            created_at=row["created_at"]
        )

