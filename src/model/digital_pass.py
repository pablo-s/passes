# digital_pass.py
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

import re

from gi.repository import GdkPixbuf, GObject


class DigitalPass(GObject.GObject):

    __gtype_name__ = 'DigitalPass'

    def __init__(self):
        super().__init__()
        self.__path = None

    def get_path(self):
        return self.__path

    def set_path(self, new_path: str):
        self.__path = new_path


class Barcode:

    def __init__(self, pkpass_barcode_dictionary):
        self.__format = pkpass_barcode_dictionary['format']
        self.__message = pkpass_barcode_dictionary['message']
        self.__message_encoding = pkpass_barcode_dictionary['messageEncoding']

        self.__alt_text = None
        if 'altText' in pkpass_barcode_dictionary.keys():
            self.__alt_text = pkpass_barcode_dictionary['altText']

    def alternative_text(self):
        return self.__alt_text

    def format(self):
        return self.__format

    def message(self):
        return self.__message

    def message_encoding(self):
        return self.__message_encoding


class Color:

    def __init__(self, r, g, b):
        self.__r = r
        self.__g = g
        self.__b = b

    def as_tuple(self):
        return (self.__r, self.__g, self.__b)

    @classmethod
    def from_css(this_class, css_string):
        result = re.search('rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
                           css_string)

        if not result or len(result.groups()) != 3:
            raise BadColor()

        return Color(result.group(1),
                     result.group(2),
                     result.group(3))


class Image:

    def __init__(self, image_data):
        self.__data = image_data

    def as_pixbuf(self):
        loader = GdkPixbuf.PixbufLoader()
        loader.write(self.__data)
        loader.close()
        return loader.get_pixbuf()


class PassDataExtractor:
    """
    A PassDataExtractor contains a reference to a dictionary and a set of helper
    functions to easy the process of creating a pass.
    """

    def __init__(self, dictionary):
        self._dictionary = dictionary

    def _cast_to_boolean(self, value):
        """
        Protected method that creates a boolean from a string.
        """
        return True if value.lower().startswith('true') else False

    def get(self, key, type_constructor=None):
        """
        Return an element from the dictionary using the provided key.

        If a constructor is specified, it will be used to create the instance
        that will be returned.
        """
        try:
            value = self._dictionary[key]

            if not type_constructor and type(value) == dict:
                return PassDataExtractor(value)

            if type_constructor:
                if type(type_constructor) == bool:
                    value = self._cast_to_boolean(value)

                else:
                    value = type_constructor(value)

            return value

        except:
            return None

    def get_list(self, key, item_constructor, extra_arguments=None):
        """
        Return a list of elements from the dictionary using the provided key.

        If a constructor is specified, it will be used to create each of the
        items that will be appended to the list.
        """

        data_list = self.get(key)

        if not data_list:
            return None

        if not extra_arguments:
            extra_arguments = ()

        elif type(extra_arguments) != tuple:
            extra_arguments = (extra_arguments,)

        result = list()
        for item_data in data_list:
            arguments = (item_data,) + extra_arguments
            instance = item_constructor(*arguments)
            result.append(instance)

        return result

    def keys(self):
        """
        Return the set of keys
        """
        return self._dictionary.keys()


class BadColor(Exception):
    pass
