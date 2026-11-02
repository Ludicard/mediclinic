"""
Módulo de validaciones de formatos de entrada de datos.
Contiene validaciones para correos, teléfonos, documentos de identidad y fechas.
"""

import re
from typing import Tuple, List, Optional


def validate_email(email: str) -> bool:
    """Valida el formato básico de una dirección de correo electrónico."""
    if not email or not isinstance(email, str):
        return False
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(regex, email.strip()))


def validate_phone(phone: str) -> bool:
    """Valida que el número telefónico tenga entre 7 y 15 dígitos numéricos."""
    if not phone or not isinstance(phone, str):
        return False
    clean_digits = re.sub(r"\D", "", phone)
    return 7 <= len(clean_digits) <= 15


def validate_dni(dni: str) -> bool:
    """Valida formato de cédula/DNI de 10 dígitos numéricos."""
    if not dni or not isinstance(dni, str):
        return False
    cleaned = dni.strip()
    return cleaned.isdigit() and len(cleaned) == 10


# =====================================================================
# Hallazgo de Código Duplicado (Pylint duplicate-code / SonarQube):
# Las siguientes dos funciones duplican exactamente la misma lógica de
# validación y formateo con ligeras variantes en mensajes de error.
# =====================================================================

def validate_patient_contact_info(email: str, phone: str, address: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Valida la información de contacto completa de un paciente."""
    errors = []
    unused_debug_counter = 0  # Hallazgo de estilo: variable local no utilizada

    if not email or not isinstance(email, str):
        errors.append("El correo del paciente no puede estar vacío.")
    elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email.strip()):
        errors.append("El formato del correo del paciente es inválido.")

    if not phone or not isinstance(phone, str):
        errors.append("El teléfono del paciente no puede estar vacío.")
    else:
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7 or len(digits) > 15:
            errors.append("El teléfono del paciente debe contener entre 7 y 15 dígitos.")

    if address is not None and len(address.strip()) < 5:
        errors.append("La dirección del paciente debe tener al menos 5 caracteres.")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_doctor_contact_info(email: str, phone: str, office_address: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Valida la información de contacto completa de un médico (Copia casi idéntica a la anterior)."""
    errors = []
    unused_debug_counter = 0  # Hallazgo de estilo: variable local no utilizada

    if not email or not isinstance(email, str):
        errors.append("El correo del doctor no puede estar vacío.")
    elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email.strip()):
        errors.append("El formato del correo del doctor es inválido.")

    if not phone or not isinstance(phone, str):
        errors.append("El teléfono del doctor no puede estar vacío.")
    else:
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7 or len(digits) > 15:
            errors.append("El teléfono del doctor debe contener entre 7 y 15 dígitos.")

    if office_address is not None and len(office_address.strip()) < 5:
        errors.append("La dirección del consultorio debe tener al menos 5 caracteres.")

    is_valid = len(errors) == 0
    return is_valid, errors

