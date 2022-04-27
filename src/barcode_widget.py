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

        # Amount of pixels used to draw each of the dots
        # that compound the QR-code
        self.__dot_size = 4

    def do_snapshot(self, snapshot):
        canvas_width = self.get_allocated_width()

        # Center the qr-code horizontally in the canvas
        offset_x = (canvas_width // 2) - (self.__data_width * self.__dot_size // 2)

        for i in range(self.__data_width):
            for j in range(self.__data_height):

                is_foreground = \
                    self.__data[i * self.__data_width + j] == BarcodeWidget.FOREGROUND

                if not is_foreground:
                    continue

                x = i * self.__dot_size + offset_x
                y = j * self.__dot_size
                w = self.__dot_size
                h = self.__dot_size

                rectangle = Graphene.Rect()
                rectangle.init(x, y, w, h)
                snapshot.append_color(self.__foreground_color, rectangle)

    def message(self, message, encoding):

        module_list, side = \
            BarcodeContentEncoder.encode_qr_code(message, encoding)

        self.__data = module_list
        self.__data_width = side
        self.__data_height = side

        barcode_height = self.__data_height * self.__dot_size
        bottom_margin = 4 * self.__dot_size
        self.props.height_request = barcode_height + bottom_margin
