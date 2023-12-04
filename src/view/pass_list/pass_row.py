# pkpass_row.py
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

from gi.repository import Gdk, GLib, Gtk

from .digital_pass_list_store import SortingCriteria
from .pass_icon import PassIcon
from .pass_row_header import PassRowHeader


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_row.ui')
class PassRow(Gtk.ListBoxRow):

    __gtype_name__ = 'PassRow'

    icon = Gtk.Template.Child()
    title = Gtk.Template.Child()
    subtitle = Gtk.Template.Child()

    def __init__(self, a_pass):
        super().__init__()
        self.__pass = a_pass

        self.__header_text = ''
        self.__sorting_criteria = None

        if a_pass.icon():
            self.icon.set_image(a_pass.icon())

        if a_pass.background_color():
            self.icon.set_background_color(a_pass.background_color())


        description = GLib.markup_escape_text(a_pass.description())

        if self.__pass.has_expired():
            description = '<s>%s</s>' % description

        self.title.set_label(description)
        self.subtitle.set_label(a_pass.creator())

    def activate(self):
        self.emit('activate')

    def data(self):
        return self.__pass

    def header_text(self):
        return self.__header_text

    def hide_header(self):
        self.set_header(None)

    def show_header(self):
        if not self.__header_text:
            return

        header = PassRowHeader(self.__header_text)
        self.set_header(header)

    def style(self):
        return self.__pass.style()

    def update_header_text_for(self, sorting_criteria):
        if self.__sorting_criteria == sorting_criteria:
            return

        self.__header_type = sorting_criteria

        if sorting_criteria == SortingCriteria.CREATOR:
            self.__header_text = self.__pass.creator()

        elif sorting_criteria == SortingCriteria.DESCRIPTION:
            self.__header_text = self.__pass.description()[0].upper()

        elif sorting_criteria == SortingCriteria.EXPIRATION_DATE:
            row_date = self.__pass.expiration_date()
            self.__header_text = row_date.as_relative_pretty_string() \
                                 if row_date else _('Without expiration date')

        elif sorting_criteria == SortingCriteria.RELEVANT_DATE:
            row_date = self.__pass.relevant_date()
            self.__header_text = row_date.as_relative_pretty_string() \
                                 if row_date else _('Without relevant date')

        else:
            self.__header_text = ''
