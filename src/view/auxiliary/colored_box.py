# colored_box.py
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

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/colored_box.ui')
class ColoredBox(Gtk.Box):

    __gtype_name__ = 'ColoredBox'

    def __init__(self):
        super().__init__()
        self.__color = (0, 0, 0)

        self.__style_context = self.get_style_context()
        self.__style_context.add_class('customclass')

        self.__css_provider = Gtk.CssProvider()
        self.__style_context.add_provider(self.__css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def color(self, r, g, b):
        rgb_color = 'rgb({},{},{})'.format(r, g, b)
        css_code = '.customclass{ background-color: ' + rgb_color + ';}'
        self.__css_provider.load_from_data(bytes(css_code, 'utf-8'))
