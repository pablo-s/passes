# pkpass_field_row.py
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


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_field_row.ui')
class PassFieldRow(Gtk.Box):

    __gtype_name__ = 'PassFieldRow'

    label = Gtk.Template.Child()
    value = Gtk.Template.Child()

    def __init__(self, label, value):
        super().__init__()

        if label:
            self.label.set_text(label)
        else:
            self.label.hide()

        self.value.set_text(str(value))

    def set_halign(self, alignment):
        self.label.set_halign(alignment)
        self.value.set_halign(alignment)
