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

import ctypes

from gi.repository import Adw, Gtk

from .barcode_content_encoder import BarcodeContentEncoder


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/barcode_widget.ui')
class BarcodeWidget(Gtk.DrawingArea):

    __gtype_name__ = 'BarcodeWidget'

    FOREGROUND = '1';
    BACKGROUND = '2';

    def __init__(self):
        super().__init__()

        self.__data = []
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

                is_foreground = \
                    self.__data[i * self.__data_width + j] == BarcodeWidget.FOREGROUND

                if not is_foreground:
                    continue

                cairo_context.fill()
                cairo_context.rectangle(i * self.__dot_size + offset_x,
                                        j * self.__dot_size,
                                        self.__dot_size,
                                        self.__dot_size)

    def message(self, message, encoding):

        module_list, side = \
            BarcodeContentEncoder.encode_qr_code(message, encoding)

        self.__data = module_list
        self.__data_width = side
        self.__data_height = side

        self.set_content_height(self.__data_height * self.__dot_size)
