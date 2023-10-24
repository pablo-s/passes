# pass_list.py
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

from gi.repository import Adw, GObject, Gtk

from .digital_pass import DigitalPass
from .pass_row import PassRow


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_list.ui')
class PassList(Gtk.ListBox):

    __gtype_name__ = 'PassList'

    __gsignals__ = {
        'pass-activated' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (DigitalPass,)),
        'pass-selected' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (DigitalPass,))
    }

    def __init__(self):
        super().__init__()

        self.__selected_row = None
        self.set_header_func(self.on_update_header)

        # Create a placeholder widget to be displayed when the list is empty
        placeholder = Adw.StatusPage.new()
        placeholder.set_icon_name('me.sanchezrodriguez.passes')
        placeholder.set_title(_('You have no passes'))
        placeholder.set_description(_('Use the “+” button to import a pass'))
        self.set_placeholder(placeholder)

        self.connect('row-activated', self._on_row_activated)

    def _on_row_activated(self, pass_list, pass_row):
        self.__selected_row = pass_row
        self.emit('pass-activated', pass_row.data())

    def bind_model(self, pass_list_model):
        super().bind_model(pass_list_model.get_model(), PassRow)

    def on_update_header(self, row, row_above):
        row_date = row.data().expiration_date()
        row_header = row_date.as_relative_pretty_string() if row_date else None

        row_above_date = row_above.data().expiration_date() if row_above else None
        row_above_header = row_above_date.as_relative_pretty_string()\
            if row_above and row_above_date else None

        if not row_above or row_header != row_above_header:
            row.show_header()
        else:
            row.hide_header()

    def row_at_index(self, index):
        row_at_index = self.get_row_at_index(index)

        if not row_at_index:
            row_at_index = self.get_row_at_index(0)

        return row_at_index if row_at_index else None

    def select_pass_at_index(self, index):
        row_at_index = self.row_at_index(index)

        if row_at_index:
            self.select_row(row_at_index)
            self.emit('pass-selected', row_at_index.data())

    def selected_pass(self):
        selected_pass = None

        if self.__selected_row:
            selected_pass = self.__selected_row.data()

        return selected_pass

    def selected_pass_index(self):
        index = None

        if self.__selected_row:
            index = self.__selected_row.get_index()

        return index



    
