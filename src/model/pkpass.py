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

from gi.repository import Gdk, Gtk

from .digital_pass import Barcode, Color, DigitalPass, Image, PassDataExtractor


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

        self.__data = PassDataExtractor(pass_data)
        self.__translation = pass_translation
        self.__images = pass_images

        self.__style = None
        for style in PKPass.styles:
            if style in self.__data.keys():
                self.__style = style
                break

        self.__auxiliary_fields = self.__data\
            .get(self.__style)\
            .get_list('auxiliaryFields', StandardField, self.__translation)

        self.__back_fields = self.__data\
            .get(self.__style)\
            .get_list('backFields', StandardField, self.__translation)

        self.__header_fields = self.__data\
            .get(self.__style)\
            .get_list('headerFields', StandardField, self.__translation)

        self.__primary_fields = self.__data\
            .get(self.__style)\
            .get_list('primaryFields', StandardField, self.__translation)

        self.__secondary_fields = self.__data\
            .get(self.__style)\
            .get_list('secondaryFields', StandardField, self.__translation)


    # Standard

    # mandatory
    def description(self):
        return self.__data.get('description')

    # mandatory
    def format_version(self):
        return self.__data.get('formatVersion')

    # mandatory
    def organization_name(self):
        return self.__data.get('organizationName')

    # mandatory
    def pass_type_identifier(self):
        return self.__data.get('passTypeIdentifier')

    # mandatory
    def serial_number(self):
        return self.__data.get('serialNumber')

    # mandatory
    def team_identifier(self):
        return self.__data.get('teamIdentifier')


    # Expiration

    def expiration_date(self):
        return self.__data.get('expirationDate')

    def voided(self):
        return self.__data.get('voided', bool)


    # Relevance

    def locations(self):
        return self.__data.get('locations')

    def maximum_distance(self):
        return self.__data.get('maxDistance')

    def relevant_date(self):
        return self.__data.get('relevantDate')


    # Style

    def style(self):
        return self.__style


    # Fields

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
        return self.__data.get(self.__style).get('transitType')


    # Visual appearance

    def barcode(self):
        return self.__data.get('barcode', Barcode)

    def barcodes(self):
        return self.__data.get_list('barcodes', Barcode)

    def background_color(self):
        return self.__data.get('backgroundColor', Color.from_css)

    def foreground_color(self):
        return self.__data.get('foregroundColor', Color.from_css)

    def grouping_identifier(self):
        if self.style() in ['boardingPass', 'eventTicket']:
            return self.__data.get('groupingIdentifier')
        else:
            return None

    def icon(self):
        return Image(self.__images['icon.png'])

    def label_color(self):
        return self.__data.get('labelColor', Color.from_css).as_tuple()

    def logo(self):
        return Image(self.__images['logo.png'])

    def logo_text(self):
        return self.__data.get('logoText')


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
