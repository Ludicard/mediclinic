"""
Modelo de datos para Pacientes de la clínica.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Patient:
    """Entidad que almacena los datos personales y de seguro de un paciente."""
    dni: str
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: str
    blood_type: str = "O+"
    insurance_provider: str = "NINGUNO"
    id: Optional[int] = None
    created_at: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Devuelve el nombre completo del paciente."""
        return f"{self.first_name} {self.last_name}"

    def has_insurance(self) -> bool:
        """Indica si el paciente tiene aseguradora privada asignada."""
        return self.insurance_provider.strip().upper() not in ("NINGUNO", "NO", "SIN SEGURO", "")

    def to_dict(self) -> dict:
        """Convierte los datos del paciente a representación de diccionario."""
        return {
            "id": self.id,
            "dni": self.dni,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date,
            "blood_type": self.blood_type,
            "insurance_provider": self.insurance_provider,
            "created_at": self.created_at,
        }

