# pkpass.py
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

from gi.repository import Gdk, GdkPixbuf, GObject


class Pass(GObject.GObject):
    """
    A representation of a digital pass
    """

    __gtype_name__ = 'GPass'

    styles = ['boardingPass',
              'coupon',
              'eventTicket',
              'generic',
              'storeCard']

    def __init__(self, pass_data, pass_translations, pass_images):
        super().__init__()

        self.__data = pass_data
        self.__translations = pass_translations
        self.__images = pass_images

        self.__style = None
        for style in Pass.styles:
            if style in self.__data.keys():
                self.__style = style
                break


    # Auxiliary methods

    def _get_mandatory_data(self, data_key):
        return self.__data[data_key]

    def _get_optional_data(self, data_key):
        if data_key in self.__data.keys():
            return self.__data[data_key]
        else:
            return None

    def _get_style_specific_mandatory_data(self, data_key):
        data = self._get_mandatory_data(self.style())

        if data_key in data.keys():
            return data[data_key]
        else:
            return None

    def _get_style_specific_optional_data(self, data_key):
        data = self._get_mandatory_data(self.style())
        return data[data_key]


    # Standard

    def description(self):
        return self._get_mandatory_data('description')

    def format_version(self):
        return self._get_mandatory_data('formatVersion')

    def organization_name(self):
        return self._get_mandatory_data('organizationName')

    def pass_type_identifier(self):
        return self._get_mandatory_data('passTypeIdentifier')

    def serial_number(self):
        return self._get_mandatory_data('serialNumber')

    def team_identifier(self):
        return self._get_mandatory_data('teamIdentifier')


    # Expiration

    def expiration_date(self):
        return self._get_optional_data('expirationDate')

    def voided(self):
        return self._get_optional_data('voided')


    # Relevance

    def locations(self):
        return self._get_optional_data('locations')

    def maximum_distance(self):
        return self._get_optional_data('maxDistance')

    def relevant_date(self):
        return self._get_optional_data('relevantDate')


    # Style

    def style(self):
        return self.__style


    # Fields

    def auxiliary_fields(self):
        return self._get_style_specific_optional_data('auxiliaryFields')

    def back_fields(self):
        return self._get_style_specific_optional_data('backFields')

    def header_fields(self):
        return self._get_style_specific_optional_data('headerFields')

    def primary_fields(self):
        return self._get_style_specific_optional_data('primaryFields')

    def secondary_fields(self):
        return self._get_style_specific_optional_data('secondaryFields')

    def transit_type(self):
        if self.style() == 'boardingPass':
            return self._get_style_specific_mandatory_data('transitType')
        else:
            return None

    # Visual appearance

    def barcode(self):
        barcode_data = self._get_optional_data('barcode')
        barcode = None

        if barcode_data:
            barcode = Barcode(barcode_data)

        return barcode

    def barcodes(self):
        return self._get_optional_data('barcodes')

    def background_color(self):
        color_as_text = self._get_optional_data('backgroundColor')

        if not color_as_text:
            return None

        result = re.search('rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
                           color_as_text)

        if not result or len(result.groups()) != 3:
            return None

        return (result.group(1),
                result.group(2),
                result.group(3))

    def foreground_color(self):
        color_as_text = self._get_optional_data('foregroundColor')

        if not color_as_text:
            return None

        result = re.search('rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
                           color_as_text)

        if not result or len(result.groups()) != 3:
            return None

        return (result.group(1),
                result.group(2),
                result.group(3))

    def grouping_identifier(self):
        if self.style() in ['boardingPass', 'eventTicket']:
            return self._get_optional_data('groupingIdentifier')
        else:
            return None

    def icon(self):
        return self.__images['icon.png']

    def label_color(self):
        return self._get_optional_data('labelColor')

    def logo(self):
        return self.__images['logo.png']

    def logo_text(self):
        return self._get_optional_data('logoText')


class PassFactory:
    """
    Create a digital pass
    """

    @classmethod
    def create(thisClass, pkpass_file):
        path = pkpass_file.get_path()
        archive = zipfile.ZipFile(path, 'r')

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

        return Pass(pass_data, pass_translations, pass_images)

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
