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
from .pass_list import PassList
from .pass_viewer import PassViewer


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/window.ui')
class PassesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PassesWindow'

    main_leaflet = Gtk.Template.Child()

    back_button = Gtk.Template.Child()
    barcode_button = Gtk.Template.Child()

    pass_list = Gtk.Template.Child()
    pass_viewer = Gtk.Template.Child()

    pass_list_stack = Gtk.Template.Child()

    toast_overlay = Gtk.Template.Child()

    def __init__(self, pass_list_model, **kwargs):
        super().__init__(**kwargs)

        # Whether or not the leaflet is allowed to navigate
        self.main_leaflet_can_navigate = False

        # Set help overlay
        help_overlay = Gtk.Builder\
            .new_from_resource('/me/sanchezrodriguez/passes/help_overlay.ui')\
            .get_object('help_overlay')

        self.set_help_overlay(help_overlay)

        # Bind GtkListBox with GioListStore
        self.pass_list.bind_model(pass_list_model)

        # Connect callbacks
        self.back_button.connect('clicked', self._on_back_clicked)
        self.barcode_button.connect('clicked', self._on_barcode_clicked)
        self.pass_list.connect('row-activated', self._on_row_activated)

        # Select the first pass in the list
        self.pass_list.select_pass_at_index(0)
        self.main_leaflet_can_navigate = True

    def _on_back_clicked(self, button):
        self.navigate_back()

    def _on_barcode_clicked(self, button):
        try:
            selected_pass = self.selected_pass()
            barcode = selected_pass.barcode()

            if not barcode:
                barcodes = selected_pass.barcodes()
                if len(barcodes) > 0:
                    barcode = barcodes[0]

            if barcode:
                dialog = BarcodeDialog()
                dialog.set_modal(True)
                dialog.set_transient_for(self)
                dialog.set_barcode(barcode)
                dialog.show()

        except Exception as error:
            self.show_toast(str(error))

    def _on_row_activated(self, pass_list, pass_row):
        row_data = pass_row.data()
        self.pass_viewer.content(row_data)

        if self.main_leaflet_can_navigate:
            self.main_leaflet.navigate(Adw.NavigationDirection.FORWARD)

    def force_fold(self, force):
        self.main_leaflet.set_can_unfold(not force)

    def hide_pass_list(self):
        self.pass_list_stack.set_visible_child_name('empty-list-page')

    def is_folded(self):
        return self.main_leaflet.get_folded()

    def navigate_back(self):
        self.main_leaflet.navigate(Adw.NavigationDirection.BACK)

    def select_pass_at_index(self, index):
        self.pass_list.select_pass_at_index(index)

    def selected_pass(self):
        return self.pass_list.selected_pass()

    def selected_pass_index(self):
        return self.pass_list.selected_pass_index()

    def show_pass_list(self):
        self.pass_list_stack.set_visible_child_name('pass-list-page')

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = _('Passes')
        self.props.version = "0.6"
        self.props.authors = ['Pablo Sánchez Rodríguez']
        self.props.copyright = '(C) 2022 Pablo Sánchez Rodríguez'
        self.props.logo_icon_name = 'me.sanchezrodriguez.passes'
        self.props.website = "https://github.com/pablo-s/passes"
        self.props.comments = _("A digital pass manager")
        self.set_transient_for(parent)
