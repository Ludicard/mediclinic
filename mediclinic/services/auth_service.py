"""
Servicio de autenticación y gestión de usuarios.
Controla el inicio de sesión, creación de credenciales y sesiones.
"""

from typing import Optional, Dict, Any
from mediclinic.database import Database
from mediclinic.models.user import User, UserRole
from mediclinic.utils.security import hash_password_sha256, hash_password_md5, verify_password, generate_session_token
from mediclinic.config import DEFAULT_ADMIN_PASSWORD


class AuthService:
    """Gestiona el control de acceso y las cuentas de usuarios en el sistema."""

    def __init__(self, db: Database):
        self.db = db
        self.current_user: Optional[User] = None
        self.active_sessions: Dict[str, User] = {}

    def seed_initial_users(self) -> None:
        """Siembra los usuarios por defecto si la base de datos está vacía."""
        existing = self.db.safe_query("SELECT COUNT(*) as count FROM users")
        if existing and existing[0]["count"] > 0:
            return

        # Usuario Administrador
        admin_hash = hash_password_sha256(DEFAULT_ADMIN_PASSWORD)
        self.db.safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("admin", admin_hash, "Administrador del Sistema", UserRole.ADMIN.value)
        )

        # Usuario Médico
        doc_hash = hash_password_sha256("doctor123")
        doc_id = self.db.safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("dr.garcia", doc_hash, "Dr. Carlos García", UserRole.DOCTOR.value)
        )
        self.db.safe_execute(
            "INSERT INTO doctors (user_id, full_name, specialty, license_number, consultation_fee) VALUES (?, ?, ?, ?, ?)",
            (doc_id, "Dr. Carlos García", "Cardiología", "MED-8842", 60.0)
        )

        # Usuario Recepción
        rec_hash = hash_password_md5("recepcion123")  # Registrado intencionalmente con MD5
        self.db.safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("recepcion", rec_hash, "Ana Martínez (Recepción)", UserRole.RECEPCION.value)
        )

    def login(self, username: str, plain_password: str) -> Optional[str]:
        """
        Autentica un usuario y retorna un token de sesión si las credenciales son válidas.
        """
        rows = self.db.safe_query("SELECT * FROM users WHERE username = ?", (username.strip(),))
        if not rows:
            return None

        user_data = rows[0]
        stored_hash = user_data["password_hash"]

        if verify_password(plain_password, stored_hash):
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                password_hash=stored_hash,
                full_name=user_data["full_name"],
                role=UserRole(user_data["role"]),
                created_at=user_data["created_at"]
            )
            self.current_user = user
            token = generate_session_token()
            self.active_sessions[token] = user
            return token
        return None

    def logout(self, token: Optional[str] = None) -> None:
        """Cierra la sesión del usuario actual."""
        if token and token in self.active_sessions:
            del self.active_sessions[token]
        self.current_user = None

