import ctypes, os, time
from ctypes import byref, c_int, c_void_p, c_ubyte
from PIL import Image

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

        # Buffer de imagen
        self.ufscanner.UFS_GetCaptureImageBuffer.argtypes = [c_void_p, ctypes.POINTER(c_void_p)]
        self.ufscanner.UFS_GetCaptureImageBuffer.restype = c_int
        self.ufscanner.UFS_GetCaptureImageBufferInfo.argtypes = [
            c_void_p,
            ctypes.POINTER(c_int),
            ctypes.POINTER(c_int),
            ctypes.POINTER(c_int)
        ]
        self.ufscanner.UFS_GetCaptureImageBufferInfo.restype = c_int

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

    def capture_template(self, max_retries=3):
        scanner = self.get_scanner()
        print("🔄 Activando sensor...")
        self.ufscanner.UFS_StartCapturing(scanner)

        TEMPLATE_TYPE_SUPREMA = 2001
        self.ufscanner.UFS_SetTemplateType(scanner, TEMPLATE_TYPE_SUPREMA)

        print("Coloca el dedo en el lector...")
        while True:
            finger = c_int()
            self.ufscanner.UFS_IsFingerOn(scanner, byref(finger))
            if finger.value == 1:
                break
            self.ufscanner.UFS_Update(scanner)
            time.sleep(0.1)

        print("✅ Dedo detectado")

        # Captura de imagen
        for attempt in range(1, max_retries + 1):
            self.ufscanner.UFS_Update(scanner)
            ret = self.ufscanner.UFS_CaptureSingleImage(scanner)
            if ret == 0:
                print(f"✅ Imagen capturada en intento {attempt}")
                break
            print(f"⚠️ Intento {attempt} fallido. Código: {ret}")
            if attempt == max_retries:
                raise Exception("❌ No se pudo capturar la imagen.")

        # Obtener info de imagen
        width = c_int()
        height = c_int()
        buffer_size = c_int()
        ret_info = self.ufscanner.UFS_GetCaptureImageBufferInfo(scanner, byref(width), byref(height), byref(buffer_size))
        if ret_info != 0:
            raise Exception(f"❌ Error obteniendo info de la imagen. Código: {ret_info}")

        # Obtener buffer
        img_ptr = c_void_p()
        self.ufscanner.UFS_GetCaptureImageBuffer(scanner, byref(img_ptr))
        buffer_type = c_ubyte * buffer_size.value
        img_bytes = buffer_type.from_address(img_ptr.value)

        # Guardar imagen BMP
        img = Image.frombytes("L", (width.value, height.value), bytes(img_bytes))
        img.save("huella.bmp")
        print("✅ Huella guardada como huella.bmp")

        # Extraer plantilla
        MAX_TEMPLATE_SIZE = 1024
        template = (c_ubyte * MAX_TEMPLATE_SIZE)()
        template_size = c_int(MAX_TEMPLATE_SIZE)

        ret = self.ufscanner.UFS_Extract(
            scanner,
            ctypes.cast(img_ptr, ctypes.POINTER(c_ubyte)),
            template,
            byref(template_size)
        )
        if ret != 0:
            raise Exception(f"❌ Error extrayendo la plantilla. Código: {ret}")

        print(f"✅ Plantilla generada correctamente ({template_size.value} bytes)")
        return bytes(template[:template_size.value])

    def close(self):
        self.ufscanner.UFS_Uninit()
        print("🔻 SDK cerrado correctamente")
