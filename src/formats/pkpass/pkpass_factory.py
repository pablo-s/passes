# pkpass_pass_factory.py
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
from .pkpass import PKPass, PKPassAdapter


class PkPassFactory(PassFactory):
    """
    Create a PKPass
    """

    @classmethod
    def understands(cls, pass_file):
        """
        Whether or not this factory understands the pass file
        """
        try:
            path = pass_file.get_path()
            archive = zipfile.ZipFile(path, 'r')
            return 'pass.json' in archive.namelist()

        except zipfile.BadZipFile as exception:
            return False

    @classmethod
    def create(cls, pass_file):
        """
        Create a PKPass object from pass file
        """

        path = pass_file.get_path()
        archive = zipfile.ZipFile(path, 'r')
        manifest_text = archive.read('manifest.json')
        manifest = json.loads(manifest_text)

        pass_data = dict()
        pass_translations = dict()
        pass_images = dict()

        for file_name in sorted(manifest.keys()):
            if file_name.endswith('.png'):
                image = archive.read(file_name)

                # For every type of image (background, footer, icon, logo, strip
                # and thumbnail), only load the image with lowest resolution

                image_type = re.split(r'\.|@', file_name)[0]

                if image_type in pass_images.keys():
                    continue

                pass_images[image_type] = image

            if file_name.endswith('pass.strings'):
                language = file_name.split('.')[0]
                file_content = archive.read(file_name)
                translation_dict = cls._create_translation_dict(file_content)
                pass_translations[language] = translation_dict

            if file_name.endswith('pass.json'):
                json_content = archive.read(file_name)
                pass_data = json.loads(json_content)


        language_to_import = None
        if pass_translations:
            user_language = Gtk.get_default_language().to_string()

            for language in pass_translations:
                if language in user_language:
                    language_to_import = language
                    break

            if language_to_import is None:
                # TODO: Open a dialogue and ask the user what language to import
                pass

        pass_translation = None
        if language_to_import:
            pass_translation = pass_translations[language_to_import]

        pkpass = PKPass(pass_data, pass_translation, pass_images)
        return PKPassAdapter(pkpass)
