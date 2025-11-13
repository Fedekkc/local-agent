
class FileTool:
    @staticmethod
    def listar_archivos(directorio: str) -> list:

        import os

        try:
            archivos = os.listdir(directorio)
            return archivos
        except FileNotFoundError:
            return f"El directorio '{directorio}' no existe."
        except Exception as e:
            return str(e)
    
    @staticmethod
    def leer_archivo(filename: str) -> str:

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return contenido
        except FileNotFoundError:
            return f"El archivo '{filename}' no existe."
        except PermissionError:
            return f"No tienes permisos para leer '{filename}'."
        except Exception as e:
            return f"Error al leer el archivo: {str(e)}"
        
