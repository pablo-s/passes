# persistence.py
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

import os, tempfile

from gi.repository import Gio, GLib
from .digital_pass import DigitalPass


class PersistenceManager:
    """
    """

    def __init__(self):
        self.__data_dir = GLib.get_user_data_dir()
        self.__supported_file_extensions = DigitalPass.supported_file_extensions()

    def load_pass_files(self):
        file_names = os.listdir(self.__data_dir)
        pass_files = list()

        for file_name in file_names:
            basename, extension = os.path.splitext(file_name)

            if extension not in self.__supported_file_extensions:
                continue

            pass_file_path = os.path.join(self.__data_dir, file_name)
            pass_file = Gio.File.new_for_path(pass_file_path)
            pass_files.append(pass_file)

        return pass_files

    def delete_pass_file(self, a_pass):
        target_path = a_pass.get_path()
        target_file = Gio.File.new_for_path(target_path)
        target_file.delete()

    def save_pass_data(self, pass_data, file_name):
        with tempfile.NamedTemporaryFile() as temp_pass_file:
            temp_pass_file.write(pass_data)

            pass_file_path = os.path.join(tempfile.gettempdir(), str(temp_pass_file.name))
            pass_file = Gio.File.new_for_path(pass_file_path)
            return self.save_pass_file(pass_file, file_name)

    def save_pass_file(self, pass_file, file_name):
        destination_file_path = os.path.join(self.__data_dir, file_name)
        destination_file = Gio.File.new_for_path(destination_file_path)

        if Gio.File.query_exists(destination_file):
            raise FileAlreadyImported()

        pass_file.copy(destination=destination_file,
                       flags=Gio.FileCopyFlags.NONE,
                       cancellable=None,
                       progress_callback=None,
                       progress_callback_data=None)

        return destination_file


class FileAlreadyImported(Exception):
    def __init__(self):
        message = _('File already imported')
        super().__init__(message)
