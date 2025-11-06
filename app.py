# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import base64
from biomini import BioMiniSDK  # Tu SDK del huellero

app = Flask(__name__)
CORS(app)

# Inicializar SDK solo una vez
sdk = BioMiniSDK()
print("✅ SDK Inicializado correctamente")

@app.route("/capturar_huella", methods=["GET"])
def capturar_huella():
    """
    Captura la huella desde el huellero y devuelve:
    - Imagen en Base64 para mostrar
    - Plantilla en Base64 para registrar
    """
    try:
        template_bytes = sdk.capture_template()
        # Guardar imagen BMP temporal
        with open("huella_usuario.bmp", "rb") as f:
            img_bytes = f.read()
        
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        template_b64 = base64.b64encode(template_bytes).decode("utf-8")

        return jsonify({"status": "ok", "huella": f"data:image/bmp;base64,{img_b64}", "plantilla": template_b64})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/estado_huellero", methods=["GET"])
def estado_huellero():
    """
    Verifica si el SDK está activo
    """
    try:
        if sdk.is_sensor_active():
            return jsonify({"status": "ok", "mensaje": "Sensor activo"})
        else:
            return jsonify({"status": "error", "mensaje": "Sensor inactivo"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# Cierre del SDK solo al detener el servidor
import atexit
@atexit.register
def cerrar_sdk():
    try:
        sdk.close()
        print("🔻 SDK cerrado correctamente")
    except:
        pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
