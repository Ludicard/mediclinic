#!/usr/bin/env python3
"""
Punto de entrada principal para ejecutar el sistema MediClinic.
Inicializa la base de datos, inserta datos iniciales y arranca el menú interactivo.
"""

import sys
from mediclinic.database import Database
from mediclinic.services.auth_service import AuthService
from mediclinic.services.patient_service import PatientService
from mediclinic.services.appointment_service import AppointmentService
from mediclinic.cli.menu import CLIMenu


def bootstrap_application() -> Database:
    """Inicializa la infraestructura y los datos de prueba del sistema."""
    db = Database()
    db.init_schema()

    # Sembrado de usuarios y pacientes por defecto
    auth_service = AuthService(db)
    auth_service.seed_initial_users()

    patient_service = PatientService(db)
    patient_service.seed_initial_patients()

    # Sembrado de cita inicial si no existe ninguna
    appt_service = AppointmentService(db)
    existing_appts = appt_service.list_appointments()
    if not existing_appts:
        doctors = appt_service.get_doctors()
        patients = patient_service.get_all_patients()
        if doctors and patients:
            appt_service.schedule_appointment(
                patient_id=patients[0].id,
                doctor_id=doctors[0]["id"],
                appointment_date="2026-11-15",
                appointment_time="10:30",
                reason="Chequeo cardiovascular semestral",
                base_fee=60.0,
                insurance_discount=36.0,
                notes="Paciente asegurado con cobertura del 60%"
            )

    return db


def main():
    """Función principal."""
    print("Iniciando componentes de MediClinic...")
    db = bootstrap_application()
    try:
        menu = CLIMenu(db)
        menu.run()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario. Saliendo...")
    finally:
        db.close()


if __name__ == "__main__":
    main()

