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

    carousel = Gtk.Template.Child()
    front_view = Gtk.Template.Child()
    back_view = Gtk.Template.Child()

    def __init__(self):
       super().__init__()
       self.__current_front_widget = None

    def content(self, a_pass):
        if self.__current_front_widget:
            self.front_view.remove(self.__current_front_widget)

        self.__current_front_widget = PassFrontView.new(a_pass)
        self.front_view.append(self.__current_front_widget)
        self.carousel.scroll_to(self.front_view, True)
