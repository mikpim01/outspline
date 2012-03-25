# Organism - A simple and extensible outliner.
# Copyright (C) 2011 Dario Giovannetti <dev@dariogiovannetti.net>
#
# This file is part of Organism.
#
# Organism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Organism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Organism.  If not, see <http://www.gnu.org/licenses/>.

copy_create = ("CREATE TABLE Copy (C_id INTEGER, "
                                  "C_parent INTEGER, "
                                  "C_previous INTEGER, "
                                  "C_text TEXT)")

copy_select = 'SELECT * FROM Copy'

copy_select_check = 'SELECT C_id FROM Copy LIMIT 1'

copy_select_parent = ('SELECT C_id, C_text FROM Copy WHERE C_parent=? '
                      'AND C_previous=? LIMIT 1')

copy_select_parent_roots = ('SELECT C_id, C_text FROM Copy '
                            'WHERE C_parent NOT IN (SELECT C_id FROM Copy)')

copy_insert = ('INSERT INTO Copy (C_id, C_parent, C_previous, C_text) '
               'VALUES (?, ?, ?, ?)')

copy_delete = 'DELETE FROM Copy'
