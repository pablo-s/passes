# pkpass_back_view.py
#
# Copyright 2022-2023 Pablo Sánchez Rodríguez
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

from .pass_field_row import PassFieldRow


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/additional_information_pane.ui')
class AdditionalInformationPane(Gtk.Stack):

    __gtype_name__ = 'AdditionalInformationPane'

    fields = Gtk.Template.Child()

    def content(self, a_pass):
        self.fields.remove_all()
        fields = a_pass.additional_information()

        if len(fields) == 0:
            self.set_visible_child_name("empty_page")
        else:
            self.set_visible_child_name("fields_page")

        for field in fields:
            label = field.label()
            value = field.value()

            passFieldRow = PassFieldRow()
            passFieldRow.set_label(label)
            passFieldRow.set_value(value)
            self.fields.append(passFieldRow)
