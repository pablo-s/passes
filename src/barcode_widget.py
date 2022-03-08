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

import qrcode

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/barcode_widget.ui')
class BarcodeWidget(Gtk.DrawingArea):

    __gtype_name__ = 'BarcodeWidget'

    def __init__(self):
        super().__init__()

        self.__data_matrix = []
        self.__data_width = 0
        self.__data_height = 0

        # Amount of pixels used to draw each of the dots
        # that compound the QR-code
        self.__dot_size = 4

        self.set_draw_func(self._update_drawing_area)
        self.set_content_height(self.__data_height * self.__dot_size)

    def _update_drawing_area(self, drawing_area, cairo_context, canvas_width, canvas_height):
        # Center the qr-code horizontally in the canvas
        offset_x = (canvas_width // 2) - (self.__data_width * self.__dot_size // 2)

        for i in range(self.__data_width):
            for j in range(self.__data_height):
                dot_is_dark = self.__data_matrix[i][j]

                if not dot_is_dark:
                    continue

                cairo_context.fill()
                cairo_context.rectangle(i * self.__dot_size + offset_x,
                                        j * self.__dot_size,
                                        self.__dot_size,
                                        self.__dot_size)

    def message(self, message, encoding):
        qr_code = qrcode.QRCode(border = 0)
        qr_code.add_data(message.encode(encoding))

        self.__data_matrix = qr_code.get_matrix()
        self.__data_width = len(self.__data_matrix)
        self.__data_height = len(self.__data_matrix[0])
        self.set_content_height(self.__data_height * self.__dot_size)

