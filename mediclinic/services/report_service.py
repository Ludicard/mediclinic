"""
Servicio para generación y exportación de reportes clínicos y estadísticos.
"""

import os
import csv
import json
import tempfile
from typing import Dict, Any, List
from mediclinic.database import Database


class ReportService:
    """Provee estadísticas de atención médica e ingresos de la clínica."""

    def __init__(self, db: Database):
        self.db = db

    def get_clinic_summary(self) -> Dict[str, Any]:
        """Calcula el resumen general de pacientes, citas e ingresos proyectados."""
        total_patients = self.db.safe_query("SELECT COUNT(*) AS total FROM patients")[0]["total"]
        total_doctors = self.db.safe_query("SELECT COUNT(*) AS total FROM doctors")[0]["total"]
        
        appt_stats = self.db.safe_query("""
            SELECT 
                COUNT(*) AS total_appointments,
                SUM(final_fee) AS total_revenue,
                SUM(insurance_discount) AS total_discounts
            FROM appointments
        """)[0]

        specialty_distribution = self.db.safe_query("""
            SELECT d.specialty, COUNT(a.id) as count
            FROM doctors d
            LEFT JOIN appointments a ON d.id = a.doctor_id
            GROUP BY d.specialty
        """)

        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": appt_stats["total_appointments"] or 0,
            "total_revenue": round(appt_stats["total_revenue"] or 0.0, 2),
            "total_discounts": round(appt_stats["total_discounts"] or 0.0, 2),
            "specialty_distribution": specialty_distribution,
        }

    # Hallazgo de Seguridad (Bandit B306 / SonarQube):
    # Uso de función insegura mktemp() vulnerable a condiciones de carrera (Race Condition)
    def export_appointments_to_csv_insecure_temp(self, output_path: str = "") -> str:
        """
        Exporta las citas a un archivo temporal.
        ADVERTENCIA: Usa mktemp() intencionalmente para revisión estática de seguridad.
        """
        if not output_path:
            # Bandit B306: Use of insecure and deprecated function (mktemp)
            output_path = tempfile.mktemp(prefix="citas_mediclinic_", suffix=".csv")

        appointments = self.db.safe_query("""
            SELECT a.id, a.appointment_date, a.appointment_time, a.status, a.final_fee,
                   p.first_name || ' ' || p.last_name as paciente, d.full_name as doctor
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        """)

        fieldnames = ["id", "appointment_date", "appointment_time", "status", "final_fee", "paciente", "doctor"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in appointments:
                writer.writerow(row)

        return output_path

    def export_summary_json(self, output_file: str = "resumen_clinica.json") -> str:
        """Exporta el resumen estadístico a formato JSON."""
        summary = self.get_clinic_summary()
        with open(output_file, mode="w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        return output_file

