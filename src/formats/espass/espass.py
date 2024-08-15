# espass.py
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

from passes.digital_pass import Barcode, Color, Date, DigitalPass, Image, \
                                PassDataExtractor, PassField, Date, TimeInterval

from .espass_plotter import EsPassPlotter


class EsPass():
    """
    A representation of an esPass pass
    """

    types = ['BOARDING',
             'COUPON',
             'EVENT',
             'LOYALTY',
             'VOUCHER']

    def __init__(self, pass_data, pass_images):
        self.__data = PassDataExtractor(pass_data)
        self.__images = pass_images

        self.__type = self.__data.get('type')

        self.__front_fields = []
        self.__hidden_fields = []
        fields = self.__data\
            .get_list('fields', EsPassField)

        for field in fields:
            if field.is_hidden():
                self.__hidden_fields.append(field)
            else:
                self.__front_fields.append(field)

        self.__validity_time_intervals = []
        timespan_dicts = self.__data\
            .get_list('validTimespans')

        for dict in timespan_dicts:
            timespan = TimeInterval.from_iso_strings(dict['from'], dict['to'])
            self.__validity_time_intervals.append(timespan)


    # Container

    def icon(self):
        return Image(self.__images['icon.png'])


    # Mandatory fields

    def type(self):
        return self.__type

    def description(self):
        return self.__data.get('description')

    def id(self):
        return self.__data.get('id')


    # Time info

    def valid_timespans(self):
        return self.__validity_time_intervals


    # Metadata

    def creator(self):
        return self.__data.get('creator') or _('Unknown')


    # Fields

    def front_fields(self):
        return self.__front_fields

    def hidden_fields(self):
        return self.__hidden_fields


    # Color

    def accent_color(self):
        return self.__data.get('accentColor', Color.from_css)


    # Barcode

    def barcode(self):
        return self.__data.get('barCode', Barcode)


class EsPassAdapter(DigitalPass):
    def __init__(self, pkpass):
        super().__init__()
        self.__adaptee = pkpass

    def adaptee(self):
        return self.__adaptee

    def additional_information(self):
        return self.__adaptee.hidden_fields()

    def background_color(self):
        return self.__adaptee.accent_color()

    def barcodes(self):
        return [self.__adaptee.barcode()]

    def creator(self):
        return self.__adaptee.creator()

    def description(self):
        return self.__adaptee.description()

    def expiration_date(self):
        now = Date.now()
        latest_expiration_date = None

        for interval in self.__adaptee.valid_timespans():
            latest_expiration_date = interval.end_time()
            if now in interval:
                break

        return latest_expiration_date

    def file_extension():
        return '.espass'

    def format(self):
        return 'espass'

    def icon(self):
        return self.__adaptee.icon()

    def is_updatable(self):
        return False

    def mime_type():
        return 'application/vnd.espass-espass+zip'

    def plotter(self, widget):
        return EsPassPlotter(self, widget)

    def relevant_date(self):
        return None

    def unique_identifier(self):
        return '.'.join([self.__adaptee.id(), self.format()])

    def voided(self):
        return False


class EsPassField(PassField):
    """
    An EsPass Field
    """

    __slots__ = ('__hide')

    def __init__(self, espass_field_dictionary):

        super().__init__()

        self.__hide = False
        if 'hide' in espass_field_dictionary.keys():
            self.__hide = espass_field_dictionary['hide']

        if 'label' in espass_field_dictionary.keys():
            self._label = espass_field_dictionary['label']

        self._value = espass_field_dictionary['value']

    def is_hidden(self):
        return self.__hide
