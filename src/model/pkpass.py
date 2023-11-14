# pkpass.py
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

from gi.repository import Gdk, Gtk

from .digital_pass import Barcode, Color, Currency, Date, DigitalPass, Image, PassDataExtractor


class PKPass:
    """
    A representation of a PassKit pass
    """

    styles = ['boardingPass',
              'coupon',
              'eventTicket',
              'generic',
              'storeCard']

    __slots__ = ('__description', '__format_version', '__organization_name',
        '__pass_type_identifier', '__serial_number', '__team_identifier',
        '__expiration_date', '__voided', '__locations', '__maximum_distance',
        '__relevant_date', '__style', '__auxiliary_fields', '__back_fields',
        '__header_fields', '__primary_fields', '__secondary_fields',
        '__transit_type', '__barcode', '__barcodes', '__background',
        '__background_color', '__foreground_color', '__grouping_identifier',
        '__icon', '__label_color', '__logo', '__logo_text', '__strip',
        '__authentication_token', '__web_service_url')

    def __init__(self, pass_data, translation, images):
        data = PassDataExtractor(pass_data)

        self.__description = data.get('description')
        self.__format_version = data.get('formatVersion')
        self.__organization_name = data.get('organizationName')
        self.__pass_type_identifier = data.get('passTypeIdentifier')
        self.__serial_number = data.get('serialNumber')
        self.__team_identifier = data.get('teamIdentifier')

        self.__expiration_date = data.get('expirationDate', Date.from_iso_string)
        self.__voided = data.get('voided', bool)

        self.__locations = data.get('locations')
        self.__maximum_distance = data.get('maxDistance')
        self.__relevant_date = data.get('relevantDate', Date.from_iso_string)

        self.__style = None
        for style in PKPass.styles:
            if style in data.keys():
                self.__style = style
                break

        self.__auxiliary_fields = data.get(self.__style)\
            .get_list('auxiliaryFields', StandardField, translation)
        self.__back_fields = data.get(self.__style)\
            .get_list('backFields', StandardField, translation)
        self.__header_fields = data.get(self.__style)\
            .get_list('headerFields', StandardField, translation)
        self.__primary_fields = data.get(self.__style)\
            .get_list('primaryFields', StandardField, translation)
        self.__secondary_fields = data.get(self.__style)\
            .get_list('secondaryFields', StandardField, translation)
        self.__transit_type = data.get(self.__style).get('transitType')

        self.__barcode = data.get('barcode', Barcode)
        self.__barcodes = data.get_list('barcodes', Barcode)
        self.__background = Image(images['background']) \
            if 'background' in images else None
        self.__background_color = data.get('backgroundColor', Color.from_css)
        self.__foreground_color = data.get('foregroundColor', Color.from_css)
        self.__grouping_identifier = data.get('groupingIdentifier') \
            if self.style() in ['boardingPass', 'eventTicket'] else None
        self.__icon = Image(images['icon']) if 'icon' in images else None
        self.__label_color = data.get('labelColor', Color.from_css)
        self.__logo = Image(images['logo']) if 'logo' in images else None
        self.__logo_text = data.get('logoText')
        self.__strip = Image(images['strip']) if 'strip' in images else None

        self.__authentication_token = data.get('authenticationToken')
        self.__web_service_url = data.get('webServiceURL')


    # Standard

    # mandatory
    def description(self):
        return self.__description

    # mandatory
    def format_version(self):
        return self.__format_version

    # mandatory
    def organization_name(self):
        return self.__organization_name

    # mandatory
    def pass_type_identifier(self):
        return self.__pass_type_identifier

    # mandatory
    def serial_number(self):
        return self.__serial_number

    # mandatory
    def team_identifier(self):
        return self.__team_identifier


    # Expiration

    def expiration_date(self):
        return self.__expiration_date

    def voided(self):
        return self.__voided


    # Relevance

    def locations(self):
        return self.__locations

    def maximum_distance(self):
        return self.__maximum_distance

    def relevant_date(self):
        return self.__relevant_date


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
        return self.__transit_type


    # Visual appearance

    def barcode(self):
        return self.__barcode

    def barcodes(self):
        return self.__barcodes

    def background(self):
        return self.__background

    def background_color(self):
        return self.__background_color

    def foreground_color(self):
        return self.__foreground_color

    def grouping_identifier(self):
        return self.__grouping_identifier

    def icon(self):
        return self.__icon

    def label_color(self):
        return self.__label_color

    def logo(self):
        return self.__logo

    def logo_text(self):
        return self.__logo_text

    def strip(self):
        return self.__strip

    # Web Service

    def authentication_token(self):
        return self.__authentication_token

    def web_service_url(self):
        return self.__web_service_url


class PKPassAdapter(DigitalPass):
    def __init__(self, pkpass):
        super().__init__()
        self.__adaptee = pkpass

    def adaptee(self):
        return self.__adaptee

    def additional_information(self):
        return self.__adaptee.back_fields()

    def background_color(self):
        return self.__adaptee.background_color()

    def barcodes(self):
        barcodes = self.__adaptee.barcodes()

        if not barcodes:
            barcodes = [self.__adaptee.barcode()]

        return barcodes

    def creator(self):
        return self.__adaptee.organization_name()

    def description(self):
        pass_style = self.__adaptee.style()
        fields = self.__adaptee.primary_fields()

        if pass_style == 'boardingPass' and len(fields) == 2:
            return '%s → %s' % (fields[0].label(), fields[1].label())

        return self.__adaptee.description()

    def expiration_date(self):
        return self.__adaptee.expiration_date()

    def file_extension():
        return '.pkpass'

    def format(self):
        return 'pkpass'

    def icon(self):
        return self.__adaptee.icon()

    def is_updatable(self):
        return self.__adaptee.web_service_url() and not self.has_expired()

    def mime_type():
        return 'application/vnd.apple.pkpass'

    def relevant_date(self):
        return self.__adaptee.relevant_date()

    def unique_identifier(self):
        return '.'.join([self.__adaptee.pass_type_identifier(),
                         self.__adaptee.serial_number(),
                         self.format()])

    def voided(self):
        return self.__adaptee.voided()


class StandardField:
    """
    A PKPass Standard Field
    """

    def __init__(self, pkpass_field_dictionary, translation_dictionary = None):
        self.__key = pkpass_field_dictionary['key']

        try:
            # Pass field values contain information, provided as a string, that
            # may have to be parsed and formatted. This is the case of numbers,
            # currencies and dates.

            value = pkpass_field_dictionary['value']

            if 'dateStyle' in pkpass_field_dictionary:
                value = Date.from_iso_string(value)

            elif 'currencyCode' in pkpass_field_dictionary:
                value = Currency.format(value, pkpass_field_dictionary['currencyCode'])

            elif translation_dictionary and value in translation_dictionary.keys():
                # The value is neither a date nor a currency
                value = translation_dictionary[value]

        except Exception:
            # If any error occur during the processing of the provided value,
            # this software will show the original text (as is). Because of
            # this, all exceptions produced in this block will be ignored.
            pass

        finally:
            self.__value = value.strip()

        if not self.__key or not self.__value:
            # Keys and values are required fields.
            raise Exception()

        self.__label = None
        if 'label' in pkpass_field_dictionary.keys():
            self.__label = pkpass_field_dictionary['label']
            if translation_dictionary and self.__label in translation_dictionary.keys():
                self.__label = translation_dictionary[self.__label]
            self.__label = self.__label.upper()

        self.__text_alignment = None
        if 'textAlignment' in pkpass_field_dictionary.keys():
            self.__text_alignment = pkpass_field_dictionary['textAlignment']

    def key(self):
        return self.__key

    def label(self):
        return self.__label

    def value(self):
        return self.__value

    def text_alignment(self):
        return self.__text_alignment
