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

import re

from gi.repository import Gdk, GdkPixbuf, Gtk

from .digital_pass import DigitalPass


class PKPass(DigitalPass):
    """
    A representation of a PassKit pass
    """

    styles = ['boardingPass',
              'coupon',
              'eventTicket',
              'generic',
              'storeCard']

    def __init__(self, pass_data, pass_translation, pass_images):
        super().__init__()

        self.__data = pass_data
        self.__translation = pass_translation
        self.__images = pass_images

        self.__style = None
        for style in PKPass.styles:
            if style in self.__data.keys():
                self.__style = style
                break

        self._setup_fields()


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
        return data[data_key]

    def _get_style_specific_optional_data(self, data_key):
        data = self._get_mandatory_data(self.style())

        if data_key in data.keys():
            return data[data_key]
        else:
            return None


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

    def _create_field_group(self, field_group_name):
        field_data_list = \
            self._get_style_specific_optional_data(field_group_name)

        if not field_data_list:
            return None

        field_group = list()
        for field_data in field_data_list:
            field_group.append(StandardField(field_data, self.__translation))

        return field_group

    def _setup_fields(self):
        self.__auxiliary_fields = self._create_field_group('auxiliaryFields')
        self.__back_fields = self._create_field_group('backFields')
        self.__header_fields = self._create_field_group('headerFields')
        self.__primary_fields = self._create_field_group('primaryFields')
        self.__secondary_fields = self._create_field_group('secondaryFields')

    def auxiliary_fields(self):
        return self.__auxiliary_fields

    def back_fields(self):
        return self.__back_fields

    def header_fields(self):
        return self.__header_fields

    def primary_fields(self):
        return self.__primary_fields

    def secondary_fields(self):
        return self.__secondary_fields

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
        barcode_data_list = self._get_optional_data('barcodes')

        if not barcode_data_list:
            return None

        barcodes = list()

        for barcode_data in barcode_data_list:
            barcode = Barcode(barcode_data)
            barcodes.append(barcode)

        return barcodes

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


class StandardField:
    """
    A PKPass Standard Field
    """

    def __init__(self, pkpass_field_dictionary, translation_dictionary = None):
        self.__key = pkpass_field_dictionary['key']

        self.__value = pkpass_field_dictionary['value']
        if translation_dictionary and self.__value in translation_dictionary.keys():
            self.__value = translation_dictionary[self.__value]

        self.__label = None
        if 'label' in pkpass_field_dictionary.keys():
            self.__label = pkpass_field_dictionary['label']
            if translation_dictionary and self.__label in translation_dictionary.keys():
                self.__label = translation_dictionary[self.__label]

    def key(self):
        return self.__key

    def label(self):
        return self.__label

    def value(self):
        return self.__value
