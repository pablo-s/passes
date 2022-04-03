# pkpass_front_view.py
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

from gi.repository import Gtk

from .barcode_widget import BarcodeWidget


class PassFrontView:
    """
    A factory to instance the appropriate view
    """
    @staticmethod
    def new(a_pass):
        return FallbackView(a_pass)


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_front_view_fallback.ui')
class FallbackView(Gtk.Box):

    __gtype_name__ = 'FallbackView'

    logo = Gtk.Template.Child()
    logo_row = Gtk.Template.Child()
    description = Gtk.Template.Child()
    header_fields = Gtk.Template.Child()
    primary_fields = Gtk.Template.Child()
    secondary_fields = Gtk.Template.Child()
    auxiliary_fields = Gtk.Template.Child()

    def __init__(self, a_pass):
        super().__init__()

        self.logo.set_pixbuf(a_pass.logo())

        background_color = a_pass.background_color()
        self.logo_row.color(*background_color)
        self.logo_row.add_css_class('card')

        self.description.set_text(a_pass.description())

        for field_group_name in ['header_fields',
                                 'primary_fields',
                                 'secondary_fields',
                                 'auxiliary_fields']:

            field_group = getattr(a_pass, field_group_name)()
            gtk_list = getattr(self, field_group_name)

            if not field_group:
                gtk_list.set_visible(False)
                continue

            for field in field_group:
                label = field.label()
                value = field.value()

                self.add_field_to(gtk_list, label, value)

    def add_field_to(self, field_list, label, value):
        row = Gtk.Box()
        row.props.orientation = Gtk.Orientation.VERTICAL

        if label:
            label_widget = Gtk.Label()
            label_widget.set_text(label)
            label_widget.add_css_class('caption-heading')
            row.append(label_widget)

        label_widget = Gtk.Label()
        label_widget.set_text(value)
        row.append(label_widget)

        field_list.append(row)
        
