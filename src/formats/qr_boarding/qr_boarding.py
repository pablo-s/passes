# qr_boarding.py
#
# Copyright 2026 Jan-Michael Brummer <jan.brummer@tabos.org>
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
from datetime import date
import hashlib

from passes.digital_pass import Barcode, Color, Date, DigitalPass, PassField
from .qr_boarding_plotter import QRBoardingPassPlotter


COMPARTMENT_NAMES = {
    'Y': 'Economy',
    'W': 'Premium Economy',
    'C': 'Business',
    'J': 'Business',
    'F': 'First',
}

AIRPORT_NAMES = {
    # Turkey
    'AYT': 'Antalya', 'ADB': 'Izmir', 'ESB': 'Ankara', 'IST': 'Istanbul',
    'SAW': 'Istanbul', 'ADB': 'Izmir', 'ADB': 'Izmir', 'ASR': 'Kayseri',
    'TZX': 'Trabzon', 'ERZ': 'Erzurum', 'GZT': 'Gaziantep', 'DLM': 'Dalaman',
    'BJV': 'Bodrum', 'ADF': 'Adana', 'GNY': 'Sanliurfa', 'VAN': 'Van',
    'KZS': 'Kars', 'MQM': 'Mardin', 'BAL': 'Batman', 'DIY': 'Diyarbakir',
    'SZF': 'Samsun', 'NOP': 'Nevsehir', 'NAV': 'Nevsehir', 'KYA': 'Konya',
    'AOE': 'Eskisehir', 'USQ': 'Usak', 'BZI': 'Balikesir', 'BDM': 'Bolu',
    # Germany
    'FRA': 'Frankfurt', 'MUC': 'München', 'TXL': 'Berlin', 'BER': 'Berlin',
    'SXF': 'Berlin', 'HAM': 'Hamburg', 'CGN': 'Köln/Bonn', 'DUS': 'Düsseldorf',
    'STR': 'Stuttgart', 'HAJ': 'Hannover', 'BRE': 'Bremen', 'NUE': 'Nürnberg',
    'LEJ': 'Leipzig', 'DRS': 'Dresden', 'FMO': 'Münster', 'KSF': 'Kassel',
    'DTM': 'Dortmund', 'FDH': 'Friedrichshafen', 'ZQW': 'Zweibrücken',
    # Europe
    'VIE': 'Wien', 'ZRH': 'Zürich', 'CDG': 'Paris', 'ORY': 'Paris',
    'NCE': 'Nizza', 'LHR': 'London', 'LGW': 'London', 'STN': 'London',
    'LTN': 'London', 'SEN': 'London', 'AMS': 'Amsterdam', 'BRU': 'Brüssel',
    'FCO': 'Rom', 'CIA': 'Rom', 'MXP': 'Mailand', 'BGY': 'Mailand',
    'BCN': 'Barcelona', 'MAD': 'Madrid', 'LIS': 'Lissabon', 'ATH': 'Athenen',
    'ARN': 'Stockholm', 'OSL': 'Oslo', 'CPH': 'Kopenhagen', 'HEL': 'Helsinki',
    'WAW': 'Warschau', 'PRG': 'Prag', 'BUD': 'Budapest', 'OTP': 'Bukarest',
    'SOF': 'Sofia', 'ZAG': 'Zagreb', 'BEG': 'Belgrad', 'TLL': 'Tallinn',
    'RIX': 'Riga', 'VNO': 'Vilnius', 'DUB': 'Dublin', 'EDI': 'Edinburgh',
    'GVA': 'Genf', 'NAP': 'Neapel', 'PMI': 'Palma', 'TFS': 'Teneriffa',
    'LPA': 'Gran Canaria', 'FUE': 'Fuerteventura', 'ACE': 'Lanzarote',
    'AGP': 'Málaga', 'ALC': 'Alicante', 'VLC': 'Valencia', 'BIO': 'Bilbao',
    'OPO': 'Porto', 'SKG': 'Thessaloniki', 'KGS': 'Kos', 'RHO': 'Rhodos',
    'HER': 'Kreta', 'CHQ': 'Kreta', 'JTR': 'Santorini', 'CFU': 'Korfu',
    'ZAD': 'Zadar', 'SPU': 'Split', 'DBV': 'Dubrovnik', 'TGD': 'Podgorica',
    'SKP': 'Skopje', 'TIA': 'Tirana', 'PRN': 'Pristina', 'SJJ': 'Sarajevo',
    # Russia/CIS
    'SVO': 'Moskau', 'DME': 'Moskau', 'LED': 'Sankt Petersburg',
    'KZN': 'Kasan', 'SVX': 'Jekaterinburg', 'OVB': 'Nowosibirsk',
    # Middle East
    'DXB': 'Dubai', 'AUH': 'Abu Dhabi', 'DOH': 'Doha', 'RUH': 'Riad',
    'JED': 'Dschidda', 'BAH': 'Bahrain', 'MCT': 'Maskat', 'KWI': 'Kuwait',
    'AMM': 'Amman', 'BEY': 'Beirut', 'TLV': 'Tel Aviv', 'TBS': 'Tiflis',
    'EVN': 'Eriwan', 'GYD': 'Baku',
    # Asia
    'BKK': 'Bangkok', 'HKT': 'Phuket', 'CNX': 'Chiang Mai', 'DMK': 'Bangkok',
    'SIN': 'Singapur', 'KUL': 'Kuala Lumpur', 'CGK': 'Jakarta', 'DPS': 'Bali',
    'HAN': 'Hanoi', 'SGN': 'Ho-Chi-Minh-Stadt', 'MNL': 'Manila',
    'HKG': 'Hongkong', 'TPE': 'Taipeh', 'ICN': 'Seoul', 'NRT': 'Tokio',
    'HND': 'Tokio', 'KIX': 'Osaka', 'PEK': 'Peking', 'PKX': 'Peking',
    'PVG': 'Shanghai', 'SHA': 'Shanghai', 'CTU': 'Chengdu', 'CAN': 'Guangzhou',
    'DEL': 'Neu-Delhi', 'BOM': 'Mumbai', 'BLR': 'Bangalore', 'COK': 'Kochi',
    'CMB': 'Colombo', 'KTM': 'Kathmandu', 'MLE': 'Male',
    # Americas
    'JFK': 'New York', 'LGA': 'New York', 'EWR': 'Newark', 'LAX': 'Los Angeles',
    'SFO': 'San Francisco', 'ORD': 'Chicago', 'ATL': 'Atlanta', 'DFW': 'Dallas',
    'MIA': 'Miami', 'MCO': 'Orlando', 'BOS': 'Boston', 'SEA': 'Seattle',
    'DEN': 'Denver', 'IAH': 'Houston', 'PHX': 'Phoenix', 'LAS': 'Las Vegas',
    'IAD': 'Washington', 'DCA': 'Washington', 'YYZ': 'Toronto',
    'YVR': 'Vancouver', 'YUL': 'Montreal', 'MEX': 'Mexiko-Stadt',
    'CUN': 'Cancún', 'GDL': 'Guadalajara', 'SJO': 'San José',
    'PTY': 'Panama-Stadt', 'BOG': 'Bogotá', 'LIM': 'Lima',
    'SCL': 'Santiago', 'EZE': 'Buenos Aires', 'GIG': 'Rio de Janeiro',
    'GRU': 'São Paulo',
    # Africa
    'CAI': 'Kairo', 'CMN': 'Casablanca', 'RAK': 'Marrakesch', 'RBA': 'Rabat',
    'TUN': 'Tunis', 'ALG': 'Algier', 'JNB': 'Johannesburg', 'CPT': 'Kapstadt',
    'NBO': 'Nairobi', 'ADD': 'Addis Abeba', 'LOS': 'Lagos', 'ACC': 'Accra',
    'DSS': 'Dakar', 'MRU': 'Mauritius', 'ANR': 'Antananarivo',
    # Oceania
    'SYD': 'Sydney', 'MEL': 'Melbourne', 'BNE': 'Brisbane', 'AKL': 'Auckland',
    'WLG': 'Wellington',
}


def _airport_name(code):
    return AIRPORT_NAMES.get(code, code)


class QRBoardingPass:
    """A boarding pass decoded from a QR/Aztec barcode (IATA BCBP format)."""

    def __init__(self, qr_data, barcode_format=''):
        self.__qr_data = qr_data
        self.__barcode_format = barcode_format
        self.__parsed = self._parse(qr_data)

    def _parse(self, qr_data):
        parsed = {
            'passenger_name': '',
            'flight_number': '',
            'departure_airport': '',
            'arrival_airport': '',
            'seat': '',
            'airline': '',
            'compartment': '',
            'boarding_time': None,
            'display_date': '',
        }

        try:
            data = json.loads(qr_data)
            if isinstance(data, dict):
                parsed.update(data)
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        if qr_data.startswith('http'):
            return parsed

        if len(qr_data) >= 22 and qr_data[0] == 'M':
            self._parse_bcbp(qr_data, parsed)

        return parsed

    def _parse_bcbp(self, data, parsed):
        # Passenger name (pos 2-21, 20 chars)
        parsed['passenger_name'] = data[2:22].strip()

        # Origin airport (pos 30-32, 3 chars)
        if len(data) >= 33:
            origin = data[30:33].strip()
            if origin.isalpha():
                parsed['departure_airport'] = origin

        # Destination airport (pos 33-35, 3 chars)
        if len(data) >= 36:
            dest = data[33:36].strip()
            if dest.isalpha():
                parsed['arrival_airport'] = dest

        # Operating carrier (pos 36-37, 2 chars)
        if len(data) >= 38:
            carrier = data[36:38].strip()
            if carrier:
                parsed['airline'] = carrier

        # Flight number (pos 39-42, 4 chars)
        if len(data) >= 43:
            flight = data[39:43].strip()
            if flight:
                parsed['flight_number'] = flight

        # Date - Julian day (pos 44-46, 3 chars)
        if len(data) >= 47:
            julian = data[44:47].strip()
            if julian:
                try:
                    dt = date.fromordinal(date(date.today().year, 1, 1).toordinal() + int(julian) - 1)
                    parsed['boarding_time'] = dt.strftime('%Y-%m-%d')
                    parsed['display_date'] = dt.strftime('%d. %b %Y')
                except (ValueError, OverflowError):
                    parsed['display_date'] = julian

        # Compartment code (pos 47, 1 char)
        if len(data) >= 48:
            code = data[47].strip()
            if code:
                parsed['compartment'] = COMPARTMENT_NAMES.get(code, code)

        # Seat number (pos 48-51, 4 chars) - strip leading zeros
        if len(data) >= 52:
            seat = data[48:52].strip().lstrip('0')
            if seat:
                parsed['seat'] = seat

    def passenger_name(self):
        return self.__parsed.get('passenger_name', '')

    def flight_number(self):
        return self.__parsed.get('flight_number', '')

    def departure_airport(self):
        return self.__parsed.get('departure_airport', '')

    def arrival_airport(self):
        return self.__parsed.get('arrival_airport', '')

    def boarding_time(self):
        return self.__parsed.get('boarding_time')

    def display_date(self):
        return self.__parsed.get('display_date', '')

    def seat(self):
        return self.__parsed.get('seat', '')

    def compartment(self):
        return self.__parsed.get('compartment', '')

    def airline(self):
        return self.__parsed.get('airline', '')

    def qr_data(self):
        return self.__qr_data

    def barcode_format(self):
        return self.__barcode_format


class QRBoardingPassAdapter(DigitalPass):

    BARCODE_FORMAT_MAP = {
        'Aztec': 'PKBarcodeFormatAztec',
        'QR': 'PKBarcodeFormatQR',
        'DataMatrix': 'PKBarcodeFormatPDF417',
    }

    def __init__(self, qr_boarding_pass):
        super().__init__()
        self.__adaptee = qr_boarding_pass

    def additional_information(self):
        return []

    def background_color(self):
        return Color(255, 255, 255)

    def barcodes(self):
        raw = self.__adaptee.barcode_format()
        pk_format = 'PKBarcodeFormatQR'
        for key, val in self.BARCODE_FORMAT_MAP.items():
            if key in raw:
                pk_format = val
                break
        return [Barcode({
            'format': pk_format,
            'message': self.__adaptee.qr_data(),
            'messageEncoding': 'iso-8859-1',
        })]

    def creator(self):
        return self.__adaptee.passenger_name() or 'QR Code Import'

    def description(self):
        airline = self.__adaptee.airline()
        dep = _airport_name(self.__adaptee.departure_airport())
        arr = _airport_name(self.__adaptee.arrival_airport())
        flight = self.__adaptee.flight_number()
        parts = []
        if dep and arr:
            parts.append(f'{dep} → {arr}')
        return ' '.join(parts) if parts else 'Boarding Pass'

    def expiration_date(self):
        return None

    @classmethod
    def file_extension(cls):
        return '.qr-boarding'

    def format(self):
        return 'qr-boarding'

    def icon(self):
        return None

    def logo_text(self):
        return self.__adaptee.airline()

    def is_updatable(self):
        return False

    @classmethod
    def mime_type(cls):
        return 'image/png'

    @classmethod
    def supported_mime_types(cls):
        return ['image/png', 'image/jpeg', 'image/gif', 'image/bmp']

    def plotter(self, widget):
        return QRBoardingPassPlotter.new(self, widget)

    def relevant_date(self):
        boarding_time = self.__adaptee.boarding_time()
        if boarding_time:
            try:
                return Date.from_iso_string(boarding_time)
            except Exception:
                pass
        return None

    def unique_identifier(self):
        h = hashlib.new('sha256')
        h.update(self.__adaptee.qr_data().encode())
        identifier = h.hexdigest()
        print(identifier)
        return f'{identifier}.qr-boarding'

    def voided(self):
        return False

    def header_fields(self):
        dep = _airport_name(self.__adaptee.departure_airport())
        arr = _airport_name(self.__adaptee.arrival_airport())
        if dep and arr:
            return [QRBoardingField('Route', f'{dep} → {arr}')]
        if dep:
            return [QRBoardingField('From', dep)]
        if arr:
            return [QRBoardingField('To', arr)]
        return []

    def primary_fields(self):
        name = self.__adaptee.passenger_name()
        return [QRBoardingField('Passenger', name)] if name else []

    def secondary_fields(self):
        fields = []
        airline = self.__adaptee.airline()
        flight = self.__adaptee.flight_number()
        if airline or flight:
            fields.append(QRBoardingField('Flight', f'{airline} {flight}'.strip()))
        seat = self.__adaptee.seat()
        if seat:
            compartment = self.__adaptee.compartment()
            label = f'Seat ({compartment})' if compartment else 'Seat'
            fields.append(QRBoardingField(label, seat))
        return fields

    def auxiliary_fields(self):
        date_str = self.__adaptee.display_date()
        return [QRBoardingField('Date', date_str)] if date_str else []


class QRBoardingField(PassField):
    def __init__(self, label, value):
        super().__init__()
        self._label = label
        self._value = value
