# pkpass_field_row.py
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

import re

from gi.repository import GLib, Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_field_row.ui')
class PassFieldRow(Gtk.ListBoxRow):

    __gtype_name__ = 'PassFieldRow'

    label = Gtk.Template.Child()
    value = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.value.set_use_markup(True)

    def set_label(self, label):
        if label and label.strip():
            self.label.set_text(label)
            self.label.show()
        else:
            self.label.hide()

    def set_value(self, value):
        value = str(value)
        value = re.sub(r'\<br\/>', '\n', value)
        value_has_links = re.search('</a>', value)

        if value_has_links:
            value = re.sub('&', '&amp;', value)

        else:
            value = GLib.markup_escape_text(value)

            # Create a link for URLs
            value = re.sub('(?:(https?://)|(www))(\S+)',
                           '<a href="https://\\2\\3">\\1\\2\\3</a>',
                           value)

            # Create a link for telephone numbers
            value = re.sub('(\+\d+[\(\)\-\d\s\.]+\d)',
                           '<a href="tel:\\1">\\1</a>',
                           value)

            # Create a link for e-mails
            value = re.sub('(\S+\@[\w\-]+\.\w+)',
                           '<a href="mailto:\\1">\\1</a>',
                           value)

        self.value.set_label(value)
