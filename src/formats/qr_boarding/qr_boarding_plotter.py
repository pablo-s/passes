# qr_boarding_plotter.py
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

from gi.repository import Gdk, Graphene, Pango

from passes.pass_widget import FieldLayout, PassFont, PassPlotter


class QRBoardingPassPlotter(PassPlotter):

    def __init__(self, a_pass, pass_widget):
        super().__init__(a_pass, pass_widget)
        self._pass = a_pass

        self._bg_color = Gdk.RGBA()
        self._bg_color.parse('#ffffff')
        self._fg_color = Gdk.RGBA()
        self._fg_color.parse('#000000')
        self._label_color = Gdk.RGBA()
        self._label_color.parse('#1e1e1e')

    @classmethod
    def new(cls, a_pass, pass_widget):
        return cls(a_pass, pass_widget)

    def plot(self, snapshot):
        self._snapshot = snapshot

        self._snapshot.save()
        self._plot_background()
        self._plot_header_fields()
        self._plot_primary_fields()
        self._plot_secondary_fields()
        self._plot_auxiliary_fields()
        self._snapshot.restore()

    def pass_height(self):
        return 480

    def _plot_background(self):
        rectangle = Graphene.Rect()
        rectangle.init(0, 0, self.pass_width(), self.pass_height())
        self._snapshot.append_color(self._bg_color, rectangle)

    def _plot_header_fields(self):
        fields = self._pass.header_fields()
        if not fields:
            return

        max_row_width = self.pass_width() - 2 * self.pass_margin()
        point = Graphene.Point()

        self._snapshot.save()
        point.x = self.pass_margin()
        point.y = self.pass_margin()
        self._snapshot.translate(point)

        for i, field in enumerate(fields):
            if i == 0:
                alignment = Pango.Alignment.LEFT
            else:
                alignment = Pango.Alignment.RIGHT

            field_layout = FieldLayout(self._pango_context, field, max_row_width,
                                       value_font=PassFont.biggest_value,
                                       alignment=alignment)
            field_layout.append(self._snapshot, self._label_color, self._fg_color)

        self._snapshot.restore()

        point.x = 0
        point.y = 90
        self._snapshot.translate(point)

    def _plot_primary_fields(self):
        fields = self._pass.primary_fields()
        if not fields:
            return

        max_row_width = self.pass_width() - 2 * self.pass_margin()

        self._snapshot.save()
        point = Graphene.Point()
        point.x = self.pass_margin()
        point.y = 0
        self._snapshot.translate(point)

        for field in fields:
            field_layout = FieldLayout(self._pango_context, field, max_row_width,
                                       value_font=PassFont.big_value)
            field_layout.append(self._snapshot, self._label_color, self._fg_color)

        self._snapshot.restore()

        point.x = 0
        point.y = 50
        self._snapshot.translate(point)

    def _plot_secondary_fields(self):
        fields = self._pass.secondary_fields()
        if fields:
            self._plot_fields_layouts(fields)

    def _plot_auxiliary_fields(self):
        fields = self._pass.auxiliary_fields()
        if fields:
            self._plot_fields_layouts(fields)

    def _plot_fields_layouts(self, fields):
        self._snapshot.save()

        point = Graphene.Point()
        point.x = self.pass_margin()
        point.y = 0
        self._snapshot.translate(point)

        row_height = 0
        rows, spacing_per_row = self._create_fields_layouts(fields)

        for row in rows:
            row_height = 0
            spacing = spacing_per_row.pop(0)
            amount_of_fields = len(row)

            self._snapshot.save()
            for index, field_layout in enumerate(row):
                if index == 0:
                    field_layout.set_alignment(Pango.Alignment.LEFT)
                elif index == amount_of_fields - 1:
                    field_layout.set_alignment(Pango.Alignment.RIGHT)
                else:
                    field_layout.set_alignment(Pango.Alignment.CENTER)

                field_layout.append(self._snapshot, self._label_color, self._fg_color)

                layout_height = field_layout.get_height()
                if layout_height > row_height:
                    row_height = layout_height

                point.x = field_layout.get_width() + spacing
                point.y = 0
                self._snapshot.translate(point)

            self._snapshot.restore()

            point.x = 0
            point.y = row_height + 12
            self._snapshot.translate(point)

        self._snapshot.restore()

        point.x = 0
        point.y = row_height * len(rows) + self.pass_margin()
        self._snapshot.translate(point)
