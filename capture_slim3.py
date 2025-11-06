import ctypes
from ctypes import c_int, c_void_p, c_ubyte, POINTER, byref, create_string_buffer

uf = ctypes.WinDLL("UFScanner.dll")

# Inicializar
uf.UFS_Init()

count = c_int()
uf.UFS_GetScannerNumber(byref(count))
if count.value < 1:
    raise Exception("No se detectó lector")

handle = c_void_p()
uf.UFS_GetScannerHandle(0, byref(handle))

# Activar sensor
uf.UFS_SetAutoDetection(handle, 1)

print("Coloca el dedo en el lector...")

# Capturar imagen en bruto (RAW)
uf.UFS_CaptureSingleRawImage.argtypes = [c_void_p]
uf.UFS_CaptureSingleRawImage.restype = c_int

ret = uf.UFS_CaptureSingleRawImage(handle)
if ret != 0:
    raise Exception("Error capturando la imagen")

# Conseguir ancho/alto
w = c_int()
h = c_int()
uf.UFS_GetFPImageSize(handle, byref(w), byref(h))

# Buffer para imagen
img = (c_ubyte * (w.value * h.value))()
uf.UFS_GetFPImage(handle, img)

# Extraer plantilla
template = create_string_buffer(1024)
template_size = c_int()

uf.UFS_ExtractEx.argtypes = [c_void_p, POINTER(c_ubyte), POINTER(c_int)]
uf.UFS_ExtractEx(handle, template, byref(template_size))

print("✅ Huella capturada y plantilla extraída")
print("Tamaño plantilla:", template_size.value)

uf.UFS_Uninit()
