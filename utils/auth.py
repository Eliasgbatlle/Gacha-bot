from typing import Dict
from fastapi import Request

def get_current_user(request: Request) -> Dict[str, str]:
    """
    Obtiene dinámicamente el usuario actual desde la solicitud.
    Devuelve un diccionario con información del usuario.
    """
    # Extraer información del usuario desde los encabezados de la solicitud
    user_id = request.headers.get("X-User-ID")
    user_name = request.headers.get("X-User-Name")

    if not user_id or not user_name:
        print("[ERROR] Faltan los encabezados 'X-User-ID' o 'X-User-Name' en la solicitud.")
        raise ValueError("Faltan los encabezados 'X-User-ID' o 'X-User-Name' en la solicitud. Asegúrate de incluirlos.")

    return {
        "id": user_id,  # ID del usuario
        "name": user_name  # Nombre del usuario
    }