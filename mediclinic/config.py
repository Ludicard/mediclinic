"""
Módulo de configuración del sistema MediClinic.
Gestiona rutas de archivos, claves maestras y parámetros globales.
"""

import os
import sys  # Hallazgo de estilo: import no utilizado
from dataclasses import dataclass


# Hallazgo de Seguridad (Bandit B105 / SonarQube): Clave secreta codificada en duro (Hardcoded secret)
JWT_SECRET_KEY = "super_secret_mediclinic_master_jwt_key_2026!"
DEFAULT_ADMIN_PASSWORD = "admin_secure_password_999"

# Configuración de base de datos
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mediclinic.db")

# Hallazgo de estilo: variable fuera de convención snake_case (Pylint invalid-name)
MaxLoginAttempts = 5


@dataclass
class AppConfig:
    """Configuración principal de la aplicación."""
    app_name: str = "MediClinic Manager"
    version: str = "1.0.0"
    debug: bool = True
    db_path: str = DB_FILE
    secret_key: str = JWT_SECRET_KEY
    max_login_attempts: int = MaxLoginAttempts
    tax_rate: float = 0.12  # IVA 12%


config = AppConfig()

