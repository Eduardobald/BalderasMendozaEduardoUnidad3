
import getpass
import sqlite3

from database import crear_base_datos, crear_usuario


def main():
    print("=" * 45)
    print("MATERIALCONTROL - CREAR ADMINISTRADOR")
    print("=" * 45)

    crear_base_datos()

    usuario = input("Nombre del administrador: ").strip()

    if not usuario:
        print("Error: debes escribir un usuario.")
        return

    password = getpass.getpass(
        "Contraseña (mínimo 12 caracteres): "
    )

    confirmar = getpass.getpass(
        "Confirmar contraseña: "
    )

    if password != confirmar:
        print("Error: las contraseñas no coinciden.")
        return

    try:
        crear_usuario(usuario, password)
        print("\nAdministrador creado correctamente.")

    except sqlite3.IntegrityError:
        print("\nError: ese usuario ya existe.")

    except ValueError as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
