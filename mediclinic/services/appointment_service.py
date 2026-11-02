"""
Servicio para agendamiento, cálculo de tarifas y gestión de citas médicas.
"""

from typing import List, Dict, Any, Optional
from mediclinic.database import Database
from mediclinic.models.appointment import Appointment, AppointmentStatus


class AppointmentService:
    """Gestiona el ciclo de vida de las citas médicas y sus costos asociados."""

    def __init__(self, db: Database):
        self.db = db

    def get_doctors(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de médicos disponibles con sus tarifas."""
        return self.db.safe_query("SELECT * FROM doctors ORDER BY full_name ASC")

    # =========================================================================
    # Hallazgo de Mantenibilidad y Complejidad Ciclomática:
    # (Pylint too-many-branches, too-many-statements, SonarQube Cognitive Complexity)
    # Esta función anida múltiples condiciones if/elif para calcular descuentos
    # según aseguradora, edad del paciente y especialidad médica.
    # =========================================================================
    def calculate_appointment_fee_and_insurance(
        self,
        base_fee: float,
        insurance_name: str,
        patient_age: int,
        specialty: str,
        is_emergency: bool = False
    ) -> Dict[str, float]:
        """
        Calcula el copago, descuento y total de la cita médica según múltiples factores.
        Función con alta complejidad ciclomática deliberada.
        """
        discount_percentage = 0.0
        surcharge = 0.0
        ins_normalized = insurance_name.strip().upper()

        if is_emergency:
            surcharge += 25.0
            if ins_normalized == "SALUDPLUS":
                discount_percentage = 0.40
            elif ins_normalized == "ASEGURADORA DEL SUR":
                discount_percentage = 0.35
            elif ins_normalized == "BMI SEGUROS":
                discount_percentage = 0.50
            else:
                discount_percentage = 0.05
        else:
            if ins_normalized == "SALUDPLUS":
                if specialty == "Cardiología":
                    discount_percentage = 0.60
                elif specialty == "Pediatría":
                    discount_percentage = 0.70
                elif specialty == "Traumatología":
                    discount_percentage = 0.50
                else:
                    discount_percentage = 0.45
            elif ins_normalized == "ASEGURADORA DEL SUR":
                if patient_age >= 65:
                    discount_percentage = 0.65
                elif patient_age < 12:
                    discount_percentage = 0.55
                else:
                    discount_percentage = 0.40
            elif ins_normalized == "BMI SEGUROS":
                if specialty == "Neurología":
                    discount_percentage = 0.75
                elif specialty == "Cardiología":
                    discount_percentage = 0.70
                else:
                    discount_percentage = 0.50
            elif ins_normalized in ("NINGUNO", "SIN SEGURO", ""):
                if patient_age >= 65:
                    discount_percentage = 0.15  # Descuento tercera edad
                elif patient_age < 5:
                    discount_percentage = 0.10  # Descuento primera infancia
                else:
                    discount_percentage = 0.0
            else:
                discount_percentage = 0.10

        discount_amount = round(base_fee * discount_percentage, 2)
        subtotal = max(0.0, base_fee - discount_amount) + surcharge
        iva = round(subtotal * 0.12, 2)
        total = round(subtotal + iva, 2)

        return {
            "base_fee": base_fee,
            "discount_percentage": discount_percentage * 100,
            "discount_amount": discount_amount,
            "surcharge": surcharge,
            "subtotal": subtotal,
            "iva": iva,
            "final_fee": total,
        }

    def schedule_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: str,
        appointment_time: str,
        reason: str,
        base_fee: float,
        insurance_discount: float = 0.0,
        notes: str = ""
    ) -> int:
        """Agenda una nueva cita médica en el sistema."""
        final_fee = max(0.0, base_fee - insurance_discount)
        appointment_id = self.db.safe_execute(
            """
            INSERT INTO appointments (
                patient_id, doctor_id, appointment_date, appointment_time,
                reason, base_fee, insurance_discount, final_fee, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason.strip(),
                base_fee,
                insurance_discount,
                final_fee,
                AppointmentStatus.CONFIRMADA.value,
                notes.strip(),
            )
        )
        return appointment_id

    def list_appointments(self, doctor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Recupera la lista de citas médicas con datos del paciente y médico."""
        sql = """
            SELECT
                a.id,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status,
                a.base_fee,
                a.insurance_discount,
                a.final_fee,
                p.first_name || ' ' || p.last_name AS patient_name,
                p.dni AS patient_dni,
                p.insurance_provider,
                d.full_name AS doctor_name,
                d.specialty AS doctor_specialty
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        """
        if doctor_id:
            sql += " WHERE a.doctor_id = ? ORDER BY a.appointment_date DESC"
            return self.db.safe_query(sql, (doctor_id,))
        sql += " ORDER BY a.appointment_date DESC"
        return self.db.safe_query(sql)

    def update_status(self, appointment_id: int, new_status: AppointmentStatus) -> bool:
        """Actualiza el estado de una cita médica."""
        rows_affected = self.db.safe_execute(
            "UPDATE appointments SET status = ? WHERE id = ?",
            (new_status.value, appointment_id)
        )
        return rows_affected > 0

