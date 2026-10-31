
import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Clave secreta para proteger las sesiones
secret_key = os.getenv("SECRET_KEY")

if not secret_key or len(secret_key) < 64:
    raise RuntimeError(
        "Configura una SECRET_KEY segura en el archivo .env"
    )

app.config["SECRET_KEY"] = secret_key

# Configuración de seguridad de las cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# False únicamente para desarrollo local con HTTP
app.config["SESSION_COOKIE_SECURE"] = False

# Duración máxima de una sesión permanente
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)

# Protección contra ataques CSRF
csrf = CSRFProtect(app)


# ==========================================
# ENCABEZADOS DE SEGURIDAD
# ==========================================
@app.after_request
def agregar_seguridad(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================
@app.route("/")
def inicio():
    return render_template("index.html")


# ==========================================
# REGISTRO DE MATERIALES
# ==========================================
@app.route("/materiales")
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
# INICIAR APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app.run(debug=False)
