import ctypes, os, time, base64
from ctypes import byref, c_int, c_void_p, c_ubyte
import requests

class BioMiniSDK:
    def __init__(self):
        dll_path = os.path.join(os.getcwd(), "UFScanner.dll")
        print("Cargando DLL desde:", dll_path)
        self.ufscanner = ctypes.WinDLL(dll_path)

        # Inicialización básica
        self.ufscanner.UFS_Init.restype = c_int
        self.ufscanner.UFS_Uninit.restype = c_int

        # Scanner
        self.ufscanner.UFS_GetScannerNumber.argtypes = [ctypes.POINTER(c_int)]
        self.ufscanner.UFS_GetScannerNumber.restype = c_int
        self.ufscanner.UFS_GetScannerHandle.argtypes = [c_int, ctypes.POINTER(c_void_p)]
        self.ufscanner.UFS_GetScannerHandle.restype = c_int

        # Captura
        self.ufscanner.UFS_CaptureSingleImage.argtypes = [c_void_p]
        self.ufscanner.UFS_CaptureSingleImage.restype = c_int
        self.ufscanner.UFS_StartCapturing.argtypes = [c_void_p]
        self.ufscanner.UFS_StartCapturing.restype = c_int
        self.ufscanner.UFS_IsFingerOn.argtypes = [c_void_p, ctypes.POINTER(c_int)]
        self.ufscanner.UFS_IsFingerOn.restype = c_int
        self.ufscanner.UFS_Update.argtypes = [c_void_p]
        self.ufscanner.UFS_Update.restype = c_int

        # Template
        self.ufscanner.UFS_SetTemplateType.argtypes = [c_void_p, c_int]
        self.ufscanner.UFS_SetTemplateType.restype = c_int
        self.ufscanner.UFS_Extract.argtypes = [
            c_void_p,
            ctypes.POINTER(c_ubyte),
            ctypes.POINTER(c_ubyte),
            ctypes.POINTER(c_int)
        ]
        self.ufscanner.UFS_Extract.restype = c_int

        # Guardar BMP
        self.ufscanner.UFS_SaveCaptureImageBufferToBMP.argtypes = [c_void_p, ctypes.c_char_p]
        self.ufscanner.UFS_SaveCaptureImageBufferToBMP.restype = c_int

        # Inicializar SDK
        result = self.ufscanner.UFS_Init()
        if result != 0:
            raise Exception(f"❌ UFS_Init falló. Código: {result}")
        print("✅ SDK Inicializado correctamente")

    def get_scanner(self):
        count = c_int()
        self.ufscanner.UFS_GetScannerNumber(byref(count))
        if count.value < 1:
            raise Exception("❌ No se detecta lector conectado.")
        handle = c_void_p()
        ret = self.ufscanner.UFS_GetScannerHandle(0, byref(handle))
        if ret != 0:
            raise Exception(f"❌ No se pudo obtener handle. Código: {ret}")
        return handle

    def capture_template(self, archivo_bmp="huella_usuario.bmp", archivo_dat="huella_usuario.dat"):
        scanner = self.get_scanner()
        print("🔹 Capturando huella desde el huellero...")
        self.ufscanner.UFS_StartCapturing(scanner)

        TEMPLATE_TYPE_SUPREMA = 2001
        self.ufscanner.UFS_SetTemplateType(scanner, TEMPLATE_TYPE_SUPREMA)

        # Esperar dedo
        print("Coloca el dedo en el lector...")
        while True:
            finger = c_int()
            self.ufscanner.UFS_IsFingerOn(scanner, byref(finger))
            if finger.value == 1:
                break
            self.ufscanner.UFS_Update(scanner)
            time.sleep(0.1)

        print("✅ Dedo detectado")
        time.sleep(0.4)

        # Captura de imagen
        MAX_RETRIES = 3
        for attempt in range(1, MAX_RETRIES + 1):
            self.ufscanner.UFS_Update(scanner)
            ret = self.ufscanner.UFS_CaptureSingleImage(scanner)
            if ret == 0:
                print(f"✅ Imagen capturada en intento {attempt}")
                break
            print(f"⚠️ Intento {attempt} fallido. Código: {ret}")
            if attempt == MAX_RETRIES:
                raise Exception("❌ No se pudo capturar la imagen.")

        # Guardar BMP
        ret_bmp = self.ufscanner.UFS_SaveCaptureImageBufferToBMP(scanner, archivo_bmp.encode('utf-8'))
        if ret_bmp != 0:
            raise Exception(f"❌ Error guardando BMP. Código: {ret_bmp}")
        print(f"✅ Imagen BMP guardada en {archivo_bmp}")

        # Extraer plantilla
        img_ptr = c_void_p()
        self.ufscanner.UFS_GetCaptureImageBuffer(scanner, byref(img_ptr))
        MAX_TEMPLATE_SIZE = 1024
        template = (c_ubyte * MAX_TEMPLATE_SIZE)()
        template_size = c_int(MAX_TEMPLATE_SIZE)
        ret_extract = self.ufscanner.UFS_Extract(
            scanner,
            ctypes.cast(img_ptr, ctypes.POINTER(c_ubyte)),
            template,
            byref(template_size)
        )
        if ret_extract != 0:
            raise Exception(f"❌ Error extrayendo plantilla. Código: {ret_extract}")

        # Guardar plantilla en archivo
        with open(archivo_dat, "wb") as f:
            f.write(bytes(template[:template_size.value]))
        print(f"✅ Plantilla guardada en {archivo_dat}")

        return bytes(template[:template_size.value])

    def close(self):
        self.ufscanner.UFS_Uninit()
        print("🔻 SDK cerrado correctamente")


# --- USO ---
sdk = BioMiniSDK()
try:
    template = sdk.capture_template()
finally:
    sdk.close()
