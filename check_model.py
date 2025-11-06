import ctypes, os
from ctypes import c_int, c_void_p, byref

dll_path = os.path.join(os.getcwd(), "UFScanner.dll")
print("Cargando DLL:", dll_path)

uf = ctypes.WinDLL(dll_path)

# Firmas
uf.UFS_Init.restype = c_int
uf.UFS_Uninit.restype = c_int
uf.UFS_GetScannerNumber.argtypes = [ctypes.POINTER(c_int)]
uf.UFS_GetScannerNumber.restype = c_int
uf.UFS_GetScannerHandle.argtypes = [c_int, ctypes.POINTER(c_void_p)]
uf.UFS_GetScannerHandle.restype = c_int

# Esta función sí existe en tu SDK
uf.UFS_GetScannerType.argtypes = [c_void_p, ctypes.POINTER(c_int)]
uf.UFS_GetScannerType.restype = c_int

# Iniciar
uf.UFS_Init()

count = c_int()
uf.UFS_GetScannerNumber(byref(count))
if count.value < 1:
    raise Exception("No se detecta lector.")

handle = c_void_p()
uf.UFS_GetScannerHandle(0, byref(handle))

type_code = c_int()
uf.UFS_GetScannerType(handle, byref(type_code))

types = {
    1001: "BioMini",
    1002: "BioMini Plus",
    1003: "BioMini Slim",
    1004: "BioMini Slim 2",
    1005: "BioMini Plus 2",
}

print("\n🔍 Modelo detectado:", types.get(type_code.value, f"Desconocido ({type_code.value})"))

uf.UFS_Uninit()
