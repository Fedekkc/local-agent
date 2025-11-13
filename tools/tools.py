from .files_tool import FileTool
from .system_tool import SystemTool


TOOLS = {
        "listar_archivos": {
            "description": "Lista los archivos en un directorio especificado.",
            "parameters": {
                "directorio": {
                    "type": "string",
                    "description": "El camino del directorio cuyos archivos se desean listar."
                }
            }
        },
        "leer_archivo": {
            "description": "Lee un archivo y devuelve su contenido.",
            "parameters": {
                "filename": {
                    "type": "string",
                    "description": "Nombre o ruta del archivo a leer."
                }
            }
        },
        "hora_actual": {
            "description": "Devuelve la hora actual del sistema.",
            "parameters": {}
        },
}


TOOLS_MAP = {
    "listar_archivos": FileTool.listar_archivos,
    "leer_archivo": FileTool.leer_archivo,
    "hora_actual": SystemTool.hora_actual,
}

