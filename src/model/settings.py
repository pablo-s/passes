# settings.py
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

import os, tempfile

from gi.repository import Gio

from .digital_pass_list_store import SortingCriteria


class Settings:
    """
    """

    def __init__(self, application_id):
        self.__gsettings = Gio.Settings.new(application_id)

    def get_sorting_criteria(self):
        value = self.__gsettings\
            .get_value('default-sorting-criteria')\
            .get_string()

        return SortingCriteria.from_string(value)

    def set_sorting_criteria(self, sorting_criteria):
        self.__gsettings.set_string('default-sorting-criteria', sorting_criteria)

