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
class AdditionalInformationPane(Gtk.Box):

    __gtype_name__ = 'AdditionalInformationPane'

    fields = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        # Create a placeholder widget to be displayed when the pane is empty
        placeholder = Adw.StatusPage.new()
        placeholder.set_icon_name('info-symbolic')
        placeholder.set_title(_('No Additional Information'))
        placeholder.add_css_class('compact')
        self.fields.set_placeholder(placeholder)

    def clean(self):
        row = self.fields.get_row_at_index(0)
        while row:
            self.fields.remove(row)
            row = self.fields.get_row_at_index(0)

    def content(self, a_pass):
        self.clean()
        fields = a_pass.additional_information()

        if len(fields) == 0:
            alignment = Gtk.Align.FILL
            if self.fields.has_css_class('boxed-list'):
                self.fields.remove_css_class('boxed-list')
        else:
            alignment = Gtk.Align.START
            if not self.fields.has_css_class('boxed-list'):
                self.fields.add_css_class('boxed-list')

        self.fields.set_valign(alignment)

        for field in fields:
            label = field.label()
            value = field.value()

            passFieldRow = PassFieldRow()
            passFieldRow.set_label(label)
            passFieldRow.set_value(value)
            self.fields.append(passFieldRow)
