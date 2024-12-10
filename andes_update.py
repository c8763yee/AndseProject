import zlib

from andes_aes256 import AESProcess
from andes_epaper import GenerateEPaperImage
from andes_file import ProcessFile
from andes_mqtt import MQTTSend

# --------------- 流程圖 ---------------- #

# backend: 原圖 > Zlib壓縮 > AES256加密 > MQTT發送

# esp32:   MQTT接收 > UART(Serial2 [RX:16 TX:17]) 發送

# ads:     UART(SoftWareSerial [RX:2 TX:3]) 接收 > AES解密 > Miniz解壓 > 電子紙

# -------------------------------------- #

# EPAPER(W、H)
EPAPER_W, EPAPER_H = 800, 480

# EX data
Payload = {
    "number": "P-114514",
    "id": "1",
    "name": "MyGO!!!!!",
    "case": "frcture",
    "medication": "Sumatriptan, Sanikit",
    "notice": "none",
    "location": "2F-01",
    "bed number": "1",
}

# EPAPER_payload
epaper_payload = {
    "Location": Payload["location"],
    "Bed number": Payload["bed number"],
    "Number": Payload["number"],
    "Name": Payload["name"],
    "Case": Payload["case"],
    "Medication": Payload["medication"],
    "Notice": Payload["notice"],
}

# QRcode_payload
QR_Payload = {"number": Payload["number"], "id": Payload["id"]}

# Gen_Image
epaper = GenerateEPaperImage(EPAPER_W, EPAPER_H)
epaper.gen_image(epaper_payload)

# Gen_QRcode & Convert
qr_image = epaper.add_qrcode(QR_Payload)

# Zlib_Compress
compressed_data = zlib.compress(qr_image.byte_data, 9)
print("Compress_Data len: ", len(compressed_data))

# AES_All_Image
aes_bytes = AESProcess.gen_all_aes_data(compressed_data)
print("AES_Bytes len: ", len(aes_bytes))

# Save_Json
ProcessFile.binary_image_2_base64_json(aes_bytes, "CompressAllPhoto.json")

# MQTT_Send
MQTTSend.send_data()
