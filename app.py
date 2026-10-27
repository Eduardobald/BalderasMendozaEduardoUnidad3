
from flask import Flask, render_template

# Configuración de la aplicación
app = Flask(__name__)


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
# MANEJO DE ERRORES
# ==========================================
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return """
    <div style="font-family:Arial; text-align:center; margin-top:100px;">
        <h1>Error 404</h1>
        <p>La página que buscas no existe.</p>
        <a href="/">Volver al inicio</a>
    </div>
    """, 404


# ==========================================
# INICIAR SERVIDOR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
