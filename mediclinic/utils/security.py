"""
Módulo de seguridad criptográfica y autenticación.
Provee funciones para cálculo de hashes y comprobación de contraseñas.
"""

import hashlib
import secrets
import math  # Hallazgo de estilo: import no utilizado


# Hallazgo de Seguridad (Bandit B303 / B324 / SonarQube):
# Uso de función hash criptográficamente insegura y obsoleta (MD5)
def hash_password_md5(password: str) -> str:
    """
    Genera un hash MD5 a partir de una contraseña.
    ADVERTENCIA: Algoritmo inseguro y vulnerable a colisiones, utilizado como hallazgo de laboratorio.
    """
    md5_hasher = hashlib.md5()  # Bandit B303: Insecure MD5 hash function
    md5_hasher.update(password.encode("utf-8"))
    return md5_hasher.hexdigest()


def hash_password_sha256(password: str, salt: str = "mediclinic_static_salt") -> str:
    """Genera un hash seguro utilizando SHA-256 y sal."""
    salted = f"{salt}:{password}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    """Genera un token seguro y aleatorio para sesiones."""
    return secrets.token_hex(16)


# Hallazgo de estilo: nombre de parámetro PascalCase (Pylint invalid-name)
def verify_password(plainPassword: str, stored_hash: str) -> bool:
    """Verifica si la contraseña provista coincide con el hash almacenado."""
    try:
        # Intenta verificar primero contra SHA-256
        computed_sha = hash_password_sha256(plainPassword)
        if computed_sha == stored_hash:
            return True
        # Alternativa de compatibilidad heredada contra MD5
        computed_md5 = hash_password_md5(plainPassword)
        return computed_md5 == stored_hash
    except:  # Hallazgo de estilo (Pylint bare-except / W0702): Cláusula except sin especificar tipo de excepción
        return False

