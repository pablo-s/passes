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

    def __init__(self, pass_data, pass_translation, pass_images):
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
        return self.__data.get('expirationDate', Date.from_iso_string)

    def voided(self):
        return self.__data.get('voided', bool)


    # Relevance

    def locations(self):
        return self.__data.get('locations')

    def maximum_distance(self):
        return self.__data.get('maxDistance')

    def relevant_date(self):
        return self.__data.get('relevantDate', Date.from_iso_string)


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

    def background(self):
        return Image(self.__images['background']) \
            if 'background' in self.__images \
            else None

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
        return Image(self.__images['icon']) \
            if 'icon' in self.__images \
            else None

    def label_color(self):
        return self.__data.get('labelColor', Color.from_css)

    def logo(self):
        return Image(self.__images['logo']) \
            if 'logo' in self.__images \
            else None

    def logo_text(self):
        return self.__data.get('logoText')

    def strip(self):
        return Image(self.__images['strip']) \
            if 'strip' in self.__images \
            else None

    # Web Service

    def authentication_token(self):
        return self.__data.get('authenticationToken')

    def web_service_url(self):
        return self.__data.get('webServiceURL')


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
