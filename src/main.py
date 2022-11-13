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

from .digital_pass_factory import FileIsNotAPass, FormatNotSupportedYet, PassFactory
from .digital_pass_list_store import DigitalPassListStore
from .persistence import FileAlreadyImported, PersistenceManager
from .window import PassesWindow


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id='me.sanchezrodriguez.passes',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.__file_chooser = None
        self.__pass_list = DigitalPassListStore()
        self.__persistence = PersistenceManager()

        pass_files = self.__persistence.load_pass_files()
        for pass_file in pass_files:
            digital_pass = PassFactory.create(pass_file)
            digital_pass.set_path(pass_file.get_path())
            self.__pass_list.insert(digital_pass)

    def do_activate(self):
        window = self.props.active_window

        if not window:
            window = PassesWindow(application=self,
                                  pass_list_model=self.__pass_list.get_model())

        self.create_action('about', self.on_about_action)
        self.create_action('delete', self.on_delete_action)
        self.create_action('import', self.on_import_action)
        self.create_action('quit', self.on_quit_action, ['<Control>q'])

        pass_list_is_empty = self.__pass_list.is_empty()
        window.force_fold(pass_list_is_empty)

        if not pass_list_is_empty:
            window.show_pass_list()

        window.present()

    def do_startup(self):
        Adw.Application.do_startup(self)

    def on_about_action(self, widget, __):
        about = Adw.AboutWindow()
        about.set_application_icon('me.sanchezrodriguez.passes')
        about.set_application_name(_('Passes'))
        about.set_copyright('Copyright © 2022 Pablo Sánchez Rodríguez')
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_developer_name('Pablo Sánchez Rodríguez')
        about.set_issue_url('https://github.com/pablo-s/passes/issues')
        about.set_version('0.7')
        about.set_website('https://github.com/pablo-s/passes')
        about.set_transient_for(self.window())
        about.show()

    def on_delete_action(self, widget, _):
        if not self.window():
            return

        selected_pass = self.window().selected_pass()
        selected_pass_index = self.window().selected_pass_index()

        self.__persistence.delete_pass_file(selected_pass)
        self.__pass_list.remove(selected_pass_index)

        if self.__pass_list.is_empty():
            self.window().hide_pass_list()
            self.window().force_fold(True)
            self.window().navigate_back()
            return

        index_to_select = min(self.__pass_list.length() - 1, selected_pass_index)
        self.window().select_pass_at_index(index_to_select)

    def on_import_action(self, widget, __):
        if not self.__file_chooser:
            self.__file_chooser = Gtk.FileChooserNative.new(
                _('Import a pass'),
                self.window(),
                Gtk.FileChooserAction.OPEN,
                None,
                None)

            self.__file_chooser.connect('response', self._on_file_chosen)

        self.__file_chooser.show()

    def on_preferences_action(self, widget, _):
        print('app.preferences action activated')

    def on_quit_action(self, widget, _):
        self.window().close()

    def create_action(self, name, callback, shortcuts=None):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

        if shortcuts:
            self.set_accels_for_action(f'app.{name}',
                                       shortcuts)

    def _on_file_chosen(self, filechooser, response):
        if response != Gtk.ResponseType.ACCEPT:
            return

        try:
            pass_file = filechooser.get_file()
            digital_pass = PassFactory.create(pass_file)

            stored_file = self.__persistence\
                .save_pass_file(pass_file, digital_pass.format())

            digital_pass.set_path(stored_file.get_path())
            self.__pass_list.insert(digital_pass)

            if not self.__pass_list.is_empty():
                self.window().show_pass_list()
                self.window().force_fold(False)

            found, index = self.__pass_list.find(digital_pass)
            if found:
                self.window().select_pass_at_index(index)

        except Exception as exception:
            self.window().show_toast(str(exception))

    def window(self):
        return self.props.active_window

def main(version):
    app = Application()
    return app.run(sys.argv)
