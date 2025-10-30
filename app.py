from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)

@app.route("/capture", methods=["GET"])
def capture_fingerprint():
    """
    Simula la captura de una huella desde el huellero.
    Cuando tengas el SDK, reemplaza el bloque simulado
    por la función real del lector (ej. huellero.capture()).
    """
    try:
        # Simulación: lee una imagen de muestra en la carpeta
        with open("sample_fingerprint.bmp", "rb") as f:
            img_bytes = f.read()
        base64_data = base64.b64encode(img_bytes).decode("utf-8")
        return jsonify({"status": "ok", "huella": base64_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/compare", methods=["POST"])
def compare_fingerprints():
    """
    Compara dos huellas base64 (t1 y t2).
    Aquí puedes usar tu algoritmo real o SDK de comparación.
    """
    try:
        data = request.get_json()
        t1 = data.get("t1")
        t2 = data.get("t2")

        if not t1 or not t2:
            return jsonify({"status": "error", "message": "Faltan datos t1 o t2"}), 400

        # Simulación: si los primeros 50 caracteres son iguales, asumimos que coincide
        score = sum(1 for a, b in zip(t1[:50], t2[:50]) if a == b) * 2
        estado = "Coinciden" if score > 80 else "No coinciden"

        return jsonify({"status": "ok", "estado": estado, "score": score})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
