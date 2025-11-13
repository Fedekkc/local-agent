from flask import Flask, request, jsonify
from agent import Agent

app = Flask(__name__)

agent = Agent()

@app.route("/mcp", methods=["POST"])
def mcp():
    """
    Endpoint principal del MCP server.
    Espera un JSON como {"prompt": "mensaje del usuario"}.
    """
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({"error": "Falta el campo 'prompt' en el cuerpo JSON"}), 400

    prompt = data["prompt"]
    try:
        result = agent.run_message(prompt)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Servidorcorriendo en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
