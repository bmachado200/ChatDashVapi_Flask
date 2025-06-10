import os
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
BASE_URL = "https://api.vapi.ai" # <-- LÍNEA TEMPORAL PARA DEPURAR

def get_headers():
    if not API_KEY: raise ValueError("VAPI_API_KEY no encontrada.")
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def get_assistant_details(assistant_id: str):
    endpoint = f"{BASE_URL}/assistant/{assistant_id}"
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e: logging.error(f"Error en get_assistant_details: {e}")
    return None

def get_call_details(call_id: str):
    endpoints_to_try = [f"{BASE_URL}/call/{call_id}", f"{BASE_URL}/calls/{call_id}"]
    for endpoint in endpoints_to_try:
        try:
            logging.info(f"Intentando obtener detalles de la llamada desde: {endpoint}")
            response = requests.get(endpoint, headers=get_headers(), timeout=10)
            response.raise_for_status()
            logging.info(f"Éxito al obtener detalles desde: {endpoint}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404: logging.warning(f"Endpoint no encontrado (404): {endpoint}.")
            else: logging.error(f"Error HTTP en {endpoint}: {e}"); break
        except Exception as e: logging.error(f"Error inesperado en {endpoint}: {e}"); break
    logging.error(f"No se pudieron obtener detalles para la llamada {call_id}.")
    return None

def get_active_calls(assistant_id=None):
    endpoint = f"{BASE_URL}/call"
    params = {'assistantId': assistant_id} if assistant_id else {}
    try:
        response = requests.get(endpoint, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list): return data
        if isinstance(data, dict) and 'data' in data: return data['data']
        return []
    except Exception as e: logging.error(f"Error en get_active_calls: {e}")
    return []