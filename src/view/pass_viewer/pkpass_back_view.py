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

from .pkpass_field_row import PassFieldRow


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_back_view.ui')
class PassBackView(Gtk.Box):

    __gtype_name__ = 'PassBackView'

    back_fields = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    def clean(self):
        row = self.back_fields.get_row_at_index(0)
        while row:
            self.back_fields.remove(row)
            row = self.back_fields.get_row_at_index(0)

    def content(self, a_pass):
        self.clean()
        back_fields = a_pass.back_fields()

        # Make the field list invisible if we do not have back fields
        self.back_fields.set_visible(back_fields)

        for field in back_fields:
            label = field.label()
            value = field.value()

            passFieldRow = PassFieldRow(label, value, create_links=True)
            passFieldRow.set_halign(Gtk.Align.START)
            self.back_fields.append(passFieldRow)
