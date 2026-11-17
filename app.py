
import os
from datetime import timedelta
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
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

from database import (
    buscar_usuario,
    crear_base_datos,
    conectar
)

# API externa de precios de metales
from api_metales import obtener_precios

from api_materiales import api_materiales, MATERIALES


# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api_materiales)
secret_key = os.getenv("SECRET_KEY")

if not secret_key or len(secret_key) < 64:
    raise RuntimeError(
        "Configura una SECRET_KEY segura en el archivo .env"
    )

app.config["SECRET_KEY"] = secret_key

# Seguridad de cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# False para desarrollo local con HTTP.
# En producción se necesita HTTPS.
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("USE_HTTPS", "0") == "1"
)

# Duración de sesión
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)

app.config["SESSION_REFRESH_EACH_REQUEST"] = False

# Protección contra CSRF
csrf = CSRFProtect(app)

# Verificación de contraseñas
password_hasher = PasswordHasher()

# ==========================================
# PROTECCIÓN CONTRA FUERZA BRUTA
# ==========================================

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

# Preparar base de datos
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
# PROTECCIÓN DE RUTAS
# ==========================================

def login_requerido(funcion):

    @wraps(funcion)
    def verificar(*args, **kwargs):

        usuario_id = session.get("usuario_id")

        if not usuario_id:
            return redirect(url_for("login"))

        # Comprobar que el usuario siga activo
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
# INICIO DE SESIÓN SEGURO
# ==========================================

@app.route("/login", methods=["GET", "POST"])
@limiter.limit(
    "5 per 5 minutes",
    methods=["POST"]
)
def login():

    if session.get("usuario_id"):

        with conectar() as conexion:
            usuario_activo = conexion.execute(
                """
                SELECT id
                FROM usuarios
                WHERE id = ? AND activo = 1
                """,
                (session["usuario_id"],)
            ).fetchone()

        if usuario_activo:
            return redirect(url_for("inicio"))

        session.clear()

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
# MENSAJE POR EXCESO DE INTENTOS
# ==========================================

@app.errorhandler(RateLimitExceeded)
def limite_intentos(error):

    return render_template(
        "login.html",
        error=(
            "Demasiados intentos de inicio de sesión. "
            "Espera 5 minutos antes de volver a intentarlo."
        )
    ), 429



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
# PRECIOS DE MATERIALES - API EXTERNA
# ==========================================

@app.route("/precios")
@login_requerido
def precios_materiales():

    # Consultar MetalCharts API
    precios = obtener_precios()

    # Preparar información para la página
    aluminio = None
    cobre = None

    if precios:

        aluminio = precios.get("aluminio")
        cobre = precios.get("cobre")

        # Convertir precios a USD por kilogramo
        if isinstance(aluminio, dict):
            if aluminio.get("unit") == "mt":
                aluminio = dict(aluminio)
                aluminio["precio_kg"] = (
                    aluminio["price"] / 1000
                )

        if isinstance(cobre, dict):
            if cobre.get("unit") == "lb":
                cobre = dict(cobre)
                cobre["precio_kg"] = (
                    cobre["price"] / 0.45359237
                )

    return render_template(
        "precios.html",
        aluminio=aluminio,
        cobre=cobre
    )


# ==========================================
# ERROR 404
# ==========================================

@app.errorhandler(404)
def pagina_no_encontrada(error):

    return """
    <div style="
        font-family: Arial;
        text-align: center;
        margin-top: 100px;
    ">
        <h1>Error 404</h1>
        <p>La página solicitada no existe.</p>
        <a href="/">Volver al inicio</a>
    </div>
    """, 404


# ==========================================
# VISTA DEL WEB SERVICE PROPIO
# ==========================================

@app.route("/servicio-materiales")
@login_requerido
def servicio_materiales():

    return render_template(
        "servicio_materiales.html",
        materiales=MATERIALES,
        total=len(MATERIALES)
    )

# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == "__main__":

    app.run(debug=False)
