# Outspline - A highly modular and extensible outliner.
# Copyright (C) 2011-2014 Dario Giovannetti <dev@dariogiovannetti.net>
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

import wx

from outspline.static.wxclasses.timectrls import TimeSpanCtrl
from outspline.static.wxclasses.misc import NarrowSpinCtrl

import outspline.coreaux_api as coreaux_api
import outspline.core_api as core_api
import outspline.interfaces.wxgui_api as wxgui_api
import outspline.extensions.organism_alarms_api as organism_alarms_api

import list as list_
import filters as filters_
import export


class MainMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)

        self.tasklist = tasklist
        self.occview = tasklist.list_

        self.ID_NAVIGATOR = wx.NewId()
        self.ID_SCROLL = wx.NewId()
        self.ID_FIND = wx.NewId()
        self.ID_EDIT = wx.NewId()
        self.ID_SNOOZE = wx.NewId()
        self.ID_SNOOZE_ALL = wx.NewId()
        self.ID_DISMISS = wx.NewId()
        self.ID_DISMISS_ALL = wx.NewId()
        self.ID_EXPORT = wx.NewId()

        self.navigator_submenu = NavigatorMenu(tasklist)
        self.snooze_selected_submenu = SnoozeSelectedConfigMenu(tasklist)
        self.snooze_all_submenu = SnoozeAllConfigMenu(tasklist)
        self.export_submenu = ExportMenu(tasklist)

        config = coreaux_api.get_plugin_configuration('wxtasklist')(
                                                                'Shortcuts')

        self.navigator = wx.MenuItem(self, self.ID_NAVIGATOR, 'Na&vigator',
                        'Navigator actions', subMenu=self.navigator_submenu)
        self.scroll = wx.MenuItem(self, self.ID_SCROLL,
                "Scro&ll to ongoing\t{}".format(config['scroll_to_ongoing']),
                "Order the list by State and scroll "
                "to the first ongoing event")
        self.find = wx.MenuItem(self, self.ID_FIND,
            "&Find in database\t{}".format(config('Items')['find_selected']),
            "Select the database items associated to the selected events")
        self.edit = wx.MenuItem(self, self.ID_EDIT,
                "&Edit selected\t{}".format(config('Items')['edit_selected']),
                "Open in the editor the database items associated "
                "to the selected events")

        self.snooze = wx.MenuItem(self, self.ID_SNOOZE, "&Snooze selected",
                                        "Snooze the selected alarms",
                                        subMenu=self.snooze_selected_submenu)
        self.snooze_all = wx.MenuItem(self, self.ID_SNOOZE_ALL,
                                "S&nooze all", "Snooze all the active alarms",
                                subMenu=self.snooze_all_submenu)

        self.dismiss = wx.MenuItem(self, self.ID_DISMISS,
                                        "&Dismiss selected\t{}".format(
                                        config('Items')['dismiss_selected']),
                                        "Dismiss the selected alarms")
        self.dismiss_all = wx.MenuItem(self, self.ID_DISMISS_ALL,
                    "Dis&miss all\t{}".format(config('Items')['dismiss_all']),
                    "Dismiss all the active alarms")
        self.export = wx.MenuItem(self, self.ID_EXPORT, 'E&xport view',
                                        'Export the current view to a file',
                                        subMenu=self.export_submenu)

        self.navigator.SetBitmap(wx.ArtProvider.GetBitmap('@navigator',
                                                                wx.ART_MENU))
        self.scroll.SetBitmap(wx.ArtProvider.GetBitmap('@movedown',
                                                                wx.ART_MENU))
        self.find.SetBitmap(wx.ArtProvider.GetBitmap('@find', wx.ART_MENU))
        self.edit.SetBitmap(wx.ArtProvider.GetBitmap('@edit', wx.ART_MENU))
        self.snooze.SetBitmap(wx.ArtProvider.GetBitmap('@alarms', wx.ART_MENU))
        self.snooze_all.SetBitmap(wx.ArtProvider.GetBitmap('@alarms',
                                                                  wx.ART_MENU))
        self.dismiss.SetBitmap(wx.ArtProvider.GetBitmap('@alarmoff',
                                                                  wx.ART_MENU))
        self.dismiss_all.SetBitmap(wx.ArtProvider.GetBitmap('@alarmoff',
                                                                  wx.ART_MENU))
        self.export.SetBitmap(wx.ArtProvider.GetBitmap('@saveas', wx.ART_MENU))

        self.AppendItem(self.navigator)
        self.AppendItem(self.scroll)
        self.AppendSeparator()
        self.AppendItem(self.find)
        self.AppendItem(self.edit)
        self.AppendSeparator()
        self.AppendItem(self.snooze)
        self.AppendItem(self.snooze_all)
        self.AppendItem(self.dismiss)
        self.AppendItem(self.dismiss_all)
        self.AppendSeparator()
        self.AppendItem(self.export)

        wxgui_api.bind_to_menu(self._scroll_to_ongoing, self.scroll)
        wxgui_api.bind_to_menu(self._find_in_tree, self.find)
        wxgui_api.bind_to_menu(self._edit_items, self.edit)
        wxgui_api.bind_to_menu(self._dismiss_selected_alarms, self.dismiss)
        wxgui_api.bind_to_menu(self._dismiss_all_alarms, self.dismiss_all)

        wxgui_api.bind_to_update_menu_items(self._update_items)
        wxgui_api.bind_to_reset_menu_items(self._reset_items)

        wxgui_api.insert_menu_main_item('Even&ts',
                                    wxgui_api.get_menu_view_position(), self)

    def _update_items(self, kwargs):
        if kwargs['menu'] is self:
            self.navigator.Enable(False)
            self.scroll.Enable(False)
            self.find.Enable(False)
            self.edit.Enable(False)
            self.snooze.Enable(False)
            self.snooze_all.Enable(False)
            self.dismiss.Enable(False)
            self.dismiss_all.Enable(False)
            self.export.Enable(False)

            self.navigator_submenu.update_items()

            tab = wxgui_api.get_selected_right_nb_tab()

            if tab is self.tasklist.panel:
                self.scroll.Enable()

                sel = self.occview.listview.GetFirstSelected()

                while sel > -1:
                    item = self.occview.occs[
                                    self.occview.listview.GetItemData(sel)]

                    canbreak = 0

                    # Check item is not a gap or an overlapping
                    if item.get_filename() is not None:
                        self.find.Enable()
                        self.edit.Enable()
                        canbreak += 1

                    if item.get_alarm() is False:
                        self.snooze.Enable()
                        self.dismiss.Enable()
                        canbreak += 1

                    if canbreak > 1:
                        break

                    sel = self.occview.listview.GetNextSelected(sel)

                # Note that "all" means all the visible active alarms; some
                # may be hidden in the current view; this is also why these
                # actions must be disabled if the tasklist is not focused
                if len(self.occview.get_active_alarms()) > 0:
                    self.snooze_all.Enable()
                    self.dismiss_all.Enable()

                self.navigator_submenu.update_items_selected()

            if self.tasklist.is_shown():
                # Already appropriately checked above
                self.navigator.Enable()
                self.export.Enable()

    def _reset_items(self, kwargs):
        # Re-enable all the actions so they are available for their
        # accelerators
        self.navigator.Enable()
        self.scroll.Enable()
        self.find.Enable()
        self.edit.Enable()
        self.snooze.Enable()
        self.snooze_all.Enable()
        self.dismiss.Enable()
        self.dismiss_all.Enable()
        self.export.Enable()

        self.navigator_submenu.reset_items()

    def _scroll_to_ongoing(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.occview.autoscroll.execute_force()

    def _find_in_tree(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            sel = self.occview.listview.GetFirstSelected()

            if sel > -1:
                for filename in core_api.get_open_databases():
                    wxgui_api.unselect_all_items(filename)

                # Loop that selects a database tab (but doesn't select items)
                while sel > -1:
                    item = self.occview.occs[self.occview.listview.GetItemData(
                                                                        sel)]

                    if item.get_filename() is not None:
                        wxgui_api.select_database_tab(item.get_filename())
                        # The item is selected in the loop below
                        break
                    else:
                        sel = self.occview.listview.GetNextSelected(sel)

                # Loop that doesn't select a database tab but selects items,
                # including the one found in the loop above
                while sel > -1:
                    item = self.occview.occs[self.occview.listview.GetItemData(
                                                                        sel)]

                    if item.get_filename() is not None:
                        wxgui_api.add_item_to_selection(item.get_filename(),
                                                                item.get_id())

                    sel = self.occview.listview.GetNextSelected(sel)

    def _edit_items(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            sel = self.occview.listview.GetFirstSelected()

            while sel > -1:
                item = self.occview.occs[self.occview.listview.GetItemData(
                                                                        sel)]

                if item.get_filename() is not None:
                    wxgui_api.open_editor(item.get_filename(), item.get_id())

                sel = self.occview.listview.GetNextSelected(sel)

    def _dismiss_selected_alarms(self, event):
        if core_api.block_databases():
            tab = wxgui_api.get_selected_right_nb_tab()

            if tab is self.tasklist.panel:
                alarmsd = self.occview.get_selected_active_alarms()

                if len(alarmsd) > 0:
                    organism_alarms_api.dismiss_alarms(alarmsd)
                    # Let the alarm off event update the tasklist

            core_api.release_databases()

    def _dismiss_all_alarms(self, event):
        # Note that "all" means all the visible active alarms; some may be
        # hidden in the current view
        if core_api.block_databases():
            tab = wxgui_api.get_selected_right_nb_tab()

            if tab is self.tasklist.panel:
                alarmsd = self.occview.get_active_alarms()

                if len(alarmsd) > 0:
                    organism_alarms_api.dismiss_alarms(alarmsd)
                    # Let the alarm off event update the tasklist

            core_api.release_databases()


class NavigatorMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist

        self.ID_PREVIOUS = wx.NewId()
        self.ID_NEXT = wx.NewId()
        self.ID_APPLY = wx.NewId()
        self.ID_SET = wx.NewId()
        self.ID_RESET = wx.NewId()

        config = coreaux_api.get_plugin_configuration('wxtasklist')(
                                                    'Shortcuts')('Navigator')

        self.previous = wx.MenuItem(self, self.ID_PREVIOUS,
                            "&Previous page\t{}".format(config['previous']),
                            "View the previous page of events")
        self.next = wx.MenuItem(self, self.ID_NEXT,
                                    "&Next page\t{}".format(config['next']),
                                    "View the next page of events")
        self.apply = wx.MenuItem(self, self.ID_APPLY,
                                "&Apply filters\t{}".format(config['apply']),
                                "Apply the configured filters")
        self.set = wx.MenuItem(self, self.ID_SET,
                                    "Se&t filters\t{}".format(config['set']),
                                    "Apply and save the configured filters")
        self.reset = wx.MenuItem(self, self.ID_RESET,
                                "&Reset filters\t{}".format(config['reset']),
                                "Reset the filters to the saved ones")

        self.previous.SetBitmap(wx.ArtProvider.GetBitmap('@previous',
                                                                  wx.ART_MENU))
        self.next.SetBitmap(wx.ArtProvider.GetBitmap('@next', wx.ART_MENU))
        self.apply.SetBitmap(wx.ArtProvider.GetBitmap('@apply',  wx.ART_MENU))
        self.set.SetBitmap(wx.ArtProvider.GetBitmap('@save', wx.ART_MENU))
        self.reset.SetBitmap(wx.ArtProvider.GetBitmap('@undo', wx.ART_MENU))

        self.AppendSeparator()
        self.AppendItem(self.previous)
        self.AppendItem(self.next)
        self.AppendItem(self.apply)
        self.AppendItem(self.set)
        self.AppendItem(self.reset)

        wxgui_api.bind_to_menu(self._go_to_previous_page, self.previous)
        wxgui_api.bind_to_menu(self._go_to_next_page, self.next)
        wxgui_api.bind_to_menu(self._apply_filters, self.apply)
        wxgui_api.bind_to_menu(self._set_filters, self.set)
        wxgui_api.bind_to_menu(self._reset_filters, self.reset)

    def update_items(self):
        self.previous.Enable(False)
        self.next.Enable(False)
        self.apply.Enable(False)
        self.set.Enable(False)
        self.reset.Enable(False)

    def update_items_selected(self):
        self.previous.Enable()
        self.next.Enable()
        self.apply.Enable()
        self.set.Enable()
        self.reset.Enable()

    def reset_items(self):
        # Re-enable all the actions so they are available for their
        # accelerators
        self.previous.Enable()
        self.next.Enable()
        self.apply.Enable()
        self.set.Enable()
        self.reset.Enable()

    def _go_to_previous_page(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.tasklist.navigator.show_previous_page()

    def _go_to_next_page(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.tasklist.navigator.show_next_page()

    def _apply_filters(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.tasklist.navigator.apply()

    def _set_filters(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.tasklist.navigator.set()

    def _reset_filters(self, event):
        tab = wxgui_api.get_selected_right_nb_tab()

        if tab is self.tasklist.panel:
            self.tasklist.navigator.reset()


class ExportMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist

        self.exporter = export.Exporter(tasklist.list_)

        self.ID_JSON = wx.NewId()
        self.ID_TSV = wx.NewId()
        self.ID_XML = wx.NewId()

        self.json = wx.MenuItem(self, self.ID_JSON,
                            "&JSON...", "Export to JSON format")
        self.tsv = wx.MenuItem(self, self.ID_TSV,
                            "&TSV...", "Export to tab-separated values format")
        self.xml = wx.MenuItem(self, self.ID_XML,
                            "&XML...", "Export to XML format")

        self.json.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))
        self.tsv.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))
        self.xml.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))

        self.AppendItem(self.json)
        self.AppendItem(self.tsv)
        self.AppendItem(self.xml)

        wxgui_api.bind_to_menu(self._export_to_json, self.json)
        wxgui_api.bind_to_menu(self._export_to_tsv, self.tsv)
        wxgui_api.bind_to_menu(self._export_to_xml, self.xml)

    def _export_to_json(self, event):
        if self.tasklist.is_shown():
            self.exporter.export_to_json()

    def _export_to_tsv(self, event):
        if self.tasklist.is_shown():
            self.exporter.export_to_tsv()

    def _export_to_xml(self, event):
        if self.tasklist.is_shown():
            self.exporter.export_to_xml()


class ViewMenu(object):
    def __init__(self, tasklist):
        self.tasklist = tasklist
        self.occview = tasklist.list_

        self.ID_EVENTS = wx.NewId()
        self.ID_SHOW = wx.NewId()
        self.ID_FOCUS = wx.NewId()
        self.ID_ALARMS = wx.NewId()
        self.ID_TOGGLE_NAVIGATOR = wx.NewId()
        self.ID_GAPS = wx.NewId()
        self.ID_OVERLAPS = wx.NewId()
        self.ID_AUTOSCROLL = wx.NewId()

        submenu = wx.Menu()
        self.alarms_submenu = AlarmsMenu(tasklist)

        config = coreaux_api.get_plugin_configuration('wxtasklist')(
                                                        'Shortcuts')('View')

        self.events = wx.MenuItem(wxgui_api.get_menu_view(), self.ID_EVENTS,
                        'Even&ts', 'Events navigation actions',
                        subMenu=submenu)
        self.show = wx.MenuItem(submenu, self.ID_SHOW,
                                "Show &panel\t{}".format(config['show']),
                                "Show the events panel", kind=wx.ITEM_CHECK)
        self.focus = wx.MenuItem(submenu, self.ID_FOCUS,
                        "&Focus\t{}".format(config['focus']),
                        "Set focus on the events tab")
        self.alarms = wx.MenuItem(submenu, self.ID_ALARMS, '&Active alarms',
                                        'Set the visibility of active alarms',
                                        subMenu=self.alarms_submenu)
        self.navigator = wx.MenuItem(submenu, self.ID_TOGGLE_NAVIGATOR,
                        "Show &navigator\t{}".format(config['show_navigator']),
                        "Show or hide the navigator bar", kind=wx.ITEM_CHECK)
        self.gaps = wx.MenuItem(submenu, self.ID_GAPS,
                            "Show &gaps\t{}".format(config['toggle_gaps']),
                            "Show any unallocated time in the shown interval",
                            kind=wx.ITEM_CHECK)
        self.overlaps = wx.MenuItem(submenu, self.ID_OVERLAPS,
                "Show &overlappings\t{}".format(config['toggle_overlappings']),
                "Show time intervals used by more than one event",
                kind=wx.ITEM_CHECK)
        self.autoscroll = wx.MenuItem(submenu, self.ID_AUTOSCROLL,
                                            "Enable a&uto-scroll",
                                            "Auto-scroll to the first ongoing "
                                            "event when refreshing",
                                            kind=wx.ITEM_CHECK)

        self.events.SetBitmap(wx.ArtProvider.GetBitmap('@tasklist',
                                                                wx.ART_MENU))
        self.focus.SetBitmap(wx.ArtProvider.GetBitmap('@focus', wx.ART_MENU))
        self.alarms.SetBitmap(wx.ArtProvider.GetBitmap('@alarms', wx.ART_MENU))

        wxgui_api.insert_menu_right_tab_group(self.events)
        submenu.AppendItem(self.show)
        submenu.AppendItem(self.focus)
        submenu.AppendSeparator()
        submenu.AppendItem(self.alarms)
        submenu.AppendItem(self.navigator)
        submenu.AppendItem(self.gaps)
        submenu.AppendItem(self.overlaps)
        submenu.AppendItem(self.autoscroll)

        wxgui_api.bind_to_menu(self.tasklist.toggle_shown, self.show)
        wxgui_api.bind_to_menu(self._focus, self.focus)
        wxgui_api.bind_to_menu(self._toggle_navigator, self.navigator)
        wxgui_api.bind_to_menu(self._show_gaps, self.gaps)
        wxgui_api.bind_to_menu(self._show_overlappings, self.overlaps)
        wxgui_api.bind_to_menu(self._enable_autoscroll, self.autoscroll)

        wxgui_api.bind_to_reset_menu_items(self._reset_items)
        wxgui_api.bind_to_menu_view_update(self._update_items)

    def _update_items(self, kwargs):
        self.show.Check(check=self.tasklist.is_shown())
        self.focus.Enable(False)
        self.alarms.Enable(False)
        self.navigator.Enable(False)
        self.navigator.Check(check=self.tasklist.navigator.is_shown())
        self.gaps.Enable(False)
        self.gaps.Check(check=self.occview.show_gaps)
        self.overlaps.Enable(False)
        self.overlaps.Check(check=self.occview.show_overlappings)
        self.autoscroll.Enable(False)
        self.autoscroll.Check(check=self.occview.autoscroll.is_enabled())

        self.alarms_submenu.update_items()

        if self.tasklist.is_shown():
            self.focus.Enable()
            self.alarms.Enable()
            self.navigator.Enable()
            self.gaps.Enable()
            self.overlaps.Enable()
            self.autoscroll.Enable()

    def _reset_items(self, kwargs):
        # Re-enable all the actions so they are available for their
        # accelerators
        self.show.Enable()
        self.focus.Enable()
        self.alarms.Enable()
        self.navigator.Enable()
        self.gaps.Enable()
        self.overlaps.Enable()
        self.autoscroll.Enable()

    def _focus(self, event):
        if self.tasklist.is_shown():
            wxgui_api.select_right_nb_tab(self.tasklist.panel)
            self.occview.set_focus()

    def _toggle_navigator(self, event):
        self.tasklist.navigator.toggle_shown()

    def _show_gaps(self, event):
        if self.tasklist.is_shown():
            self.occview.show_gaps = not self.occview.show_gaps
            self.occview.refresh()

    def _show_overlappings(self, event):
        if self.tasklist.is_shown():
            self.occview.show_overlappings = not self.occview.show_overlappings
            self.occview.refresh()

    def _enable_autoscroll(self, event):
        if self.occview.autoscroll.is_enabled():
            self.occview.autoscroll.disable()
        else:
            self.occview.autoscroll.enable()


class AlarmsMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist
        self.occview = tasklist.list_

        self.ID_IN_RANGE = wx.NewId()
        self.ID_AUTO = wx.NewId()
        self.ID_ALL = wx.NewId()

        self.inrange = wx.MenuItem(self, self.ID_IN_RANGE,
                        "Show in &range",
                        "Show only the active alarms in the filtered range",
                        kind=wx.ITEM_RADIO)
        self.auto = wx.MenuItem(self, self.ID_AUTO,
                    "Show &smartly",
                    "Show all the active alarms only if current time is shown",
                    kind=wx.ITEM_RADIO)
        self.all = wx.MenuItem(self, self.ID_ALL,
                        "Show &all",
                        "Always show all the active alarms",
                        kind=wx.ITEM_RADIO)

        self.modes_to_items = {
            'in_range': self.inrange,
            'auto': self.auto,
            'all': self.all,
        }

        self.AppendItem(self.inrange)
        self.AppendItem(self.auto)
        self.AppendItem(self.all)

        wxgui_api.bind_to_menu(self._set_in_range, self.inrange)
        wxgui_api.bind_to_menu(self._set_auto, self.auto)
        wxgui_api.bind_to_menu(self._set_all, self.all)

    def update_items(self):
        self.modes_to_items[self.occview.active_alarms_mode].Check()

    def _set_in_range(self, event):
        if self.tasklist.is_shown():
            self.occview.active_alarms_mode = 'in_range'
            self.occview.refresh()

    def _set_auto(self, event):
        if self.tasklist.is_shown():
            self.occview.active_alarms_mode = 'auto'
            self.occview.refresh()

    def _set_all(self, event):
        if self.tasklist.is_shown():
            self.occview.active_alarms_mode = 'all'
            self.occview.refresh()


class TabContextMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist

        self.navigator_submenu = TabContextNavigatorMenu(tasklist)
        self.alarms_submenu = TabContextAlarmsMenu(tasklist)
        self.snooze_all_submenu = SnoozeAllConfigMenu(tasklist)
        self.export_submenu = TabContextExportMenu(tasklist)

        self.show = wx.MenuItem(self, self.tasklist.viewmenu.ID_SHOW,
                                                                "Hide &panel")
        self.navigator = wx.MenuItem(self, self.tasklist.mainmenu.ID_NAVIGATOR,
                                'Na&vigator', subMenu=self.navigator_submenu)
        self.alarms = wx.MenuItem(self, self.tasklist.viewmenu.ID_ALARMS,
                                '&Active alarms', subMenu=self.alarms_submenu)
        self.gaps = wx.MenuItem(self, self.tasklist.viewmenu.ID_GAPS,
                                            "Show &gaps", kind=wx.ITEM_CHECK)
        self.overlaps = wx.MenuItem(self,
                    self.tasklist.viewmenu.ID_OVERLAPS, "Show &overlappings",
                    kind=wx.ITEM_CHECK)
        self.scroll = wx.MenuItem(self,
                    self.tasklist.mainmenu.ID_SCROLL, "Scro&ll to ongoing")
        self.autoscroll = wx.MenuItem(self,
                                        self.tasklist.viewmenu.ID_AUTOSCROLL,
                                        "Enable a&uto-scroll",
                                        kind=wx.ITEM_CHECK)
        self.snooze_all = wx.MenuItem(self,
                                self.tasklist.mainmenu.ID_SNOOZE_ALL,
                                "S&nooze all", subMenu=self.snooze_all_submenu)
        self.dismiss_all = wx.MenuItem(self,
                        self.tasklist.mainmenu.ID_DISMISS_ALL, "Dis&miss all")
        self.export = wx.MenuItem(self, self.tasklist.mainmenu.ID_EXPORT,
                                'E&xport view', subMenu=self.export_submenu)

        self.show.SetBitmap(wx.ArtProvider.GetBitmap('@close', wx.ART_MENU))
        self.navigator.SetBitmap(wx.ArtProvider.GetBitmap('@navigator',
                                                                wx.ART_MENU))
        self.alarms.SetBitmap(wx.ArtProvider.GetBitmap('@alarms', wx.ART_MENU))
        self.scroll.SetBitmap(wx.ArtProvider.GetBitmap('@movedown',
                                                                wx.ART_MENU))
        self.snooze_all.SetBitmap(wx.ArtProvider.GetBitmap('@alarms',
                                                                  wx.ART_MENU))
        self.dismiss_all.SetBitmap(wx.ArtProvider.GetBitmap('@alarmoff',
                                                                  wx.ART_MENU))
        self.export.SetBitmap(wx.ArtProvider.GetBitmap('@saveas', wx.ART_MENU))

        self.AppendItem(self.show)
        self.AppendSeparator()
        self.AppendItem(self.navigator)
        self.AppendItem(self.alarms)
        self.AppendItem(self.gaps)
        self.AppendItem(self.overlaps)
        self.AppendSeparator()
        self.AppendItem(self.scroll)
        self.AppendItem(self.autoscroll)
        self.AppendSeparator()
        self.AppendItem(self.snooze_all)
        self.AppendItem(self.dismiss_all)
        self.AppendSeparator()
        self.AppendItem(self.export)

    def update(self):
        if len(self.tasklist.list_.get_active_alarms()) > 0:
            self.snooze_all.Enable()
            self.dismiss_all.Enable()
        else:
            self.snooze_all.Enable(False)
            self.dismiss_all.Enable(False)

        self.gaps.Check(check=self.tasklist.list_.show_gaps)
        self.overlaps.Check(check=self.tasklist.list_.show_overlappings)
        self.autoscroll.Check(
                            check=self.tasklist.list_.autoscroll.is_enabled())

        self.navigator_submenu.update_items()
        self.alarms_submenu.update_items()


class TabContextNavigatorMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist

        self.navigator = wx.MenuItem(self,
                self.tasklist.viewmenu.ID_TOGGLE_NAVIGATOR,
                "&Show", "Show or hide the navigator bar", kind=wx.ITEM_CHECK)
        self.previous = wx.MenuItem(self,
                        self.tasklist.mainmenu.navigator_submenu.ID_PREVIOUS,
                        "&Previous page")
        self.next = wx.MenuItem(self,
                            self.tasklist.mainmenu.navigator_submenu.ID_NEXT,
                            "&Next page")
        self.apply = wx.MenuItem(self,
                            self.tasklist.mainmenu.navigator_submenu.ID_APPLY,
                            "&Apply filters")
        self.set = wx.MenuItem(self,
                            self.tasklist.mainmenu.navigator_submenu.ID_SET,
                            "Se&t filters")
        self.reset = wx.MenuItem(self,
                            self.tasklist.mainmenu.navigator_submenu.ID_RESET,
                            "&Reset filters")

        self.previous.SetBitmap(wx.ArtProvider.GetBitmap('@previous',
                                                                  wx.ART_MENU))
        self.next.SetBitmap(wx.ArtProvider.GetBitmap('@next', wx.ART_MENU))
        self.apply.SetBitmap(wx.ArtProvider.GetBitmap('@apply',  wx.ART_MENU))
        self.set.SetBitmap(wx.ArtProvider.GetBitmap('@save', wx.ART_MENU))
        self.reset.SetBitmap(wx.ArtProvider.GetBitmap('@undo', wx.ART_MENU))

        self.AppendItem(self.navigator)
        self.AppendSeparator()
        self.AppendItem(self.previous)
        self.AppendItem(self.next)
        self.AppendItem(self.apply)
        self.AppendItem(self.set)
        self.AppendItem(self.reset)

    def update_items(self):
        self.navigator.Check(check=self.tasklist.navigator.is_shown())


class TabContextAlarmsMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.occview = tasklist.list_

        self.inrange = wx.MenuItem(self,
                                tasklist.viewmenu.alarms_submenu.ID_IN_RANGE,
                                "Show in &range", kind=wx.ITEM_RADIO)
        self.auto = wx.MenuItem(self,
                                tasklist.viewmenu.alarms_submenu.ID_AUTO,
                                "Show &smartly", kind=wx.ITEM_RADIO)
        self.all = wx.MenuItem(self,
                                tasklist.viewmenu.alarms_submenu.ID_ALL,
                                "Show &all", kind=wx.ITEM_RADIO)

        self.modes_to_items = {
            'in_range': self.inrange,
            'auto': self.auto,
            'all': self.all,
        }

        self.AppendItem(self.inrange)
        self.AppendItem(self.auto)
        self.AppendItem(self.all)

    def update_items(self):
        self.modes_to_items[self.occview.active_alarms_mode].Check()


class TabContextExportMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)

        self.json = wx.MenuItem(self, tasklist.mainmenu.export_submenu.ID_JSON,
                                                                    "&JSON...")
        self.tsv = wx.MenuItem(self, tasklist.mainmenu.export_submenu.ID_TSV,
                                                                    "&TSV...")
        self.xml = wx.MenuItem(self, tasklist.mainmenu.export_submenu.ID_XML,
                                                                    "&XML...")

        self.json.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))
        self.tsv.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))
        self.xml.SetBitmap(wx.ArtProvider.GetBitmap('@exporttype',
                                                                wx.ART_MENU))

        self.AppendItem(self.json)
        self.AppendItem(self.tsv)
        self.AppendItem(self.xml)


class ListContextMenu(wx.Menu):
    def __init__(self, tasklist, mainmenu):
        wx.Menu.__init__(self)
        self.tasklist = tasklist
        self.occview = tasklist.list_
        self.mainmenu = mainmenu

        self.snooze_selected_submenu = SnoozeSelectedConfigMenu(tasklist,
                                                            accelerator=False)

        self.find = wx.MenuItem(self, self.mainmenu.ID_FIND,
                                                        "&Find in database")
        self.edit = wx.MenuItem(self, self.mainmenu.ID_EDIT, "&Edit selected")
        self.snooze = wx.MenuItem(self, self.mainmenu.ID_SNOOZE,
                                        "&Snooze selected",
                                        subMenu=self.snooze_selected_submenu)
        self.dismiss = wx.MenuItem(self, self.mainmenu.ID_DISMISS,
                                                           "&Dismiss selected")

        self.find.SetBitmap(wx.ArtProvider.GetBitmap('@find', wx.ART_MENU))
        self.edit.SetBitmap(wx.ArtProvider.GetBitmap('@edit', wx.ART_MENU))
        self.snooze.SetBitmap(wx.ArtProvider.GetBitmap('@alarms', wx.ART_MENU))
        self.dismiss.SetBitmap(wx.ArtProvider.GetBitmap('@alarmoff',
                                                                  wx.ART_MENU))

        self.AppendItem(self.find)
        self.AppendItem(self.edit)
        self.AppendSeparator()
        self.AppendItem(self.snooze)
        self.AppendItem(self.dismiss)

    def update(self):
        self.find.Enable(False)
        self.edit.Enable(False)
        self.snooze.Enable(False)
        self.dismiss.Enable(False)

        sel = self.occview.listview.GetFirstSelected()

        while sel > -1:
            item = self.occview.occs[self.occview.listview.GetItemData(sel)]

            canbreak = 0

            # Check item is not a gap or an overlapping
            if item.get_filename() is not None:
                self.find.Enable()
                self.edit.Enable()
                canbreak += 1

            if item.get_alarm() is False:
                self.snooze.Enable()
                self.dismiss.Enable()
                canbreak += 1

            if canbreak > 1:
                break

            sel = self.occview.listview.GetNextSelected(sel)


class _SnoozeConfigMenu(wx.Menu):
    def __init__(self, tasklist):
        wx.Menu.__init__(self)
        self.tasklist = tasklist
        self.snoozetimes = {}
        self.ID_SNOOZE_FOR = wx.NewId()

        # Using a set here to remove any duplicates would lose the order of
        # the times
        snooze_times = coreaux_api.get_plugin_configuration('wxtasklist')[
                                                     'snooze_times'].split(' ')

        for stime in snooze_times:
            ID_SNOOZE_FOR_N = wx.NewId()
            time = int(stime) * 60
            number, unit = TimeSpanCtrl.compute_widget_values(time)
            # Duplicate time values are not supported, just make sure they
            # don't crash the application
            self.snoozetimes[time] = self.Append(ID_SNOOZE_FOR_N, "For " +
                                                      str(number) + ' ' + unit)
            wxgui_api.bind_to_menu(self._snooze_for_loop(time),
                                                        self.snoozetimes[time])

        self.AppendSeparator()
        self.snoozefor = self.Append(self.ID_SNOOZE_FOR, "&For...")

        wxgui_api.bind_to_menu(self._snooze_for_custom, self.snoozefor)

    def _snooze_for_loop(self, time):
        return lambda event: self._snooze_for(time)

    def _snooze_for(self, time):
        if core_api.block_databases():
            tab = wxgui_api.get_selected_right_nb_tab()

            if tab is self.tasklist.panel:
                alarmsd = self.get_alarms()

                if len(alarmsd) > 0:
                    organism_alarms_api.snooze_alarms(alarmsd, time)
                    # Let the alarm off event update the tasklist

            core_api.release_databases()

    def _snooze_for_custom(self, event):
        if core_api.block_databases():
            tab = wxgui_api.get_selected_right_nb_tab()

            if tab is self.tasklist.panel:
                alarmsd = self.get_alarms()

                if len(alarmsd) > 0:
                    dlg = SnoozeDialog()

                    if dlg.ShowModal() == wx.ID_OK:
                        organism_alarms_api.snooze_alarms(alarmsd,
                                                                dlg.get_time())
                        # Let the alarm off event update the tasklist

                    # Unlike MessageDialog, a Dialog needs to be destroyed
                    # explicitly
                    dlg.Destroy()

            core_api.release_databases()


class SnoozeDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, parent=wxgui_api.get_main_frame(),
                                                title="Snooze configuration")

        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vsizer)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        icon = wx.StaticBitmap(self, bitmap=wx.ArtProvider.GetBitmap(
                                                '@alarms', wx.ART_CMN_DIALOG))
        hsizer.Add(icon, flag=wx.ALIGN_TOP | wx.RIGHT, border=12)

        ssizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, label='Snooze for:')
        ssizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=4)

        self.number = NarrowSpinCtrl(self, min=1, max=999,
                                                        style=wx.SP_ARROW_KEYS)
        self.number.SetValue(5)
        ssizer.Add(self.number, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                                                                    border=4)

        self.unit = wx.ComboBox(self, value='minutes',
                                choices=('minutes', 'hours', 'days', 'weeks'),
                                style=wx.CB_READONLY)
        ssizer.Add(self.unit, flag=wx.ALIGN_CENTER_VERTICAL)

        hsizer.Add(ssizer, flag=wx.ALIGN_TOP)

        vsizer.Add(hsizer, flag=wx.ALIGN_CENTER | wx.ALL, border=12)

        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vsizer.Add(buttons,
                        flag=wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                        border=12)

        self.Fit()

    def get_time(self):
        mult = {'minutes': 60,
                'hours': 3600,
                'days': 86400,
                'weeks': 604800}
        return self.number.GetValue() * mult[self.unit.GetValue()]


class SnoozeSelectedConfigMenu(_SnoozeConfigMenu):
    def __init__(self, tasklist, accelerator=True):
        _SnoozeConfigMenu.__init__(self, tasklist)
        config = coreaux_api.get_plugin_configuration('wxtasklist')(
                                                        'Shortcuts')('Items')
        accel = "\t{}".format(config['snooze_selected']) if accelerator else ""
        self.snoozefor.SetText(self.snoozefor.GetText() + accel)

    def get_alarms(self):
        return self.tasklist.list_.get_selected_active_alarms()


class SnoozeAllConfigMenu(_SnoozeConfigMenu):
    def __init__(self, tasklist, accelerator=True):
        _SnoozeConfigMenu.__init__(self, tasklist)
        config = coreaux_api.get_plugin_configuration('wxtasklist')(
                                                        'Shortcuts')('Items')
        accel = "\t{}".format(config['snooze_all']) if accelerator else ""
        self.snoozefor.SetText(self.snoozefor.GetText() + accel)

    def get_alarms(self):
        # Note that "all" means all the visible active alarms; some may be
        # hidden in the current view
        return self.tasklist.list_.get_active_alarms()


