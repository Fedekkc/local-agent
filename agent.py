import json
import re
import ollama
from tools.tools import TOOLS, TOOLS_MAP

MODEL = "llama3:8b"



def extract_json_block(text: str):
    """
    Extrae el primer bloque JSON bien balanceado del texto.
    Soporta casos donde falta o sobra texto antes/después.
    """
    print("Extracting JSON block from text...")
    print("Input text:", text)
    start = text.find("{")
    if start == -1:
        return None

    stack = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            stack += 1
        elif text[i] == "}":
            stack -= 1
            if stack == 0:
                block = text[start:i + 1]
                return block
    return None


def safe_json_parse(text: str):
    """
    Intenta extraer y decodificar JSON del texto del modelo.
    Corrige errores comunes de formato (comas, escapes, saltos de línea, etc).
    """
    block = extract_json_block(text)
    if not block:
        print("⚠️ No se encontró un bloque JSON válido.")
        return None

    # Sanitizar texto antes del parseo
    fixed = block.strip()
    fixed = fixed.replace("\n", "").replace("\r", "")
    fixed = fixed.replace(",}", "}").replace(",]", "]")

    # ⚙️ Caso común: barra invertida sin escapar al final de un path
    fixed = re.sub(r'\\\\(?=[^"\\])', r'\\', fixed)  # Corrige doble barra
    fixed = re.sub(r'(?<=[a-zA-Z]):\\(?!\\)', r':\\\\', fixed)  # F:\ -> F:\\

    # Si termina con una comilla abierta por error
    if fixed.count('"') % 2 != 0:
        fixed += '"'

    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print("❌ Error al decodificar JSON:", e)
        print("Contenido problemático (arreglado):", fixed)
        return None



class Agent:
    def __init__(self, model: str = MODEL):
        self.model = model
        self.messages = []
        self.tools = TOOLS
        self._build_system_prompt()

    def _build_system_prompt(self):
        self.system_prompt = (
            "Sos un agente local inteligente con acceso a herramientas del sistema.\n\n"
            "El usuario normalmente será un desarrollador experimentado con conocimientos de todo tipo.\n\n"
            "⚙️ INSTRUCCIONES ESTRICTAS:\n"
            "1. Si una acción del usuario requiere una herramienta, respondé *solo* con un JSON válido, sin texto adicional.\n"
            "2. El JSON debe tener *exactamente* este formato:\n"
            "   {\"function\": \"nombre_funcion\", \"args\": {\"parametro\": \"valor\"}}\n"
            "3. No incluyas comentarios, explicaciones ni texto fuera del JSON.\n"
            "4. Si no necesitás usar una herramienta, respondé normalmente en texto natural.\n"
            "5. El JSON debe ser parseable por Python sin errores.\n"
            "6. NO uses markdown, comillas triples ni texto extra.\n\n"
            "🔧 HERRAMIENTAS DISPONIBLES:\n"
            + json.dumps(self.tools, indent=2, ensure_ascii=False)
            + "\n\n"
            "Listado de ejemplos a continuación:\n"
            "Ejemplo 1: Usuario: 'Qué hay en el disco C:'. Respuesta CORRECTA: {\"function\": \"listar_archivos\", \"args\": {\"directorio\": \"C:\\\\\"}}\n"
            "Ejemplo 2: Usuario: 'Lee el archivo config.txt'. Respuesta CORRECTA: {\"function\": \"leer_archivo\", \"args\": {\"filename\": \"config.txt\"}}\n"
            "Ahora ejemplos incorrectos:\n"
            "Incorrecto 1: Usuario: 'Qué hay en el disco C:'. Respuesta INCORRECTA: ```json\n{\n  \"function\": \"listar_archivos\",\n  \"args\": {\n    \"directorio\": \"C:\\\"\n  }\n}\n```\n"
            "Incorrecto 2: Usuario: 'Lee el archivo config.txt'. Respuesta INCORRECTA: Aquí está el JSON que pediste:\n\n```\n{\n  \"function\": \"leer_archivo\",\n  \"args\": {\n    \"filename\": \"config.txt\"\n  }\n}\n```\n"
            
            
        )

    def call_tool(self, func_name: str, args: dict):
        if func_name not in TOOLS_MAP:
            raise ValueError(f"Herramienta desconocida: {func_name}")
        return TOOLS_MAP[func_name](**args)

    def send_message(self, user_message: str):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.messages + [{"role": "user", "content": user_message}]

        response = ollama.chat(model=self.model, messages=messages)
        content = response["message"]["content"]

        # 🧩 Intentamos parsear cualquier JSON balanceado
        data = safe_json_parse(content)
        if data and "function" in data:
            func_name = data["function"]
            args = data.get("args", {})
            result = self.call_tool(func_name, args)
            return {"type": "tool", "result": result}

        # Si no hay JSON válido, devolvemos respuesta normal
        return {"type": "chat", "result": content}

    def run_message(self, prompt: str) -> str:
        response = self.send_message(prompt)
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append({"role": "assistant", "content": str(response['result'])})
        return response["result"]


def chat():
    """Función legacy para iniciar el agente."""
    agent = Agent()
    agent.run()


if __name__ == "__main__":
    chat()
