# digital_pass_factory.py
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

import json
import re
import zipfile

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk

from .pkpass import PKPass


class PassFactory:
    """
    Create a digital pass
    """

    @classmethod
    def create(this_class, pass_file):
        try:
            path = pass_file.get_path()
            archive = zipfile.ZipFile(path, 'r')

            digital_pass = this_class.create_pkpass(archive)

            return digital_pass

        except zipfile.BadZipFile as exception:
            raise FileIsNotAPass()

    @classmethod
    def create_pkpass(thisClass, archive):
        manifest_text = archive.read('manifest.json')
        manifest = json.loads(manifest_text)

        pass_data = dict()
        pass_translations = dict()
        pass_images = dict()

        for file_name in manifest.keys():
            if file_name.endswith('.png'):
                pixbuf = thisClass.create_pixbuf_from_filename(archive, file_name)
                pass_images[file_name] = pixbuf

            if file_name.endswith('pass.strings'):
                language = file_name.split('.')[0]
                file_content = archive.read(file_name)
                translation_dict = thisClass.create_translation_dict(file_content)
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

        return PKPass(pass_data, pass_translation, pass_images)

    @classmethod
    def create_pixbuf_from_filename(thisClass, archive, file_name):
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        image_data = archive.read(file_name)
        loader.write(image_data)
        loader.close()
        return loader.get_pixbuf()

    @classmethod
    def create_translation_dict(thisClass, translation_file_content):
        content = translation_file_content.decode()
        entries = content.split('\n')

        translation_dict = dict()

        for entry in entries:
            result = re.search('"(.*)" = "(.*)"', entry)

            if not result or len(result.groups()) != 2:
                continue

            translation_key = result.group(1)
            translation_value = result.group(2)
            translation_dict[translation_key] = translation_value

        return translation_dict


class FileIsNotAPass(Exception):
    pass
