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
from .digital_pass_list_store import SortingCriteria
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

        self.__list_model = None
        self.__selected_row = None
        self.__sorting_criteria = None
        self.set_header_func(self._on_update_headers)

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

    def _on_update_headers(self, row, row_above):
        row.update_header_text_for(self.__sorting_criteria)

        if row_above:
            row_above.update_header_text_for(self.__sorting_criteria)

        if not row_above or row.header_text() != row_above.header_text():
            row.show_header()
        else:
            row.hide_header()

    def bind_model(self, pass_list_model):
        self.__sorting_criteria = pass_list_model.sorting_criteria()
        self.__list_model = pass_list_model
        super().bind_model(pass_list_model.get_model(), PassRow)

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

    def sort_by_creator(self):
        self.__sorting_criteria = SortingCriteria.CREATOR
        self.__list_model.sort_by_creator()

    def sort_by_description(self):
        self.__sorting_criteria = SortingCritera.DESCRIPTION
        self.__list_model.sort_by_description()

    def sort_by_expiration_date(self):
        self.__sorting_criteria = SortingCriteria.EXPIRATION_DATE
        self.__list_model.sort_by_expiration_date()



    
