# Outspline - A highly modular and extensible outliner.
# Copyright (C) 2011-2013 Dario Giovannetti <dev@dariogiovannetti.net>
#
# This file is part of Outspline.
#
# Outspline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Outspline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Outspline.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3
import time as _time

import outspline.coreaux_api as coreaux_api
import outspline.core_api as core_api
import outspline.extensions.organism_api as organism_api
copypaste_api = coreaux_api.import_optional_extension_api('copypaste')

import queries
import timer

_ADDON_NAME = ('Extensions', 'organism_timer')


def handle_create_database(kwargs):
    # Cannot use core_api.get_connection() here because the database isn't
    # open yet
    conn = sqlite3.connect(kwargs['filename'])
    cur = conn.cursor()
    cur.execute(queries.timerproperties_create)
    cur.execute(queries.timerproperties_insert, (int(_time.time()), ))
    conn.commit()
    conn.close()


def handle_open_database_dirty(kwargs):
    info = coreaux_api.get_addons_info()
    dependencies = info(_ADDON_NAME[0])(_ADDON_NAME[1]
                                     )['database_dependency_group_1'].split(' ')

    if not set(dependencies) - set(kwargs['dependencies']):
        timer.cdbs.add(kwargs['filename'])


def handle_open_database(kwargs):
    filename = kwargs['filename']

    if filename in timer.cdbs:
        timer.search_old_occurrences(filename)
        timer.search_next_occurrences()


def handle_save_database_copy(kwargs):
    origin = kwargs['origin']

    if origin in timer.cdbs:
        qconn = core_api.get_connection(origin)
        qconnd = sqlite3.connect(kwargs['destination'])
        cur = qconn.cursor()
        curd = qconnd.cursor()

        cur.execute(queries.timerproperties_select)
        for row in cur:
            curd.execute(queries.timerproperties_update_copy, tuple(row))

        core_api.give_connection(origin, qconn)

        qconnd.commit()
        qconnd.close()


def handle_close_database(kwargs):
    timer.cdbs.discard(kwargs['filename'])
    timer.search_next_occurrences()


def main():
    core_api.bind_to_create_database(handle_create_database)
    core_api.bind_to_open_database_dirty(handle_open_database_dirty)
    core_api.bind_to_open_database(handle_open_database)
    core_api.bind_to_close_database(handle_close_database)
    core_api.bind_to_save_database_copy(handle_save_database_copy)
    core_api.bind_to_delete_items(timer.search_next_occurrences)
    core_api.bind_to_history(timer.search_next_occurrences)
    core_api.bind_to_exit_app_1(timer.cancel_search_next_occurrences)

    organism_api.bind_to_update_item_rules(timer.search_next_occurrences)

    if copypaste_api:
        copypaste_api.bind_to_items_pasted(timer.search_next_occurrences)