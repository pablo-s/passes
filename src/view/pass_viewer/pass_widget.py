# pass_widget.py
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

from gi.repository import Adw, Gdk, GObject, Graphene, Gsk, Gtk, Pango

from .barcode_widget import BarcodeWidget
from .digital_pass import Color


class PassFont:
    label = Pango.FontDescription.new()
    label.set_size(9 * Pango.SCALE)
    label.set_weight(600)

    value = Pango.FontDescription.new()
    value.set_size(11 * Pango.SCALE)

    big_value = Pango.FontDescription.new()
    big_value.set_size(17 * Pango.SCALE)

    biggest_value = Pango.FontDescription.new()
    biggest_value.set_size(24 * Pango.SCALE)


class FieldLayout:

    def __init__(self,
                 pango_context,
                 field,
                 max_width,
                 label_font = PassFont.label,
                 value_font = PassFont.value,
                 alignment = Pango.Alignment.LEFT):

        self.__label = Pango.Layout(pango_context)
        self.__label.set_alignment(alignment)
        self.__label.set_font_description(label_font)
        self.__label.set_text(field.label() if field.label() else '')

        self.__value = Pango.Layout(pango_context)
        self.__value.set_alignment(alignment)
        self.__value.set_font_description(value_font)
        self.__value.set_text(str(field.value()))
        self.__value.set_wrap(Pango.WrapMode.WORD_CHAR)

        width = max(self.__label.get_pixel_size().width,
                    self.__value.get_pixel_size().width)

        width = min(width, max_width) * Pango.SCALE

        self.__value.set_width(width)
        self.__label.set_width(width)

    def append(self, snapshot, label_color, value_color):
        label_height = self.__label.get_pixel_size().height
        value_height = self.__value.get_pixel_size().height

        snapshot.save()
        snapshot.append_layout(self.__label, label_color)

        point = Graphene.Point()
        point.y = label_height
        snapshot.translate(point)

        snapshot.append_layout(self.__value, value_color)
        snapshot.restore()

    def get_height(self):
        return self.__label.get_pixel_size().height + self.__value.get_pixel_size().height

    def get_width(self):
        return self.__label.get_width() / Pango.SCALE

    def set_alignment(self, alignment):
        self.__label.set_alignment(alignment)
        self.__value.set_alignment(alignment)

    def set_width(self, width):
        self.__label.set_width(width * Pango.SCALE)
        self.__value.set_width(width * Pango.SCALE)


class PassPlotter:

    def __init__(self, a_pass, pass_widget):
        self._pass_widget = pass_widget
        self._pango_context = pass_widget.get_pango_context()

    def _create_fields_layouts(self, fields):
        rows = []
        spacing_per_row = []

        current_row = []
        accumulated_width = 0

        max_row_width = self.pass_width() - 2 * self.pass_margin()

        for field in fields:
            field_layout = FieldLayout(self._pango_context, field, max_row_width)
            field_width = field_layout.get_width()

            if (accumulated_width + field_width) + len(current_row) * self.pass_margin() < max_row_width:
                current_row.append(field_layout)
                accumulated_width += field_width
                continue

            spacing = (max_row_width - accumulated_width) / (len(current_row)-1) if len(current_row) > 1 else 0
            spacing_per_row.append(spacing)
            rows.append(current_row)

            accumulated_width = field_width
            current_row = []
            current_row.append(field_layout)

        if current_row:
            spacing = (max_row_width - accumulated_width) / (len(current_row)-1) if len(current_row) > 1 else 0
            spacing_per_row.append(spacing)
            rows.append(current_row)

        return rows, spacing_per_row

    def _plot_background(self):
        rectangle = Graphene.Rect()
        rectangle.init(0, 0, self.pass_width(), self.pass_height())
        self._snapshot.append_color(self._bg_color, rectangle)

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

                # Decide the alignment of the label and value according to the
                # location of the field in the row.

                if index == 0:
                    field_layout.set_alignment(Pango.Alignment.LEFT)
                elif index == amount_of_fields - 1:
                    field_layout.set_alignment(Pango.Alignment.RIGHT)
                else:
                    field_layout.set_alignment(Pango.Alignment.CENTER)

                # Plot the standard field
                field_layout.append(self._snapshot, self._label_color, self._fg_color)

                layout_height = field_layout.get_height()
                if layout_height > row_height:
                    row_height = layout_height

                # Add a horizontal space between fields
                point.x = field_layout.get_width() + spacing
                point.y = 0
                self._snapshot.translate(point)

            self._snapshot.restore()

            # Add a vertical space between rows
            point.x = 0
            point.y = row_height + 6
            self._snapshot.translate(point)

        self._snapshot.restore()

        # Perform a translation so that the next drawing starts below this one
        point.x = 0
        point.y = row_height * len(rows) + self.pass_margin()
        self._snapshot.translate(point)

    def pass_background_blur_radius(self):
        return 30

    def pass_height(self):
        return 420

    def pass_margin(self):
        return 12

    def pass_width(self):
        return 320

    def plot(self, snapshot):
        raise NotImplementedError()


class PassWidget(Gtk.Fixed):

    __gtype_name__ = 'PassWidget'

    def __init__(self):
        super().__init__()

        self.__pass_plotter = None
        self.__barcode_button = None
        self.__children = []

        self.props.hexpand = False
        self.props.vexpand = True
        self.props.halign = Gtk.Align.CENTER
        self.props.valign = Gtk.Align.CENTER

        self.props.focusable = True

        self.add_css_class('card')

    def __on_barcode_clicked(self, args):
        self.emit('barcode_clicked')

    @GObject.Signal
    def barcode_clicked(self):
        pass

    def do_snapshot(self, snapshot):
        if not self.__pass_plotter:
            return

        self.__pass_plotter.plot(snapshot)

        if self.__barcode_button:
            self.snapshot_child(self.__barcode_button, snapshot)

    def content(self, a_pass):
        if self.__barcode_button:
            self.remove(self.__barcode_button)
            self.__barcode_button = None

        self.__pass_plotter = a_pass.plotter(self)
        self.props.width_request = self.__pass_plotter.pass_width()
        self.props.height_request = self.__pass_plotter.pass_height()
        self.create_barcode_button(a_pass)

        # After changing the plotter, we have to redraw the widget
        self.queue_draw()

    def create_barcode_button(self, a_pass):
        barcode = a_pass.barcodes()[0]

        if not barcode:
            return

        self.__barcode_button = Gtk.Button()
        self.__barcode_button.connect('clicked', self.__on_barcode_clicked)
        self.__barcode_button.add_css_class('barcode-button')
        barcode_widget = BarcodeWidget()
        barcode_widget.encode(barcode.format(),
                              barcode.message(),
                              barcode.message_encoding())

        aspect_ratio = barcode_widget.aspect_ratio()

        # Square codes
        if aspect_ratio == 1:
            max_times = 140 // barcode_widget.minimum_height()

            barcode_button_width = max_times * barcode_widget.minimum_height()
            barcode_button_height = max_times * barcode_widget.minimum_height()

        # Horizontal codes
        elif aspect_ratio > 1:
            max_times = (self.__pass_plotter.pass_width() - 2*self.__pass_plotter.pass_margin()) // barcode_widget.minimum_width()

            if max_times * barcode_widget.minimum_height() > 140:
                max_times = 140 // barcode_widget.minimum_height()

            barcode_button_width = max_times * barcode_widget.minimum_width()
            barcode_button_height = max_times * barcode_widget.minimum_height()

        # Vertical codes
        else:
            barcode_button_width = 177
            barcode_button_height = 177

        self.__barcode_button.props.width_request = barcode_button_width
        self.__barcode_button.props.height_request = barcode_button_height

        self.__barcode_button.set_child(barcode_widget)
        self.put(self.__barcode_button,
                 self.__pass_plotter.pass_width()/2 - barcode_button_width/2,
                 self.__pass_plotter.pass_height() - self.__pass_plotter.pass_margin() - barcode_button_height)
