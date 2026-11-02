"""
Módulo de base de datos para MediClinic.
Maneja la conexión a SQLite, la creación de esquemas y transacciones básicas.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from mediclinic.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Administrador centralizado de la base de datos SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.db_path
        self._connection: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Obtiene o crea una nueva conexión a la base de datos."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Cierra la conexión actual si está abierta."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def init_schema(self) -> None:
        """Inicializa las tablas y el esquema relacional del sistema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de usuarios del sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('ADMIN', 'DOCTOR', 'RECEPCION')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de pacientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dni TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                blood_type TEXT DEFAULT 'O+',
                insurance_provider TEXT DEFAULT 'NINGUNO',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de doctores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                license_number TEXT UNIQUE NOT NULL,
                consultation_fee REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Tabla de citas médicas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'PENDIENTE' CHECK(status IN ('PENDIENTE', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA')),
                base_fee REAL NOT NULL,
                insurance_discount REAL DEFAULT 0.0,
                final_fee REAL NOT NULL,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        """)

        conn.commit()

    # Hallazgo de Seguridad (Bandit B608 / SonarQube SQL Injection):
    # Uso de f-string en consulta SQL sin parametrizar
    def unsafe_raw_search(self, table_name: str, column_name: str, search_query: str) -> List[Dict[str, Any]]:
        """
        Búsqueda rápida por texto libre.
        ADVERTENCIA: Método vulnerable a inyección SQL intencional para revisión estática.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Inyección SQL directa por interpolación de cadenas
        sql = f"SELECT * FROM {table_name} WHERE {column_name} LIKE '%{search_query}%'"
        
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            # Hallazgo de estilo: Captura genérica de excepciones sin relanzar
            logger.error("Error al ejecutar consulta de búsqueda: %s", e)
            return []

    def safe_query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Ejecuta una consulta parametrizada segura contra inyección SQL."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def safe_execute(self, sql: str, params: tuple = ()) -> int:
        """Ejecuta una sentencia de inserción/actualización/borrado parametrizada."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid or cursor.rowcount

