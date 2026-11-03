
import sqlite3
from pathlib import Path

from argon2 import PasswordHasher


# Ubicación de la base de datos
DB_PATH = Path(__file__).resolve().parent / "usuarios.db"

# Protección de contraseñas
password_hasher = PasswordHasher()


# ==========================================
# CONECTAR A LA BASE DE DATOS
# ==========================================
def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


# ==========================================
# CREAR TABLA DE USUARIOS
# ==========================================
def crear_base_datos():

    with conectar() as conexion:

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1
            )
        """)


# ==========================================
# CREAR USUARIO
# ==========================================
def crear_usuario(usuario, password):

    usuario = usuario.strip()

    if len(usuario) < 3:
        raise ValueError(
            "El usuario debe tener al menos 3 caracteres."
        )

    if len(password) < 12:
        raise ValueError(
            "La contraseña debe tener al menos 12 caracteres."
        )

    # Convertir contraseña en hash Argon2id
    password_segura = password_hasher.hash(password)

    with conectar() as conexion:

        conexion.execute("""
            INSERT INTO usuarios (
                usuario,
                password_hash
            )
            VALUES (?, ?)
        """, (usuario, password_segura))


# ==========================================
# BUSCAR USUARIO
# ==========================================
def buscar_usuario(usuario):

    with conectar() as conexion:

        return conexion.execute("""
            SELECT
                id,
                usuario,
                password_hash,
                activo
            FROM usuarios
            WHERE usuario = ?
        """, (usuario,)).fetchone()
