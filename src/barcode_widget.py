# barcode_widget.py
#
# Copyright 2022 Pablo Sánchez Rodríguez
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

from gi.repository import Adw, Gdk, Graphene, Gtk

from .barcode_content_encoder import BarcodeContentEncoder


class BarcodeWidget(Gtk.Widget):

    __gtype_name__ = 'BarcodeWidget'

    FOREGROUND = '1';
    BACKGROUND = '2';

    def __init__(self):
        super().__init__()

        self.__data = []
        self.__data_width = 0
        self.__data_height = 0

        # Set foreground color to black
        self.__foreground_color = Gdk.RGBA()
        self.__foreground_color.red = 0.0
        self.__foreground_color.blue = 0.0
        self.__foreground_color.green = 0.0
        self.__foreground_color.alpha = 1.0

        # Amount of barcode dots/modules that should fit in every margin (either
        # horizontal or vertical)
        self.__margin_size_in_dots = 4

    def do_snapshot(self, snapshot):
        canvas_width = self.get_allocated_width()
        canvas_height = self.get_allocated_height()

        # Calculate the biggest dot size that allows drawing the full barcode in
        # the current canvas
        horizontal_dot_size = canvas_width // (self.__data_width + 2 * self.__margin_size_in_dots)
        vertical_dot_size = canvas_height // (self.__data_height + 2 * self.__margin_size_in_dots)
        self.__dot_size = min(horizontal_dot_size, vertical_dot_size)

        # Center the qr-code horizontal and vertically in the canvas
        offset_x = (canvas_width // 2) - (self.__data_width * self.__dot_size // 2)
        offset_y = (canvas_height // 2) - (self.__data_height * self.__dot_size // 2)

        for i in range(self.__data_height):
            for j in range(self.__data_width):

                is_foreground = \
                    self.__data[i * self.__data_width + j] == BarcodeWidget.FOREGROUND

                if not is_foreground:
                    continue

                x = j * self.__dot_size + offset_x
                y = i * self.__dot_size + offset_y
                w = self.__dot_size
                h = self.__dot_size

                rectangle = Graphene.Rect()
                rectangle.init(x, y, w, h)
                snapshot.append_color(self.__foreground_color, rectangle)

    def encode(self, format, message, encoding):
        encoding_function = None

        if format == 'PKBarcodeFormatAztec':
            encoding_function = BarcodeContentEncoder.encode_aztec_code

        elif format == 'PKBarcodeFormatQR':
            encoding_function = BarcodeContentEncoder.encode_qr_code

        else:
            raise BarcodeFormatNotSupported()

        module_list, width, height = encoding_function(message, encoding)

        self.__data = module_list
        self.__data_width = width
        self.__data_height = height


class BarcodeFormatNotSupported(Exception):
    def __init__(self):
        message = _('Barcode format not supported')
        super().__init__(message)
