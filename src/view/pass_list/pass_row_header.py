# pkpass_row_header.py
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

from gi.repository import Gtk


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_row_header.ui')
class PassRowHeader(Gtk.Label):

    __gtype_name__ = 'PassRowHeader'

    def __init__(self, a_pass):
        super().__init__()

        expiration_date = a_pass.expiration_date()

        header_text = expiration_date.as_relative_pretty_string() \
            if expiration_date else _('Without expiration date')

        self.set_text(header_text)
