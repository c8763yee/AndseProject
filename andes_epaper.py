import zlib
from typing import Any, Dict, List, Optional, Text, Union

import cv2
import numpy as np
import qrcode
from numpy.typing import NDArray
from typing_extensions import Self

from andes_aes256 import AESProcess


class GenerateEPaperImage:
    """電子紙圖像生成類別"""

    text_max_length: int = 16
    color_depth: int = 2
    color: Dict[str, int] = {"white": 0b11, "red": 0b01, "black": 0b00}
    image: Optional[NDArray[np.uint8]] = None
    img_data: Optional[NDArray[np.uint8]] = None
    byte_data: Optional[bytes] = None
    result_image: Optional[NDArray[np.uint8]] = None
    compress_data: Optional[bytes] = None

    def __init__(
        self,
        width: int = 640,
        height: int = 384,
        color: Optional[Dict[str, int]] = None,
    ) -> None:
        """初始化函數
        參數:
            width: 圖像寬度
            height: 圖像高度
            color: 自定義顏色對應表
        """
        self.width = width
        self.height = height
        if color:
            self.color = color
            self.color_depth = len(bin(max(color.values()))) - 2

    @classmethod
    def _convert_color(cls, color_value: List[int], threshold: int = 128) -> int:
        """顏色轉換方法
        將RGB顏色值轉換為電子紙可用的顏色值
        參數:
            color_value: RGB顏色值列表
            threshold: 顏色閾值
        """
        if (
            color_value[0] > threshold
            and color_value[1] > threshold
            and color_value[2] > threshold
        ):
            return cls.color["white"]
        elif color_value[2] > threshold:
            return cls.color["red"]
        else:
            return cls.color["black"]

    @classmethod
    def _split_text(cls, raw_text: Text) -> List[Text]:
        """文字分割方法
        將長文字依據最大長度分割為多行
        參數:
            raw_text: 原始文字
        """
        text_list = [""]
        for word in raw_text.split("_"):
            word += " "
            if len(text_list[-1] + word) >= cls.text_max_length:
                text_list.append(word)
            else:
                text_list[-1] += word
        return [word.strip() for word in text_list]

    def gen_image(self, data: Dict[str, Any]) -> Self:
        """生成圖像方法
        將字典資料轉換為圖像
        參數:
            data: 要顯示的資料字典
        """
        image = np.zeros((self.height, self.width, 3), np.uint8)
        image.fill(255)
        max_chars_per_line = 36
        y_offset = 50
        line_spacing = 30
        font_size = 0.8
        used_keys = set()

        for key, value in data.items():
            if key in used_keys:
                continue
            used_keys.add(key)
            text = f"{key}: {value}"
            if len(text) < max_chars_per_line:
                if "," in value:
                    value_lines = value.split(", ")
                    cv2.putText(
                        image,
                        key + ":",
                        (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_size,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    y_offset += line_spacing
                    for line in value_lines:
                        cv2.putText(
                            image,
                            line,
                            (20, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            font_size,
                            (0, 0, 0),
                            2,
                            cv2.LINE_AA,
                        )
                        y_offset += line_spacing
                else:
                    cv2.putText(
                        image,
                        text,
                        (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_size,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    y_offset += line_spacing
            else:
                lines = [
                    text[i : i + max_chars_per_line]
                    for i in range(0, len(text), max_chars_per_line)
                ]
                for line in lines:
                    cv2.putText(
                        image,
                        line,
                        (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_size,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    y_offset += line_spacing
        self.image = cv2.vconcat(image)
        cv2.imwrite("./photo_temp/photo.png", image)
        return self

    def generate_qrcode(self, encrypt_aes_data: Union[str, bytes]) -> None:
        """生成QR碼方法
        生成加密後的QR碼圖像
        參數:
            encrypt_aes_data: 加密後的資料
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=0.6,
        )
        qr.add_data(encrypt_aes_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save(f"./photo_temp/AES_QRcode.png")

    def add_qrcode(self, qr_data: Union[str, Dict[str, Any]]) -> Self:
        """添加QR碼方法
        將QR碼添加到主圖像中
        參數:
            qr_data: QR碼資料
        """
        encrypt_aes_data = AESProcess.gen_aes_data(qr_data)
        self.generate_qrcode(encrypt_aes_data)  # 在此AES加密QRcode
        qr_image = cv2.imread("./photo_temp/AES_QRcode.png")
        e_paper_image = cv2.imread("./photo_temp/photo.png")
        qr_image_np = cv2.cvtColor(
            cv2.cvtColor(qr_image, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2RGB
        )
        qr_x, qr_y = 470, 220
        e_paper_image[
            qr_y : qr_y + qr_image_np.shape[0], qr_x : qr_x + qr_image_np.shape[1]
        ] = qr_image_np
        cv2.imwrite("./photo_temp/result_image.png", e_paper_image)
        self.result_image = cv2.imread("./photo_temp/result_image.png")
        self.convert_image_to_data()
        return self

    def convert_image_to_data(self) -> Self:
        """Convert image data for e-paper display
        Args:
            x_start: Starting X coordinate for partial update
            y_start: Starting Y coordinate for partial update
        """
        # Ensure 1-bit color depth
        self.color_depth = 1

        width = self.result_image.shape[1]
        height = self.result_image.shape[0]
        bytes_per_line = width // 8

        # Initialize byte array
        self.img_data = np.zeros((bytes_per_line * height,), dtype=np.uint8)

        # Convert image to bytes, 8 pixels per byte
        for y in range(height):
            for x in range(0, width, 8):
                byte_val = 0
                for bit in range(8):
                    if x + bit < width:
                        # Pack 8 pixels into one byte
                        pixel = self._convert_color(self.result_image[y][x + bit])
                        byte_val |= pixel << (7 - bit)  # MSB first

                self.img_data[y * bytes_per_line + (x // 8)] = byte_val

        self.byte_data = self.img_data.tobytes()
        self.compress_data = zlib.compress(self.byte_data, 9)
        return self
