# pkpass_field_row.py
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

from gi.repository import GLib, Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_field_row.ui')
class PassFieldRow(Gtk.ListBoxRow):

    __gtype_name__ = 'PassFieldRow'

    label = Gtk.Template.Child()
    value = Gtk.Template.Child()

    def __init__(self, label, value, create_links=False):
        super().__init__()

        if label:
            self.label.set_text(label)
        else:
            self.label.hide()

        value_as_string = str(value)
        value_has_links = re.search('</a>', value_as_string)

        if create_links and not value_has_links:
            value_as_string = GLib.markup_escape_text(value_as_string)

            # Create a link for URLs
            value_as_string = re.sub('(https?://\S+)',
                                     '<a href="\\1">\\1</a>',
                                     value_as_string)

            # Create a link for telephone numbers
            value_as_string = re.sub('(\+\d+[\(\)\-\d\s\.]+\d)',
                                     '<a href="tel:\\1">\\1</a>',
                                     value_as_string)

            # Create a link for e-mails
            value_as_string = re.sub('(\S+\@[\w\-]+\.\w+)',
                                     '<a href="mailto:\\1">\\1</a>',
                                     value_as_string)

        self.value.set_use_markup(create_links)
        self.value.set_label(value_as_string)

    def set_halign(self, alignment):
        self.label.set_halign(alignment)
        self.value.set_halign(alignment)
