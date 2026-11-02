"""
Modelo de datos para Usuarios del sistema.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """Roles disponibles en la clínica."""
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    RECEPCION = "RECEPCION"


@dataclass
class User:
    """Entidad que representa a un usuario autorizado en el sistema."""
    username: str
    password_hash: str
    full_name: str
    role: UserRole
    id: Optional[int] = None
    created_at: Optional[str] = None

    def is_admin(self) -> bool:
        """Verifica si el usuario cuenta con permisos administrativos."""
        return self.role == UserRole.ADMIN

    def is_doctor(self) -> bool:
        """Verifica si el usuario es un médico."""
        return self.role == UserRole.DOCTOR

    def to_dict(self) -> dict:
        """Serializa el objeto a diccionario excluyendo credenciales sensibles."""
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "role": str(self.role.value if isinstance(self.role, UserRole) else self.role),
            "created_at": self.created_at,
        }

