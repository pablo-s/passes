# pass_icon.py
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

from gi.repository import Gdk, Gtk

from .colored_box import ColoredBox


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_icon.ui')
class PassIcon(Gtk.Box):

    __gtype_name__ = 'PassIcon'

    colored_box = Gtk.Template.Child()
    icon = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.__pixbuf = None
        self.__saturation = 1.0

    def __guess_background_color(self, pixel_buffer):
        data = pixel_buffer.read_pixel_bytes().get_data()

        # This method assumes that the background color of an image is the color
        # of the first pixel of the image if it is not transparent.

        background_color = None
        if not pixel_buffer.get_has_alpha() or data[3] > 0:
            background_color = data[0:3]

        return background_color

    def __update(self):
        if not self.__pixbuf:
            return

        pixbuf = self.__pixbuf

        if self.__saturation != 1.0:
            # When the saturation changes, a copy of the pixbuf is made so that
            # the original image is not modified.

            pixbuf = self.__pixbuf.copy()
            pixbuf.saturate_and_pixelate(pixbuf,
                                         saturation=self.__saturation,
                                         pixelate=False)

        self.icon.set_from_pixbuf(pixbuf)

        color = self.__guess_background_color(pixbuf)
        if color:
            self.colored_box.color(*color)

    def set_background_color(self, color):
        self.colored_box.color(*color.as_tuple())

    def set_enabled(self, enabled):
        opacity = 1.0
        self.__saturation = 1.0

        if not enabled:
            opacity = 0.6
            self.__saturation = 0.0

        self.colored_box.set_opacity(opacity)
        self.__update()

    def set_image(self, image):
        self.__pixbuf = image.as_pixbuf()
        self.__update()

