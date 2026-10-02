# qr_boarding_factory.py
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

from passes.digital_pass_factory import PassFactory
from passes.qr_code_reader import QRCodeReader, QRCodeReadError
from .qr_boarding import QRBoardingPass, QRBoardingPassAdapter


class QRBoardingFactory(PassFactory):
    """
    Create a QR Boarding Pass from an image file
    """

    @classmethod
    def understands(cls, pass_file):
        try:
            path = pass_file.get_path()
            if not path:
                return False

            path_lower = path.lower()

            # Check if it's a previously saved qr-boarding file
            if path_lower.endswith('.qr-boarding'):
                return True

            # Check if it's an image file
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            return any(path_lower.endswith(ext) for ext in image_extensions)

        except Exception:
            return False

    @classmethod
    def create(cls, pass_file):
        """
        Create a QR Boarding Pass object from an image file
        """
        path = pass_file.get_path()
        if not path:
            raise InvalidImageFile(_('Could not determine file path'))

        try:
            qr_codes = QRCodeReader.read_from_image_file(path)

            if not qr_codes:
                raise NoQRCodeFound()

            qr_data = qr_codes[0]['data']
            barcode_format = qr_codes[0]['type']

            boarding_pass = QRBoardingPass(qr_data, barcode_format)
            return QRBoardingPassAdapter(boarding_pass)

        except QRCodeReadError as e:
            raise InvalidImageFile(str(e))


class NoQRCodeFound(Exception):
    def __init__(self):
        message = _('No QR code found in image')
        super().__init__(message)


class InvalidImageFile(Exception):
    def __init__(self, message):
        super().__init__(message)
