from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os

app = Flask(__name__)

extracted_text = ""

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

if not OPENAI_API_KEY or not OPENAI_API_BASE:
    raise EnvironmentError("Faltan variables de entorno OPENAI_API_KEY y/o OPENAI_API_BASE.")

llm = ChatOpenAI(
    model="mistralai/mixtral-8x7b-instruct",
    openai_api_base=OPENAI_API_BASE,
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7
)

@app.route("/api/upload", methods=["POST"])
def upload_cobol_file():
    global extracted_text
    file = request.files.get("file")

    if not file or not file.filename.endswith(".cbl"):
        return jsonify({"error": "Solo se permiten archivos COBOL (.cbl)."}), 400

    extracted_text = file.read().decode("utf-8")
    return jsonify({"message": "Archivo COBOL cargado correctamente."})

@app.route("/api/ask", methods=["POST"])
def ask():
    global extracted_text
    if not extracted_text.strip():
        return jsonify({"error": "Primero debes subir un archivo COBOL."}), 400

    question = request.json.get("question", "")
    if not question:
        return jsonify({"error": "Falta la pregunta en el cuerpo del JSON."}), 400

    prompt = f"Contexto del programa COBOL:\n{extracted_text}\n\nPregunta: {question}"

    try:
        response = llm([
            SystemMessage(content="Eres un experto en COBOL."),
            HumanMessage(content=prompt)
        ])
        return jsonify({"respuesta": response.content})
    except Exception as e:
        return jsonify({"error": f"Error al consultar el modelo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)