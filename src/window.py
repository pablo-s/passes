# window.py
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

from gi.repository import Gio, GObject, Gtk, Adw

from .barcode_dialog import BarcodeDialog
from .pkpass_row import PassRow
from .pkpass_view import PassView


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/window.ui')
class PassesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PassesWindow'

    main_header_bar = Gtk.Template.Child()
    main_leaflet = Gtk.Template.Child()
    right_pane_title = Gtk.Template.Child()

    back_button = Gtk.Template.Child()
    barcode_button = Gtk.Template.Child()

    pass_list = Gtk.Template.Child()
    pass_view = Gtk.Template.Child()

    pass_list_stack = Gtk.Template.Child()

    toast_overlay = Gtk.Template.Child()

    def __init__(self, pass_list_model, **kwargs):
        super().__init__(**kwargs)

        self.__selected_row = None

        # Bind GtkListBox with GioListStore
        self.pass_list.bind_model(pass_list_model, self._create_pass_widget)
        self.back_button.connect('clicked', self._on_back_clicked)
        self.barcode_button.connect('clicked', self._on_barcode_clicked)
        self.pass_list.connect('row-activated', self._on_row_activated)

        self.pass_list.set_header_func(self._on_update_header)

        self.select_pass_at_index(0)

    def _create_pass_widget(self, a_pass):
        return PassRow(a_pass)

    def _on_back_clicked(self, button):
        self.navigate_back()

    def _on_barcode_clicked(self, button):
        dialog = BarcodeDialog()
        dialog.set_modal(self)
        dialog.set_transient_for(self)

        selected_pass = self.selected_pass()
        barcode = selected_pass.barcode()

        if barcode:
            dialog.set_barcode(barcode)
            dialog.show()

    def _on_row_activated(self, pass_list, pass_row):
        if self.__selected_row == pass_row:
            self.main_leaflet.navigate(Adw.NavigationDirection.FORWARD)
            return

        self.__selected_row = pass_row

        row_data = pass_row.data()
        self.pass_view.content(row_data)
        self.main_leaflet.navigate(Adw.NavigationDirection.FORWARD)
        self.right_pane_title.set_title(row_data.description())


    def _on_update_header(self, row, row_above):
        if not row_above or row.style() != row_above.style():
            row.show_header()
        else:
            row.hide_header()

    def force_fold(self, force):
        self.main_leaflet.set_can_unfold(not force)

    def hide_pass_list(self):
        self.pass_list_stack.set_visible_child_name('empty-list-page')

    def is_folded(self):
        return self.main_leaflet.get_folded()

    def navigate_back(self):
        self.main_leaflet.navigate(Adw.NavigationDirection.BACK)

    def select_pass_at_index(self, index):
        selected_row = self.pass_list.get_row_at_index(index)

        if not selected_row:
            selected_row = self.pass_list.get_row_at_index(0)

        if selected_row:
            self.pass_list.select_row(selected_row)
            self.pass_list.emit('row-activated', selected_row)

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

    def show_pass_list(self):
        self.pass_list_stack.set_visible_child_name('pass-list-page')

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)

class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = 'Passes'
        self.props.version = "0.1.0"
        self.props.authors = ['Pablo Sánchez Rodríguez']
        self.props.copyright = '(C) 2021 Pablo Sánchez Rodríguez'
        self.props.logo_icon_name = 'me.sanchezrodriguez.passes'
        self.set_transient_for(parent)
