"""
Módulo de interfaz de usuario de consola (CLI) interactiva para MediClinic.
"""

import sys
from typing import Optional
from mediclinic.database import Database
from mediclinic.services.auth_service import AuthService
from mediclinic.services.patient_service import PatientService
from mediclinic.services.appointment_service import AppointmentService
from mediclinic.services.report_service import ReportService


class CLIMenu:
    """Controlador del menú de consola interactivo."""

    def __init__(self, db: Database):
        self.db = db
        self.auth_service = AuthService(db)
        self.patient_service = PatientService(db)
        self.appointment_service = AppointmentService(db)
        self.report_service = ReportService(db)

    def print_header(self) -> None:
        """Imprime el encabezado decorativo del sistema."""
        print("=" * 65)
        print("    🏥  SISTEMA DE GESTIÓN CLÍNICA Y CITAS MÉDICAS (MediClinic) 🏥")
        print("=" * 65)

    def print_menu(self) -> None:
        """Despliega las opciones disponibles en el menú principal."""
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Listar pacientes registrados")
        print("2. Buscar paciente por DNI (Búsqueda segura)")
        print("3. Búsqueda por texto (Demostración de vulnerabilidad SQL)")
        print("4. Registrar nuevo paciente")
        print("5. Listar citas médicas programadas")
        print("6. Agendar nueva cita médica")
        print("7. Simular cotización con aseguradora (Lógica de tarifas)")
        print("8. Ver resumen estadístico y exportar reporte")
        print("0. Salir")
        print("-" * 65)

    def run(self) -> None:
        """Bucle principal de ejecución del menú interactivo."""
        self.print_header()
        while True:
            self.print_menu()
            choice = input("Seleccione una opción: ").strip()

            if choice == "1":
                self._handle_list_patients()
            elif choice == "2":
                self._handle_find_patient_dni()
            elif choice == "3":
                self._handle_unsafe_search()
            elif choice == "4":
                self._handle_register_patient()
            elif choice == "5":
                self._handle_list_appointments()
            elif choice == "6":
                self._handle_schedule_appointment()
            elif choice == "7":
                self._handle_simulate_quote()
            elif choice == "8":
                self._handle_summary_report()
            elif choice == "0":
                print("\nGracias por utilizar MediClinic. ¡Hasta pronto!\n")
                break
            else:
                print("\n[!] Opción no reconocida. Intente nuevamente.")

    def _handle_list_patients(self) -> None:
        print("\n--- LISTA DE PACIENTES ---")
        patients = self.patient_service.get_all_patients()
        if not patients:
            print("No existen pacientes registrados.")
            return

        fmt = "{:<12} {:<24} {:<14} {:<20} {:<15}"
        print(fmt.format("DNI", "NOMBRE COMPLETO", "TELÉFONO", "SEGURO", "SANGRE"))
        print("-" * 85)
        for p in patients:
            print(fmt.format(p.dni, p.full_name, p.phone, p.insurance_provider, p.blood_type))

    def _handle_find_patient_dni(self) -> None:
        dni = input("\nIngrese el DNI/Cédula del paciente (10 dígitos): ").strip()
        patient = self.patient_service.find_by_dni(dni)
        if patient:
            print(f"\n[+] Paciente encontrado:")
            print(f"    - Nombre: {patient.full_name}")
            print(f"    - DNI: {patient.dni}")
            print(f"    - Correo: {patient.email}")
            print(f"    - Teléfono: {patient.phone}")
            print(f"    - Seguro Médico: {patient.insurance_provider}")
            print(f"    - Tipo de Sangre: {patient.blood_type}")
        else:
            print(f"\n[-] No se encontró ningún paciente con el DNI '{dni}'.")

    def _handle_unsafe_search(self) -> None:
        print("\n[AVISO] Esta función ejecuta una consulta concatenada vulnerable a SQL Injection.")
        term = input("Ingrese texto para buscar en apellidos de pacientes: ").strip()
        results = self.patient_service.search_patients_unsafe(term)
        print(f"\nResultados encontrados: {len(results)}")
        for r in results:
            print(f"  • {r.get('first_name')} {r.get('last_name')} (DNI: {r.get('dni')}, Seguro: {r.get('insurance_provider')})")

    def _handle_register_patient(self) -> None:
        print("\n--- REGISTRAR NUEVO PACIENTE ---")
        dni = input("DNI/Cédula (10 dígitos): ").strip()
        fn = input("Nombres: ").strip()
        ln = input("Apellidos: ").strip()
        em = input("Correo electrónico: ").strip()
        ph = input("Teléfono: ").strip()
        bd = input("Fecha de nacimiento (AAAA-MM-DD): ").strip()
        bt = input("Tipo de sangre (O+, A+, etc.) [Enter para O+]: ").strip() or "O+"
        ins = input("Aseguradora (SaludPlus, BMI Seguros, etc.) [Enter para NINGUNO]: ").strip() or "NINGUNO"

        try:
            nuevo = self.patient_service.register_patient(
                dni=dni, first_name=fn, last_name=ln, email=em,
                phone=ph, birth_date=bd, blood_type=bt, insurance_provider=ins
            )
            print(f"\n[✓] Paciente registrado con éxito (ID: {nuevo.id}).")
        except ValueError as err:
            print(f"\n[✗] Error de validación: {err}")

    def _handle_list_appointments(self) -> None:
        print("\n--- CITAS MÉDICAS REGISTRADAS ---")
        appts = self.appointment_service.list_appointments()
        if not appts:
            print("No hay citas médicas registradas en el sistema.")
            return

        fmt = "{:<4} {:<12} {:<6} {:<20} {:<20} {:<12} {:<10}"
        print(fmt.format("ID", "FECHA", "HORA", "PACIENTE", "MÉDICO", "ESTADO", "TOTAL ($)"))
        print("-" * 88)
        for a in appts:
            print(fmt.format(
                a["id"], a["appointment_date"], a["appointment_time"],
                a["patient_name"][:18], a["doctor_name"][:18], a["status"], f"${a['final_fee']:.2f}"
            ))

    def _handle_schedule_appointment(self) -> None:
        print("\n--- AGENDAR CITA MÉDICA ---")
        patients = self.patient_service.get_all_patients()
        doctors = self.appointment_service.get_doctors()

        if not patients or not doctors:
            print("Se requiere que existan pacientes y médicos en el sistema.")
            return

        print("\nMédicos disponibles:")
        for d in doctors:
            print(f"  [{d['id']}] {d['full_name']} - {d['specialty']} (Tarifa: ${d['consultation_fee']:.2f})")

        try:
            doc_id = int(input("\nID del médico seleccionado: ").strip())
            dni = input("DNI del paciente: ").strip()
            patient = self.patient_service.find_by_dni(dni)
            if not patient:
                print("[-] Paciente no encontrado con ese DNI.")
                return

            date_str = input("Fecha de la cita (AAAA-MM-DD): ").strip()
            time_str = input("Hora de la cita (HH:MM): ").strip()
            reason = input("Motivo de consulta: ").strip()

            selected_doc = next((d for d in doctors if d["id"] == doc_id), None)
            base_fee = selected_doc["consultation_fee"] if selected_doc else 50.0

            # Cálculo de descuento con la aseguradora
            quote = self.appointment_service.calculate_appointment_fee_and_insurance(
                base_fee=base_fee,
                insurance_name=patient.insurance_provider,
                patient_age=30,
                specialty=selected_doc["specialty"] if selected_doc else "General"
            )

            appt_id = self.appointment_service.schedule_appointment(
                patient_id=patient.id,
                doctor_id=doc_id,
                appointment_date=date_str,
                appointment_time=time_str,
                reason=reason,
                base_fee=quote["base_fee"],
                insurance_discount=quote["discount_amount"],
                notes=f"Seguro aplicado: {patient.insurance_provider} ({quote['discount_percentage']}%)"
            )

            print(f"\n[✓] Cita programada exitosamente (ID: {appt_id})")
            print(f"    - Tarifa Base: ${quote['base_fee']:.2f}")
            print(f"    - Descuento seguro: -${quote['discount_amount']:.2f} ({quote['discount_percentage']}%)")
            print(f"    - Subtotal: ${quote['subtotal']:.2f}")
            print(f"    - Total a pagar (IVA incl.): ${quote['final_fee']:.2f}")

        except ValueError as e:
            print(f"[-] Entrada inválida: {e}")

    def _handle_simulate_quote(self) -> None:
        print("\n--- SIMULADOR DE TARIFAS Y COPAGOS ---")
        try:
            fee = float(input("Tarifa base ($) [ej. 60.0]: ") or "60.0")
            ins = input("Aseguradora (SaludPlus / BMI Seguros / Aseguradora del Sur / NINGUNO): ").strip()
            age = int(input("Edad del paciente en años: ").strip() or "30")
            spec = input("Especialidad médica (Cardiología, Neurología, etc.): ").strip() or "General"
            is_emer = input("¿Es atención de emergencia? (s/n): ").strip().lower() == "s"

            res = self.appointment_service.calculate_appointment_fee_and_insurance(
                base_fee=fee, insurance_name=ins, patient_age=age, specialty=spec, is_emergency=is_emer
            )

            print("\n>>> DESGLOSE DE COTIZACIÓN <<<")
            print(f"  • Tarifa Base:           ${res['base_fee']:.2f}")
            print(f"  • Descuento Aseguradora: -${res['discount_amount']:.2f} ({res['discount_percentage']:.1f}%)")
            print(f"  • Recargo Emergencia:    +${res['surcharge']:.2f}")
            print(f"  • Subtotal:              ${res['subtotal']:.2f}")
            print(f"  • IVA (12%):             ${res['iva']:.2f}")
            print(f"  • TOTAL NETO:            ${res['final_fee']:.2f}")
        except ValueError as err:
            print(f"[-] Error en valores ingresados: {err}")

    def _handle_summary_report(self) -> None:
        print("\n--- RESUMEN ESTADÍSTICO DE LA CLÍNICA ---")
        summary = self.report_service.get_clinic_summary()
        print(f"  • Total de Pacientes Registrados: {summary['total_patients']}")
        print(f"  • Total de Médicos Activos:       {summary['total_doctors']}")
        print(f"  • Total de Citas Agendadas:       {summary['total_appointments']}")
        print(f"  • Ingresos Totales Proyectados:   ${summary['total_revenue']:.2f}")
        print(f"  • Descuentos Otorgados:          ${summary['total_discounts']:.2f}")

        csv_path = self.report_service.export_appointments_to_csv_insecure_temp()
        json_path = self.report_service.export_summary_json()
        print(f"\n[✓] Reporte CSV exportado en: {csv_path}")
        print(f"[✓] Resumen JSON exportado en: {json_path}")

