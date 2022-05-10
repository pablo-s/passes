#!/bin/sh
#
# generate_reference.sh
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

readonly project_root=$(dirname $(dirname $(dirname $(realpath $0))))
cd ${project_root}

# Extract all translatable strings from the source code and generate a reference
# file.


# Blueprint
# Note: Although Blueprint is not C, it does the trick

xgettext \
    --language=C \
    --keyword=_ \
    --from-code=UTF-8 \
    --sort-by-file \
    --output=po/reference.pot \
    $(find src -type f -name "*.blp")


# Python files

xgettext \
    --join-existing \
    --language=Python \
    --sort-by-file \
    --output=po/reference.pot \
    $(find src -type f -name "*.py")
