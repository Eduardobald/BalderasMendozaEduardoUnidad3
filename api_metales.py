
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("METALS_API_KEY")

URL_API = "https://api.metalcharts.org/v1/prices"


def obtener_precios():

    if not API_KEY:
        print("No se encontro la API Key.")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }

    try:
        respuesta = requests.get(
            URL_API,
            headers=headers,
            timeout=15
        )

        respuesta.raise_for_status()
        datos = respuesta.json()

        if not datos.get("success"):
            print("La API no devolvio datos validos.")
            return None

        precios = datos.get("data", {})

        return {
            "aluminio": precios.get("ALI"),
            "cobre": precios.get("HG")
        }

    except requests.RequestException as error:
        print("Error de conexion:", error)
        return None

    except (ValueError, TypeError):
        print("Respuesta JSON no valida.")
        return None


if __name__ == "__main__":

    precios = obtener_precios()

    if precios:
        print("\nPRECIOS DE MATERIALES")
        print("-----------------------------")
        print("ALUMINIO:", precios["aluminio"])
        print("COBRE:", precios["cobre"])
    else:
        print("No se pudieron obtener los precios.")
