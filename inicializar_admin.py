
import os
import sqlite3

from database import crear_base_datos, crear_usuario, buscar_usuario


def inicializar_admin():
    crear_base_datos()

    usuario = os.getenv("ADMIN_USUARIO", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not usuario or not password:
        raise RuntimeError(
            "Configura ADMIN_USUARIO y ADMIN_PASSWORD."
        )

    if buscar_usuario(usuario):
        print("El administrador ya existe.")
        return

    try:
        crear_usuario(usuario, password)
        print("Administrador inicial creado correctamente.")

    except sqlite3.IntegrityError:
        print("El administrador ya existe.")


if __name__ == "__main__":
    inicializar_admin()
