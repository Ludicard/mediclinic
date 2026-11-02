"""
Modelo de datos para Citas Médicas y Agenda.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AppointmentStatus(str, Enum):
    """Estados posibles de una cita médica."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


@dataclass
class Appointment:
    """Entidad que representa una cita médica reservada."""
    patient_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str
    reason: str
    base_fee: float
    insurance_discount: float = 0.0
    final_fee: float = 0.0
    status: AppointmentStatus = AppointmentStatus.PENDIENTE
    notes: Optional[str] = None
    id: Optional[int] = None

    def calculate_net_total(self) -> float:
        """Calcula el costo neto luego de aplicar el descuento de aseguradora."""
        discounted = max(0.0, self.base_fee - self.insurance_discount)
        self.final_fee = round(discounted, 2)
        return self.final_fee

    def to_dict(self) -> dict:
        """Serializa la cita a diccionario."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time,
            "reason": self.reason,
            "base_fee": self.base_fee,
            "insurance_discount": self.insurance_discount,
            "final_fee": self.final_fee,
            "status": str(self.status.value if isinstance(self.status, AppointmentStatus) else self.status),
            "notes": self.notes,
        }

