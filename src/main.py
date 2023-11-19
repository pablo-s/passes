# main.py
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

import sys
import gi

gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import GLib, Gdk, Gio, Gtk, Adw

from .digital_pass import DigitalPass
from .digital_pass_factory import FileIsNotAPass, FormatNotSupportedYet, PassFactory
from .digital_pass_list_store import DigitalPassListStore
from .digital_pass_updater import PassUpdater
from .persistence import FileAlreadyImported, PersistenceManager
from .settings import Settings
from .window import PassesWindow


class Application(Adw.Application):

    # Application ID
    ID = 'me.sanchezrodriguez.passes'

    def __init__(self):
        super().__init__(application_id=Application.ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.__file_chooser = None
        self.__persistence = PersistenceManager()
        self.__settings = Settings(Application.ID)
        self.__pass_list = DigitalPassListStore(self.__settings)

        pass_files = self.__persistence.load_pass_files()
        for pass_file in pass_files:
            digital_pass = PassFactory.create(pass_file)
            self.__pass_list.insert(digital_pass)

    def do_activate(self):
        window = self.props.active_window

        if not window:
            window = PassesWindow(application=self,
                                  pass_list_model=self.__pass_list)

        self.create_action('about', self.on_about_action)
        self.create_action('delete', self.on_delete_action)
        self.create_action('import', self.on_import_action, ['<Control>o'])
        self.create_action('quit', self.on_quit_action, ['<Control>q'])
        self.create_action('update', self.on_update_action, ['<Control>u'])

        pass_list_is_empty = self.__pass_list.is_empty()
        window.force_fold(pass_list_is_empty)

        if not pass_list_is_empty:
            window.select_pass_at_index(0)

        window.present()

    def do_startup(self):
        Adw.Application.do_startup(self)

    def import_pass(self, pass_file):
        try:
            digital_pass = PassFactory.create(pass_file)

            if digital_pass in self.__pass_list:
                self.window().show_toast("Pass already imported")
                return

            stored_file = self.__persistence\
                .save_pass_file(pass_file, digital_pass.unique_identifier())

            digital_pass.set_path(stored_file.get_path())
            self.__pass_list.insert(digital_pass)

            if self.window():
                if not self.__pass_list.is_empty():
                    self.window().force_fold(False)

                found, index = self.__pass_list.find(digital_pass)
                if found:
                    self.window().select_pass_at_index(index)

        except Exception as exception:
            self.window().show_toast(str(exception))

    def on_about_action(self, widget, __):
        about = Adw.AboutWindow()
        about.set_application_icon('me.sanchezrodriguez.passes')
        about.set_application_name(_('Passes'))
        about.set_copyright('Copyright © 2022-2023 Pablo Sánchez Rodríguez')
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_developer_name('Pablo Sánchez Rodríguez')
        about.set_issue_url('https://github.com/pablo-s/passes/issues')
        about.set_version('0.9')
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
            self.window().force_fold(True)
            self.window().navigate_back()
            return

        index_to_select = min(self.__pass_list.length() - 1, selected_pass_index)
        self.window().select_pass_at_index(index_to_select)

    def on_import_action(self, widget, __):
        if not self.__file_chooser:
            self.__file_chooser = Gtk.FileDialog.new()

            supported_types_filter = Gtk.FileFilter()
            supported_types_filter.set_name(_('Supported passes'))
            for mime_type in DigitalPass.supported_mime_types():
                supported_types_filter.add_mime_type(mime_type)

            all_files_filter = Gtk.FileFilter()
            all_files_filter.set_name(_('All files'))
            all_files_filter.add_pattern('*')

            filter_list = Gio.ListStore.new(Gtk.FileFilter)
            filter_list.append(supported_types_filter)
            filter_list.append(all_files_filter)
            self.__file_chooser.set_filters(filter_list)

            self.__file_chooser.set_modal(True)

        self.__file_chooser.open(parent = self.window(),
                                 callback = self._on_file_chosen)

    def on_preferences_action(self, widget, _):
        print('app.preferences action activated')

    def on_quit_action(self, widget, _):
        self.window().close()

    def on_update_action(self, widget, __):
        """ Update currently selected pass """
        selected_pass = self.window().selected_pass()

        if not selected_pass:
            return

        try:
            # Download and save the latest version of the pass file
            latest_pass_data = PassUpdater.update(selected_pass)
            stored_file = self.__persistence\
                .save_pass_data(latest_pass_data,
                                selected_pass.unique_identifier() + '.tmp')

            # Create a new pass from the saved file
            digital_pass = PassFactory.create(stored_file)

            # Replace the old pass with the new one
            self.__pass_list.insert(digital_pass)
            selected_pass_index = self.window().selected_pass_index()
            self.__pass_list.remove(selected_pass_index)

            # Replace the old pass file with the new one
            self.__persistence.replace_pass_file(selected_pass,
                                                 replacement=digital_pass)

            # Select the new pass in the pass list
            found, updated_pass_index = self.__pass_list.find(digital_pass)
            self.window().select_pass_at_index(updated_pass_index)

            # Notify user
            self.window().show_toast(_('Pass updated'))

        except FileIsNotAPass:
            self.__persistence.delete_pass_file(stored_file)
            self.window().show_toast(_('Pass could not be updated'))

        except Exception as exception:
            self.window().show_toast(str(exception))

    def create_action(self, name, callback, shortcuts=None):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

        if shortcuts:
            self.set_accels_for_action(f'app.{name}',
                                       shortcuts)

    def _on_file_chosen(self, file_chooser, result):
        try:
            pass_file = file_chooser.open_finish(result)

            if not pass_file:
                return

            self.import_pass(pass_file)

        except Exception as exception:
            self.window().show_toast(exception.message)


    def window(self):
        return self.props.active_window

def main(version):
    app = Application()
    return app.run(sys.argv)
