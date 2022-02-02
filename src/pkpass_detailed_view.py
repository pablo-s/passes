# pkpass_detailed_view.py
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

from gi.repository import Gtk

from .pkpass_front_view import PassFrontView


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_detailed_view.ui')
class PassDetailedView(Gtk.Box):

    __gtype_name__ = 'PassDetailedView'

    clamp = Gtk.Template.Child()

    def __init__(self):
       super().__init__()

    def content(self, a_pass):
        self.clamp.set_child(PassFrontView.new(a_pass))
