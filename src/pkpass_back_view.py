# pkpass_back_view.py
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


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_back_view.ui')
class PassBackView(Gtk.Box):

    __gtype_name__ = 'PassBackView'

    back_fields = Gtk.Template.Child()

    def __init__(self, a_pass):
        super().__init__()

        for header_field in a_pass.back_fields():

            if 'label' not in header_field.keys():
                value = header_field['value']
                self.add_simple_field_to(self.back_fields, value)
                continue

            label = header_field['label']
            value = header_field['value']

            self.add_field_to(self.back_fields, label, value)

    def add_field_to(self, field_list, label, value):
        row = Gtk.Box()
        row.props.orientation = Gtk.Orientation.VERTICAL

        label_widget = Gtk.Label()
        label_widget.set_text(label)
        label_widget.add_css_class('caption-heading')
        row.append(label_widget)

        label_widget = Gtk.Label()
        label_widget.set_text(value)

        row.append(label_widget)
        field_list.append(row)

    def add_simple_field_to(self, field_list, value):
        label_widget = Gtk.Label()
        label_widget.set_text(value)
        label_widget.set_wrap(True)
        label_widget.set_halign(Gtk.Align.START)
        field_list.append(label_widget)

