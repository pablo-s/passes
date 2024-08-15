# espass_plotter.py
#
# Copyright 2022-2024 Pablo Sánchez Rodríguez
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

from gi.repository import Graphene, Pango

from passes.digital_pass import Color
from passes.pass_widget import FieldLayout, PassFont, PassPlotter


class EsPassPlotter(PassPlotter):

    def __init__(self, a_pass, pass_widget):
        super().__init__(a_pass, pass_widget)
        espass = a_pass.adaptee()

        # Accent color
        accent_color = espass.accent_color()
        self._accent_color = accent_color.as_gdk_rgba() \
            if accent_color else Gdk.RGBA()

        # Background color
        self._bg_color = Color.named('white').as_gdk_rgba()

        # Foreground color
        self._fg_color = Color.named('black').as_gdk_rgba()

        # Label color
        self._label_color = self._fg_color.copy()

        # Logo
        self._logo_texture  = None

        if espass.icon():
            self._logo_texture  = espass.icon().as_texture()

        # Fields
        self._fields = espass.front_fields()

    def _plot_background(self):
        rectangle = Graphene.Rect()
        rectangle.init(0, 0, self.pass_width(), self.pass_height())
        self._snapshot.append_color(self._bg_color, rectangle)

    def _plot_fields(self):
        self._plot_fields_layouts(self._fields)

    def _plot_header(self):
        header_height = 32

        rectangle = Graphene.Rect()
        rectangle.init(0, 0, self.pass_width(), header_height + 2 * self.pass_margin())
        self._snapshot.append_color(self._accent_color, rectangle)

        # Draw the logo if it exists
        if self._logo_texture:
            logo_scale = header_height / self._logo_texture.get_height()
            logo_width = self._logo_texture.get_width() * logo_scale

            rectangle = Graphene.Rect()
            rectangle.init(self.pass_margin(), self.pass_margin(), logo_width, header_height)
            self._snapshot.append_texture(self._logo_texture, rectangle)

        # Perform a translation so that the next drawing starts below this one
        point = Graphene.Point()
        point.y = header_height + 3 * self.pass_margin()
        self._snapshot.translate(point)

    def plot(self, snapshot):
        self._snapshot = snapshot

        self._snapshot.save()
        self._plot_background()
        self._plot_header()
        self._plot_fields()
        self._snapshot.restore()

