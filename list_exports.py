# list_exports.py
import pefile
import sys
import os

dll = "UFScanner.dll"
if not os.path.exists(dll):
    print(f"ERROR: {dll} no encontrado en {os.getcwd()}")
    sys.exit(1)

pe = pefile.PE(dll)
if not hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
    print("No se encontraron exports en la DLL.")
    sys.exit(0)

print("EXPORTS from", dll)
print("="*60)
for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    name = sym.name.decode('latin-1') if sym.name else f"<ordinal_{sym.ordinal}>"
    print(name)
