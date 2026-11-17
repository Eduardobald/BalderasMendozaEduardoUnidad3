
from flask import Blueprint, jsonify

# Crear el servicio web propio
api_materiales = Blueprint(
    "api_materiales",
    __name__
)

# Datos de ejemplo para probar la API
MATERIALES = [
    {
        "id": 1,
        "codigo": "AL-001",
        "nombre": "Aluminio",
        "unidad": "KG"
    },
    {
        "id": 2,
        "codigo": "CU-001",
        "nombre": "Cobre",
        "unidad": "KG"
    },
    {
        "id": 3,
        "codigo": "RB-001",
        "nombre": "Rebaba de aluminio",
        "unidad": "KG"
    }
]


@api_materiales.route("/api/materiales", methods=["GET"])
def consultar_materiales():
    """
    Servicio web REST propio.
    Devuelve un listado de materiales en JSON.
    """

    return jsonify({
        "success": True,
        "total": len(MATERIALES),
        "materiales": MATERIALES
    }), 200


@api_materiales.route(
    "/api/materiales/<int:material_id>",
    methods=["GET"]
)
def consultar_material(material_id):
    """
    Consultar un material por su identificador.
    """

    material = next(
        (
            item for item in MATERIALES
            if item["id"] == material_id
        ),
        None
    )

    if material is None:
        return jsonify({
            "success": False,
            "mensaje": "Material no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "material": material
    }), 200
