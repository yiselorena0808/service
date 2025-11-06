from biomini import BioMiniSDK

sdk = BioMiniSDK()
tpl = sdk.capture_template()
print("TEMPLATE (HEX):", tpl.hex())
sdk.close()
