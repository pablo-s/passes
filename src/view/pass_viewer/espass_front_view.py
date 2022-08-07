# pkpass_front_view.py
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

from gi.repository import GdkPixbuf, Gtk

from .barcode_widget import BarcodeWidget
from .pkpass_field_row import PassFieldRow


class EsPassFrontView:
    """
    A factory to instance the appropriate view
    """
    @staticmethod
    def new(a_pass):
        return EsPassFallbackView(a_pass)


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/espass_front_view_fallback.ui')
class EsPassFallbackView(Gtk.Box):

    __gtype_name__ = 'EsPassFallbackView'

    icon = Gtk.Template.Child()
    icon_row = Gtk.Template.Child()
    description = Gtk.Template.Child()
    fields = Gtk.Template.Child()

    def __init__(self, espass):
        super().__init__()

        self.icon.set_pixbuf(espass.icon().as_pixbuf())
        self.description.set_text(espass.description())

        background_color = espass.background_color()
        if background_color:
            self.icon_row.color(*background_color.as_tuple())

        for field in espass.front_fields():
            label = field.label()
            value = field.value()
            pass_field_row = PassFieldRow(label, value)
            self.fields.append(pass_field_row)

