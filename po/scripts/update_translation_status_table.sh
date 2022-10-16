#!/bin/sh
#
# update_translation_status_table.sh
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
cd ${project_root}/po

# Empty file
truncate -s 0 README.md

# Add warning
echo "<!-- This file is auto-generated. Do not edit manually. -->" >> README.md

# Add table header
echo "| File | Translated | Fuzzy | Untranslated | Progress |" >> README.md
echo "|:-----|-----------:|------:|-------------:|---------:|" >> README.md

for po_file in *.po
do
    po_stats="$(pocount ${po_file})"

    [[ ${po_stats} =~ Translated:[[:space:]]+([[:digit:]]+) ]]
    translated=${BASH_REMATCH[1]}

    [[ ${po_stats} =~ Untranslated:[[:space:]]+([[:digit:]]+) ]]
    untranslated=${BASH_REMATCH[1]}

    [[ ${po_stats} =~ Fuzzy:[[:space:]]+([[:digit:]]+) ]]
    fuzzy=${BASH_REMATCH[1]}

    [[ ${po_stats} =~ Total:[[:space:]]+([[:digit:]]+) ]]
    total=${BASH_REMATCH[1]}

    progress=$(echo "scale=2; 100 * ${translated} / ${total}" | bc)

    # Append a new row
    echo "| ${po_file} | ${translated} | ${fuzzy} | ${untranslated} " \
	 "| ${progress}% |" >> README.md
    
done
