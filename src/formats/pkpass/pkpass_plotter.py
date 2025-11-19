# pkpass_plotter.py
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


class PkPassPlotter(PassPlotter):

    PRIMARY_FIELD_LABEL_FONT = PassFont.label
    PRIMARY_FIELD_VALUE_FONT = PassFont.biggest_value

    def __init__(self, a_pass, pass_widget):
        super().__init__(a_pass, pass_widget)

        pkpass = a_pass.adaptee()

        # Background color
        bg_color = pkpass.background_color()
        self._bg_color = bg_color.as_gdk_rgba() \
            if bg_color else Color.named('white').as_gdk_rgba()

        # Foreground color
        fg_color = pkpass.foreground_color()
        self._fg_color = fg_color.as_gdk_rgba() \
            if fg_color else Color.named('black').as_gdk_rgba()

        # Label color
        label_color = pkpass.label_color()
        self._label_color = label_color.as_gdk_rgba() \
            if label_color else Color.named('black').as_gdk_rgba()

        # Images
        self._background_texture = None
        self._logo_texture = None
        self._strip_texture = None

        if pkpass.background():
            self._background_texture = pkpass.background().as_texture()

        if pkpass.logo():
            self._logo_texture = pkpass.logo().as_texture()

        if pkpass.strip():
            self._strip_texture = pkpass.strip().as_texture()

        # Fields
        self._header_fields = pkpass.header_fields()
        self._primary_fields = pkpass.primary_fields()
        self._secondary_fields = pkpass.secondary_fields()
        self._auxiliary_fields = pkpass.auxiliary_fields()

    @classmethod
    def new(clss, a_pass, pass_widget):
        pkpass = a_pass.adaptee()
        style = pkpass.style()

        if style == 'boardingPass':
            return BoardingPassPlotter(a_pass, pass_widget)
        elif style in ['coupon', 'storeCard']:
            return CouponPlotter(a_pass, pass_widget)
        elif style == 'eventTicket':
            return EventTicketPlotter(a_pass, pass_widget)
        elif style == 'generic':
            return GenericPlotter(a_pass, pass_widget)

    def plot(self, snapshot):
        self._snapshot = snapshot

        self._snapshot.save()
        self._plot_background()
        self._plot_header()
        self._plot_primary_fields()
        self._plot_secondary_and_axiliary_fields()
        self._snapshot.restore()

    def _plot_header(self):
        header_height = 32
        header_width = self.pass_width() - (self.pass_margin() * 2)

        # Draw the logo if it exists
        if self._logo_texture:
            logo_height_scale = header_height / self._logo_texture.get_height()
            logo_width_scale = (header_width / 2) / self._logo_texture.get_width()
            logo_scale = min(logo_height_scale, logo_width_scale)
            scaled_logo_width = self._logo_texture.get_width() * logo_scale
            scaled_logo_height = self._logo_texture.get_height() * logo_scale

            rectangle = Graphene.Rect()
            rectangle.init(self.pass_margin(), self.pass_margin(), scaled_logo_width, scaled_logo_height)
            self._snapshot.append_texture(self._logo_texture, rectangle)

        point = Graphene.Point()
        point.y = self.pass_margin()

        right_margin = (self.pass_width() - self.pass_margin())

        self._snapshot.save()
        self._snapshot.translate(point)

        max_row_width = self.pass_width() - 2 * self.pass_margin()

        for field in self._header_fields:
            field_layout = FieldLayout(self._pango_context, field, max_row_width,
                                       alignment = Pango.Alignment.RIGHT)

            field_original_width = field_layout.get_width()
            field_layout.set_width(right_margin)

            field_layout.append(self._snapshot,
                                self._label_color,
                                self._fg_color)

            right_margin -= field_original_width + self.pass_margin()

        self._snapshot.restore()

        # Perform a translation so that the next drawing starts below this one
        point.x = 0
        point.y = header_height + 3 * self.pass_margin()
        self._snapshot.translate(point)

    def _plot_primary_fields(self):
        raise NotImplementedError

    def _plot_secondary_and_axiliary_fields(self):
        raise NotImplementedError

    def _plot_footer(self):
        raise NotImplementedError


class PkPassWithStripPlotter(PkPassPlotter):
    """
    PkPassWithStripPlotter is a PkPassPlotter for PKPasses that may contain a
    strip image.
    """

    STRIP_IMAGE_MAX_HEIGHT = 123

    def __init__(self, pkpass, pkpass_widget):
        super().__init__(pkpass, pkpass_widget)

    def _plot_primary_fields(self):

        # Draw the strip

        strip_height = 0
        draw_strip = self._strip_texture and not self._background_texture

        if draw_strip:
            strip_scale = self.pass_width() / self._strip_texture.get_width()
            strip_height = self._strip_texture.get_height() * strip_scale

            rectangle = Graphene.Rect()
            rectangle.init(0, -self.pass_margin(), self.pass_width(), strip_height)

            strip_height = min(self.STRIP_IMAGE_MAX_HEIGHT, strip_height)
            strip_area = Graphene.Rect()
            strip_area.init(0, -self.pass_margin(), self.pass_width(), strip_height)

            self._snapshot.push_clip(strip_area)
            self._snapshot.append_texture(self._strip_texture, rectangle)
            self._snapshot.pop()

        # Draw the primary fields

        point = Graphene.Point()
        field_layout_height = 0
        max_row_width = self.pass_width() - 2 * self.pass_margin()

        if self._primary_fields:
            field_layout = FieldLayout(self._pango_context,
                                       self._primary_fields[0],
                                       max_row_width,
                                       value_font = self.PRIMARY_FIELD_VALUE_FONT)

            field_layout_height = field_layout.get_height()
            self._snapshot.save()

            point.x = self.pass_margin()
            point.y = 0
            self._snapshot.translate(point)

            label_color = self._fg_color if draw_strip else self._label_color
            field_layout.append(self._snapshot, label_color, self._fg_color)

            self._snapshot.restore()

        # Perform a translation so that the next drawing starts below this one
        point.x = 0
        point.y = strip_height if strip_height > field_layout_height \
                               else field_layout_height + 2 * self.pass_margin()
        self._snapshot.translate(point)


class BoardingPassPlotter(PkPassPlotter):

    def __init__(self, pkpass, pkpass_widget):
        super().__init__(pkpass, pkpass_widget)

    def _plot_primary_fields(self):

        if not self._primary_fields:
            return

        max_row_width = self.pass_width() - 2 * self.pass_margin()

        # Origin
        origin_field = FieldLayout(self._pango_context,
                                   self._primary_fields[0],
                                   max_row_width,
                                   value_font = PassFont.biggest_value,
                                   alignment = Pango.Alignment.LEFT)

        # Destination
        destination_field = FieldLayout(self._pango_context,
                                        self._primary_fields[1],
                                        max_row_width,
                                        value_font = PassFont.biggest_value,
                                        alignment = Pango.Alignment.RIGHT)

        # Check if font size needs to be reduced
        if origin_field.get_value_width() > (max_row_width / 2) or destination_field.get_value_width() > (max_row_width / 2):
            origin_field.set_value_font(PassFont.big_value)
            destination_field.set_value_font(PassFont.big_value)

        if origin_field.get_value_width() > (max_row_width / 2) or destination_field.get_value_width() > (max_row_width / 2):
            origin_field.set_value_font(PassFont.value)
            destination_field.set_value_font(PassFont.value)

        # Set final widths
        destination_field.set_width(self.pass_width() - 2 * self.pass_margin())
        origin_field.set_width(max_row_width / 2)
        self._snapshot.save()

        point = Graphene.Point()
        point.x = self.pass_margin()
        point.y = 0
        self._snapshot.translate(point)

        origin_field.append(self._snapshot, self._label_color, self._fg_color)
        destination_field.append(self._snapshot, self._label_color, self._fg_color)

        self._snapshot.restore()

        # Perform a translation so that the next drawing starts below this one
        point.x = 0
        point.y = max(origin_field.get_height(), destination_field.get_height()) + 2 * self.pass_margin()
        self._snapshot.translate(point)

    def _plot_secondary_and_axiliary_fields(self):
        self._plot_fields_layouts(self._auxiliary_fields)
        self._plot_fields_layouts(self._secondary_fields)


class CouponPlotter(PkPassWithStripPlotter):

    STRIP_IMAGE_MAX_HEIGHT = 144

    def __init__(self, pkpass, pkpass_widget):
        super().__init__(pkpass, pkpass_widget)

    def _plot_secondary_and_axiliary_fields(self):
        self._plot_fields_layouts(self._secondary_fields + \
                                  self._auxiliary_fields)


class EventTicketPlotter(PkPassWithStripPlotter):

    PRIMARY_FIELD_VALUE_FONT = PassFont.big_value
    STRIP_IMAGE_MAX_HEIGHT = 98

    def __init__(self, pkpass, pkpass_widget):
        super().__init__(pkpass, pkpass_widget)

    def _plot_background(self):

        if not self._strip_texture and self._background_texture:
            rectangle = Graphene.Rect()
            rectangle.init(-self.pass_background_blur_radius(),
                           -self.pass_background_blur_radius(),
                           self.pass_width() + 2 * self.pass_background_blur_radius(),
                           self.pass_height() + 2 * self.pass_background_blur_radius())

            self._snapshot.push_blur(self.pass_background_blur_radius())
            self._snapshot.append_texture(self._background_texture, rectangle)
            self._snapshot.pop()

        else:
            super()._plot_background()

    def _plot_secondary_and_axiliary_fields(self):
        self._plot_fields_layouts(self._secondary_fields + \
                                  self._auxiliary_fields)



class GenericPlotter(PkPassPlotter):

    def __init__(self, pkpass, pkpass_widget):
        super().__init__(pkpass, pkpass_widget)

    def _plot_primary_fields(self):
        if not self._primary_fields:
            return

        max_row_width = self.pass_width() - 2 * self.pass_margin()

        field_layout = FieldLayout(self._pango_context,
                                   self._primary_fields[0],
                                   max_row_width,
                                   value_font = PassFont.big_value)
        self._snapshot.save()

        point = Graphene.Point()
        point.x = self.pass_margin()
        point.y = 0
        self._snapshot.translate(point)

        field_layout.append(self._snapshot, self._label_color, self._fg_color)

        self._snapshot.restore()

        # Perform a translation so that the next drawing starts below this one
        point.x = 0
        point.y = field_layout.get_height() + 2 * self.pass_margin()
        self._snapshot.translate(point)

    def _plot_secondary_and_axiliary_fields(self):
        self._plot_fields_layouts(self._auxiliary_fields)
        self._plot_fields_layouts(self._secondary_fields)
