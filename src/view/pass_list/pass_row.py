# pkpass_row.py
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
from .pass_row_header import PassRowHeader


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_row.ui')
class PassRow(Gtk.ListBoxRow):

    __gtype_name__ = 'PassRow'

    colored_box = Gtk.Template.Child()

    icon = Gtk.Template.Child()
    name = Gtk.Template.Child()

    def __init__(self, a_pass):
        super().__init__()
        self.__pass = a_pass

        try:
            background_color = self.__pass.background_color().as_tuple()
        except:
            background_color = (0,0,0)

        pixbuf = self.__pass.icon().as_pixbuf()

        # Find out the background color of the icon
        pixbuf_data = pixbuf.read_pixel_bytes().get_data()
        if not pixbuf.get_has_alpha() or pixbuf_data[3] > 0:
            background_color = pixbuf_data[0:3]

        self.colored_box.color(*background_color)
        self.icon.set_from_pixbuf(pixbuf)
        self.name.set_text(a_pass.description())

        # Gray the label out if the pass has expired
        if self.__pass.has_expired():
            self.name.set_sensitive(False)

    def data(self):
        return self.__pass

    def hide_header(self):
        self.set_header(None)

    def show_header(self):
        header = PassRowHeader(self.__pass)
        self.set_header(header)

    def style(self):
        return self.__pass.style()
