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
from .const import Config
from .window import PassesWindow


class Application(Adw.Application):

    troubleshooting = "OS: {os}\nApplication version: {wv}\nGTK: {gtk}\nlibadwaita: {adw}\nApp ID: {app_id}\nProfile: {profile}\nLanguage: {lang}"

    def __init__(self):
        super().__init__(application_id=Config.APPID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.__file_chooser = None
        self.__persistence = PersistenceManager()
        self.__settings = Settings(Config.APPID)
        self.__pass_list = DigitalPassListStore(self.__settings)

        pass_files = self.__persistence.load_pass_files()
        for pass_file in pass_files:
            digital_pass = PassFactory.create(pass_file)
            self.__pass_list.insert(digital_pass)

        gtk_version = str(Gtk.MAJOR_VERSION) + "." + str(Gtk.MINOR_VERSION) + "." + str(Gtk.MICRO_VERSION)
        adw_version = str(Adw.MAJOR_VERSION) + "." + str(Adw.MINOR_VERSION) + "." + str(Adw.MICRO_VERSION)
        os_string = GLib.get_os_info("NAME") + " " + GLib.get_os_info("VERSION")
        lang = GLib.environ_getenv(GLib.get_environ(), "LANG")

        self.troubleshooting = self.troubleshooting.format( os = os_string, wv = Config.VERSION, gtk = gtk_version, adw = adw_version, profile = Config.PROFILE, app_id = Config.APPID, lang = lang )

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
        about = Adw.AboutWindow(
            application_icon = Config.APPID,
            application_name = _('Passes'),
            copyright = 'Copyright © 2022-2023 Pablo Sánchez Rodríguez',
            license_type = Gtk.License.GPL_3_0,
            developer_name = 'Pablo Sánchez Rodríguez',
            issue_url = 'https://github.com/pablo-s/passes/issues',
            version = Config.VERSION,
            developers = [ 'Pablo Sánchez Rodríguez' ],
            # Translators: do one of the following, one per line: Your Name, Your Name <email@email.org>, Your Name https://websi.te
            translator_credits = _("translator-credits"),
            website = 'https://github.com/pablo-s/passes',
            debug_info=self.troubleshooting,
            transient_for = self.window()
        )

        about.add_credit_section(_("Contributors"), [
            # Contributors: do one of the following, one per line: Your Name, Your Name <email@email.org>, Your Name https://websi.te
            "Hari Rana (TheEvilSkeleton) https://tesk.page",
            "skøldis <passes@turtle.garden>"
        ])

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
