# pkpass_view.py
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

from .pkpass_back_view import PassBackView
from .pkpass_front_view import PassFrontView


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pkpass_view.ui')
class PassView(Gtk.Box):

    __gtype_name__ = 'PassView'

    pass_content = Gtk.Template.Child()

    def __init__(self):
       super().__init__()
       self.__back_widget = None
       self.__front_widget = None

    def content(self, a_pass):
        self.empty()

        self.__front_widget = PassFrontView.new(a_pass)
        self.__back_widget = PassBackView(a_pass)

        self.pass_content.append(self.__front_widget)
        self.pass_content.append(self.__back_widget)

    def empty(self):
        if self.__back_widget:
            self.pass_content.remove(self.__back_widget)
        if self.__front_widget:
            self.pass_content.remove(self.__front_widget)
