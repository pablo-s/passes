# espass_factory.py
#
# Copyright 2022-2024 Pablo Sánchez Rodríguez
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

import json
import re
import zipfile

from gi.repository import Gdk, GObject, Gtk

from passes.digital_pass_factory import PassFactory
from .espass import EsPass, EsPassAdapter


class EsPassFactory(PassFactory):
    """
    Create a EsPass
    """

    @classmethod
    def understands(cls, pass_file):
        """
        Whether or not this factory understands the pass file
        """

        try:
            path = pass_file.get_path()
            archive = zipfile.ZipFile(path, 'r')
            return 'main.json' in archive.namelist()

        except zipfile.BadZipFile as exception:
            return False

    @classmethod
    def create(cls, pass_file):
        """
        Create a EsPass object from pass file
        """
        pass_data = dict()
        pass_images = dict()

        path = pass_file.get_path()
        archive = zipfile.ZipFile(path, 'r')

        for file_name in archive.namelist():
            if file_name.endswith('.png'):
                image = archive.read(file_name)
                pass_images[file_name] = image

            if file_name.endswith('main.json'):
                json_content = archive.read(file_name)
                pass_data = json.loads(json_content)

        espass = EsPass(pass_data, pass_images)
        return EsPassAdapter(espass)

