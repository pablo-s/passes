# main.py
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

import sys
import gi

gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import GLib, Gdk, Gio, Gtk, Adw

from .persistence import PersistenceManager
from .pkpass import DigitalPass, PassFactory
from .window import PassesWindow, AboutDialog


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id='me.sanchezrodriguez.passes',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.__pass_list = Gio.ListStore.new(DigitalPass)
        self.__persistence = PersistenceManager()

        passes = self.__persistence.load_passes()
        for each_pass in passes:
            pkpass = PassFactory.create(each_pass)
            pkpass.set_path(each_pass.get_path())

            self.__pass_list.insert_sorted(pkpass,
                                    lambda a1, a2: a1.style() > a2.style())

    def do_activate(self):
        window = self.props.active_window

        if not window:
            window = PassesWindow(application=self,
                                  pass_list_model=self.__pass_list)

        self.create_action('about', self.on_about_action)
        self.create_action('delete', self.on_delete_action)
        self.create_action('import', self.on_import_action)
        self.create_action('preferences', self.on_preferences_action)

        pass_list_is_emtpy = len(self.__pass_list) == 0
        window.force_fold(pass_list_is_emtpy)

        if not pass_list_is_emtpy:
            window.show_pass_list()

        window.present()

    def do_startup(self):
        Adw.Application.do_startup(self)

    def on_about_action(self, widget, _):
        about = AboutDialog(self.window())
        about.present()

    def on_delete_action(self, widget, _):
        if not self.window():
            return

        selected_pass = self.window().selected_pass()
        selected_pass_index = self.window().selected_pass_index()

        self.__persistence.delete_pass_file(selected_pass)
        self.__pass_list.remove(selected_pass_index)

        pass_list_is_emtpy = len(self.__pass_list) == 0

        if pass_list_is_emtpy:
            self.window().hide_pass_list()
            self.window().force_fold(True)
            self.window().navigate_back()
            return

        index_to_select = min(len(self.__pass_list) - 1, selected_pass_index)
        self.window().select_pass_at_index(index_to_select)

    def on_import_action(self, widget, _):
        print('app.import action activated')
        self.filechooser = Gtk.FileChooserNative.new(
            'Open PK',
            self.window(),
            Gtk.FileChooserAction.OPEN,
            None,
            None)

        response = self.filechooser.show()
        self.filechooser.connect('response', self._on_file_chosen)

    def on_preferences_action(self, widget, _):
        print('app.preferences action activated')

    def create_action(self, name, callback):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def _on_file_chosen(self, filechooser, response):
        if response != Gtk.ResponseType.ACCEPT:
            print('Error')
            return

        pkpass_file = filechooser.get_file()
        pkpass = PassFactory.create(pkpass_file)

        stored_file = self.__persistence.save_pass_file(pkpass_file)
        pkpass.set_path(stored_file.get_path())

        self.__pass_list.insert_sorted(pkpass,
                                       lambda a1, a2: a1.style() > a2.style())

        pass_list_is_not_emtpy = len(self.__pass_list) > 0

        if pass_list_is_not_emtpy:
            self.window().show_pass_list()
            self.window().force_fold(False)

        found, index = self.__pass_list.find(pkpass)
        if found:
            self.window().select_pass_at_index(index)

    def window(self):
        return self.props.active_window

def main(version):
    app = Application()
    return app.run(sys.argv)
