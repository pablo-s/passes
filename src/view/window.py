# window.py
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

from gi.repository import Gio, GLib, GObject, Gtk, Adw

from .additional_information_pane import AdditionalInformationPane
from .barcode_dialog import BarcodeDialog
from .digital_pass_list_store import SortingCriteria
from .pass_list import PassList
from .pass_widget import PassWidget


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/window.ui')
class PassesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PassesWindow'

    main_split_view = Gtk.Template.Child()
    inner_split_view = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

    # Left panel
    pass_list = Gtk.Template.Child()

    # Main panel
    update_button = Gtk.Template.Child()
    info_button = Gtk.Template.Child()
    pass_widget = Gtk.Template.Child()

    # Right panel
    back_button  = Gtk.Template.Child()
    pass_additional_info  = Gtk.Template.Child()

    def __init__(self, pass_list_model, **kwargs):
        super().__init__(**kwargs)

        # Set help overlay
        help_overlay = Gtk.Builder\
            .new_from_resource('/me/sanchezrodriguez/passes/help_overlay.ui')\
            .get_object('help_overlay')

        self.set_help_overlay(help_overlay)

        self.get_application()\
            .set_accels_for_action('win.show-help-overlay',
                                   ['<Control>question'])

        # Bind pass list and model
        self.pass_list.bind_model(pass_list_model)

        # Create action for pass sorting menu
        action = Gio.SimpleAction\
            .new_stateful("sort",
                          GLib.VariantType.new('s'),
                          GLib.Variant.new_string(pass_list_model.sorting_criteria()))

        action.connect("activate", self._on_sort_action)
        self.add_action(action)

        # Connect callbacks
        self.back_button.connect('clicked', self._on_back_button_clicked)
        self.pass_list.connect('pass-activated', self._on_pass_activated)
        self.pass_list.connect('pass-selected', self._on_pass_selected)
        self.pass_widget.connect('barcode-clicked', self._on_barcode_clicked)
        self.info_button.connect('clicked', self._on_info_button_clicked)

    def _on_back_button_clicked(self, button):
        self.inner_split_view.set_show_sidebar(False);

    def _on_barcode_clicked(self, button):
        try:
            selected_pass = self.selected_pass()
            barcode = selected_pass.barcodes()[0]

            if barcode:
                dialog = BarcodeDialog()
                dialog.set_modal(True)
                dialog.set_transient_for(self)
                dialog.set_barcode(barcode)
                dialog.show()

        except Exception as error:
            self.show_toast(str(error))

    def _on_info_button_clicked(self, button):
        self.inner_split_view.set_show_sidebar(True);

    def _on_pass_activated(self, pass_list, digital_pass):
        self.update_button.set_sensitive(digital_pass.is_updatable())

        self.pass_widget.content(digital_pass)
        self.pass_additional_info.content(digital_pass)

        if self.inner_split_view.get_collapsed():
            self.inner_split_view.set_show_sidebar(False);

        self.main_split_view.set_show_content(True)

    def _on_pass_selected(self, pass_list, digital_pass):
        self.update_button.set_sensitive(digital_pass.is_updatable())

        self.pass_widget.content(digital_pass)
        self.pass_additional_info.content(digital_pass)

        if self.inner_split_view.get_collapsed():
            self.inner_split_view.set_show_sidebar(False);

    def _on_sort_action(self, action, target: GLib.Variant):
        sorting_criteria = SortingCriteria.from_string(target.get_string())
        self.pass_list.sort_by(sorting_criteria)
        action.set_state(target)

    def force_fold(self, force):
        self.main_split_view.set_collapsed(force)

    def is_folded(self):
        return self.main_split_view.get_collapsed()

    def navigate_back(self):
        self.main_split_view.set_show_content(False)

    def select_pass_at_index(self, index):
        self.pass_list.select_pass_at_index(index)

    def selected_pass(self):
        return self.pass_list.selected_pass()

    def selected_pass_index(self):
        return self.pass_list.selected_pass_index()

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)
