# digital_pass_factory.py
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

from gi.repository import Gdk, GObject, Gtk


def decode_string(string):
    encodings = ['utf-8', 'utf-16']
    decoded_string = ''

    for encoding in encodings:
        try:
            decoded_string = string.decode(encoding)
            break
        except UnicodeDecodeError:
            pass

    if not decoded_string:
        raise UnknownEncoding()

    return decoded_string


class PassFactory:
    """
    Create a digital pass
    """

    @classmethod
    def create(cls, pass_file):
        for factory in cls.__subclasses__():
            if factory.understands(pass_file):
                # Create and configure the digital pass
                digital_pass = factory.create(pass_file)
                path = pass_file.get_path()
                digital_pass.set_path(path)
                return digital_pass

        raise FileIsNotAPass()

    @classmethod
    def _create_translation_dict(cls, translation_file_content):
        content = decode_string(translation_file_content)
        entries = content.split(';')

        translation_dict = dict()

        for entry in entries:
            result = re.search('"(.*)" = "(.*)"', entry, re.DOTALL)

            if not result or len(result.groups()) != 2:
                continue

            translation_key = result.group(1)
            translation_value = result.group(2)
            translation_dict[translation_key] = translation_value

        return translation_dict


class FileIsNotAPass(Exception):
    def __init__(self):
        message = _('File is not a pass')
        super().__init__(message)


class FormatNotSupportedYet(Exception):
    def __init__(self):
        message = _('Format not supported yet')
        super().__init__(message)


class UnknownEncoding(Exception):
    def __init__(self):
        message = _('Unknown file encoding')
        super().__init__(message)
