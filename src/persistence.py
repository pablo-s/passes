# persistence.py
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

import os

from gi.repository import Gio, GLib

from .pkpass import PassFactory


class PersistenceManager:
    """
    """

    def __init__(self):
        self.__data_dir = GLib.get_user_data_dir()

    def load_passes(self):
        file_names = os.listdir(self.__data_dir)
        passes = list()

        for file_name in file_names:
            if not file_name.endswith('.pkpass'):
                continue

            pkpass_file_path = self.__data_dir + '/' + file_name
            pkpass_file = Gio.File.new_for_path(pkpass_file_path)
            passes.append(pkpass_file)

        return passes

    def delete_pass_file(self, a_pass):
        target_path = a_pass.get_path()
        target_file = Gio.File.new_for_path(target_path)
        target_file.delete()

    def save_pass_file(self, pass_file):
        print("Saving file...")

        destination_file_name = str(pass_file.hash()) + '.pkpass'
        destination_file_path = self.__data_dir + '/' + destination_file_name
        destination_file = Gio.File.new_for_path(destination_file_path)

        pass_file.copy(destination=destination_file,
                       flags=Gio.FileCopyFlags.NONE,
                       cancellable=None,
                       progress_callback=None,
                       progress_callback_data=None)

        return destination_file
