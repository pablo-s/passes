# barcode_widget.py
#
# Copyright 2022-2023 Pablo Sánchez Rodríguez
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

from gi.repository import Adw, Gdk, Graphene, Gsk, Gtk

from .barcode_content_encoder import BarcodeContentEncoder
from .digital_pass import Color


class BarcodeWidget(Gtk.Widget):

    __gtype_name__ = 'BarcodeWidget'

    FOREGROUND = '1';
    BACKGROUND = '2';

    def __init__(self):
        super().__init__()

        self.__data = []
        self.__data_width = 0
        self.__data_height = 0

        # Set background color to white
        self.__background_color = Color.named('white').as_gdk_rgba()

        # Set foreground color to black
        self.__foreground_color = Color.named('black').as_gdk_rgba()

        # Amount of barcode dots/modules that should fit in every margin (either
        # horizontal or vertical)
        self.__margin_size = 4

    def aspect_ratio(self):
        return (self.__data_width + self.__margin_size) / (self.__data_height + self.__margin_size)

    def do_snapshot(self, snapshot):
        canvas_width = self.get_allocated_width()
        canvas_height = self.get_allocated_height()

        barcode_width = self.__data_width + 2 * self.__margin_size
        barcode_height = self.__data_height + 2 * self.__margin_size

        h_scaling = canvas_width / barcode_width
        v_scaling = canvas_height / barcode_height
        scaling_factor = int(min(h_scaling, v_scaling))

        translation = Graphene.Point()
        translation.x = (canvas_width - barcode_width * scaling_factor) / 2
        translation.y = (canvas_height - barcode_height * scaling_factor) / 2
        snapshot.translate(translation)

        snapshot.scale(scaling_factor, scaling_factor)


        # Draw the barcode
        for i in range(self.__data_height):
            for j in range(self.__data_width):

                is_foreground = \
                    self.__data[i * self.__data_width + j] == BarcodeWidget.FOREGROUND

                if not is_foreground:
                    continue

                rectangle = Graphene.Rect()
                rectangle.init(j + self.__margin_size,
                               i + self.__margin_size,
                               1,
                               1)
                snapshot.append_color(self.__foreground_color, rectangle)

    def encode(self, format, message, encoding):
        encoding_function = None

        if format in ['AZTEC', 'PKBarcodeFormatAztec']:
            encoding_function = BarcodeContentEncoder.encode_aztec_code
            self.__margin_size = 2

        elif format in ['CODE_128', 'PKBarcodeFormatCode128']:
            encoding_function = BarcodeContentEncoder.encode_code128_code
            self.__margin_size = 7

        elif format in ['PDF_417', 'PKBarcodeFormatPDF417']:
            encoding_function = BarcodeContentEncoder.encode_pdf417_code
            self.__margin_size = 2

        elif format in ['PKBarcodeFormatQR', 'QR_CODE']:
            encoding_function = BarcodeContentEncoder.encode_qr_code

        else:
            raise BarcodeFormatNotSupported()

        module_list, width, height = encoding_function(message, encoding)

        self.__data = module_list
        self.__data_width = width
        self.__data_height = height

    def minimum_height(self):
        return self.__data_height + 2 * self.__margin_size

    def minimum_width(self):
        return self.__data_width + 2 * self.__margin_size


class BarcodeFormatNotSupported(Exception):
    def __init__(self):
        message = _('Barcode format not supported')
        super().__init__(message)
