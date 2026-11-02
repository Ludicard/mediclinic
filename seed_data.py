#!/usr/bin/env python3
"""
Script para poblar la base de datos de MediClinic con datos de ejemplo realistas.
Permite inicializar pacientes, doctores, usuarios y citas médicas con cálculos de seguros.
"""

import sys
import argparse
from datetime import datetime
from mediclinic.database import Database
from mediclinic.models.user import UserRole
from mediclinic.models.appointment import AppointmentStatus
from mediclinic.utils.security import hash_password_sha256, hash_password_md5
from mediclinic.services.appointment_service import AppointmentService


# =====================================================================
# DATOS DE PRUEBA REALISTAS
# =====================================================================

DOCTORS_DATA = [
    {
        "username": "dr.garcia",
        "full_name": "Dr. Carlos García",
        "specialty": "Cardiología",
        "license": "MED-8842",
        "fee": 60.0,
        "password": "doctor123"
    },
    {
        "username": "dra.morales",
        "full_name": "Dra. Elena Morales",
        "specialty": "Pediatría",
        "license": "MED-9104",
        "fee": 45.0,
        "password": "doctor123"
    },
    {
        "username": "dr.mendoza",
        "full_name": "Dr. Fernando Mendoza",
        "specialty": "Neurología",
        "license": "MED-7731",
        "fee": 75.0,
        "password": "doctor123"
    },
    {
        "username": "dra.andrade",
        "full_name": "Dra. Sofía Andrade",
        "specialty": "Traumatología",
        "license": "MED-6520",
        "fee": 55.0,
        "password": "doctor123"
    },
    {
        "username": "dr.benitez",
        "full_name": "Dr. Gabriel Benítez",
        "specialty": "Medicina General",
        "license": "MED-5411",
        "fee": 35.0,
        "password": "doctor123"
    },
    {
        "username": "dra.herrera",
        "full_name": "Dra. Valeria Herrera",
        "specialty": "Dermatología",
        "license": "MED-4398",
        "fee": 50.0,
        "password": "doctor123"
    },
]

STAFF_USERS = [
    ("admin", "admin_secure_password_999", "Administrador Principal", UserRole.ADMIN, "sha256"),
    ("recepcion", "recepcion123", "Ana Martínez (Recepción)", UserRole.RECEPCION, "md5"),
    ("caja_central", "caja2026", "Luis Romero (Caja y Facturación)", UserRole.RECEPCION, "sha256"),
]

PATIENTS_DATA = [
    ("1712345678", "María", "López Morales", "maria.lopez@email.com", "0991234567", "1990-05-14", "O+", "SaludPlus"),
    ("0923456789", "Juan", "Pérez Gómez", "juan.perez@email.com", "0987654321", "1985-11-23", "A+", "Aseguradora del Sur"),
    ("1104567890", "Elena", "Torres Romero", "elena.torres@email.com", "0971122334", "1998-03-02", "B+", "NINGUNO"),
    ("0105678901", "Roberto", "Castillo Ortiz", "roberto.castillo@email.com", "0969988776", "1954-08-30", "O-", "BMI Seguros"),
    ("1723456782", "Carmen", "Vásquez Díaz", "carmen.vasquez@email.com", "0995544332", "1972-12-05", "AB+", "SaludPlus"),
    ("0918765432", "Andrés", "Salazar Vega", "andres.salazar@email.com", "0982233445", "2018-04-18", "O+", "Aseguradora del Sur"),
    ("1709876543", "Patricia", "Flores Cárdenas", "patricia.flores@email.com", "0976655443", "1948-09-12", "A-", "NINGUNO"),
    ("1801234567", "Santiago", "Guzmán Paredes", "santiago.guzman@email.com", "0954433221", "2001-01-25", "B-", "BMI Seguros"),
    ("0702345678", "Lucía", "Paredes Rivas", "lucia.paredes@email.com", "0998877665", "1993-07-19", "O+", "SaludPlus"),
    ("1203456789", "Diego", "Moreno Cabrera", "diego.moreno@email.com", "0981122334", "1988-10-10", "A+", "NINGUNO"),
    ("1719876543", "Valentina", "Chávez León", "valentina.chavez@email.com", "0978899001", "2021-06-30", "O+", "SaludPlus"),
    ("0601234567", "Mateo", "Suárez Aguilar", "mateo.suarez@email.com", "0961122445", "1960-03-15", "O+", "BMI Seguros"),
]

APPOINTMENTS_TEMPLATES = [
    # (patient_idx, doc_idx, date, time, reason, status, is_emergency)
    (0, 0, "2026-11-10", "09:00", "Control de arritmia y presión arterial", AppointmentStatus.COMPLETADA, False),
    (1, 4, "2026-11-10", "10:30", "Chequeo médico general preventivo", AppointmentStatus.COMPLETADA, False),
    (2, 3, "2026-11-11", "11:15", "Dolor lumbar agudo post esfuerzo", AppointmentStatus.COMPLETADA, False),
    (3, 2, "2026-11-12", "14:00", "Evaluación de cefalea tensional recurrente", AppointmentStatus.COMPLETADA, False),
    (4, 5, "2026-11-13", "15:30", "Revisión dermatológica por dermatitis", AppointmentStatus.COMPLETADA, False),
    (5, 1, "2026-11-14", "08:30", "Control pediátrico de desarrollo (6 años)", AppointmentStatus.COMPLETADA, False),
    (6, 0, "2026-11-15", "09:45", "Chequeo cardiovascular semestral adulto mayor", AppointmentStatus.CONFIRMADA, False),
    (7, 2, "2026-11-15", "11:00", "Seguimiento de migraña con aura", AppointmentStatus.CONFIRMADA, False),
    (8, 5, "2026-11-16", "10:00", "Control de acné y evaluación cutánea", AppointmentStatus.CONFIRMADA, False),
    (9, 3, "2026-11-16", "16:00", "Esguince de tobillo derecho por deporte", AppointmentStatus.CONFIRMADA, True),
    (10, 1, "2026-11-17", "09:15", "Vacunación y control de 5 años", AppointmentStatus.PENDIENTE, False),
    (11, 4, "2026-11-17", "11:30", "Fiebre persistente y malestar general", AppointmentStatus.PENDIENTE, False),
    (0, 0, "2026-11-18", "08:00", "Ecocardiograma de control", AppointmentStatus.PENDIENTE, False),
    (3, 3, "2026-11-19", "15:00", "Control de artrosis de rodilla", AppointmentStatus.PENDIENTE, False),
    (2, 4, "2026-11-12", "16:30", "Cancelación por fuerza mayor del paciente", AppointmentStatus.CANCELADA, False),
]


def calculate_age(birth_date_str: str) -> int:
    """Calcula la edad en años a partir de fecha AAAA-MM-DD."""
    try:
        b_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
        return max(0, age)
    except Exception:
        return 30


def seed_database(reset: bool = False) -> None:
    """Llena la base de datos con doctores, pacientes, usuarios y citas médicas."""
    db = Database()
    db.init_schema()
    conn = db.get_connection()
    cursor = conn.cursor()

    if reset:
        print("[!] Limpiando tablas existentes...")
        cursor.execute("DELETE FROM appointments")
        cursor.execute("DELETE FROM doctors")
        cursor.execute("DELETE FROM patients")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        print("[✓] Tablas reiniciadas.")

    print("\n--- POBLANDO BASE DE DATOS MEDINIC ---")

    # 1. Insertar personal administrativo
    users_added = 0
    for username, raw_pass, name, role, hash_type in STAFF_USERS:
        existing = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not existing:
            p_hash = hash_password_sha256(raw_pass) if hash_type == "sha256" else hash_password_md5(raw_pass)
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, p_hash, name, role.value)
            )
            users_added += 1

    # 2. Insertar Doctores y sus usuarios correspondientes
    doctors_added = 0
    doctor_id_map = []
    for d in DOCTORS_DATA:
        existing_doc = cursor.execute("SELECT id FROM doctors WHERE license_number = ?", (d["license"],)).fetchone()
        if existing_doc:
            doctor_id_map.append(existing_doc[0])
            continue

        # Crear usuario para el médico si no existe
        existing_u = cursor.execute("SELECT id FROM users WHERE username = ?", (d["username"],)).fetchone()
        if not existing_u:
            p_hash = hash_password_sha256(d["password"])
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (d["username"], p_hash, d["full_name"], UserRole.DOCTOR.value)
            )
            user_id = cursor.lastrowid
        else:
            user_id = existing_u[0]

        cursor.execute(
            """
            INSERT INTO doctors (user_id, full_name, specialty, license_number, consultation_fee)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, d["full_name"], d["specialty"], d["license"], d["fee"])
        )
        doctor_id_map.append(cursor.lastrowid)
        doctors_added += 1

    conn.commit()

    # 3. Insertar Pacientes
    patients_added = 0
    patient_id_map = []
    for dni, fn, ln, em, ph, bd, bt, ins in PATIENTS_DATA:
        existing_p = cursor.execute("SELECT id FROM patients WHERE dni = ?", (dni,)).fetchone()
        if existing_p:
            patient_id_map.append((existing_p[0], bd, ins))
            continue

        cursor.execute(
            """
            INSERT INTO patients (dni, first_name, last_name, email, phone, birth_date, blood_type, insurance_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (dni, fn, ln, em, ph, bd, bt, ins)
        )
        patient_id_map.append((cursor.lastrowid, bd, ins))
        patients_added += 1

    conn.commit()

    # 4. Insertar Citas Médicas con cálculo de tarifas
    appts_added = 0
    appt_service = AppointmentService(db)

    # Recuperar doctores actualizados
    doctors_db = db.safe_query("SELECT id, full_name, specialty, consultation_fee FROM doctors")
    doc_lookup = {d["id"]: d for d in doctors_db}

    for p_idx, d_idx, date_str, time_str, reason, status, is_emerg in APPOINTMENTS_TEMPLATES:
        if p_idx >= len(patient_id_map) or d_idx >= len(doctor_id_map):
            continue

        p_id, b_date, ins_provider = patient_id_map[p_idx]
        d_id = doctor_id_map[d_idx]
        doc_info = doc_lookup.get(d_id)
        if not doc_info:
            continue

        patient_age = calculate_age(b_date)
        base_fee = doc_info["consultation_fee"]
        specialty = doc_info["specialty"]

        # Calcular seguro según reglas de la app
        quote = appt_service.calculate_appointment_fee_and_insurance(
            base_fee=base_fee,
            insurance_name=ins_provider,
            patient_age=patient_age,
            specialty=specialty,
            is_emergency=is_emerg
        )

        # Evitar duplicar cita idéntica en misma fecha/hora
        duplicate = cursor.execute(
            "SELECT id FROM appointments WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?",
            (d_id, date_str, time_str)
        ).fetchone()

        if not duplicate:
            cursor.execute(
                """
                INSERT INTO appointments (
                    patient_id, doctor_id, appointment_date, appointment_time,
                    reason, base_fee, insurance_discount, final_fee, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p_id,
                    d_id,
                    date_str,
                    time_str,
                    reason,
                    quote["base_fee"],
                    quote["discount_amount"],
                    quote["final_fee"],
                    status.value,
                    f"Seguro: {ins_provider} (Desc: {quote['discount_percentage']:.0f}%, Emergencia: {'Sí' if is_emerg else 'No'})"
                )
            )
            appts_added += 1

    conn.commit()

    # Totales en base de datos
    tot_patients = cursor.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    tot_doctors = cursor.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    tot_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    tot_appts = cursor.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]

    print(f"\n[✓] Poblado completado con éxito:")
    print(f"    • Pacientes registrados: {tot_patients} (+{patients_added} nuevos)")
    print(f"    • Médicos especialistas: {tot_doctors} (+{doctors_added} nuevos)")
    print(f"    • Usuarios en sistema:   {tot_users} (+{users_added} nuevos)")
    print(f"    • Citas programadas:     {tot_appts} (+{appts_added} nuevas)")
    print("\nLa base de datos SQLite 'mediclinic.db' está lista para ser consultada.")

    db.close()


def main():
    parser = argparse.ArgumentParser(description="Poblador de base de datos para MediClinic.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra los datos existentes y siembra desde cero."
    )
    args = parser.parse_args()
    seed_database(reset=args.reset)


if __name__ == "__main__":
    main()
