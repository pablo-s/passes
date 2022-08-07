# espass.py
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

from .digital_pass import Barcode, Color, Date, DigitalPass, Image, \
                          PassDataExtractor, Date, TimeInterval


class EsPass(DigitalPass):
    """
    A representation of an esPass pass
    """

    styles = ['BOARDING',
              'COUPON',
              'EVENT',
              'LOYALTY',
              'VOUCHER']

    def __init__(self, pass_data, pass_images):
        super().__init__()

        self.__data = PassDataExtractor(pass_data)
        self.__images = pass_images

        self.__style = self.__data.get('type')

        self.__front_fields = []
        self.__back_fields = []
        fields = self.__data\
            .get_list('fields', EsPassField)

        for field in fields:
            if field.is_hidden():
                self.__back_fields.append(field)
            else:
                self.__front_fields.append(field)

        self.__validity_time_intervals = []
        timespan_dicts = self.__data\
            .get_list('validTimespans')

        for dict in timespan_dicts:
            timespan = TimeInterval.from_iso_strings(dict['from'], dict['to'])
            self.__validity_time_intervals.append(timespan)

    def barcode(self):
        return self.__data.get('barCode', Barcode)

    def back_fields(self):
        return self.__back_fields

    def background_color(self):
        return self.__data.get('accentColor', Color.from_css)

    def description(self):
        return self.__data.get('description')

    def expiration_date(self):
        now = Date.now()
        latest_expiration_date = Date()

        for interval in self.__validity_time_intervals:
            latest_expiration_date = interval.end_time()
            if now in interval:
                break

        return latest_expiration_date

    def front_fields(self):
        return self.__front_fields

    def icon(self):
        return Image(self.__images['icon.png'])

    def relevant_date(self):
        return self.__data.get('', Date.from_iso_string)

    def voided(self):
        return False


class EsPassField:
    """
    An EsPass Field
    """

    def __init__(self, espass_field_dictionary):
        self.__hide = False
        if 'hide' in espass_field_dictionary.keys():
            self.__hide = espass_field_dictionary['hide']

        self.__label = None
        if 'label' in espass_field_dictionary.keys():
            self.__label = espass_field_dictionary['label']

        self.__value = espass_field_dictionary['value']

    def is_hidden(self):
        return self.__hide

    def label(self):
        return self.__label

    def value(self):
        return self.__value
