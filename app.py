
import os
from datetime import timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from flask_wtf.csrf import CSRFProtect
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError
)

from database import buscar_usuario, crear_base_datos


# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("SECRET_KEY")

if not secret_key or len(secret_key) < 64:
    raise RuntimeError(
        "Configura una SECRET_KEY segura en el archivo .env"
    )

app.config["SECRET_KEY"] = secret_key

# Seguridad de las cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Para localhost con HTTP.
# En producción con HTTPS debe ser True.
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("USE_HTTPS", "0") == "1"
)

# Duración de la sesión
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)

app.config["SESSION_REFRESH_EACH_REQUEST"] = False

# Protección CSRF
csrf = CSRFProtect(app)

# Contraseñas protegidas con Argon2id
password_hasher = PasswordHasher()

# Crear la tabla de usuarios si no existe
crear_base_datos()


# ==========================================
# ENCABEZADOS DE SEGURIDAD
# ==========================================

@app.after_request
def agregar_seguridad(response):

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    response.headers["Cache-Control"] = "no-store"

    return response


# ==========================================
# PROTEGER PÁGINAS
# ==========================================

def login_requerido(funcion):

    @wraps(funcion)
    def verificar(*args, **kwargs):

        usuario_id = session.get("usuario_id")

        if not usuario_id:
            return redirect(url_for("login"))

        # Verificar que la cuenta siga activa
        from database import conectar

        with conectar() as conexion:
            usuario = conexion.execute(
                """
                SELECT id
                FROM usuarios
                WHERE id = ? AND activo = 1
                """,
                (usuario_id,)
            ).fetchone()

        if usuario is None:
            session.clear()
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return verificar


# ==========================================
# INICIO DE SESIÓN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("usuario_id"):
        return redirect(url_for("inicio"))

    error = None

    if request.method == "POST":

        usuario = request.form.get(
            "usuario", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        error = "Usuario o contraseña incorrectos."

        registro = buscar_usuario(usuario)

        if registro and registro["activo"] == 1:

            try:
                password_hasher.verify(
                    registro["password_hash"],
                    password
                )

                # Limpiar sesión anterior
                session.clear()

                session.permanent = True

                session["usuario_id"] = registro["id"]

                session["usuario"] = registro["usuario"]

                return redirect(url_for("inicio"))

            except (
                VerifyMismatchError,
                VerificationError,
                InvalidHashError
            ):
                pass

    return render_template(
        "login.html",
        error=error
    )


# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
@login_requerido
def inicio():

    return render_template("index.html")


# ==========================================
# REGISTRO DE MATERIALES
# ==========================================

@app.route("/materiales")
@login_requerido
def materiales():

    return render_template("materiales.html")


# ==========================================
# ERROR 404
# ==========================================

@app.errorhandler(404)
def pagina_no_encontrada(error):

    return """
    <h1>Error 404</h1>
    <p>La página solicitada no existe.</p>
    <a href="/">Volver al inicio</a>
    """, 404


# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == "__main__":

    app.run(debug=False)
