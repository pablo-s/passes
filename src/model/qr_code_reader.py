# qr_code_reader.py
#
# Copyright 2026 Jan-Michael Brummer <jan.brummer@tabos.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PIL import Image


ZXING_AVAILABLE = None


def _is_zxing_available():
    global ZXING_AVAILABLE
    if ZXING_AVAILABLE is None:
        try:
            import zxingcpp
            ZXING_AVAILABLE = True
        except ImportError:
            ZXING_AVAILABLE = False
    return ZXING_AVAILABLE


class QRCodeReader:
    """
    A reader for barcodes (QR, Aztec, etc.) from images
    """

    @classmethod
    def read_from_image_file(cls, image_path):
        try:
            image = Image.open(image_path)
            return cls._decode_image(image)
        except Exception as e:
            raise QRCodeReadError(f"Could not read image: {str(e)}")

    @classmethod
    def _prepare_image(cls, image):
        """
        Convert image to RGB (required by most decoders)
        """
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            return background
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image

    @classmethod
    def _decode_image(cls, image):
        rgb_image = cls._prepare_image(image)
        return cls._try_decode(rgb_image)

    @classmethod
    def _try_decode(cls, image):
        if not _is_zxing_available():
            return []

        try:
            import zxingcpp
            decoded = zxingcpp.read_barcodes(image)
            if decoded:
                results = []
                for obj in decoded:
                    results.append({
                        'type': str(obj.format),
                        'data': obj.text,
                    })
                return results
        except Exception as e:
            print(f"zxing-cpp error: {e}")

        return []


class QRCodeReadError(Exception):
    """Exception raised when barcode reading fails"""
    pass
