# barcode_dialog.py
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

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/barcode_dialog.ui')
class BarcodeDialog(Adw.Dialog):

    __gtype_name__ = 'BarcodeDialog'

    barcode = Gtk.Template.Child()
    alternative_text = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    def set_barcode(self, code):

        self.barcode\
            .encode(code.format(), code.message(), code.message_encoding())

        alternative_text = code.alternative_text()
        if alternative_text:
            self.alternative_text.set_text(alternative_text)
