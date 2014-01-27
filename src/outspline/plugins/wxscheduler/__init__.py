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

import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from outspline.coreaux_api import Event
import outspline.extensions.organism_api as organism_api
import outspline.interfaces.wxgui_api as wxgui_api

init_rules_list_event = Event()
insert_rule_event = Event()
create_rule_event = Event()
edit_rule_event = Event()
choose_rule_event = Event()
check_editor_event = Event()

items = {}


class Scheduler():
    filename = None
    id_ = None
    fpanel = None
    panel = None
    rule_list = None
    rule_editor = None

    def __init__(self, filename, id_):
        self.filename = filename
        self.id_ = id_

        self.fpanel = wxgui_api.add_plugin_to_editor(filename, id_,
                                                            'Schedule rules')

    def post_init(self):
        self.panel = wx.Panel(self.fpanel)
        box = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(box)

        self.rule_list = RuleList(self, self.filename, self.id_)
        self.rule_editor = RuleEditor(self, self.filename, self.id_)
        self.rule_list.post_init()
        self.rule_editor.post_init()

        box.Add(self.rule_list.panel, flag=wx.EXPAND | wx.BOTTOM, border=4)
        box.Add(self.rule_editor.panel, flag=wx.EXPAND | wx.BOTTOM, border=4)

        wxgui_api.add_window_to_plugin(self.filename, self.id_, self.fpanel,
                                                                    self.panel)
        self.resize()

        # Must be done *after* resizing
        if not self.rule_list.rules:
            self.collapse_foldpanel()

    def resize(self):
        # This is necessary for letting the fold panel adapt to the variable
        # height
        self.panel.SetMinSize((-1, -1))
        self.panel.Fit()
        wxgui_api.expand_panel(self.filename, self.id_, self.fpanel)
        wxgui_api.resize_foldpanelbar(self.filename, self.id_)

    def collapse_foldpanel(self):
        wxgui_api.collapse_panel(self.filename, self.id_, self.fpanel)
        wxgui_api.resize_foldpanelbar(self.filename, self.id_)

    def show_list(self):
        self.rule_editor.panel.Show(False)
        self.rule_list.panel.Show()
        self.resize()

    def show_editor(self):
        self.rule_list.panel.Show(False)
        self.rule_editor.panel.Show()
        self.resize()

    @staticmethod
    def make_itemid(filename, id_):
        return '_'.join((filename, str(id_)))


class RuleList():
    parent = None
    filename = None
    id_ = None
    panel = None
    listview = None
    origrules = None
    rules = None
    mrules = None
    mmode = None
    button_up = None
    button_remove = None
    button_add = None
    button_down = None
    button_edit = None

    def __init__(self, parent, filename, id_):
        self.parent = parent
        self.filename = filename
        self.id_ = id_
        self.panel = wx.Panel(parent.panel)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(hbox)

        # Do not allow multiple selections, so that it's possible to move rules
        # up and down
        # Initialize with a small size so that it will expand properly in the
        # sizer
        self.listview = wx.ListView(self.panel, size=(10, 10),
                    style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL)
        self.listview.InsertColumn(0, 'Rules')
        hbox.Add(self.listview, 1, flag=wx.EXPAND | wx.RIGHT, border=4)

        self.rules = []

        self.mmode = 'append'

        pgrid = wx.GridSizer(3, 2, 4, 4)

        self.button_up = wx.Button(self.panel, label='Move up', size=(-1, 24),
                                                            style=wx.BU_LEFT)
        pgrid.Add(self.button_up)

        pgrid.AddSpacer(1)

        self.button_remove = wx.Button(self.panel, label='Remove',
                                            size=(-1, 24), style=wx.BU_LEFT)
        pgrid.Add(self.button_remove)

        self.button_add = wx.Button(self.panel, label='Add...', size=(-1, 24),
                                                            style=wx.BU_LEFT)
        pgrid.Add(self.button_add)

        self.button_down = wx.Button(self.panel, label='Move down',
                                            size=(-1, 24), style=wx.BU_LEFT)
        pgrid.Add(self.button_down)

        self.button_edit = wx.Button(self.panel, label='Edit...',
                                            size=(-1, 24), style=wx.BU_LEFT)
        pgrid.Add(self.button_edit)

        self.update_buttons()

        hbox.Add(pgrid, flag=wx.EXPAND)

        self.panel.Bind(wx.EVT_BUTTON, self.add_rule, self.button_add)
        self.panel.Bind(wx.EVT_BUTTON, self.edit_rule, self.button_edit)
        self.panel.Bind(wx.EVT_BUTTON, self.remove_rule, self.button_remove)
        self.panel.Bind(wx.EVT_BUTTON, self.move_rule_up, self.button_up)
        self.panel.Bind(wx.EVT_BUTTON, self.move_rule_down, self.button_down)

        self.listview.Bind(wx.EVT_LIST_ITEM_SELECTED, self._update_buttons)
        self.listview.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._update_buttons)
        self.listview.Bind(wx.EVT_LIST_DELETE_ITEM, self._update_buttons)

        wxgui_api.bind_to_apply_editor(self.handle_apply)
        wxgui_api.bind_to_check_editor_modified_state(
                                             self.handle_check_editor_modified)
        wxgui_api.bind_to_close_editor(self.handle_close)

    def post_init(self):
        oprules = organism_api.get_item_rules(self.filename, self.id_)

        for rule in oprules:
            insert_rule_event.signal(filename=self.filename, id_=self.id_,
                                                                    rule=rule)

        self.refresh_mod_state()

        init_rules_list_event.signal(filename=self.filename, id_=self.id_)

    def _update_buttons(self, event):
        self.update_buttons()

    def update_buttons(self):
        if self.listview.GetSelectedItemCount():
            self.button_edit.Enable()
            self.button_remove.Enable()
            self.button_up.Enable()
            self.button_down.Enable()
        else:
            self.button_edit.Enable(False)
            self.button_remove.Enable(False)
            self.button_up.Enable(False)
            self.button_down.Enable(False)

    def handle_apply(self, kwargs):
        if kwargs['filename'] == self.filename and kwargs['id_'] == self.id_ \
                                                        and self.is_modified():
            organism_api.update_item_rules(self.filename, self.id_,
                            self.rules, kwargs['group'], kwargs['description'])
            self.refresh_mod_state()

    def handle_check_editor_modified(self, kwargs):
        if kwargs['filename'] == self.filename and kwargs['id_'] == self.id_ \
                                                        and self.is_modified():
            wxgui_api.set_editor_modified(self.filename, self.id_)

    def handle_close(self, kwargs):
        if kwargs['filename'] == self.filename and kwargs['id_'] == self.id_:
            # It's necessary to explicitly unbind the handlers, otherwise this
            # object will never be garbage-collected due to circular
            # references, and the automatic unbinding won't work
            wxgui_api.bind_to_apply_editor(self.handle_apply, False)
            wxgui_api.bind_to_check_editor_modified_state(
                                      self.handle_check_editor_modified, False)
            wxgui_api.bind_to_close_editor(self.handle_close, False)

    def is_modified(self):
        return self.origrules != self.rules

    def refresh_mod_state(self):
        self.origrules = self.rules[:]

    def add_rule(self, event):
        self.mrules = {}
        self.mmode = 'append'

        create_rule_event.signal(filename=self.filename, id_=self.id_,
                                    parent=self.parent.rule_editor.scwindow)

        self.parent.show_editor()

    def edit_rule(self, event):
        index = self.listview.GetFirstSelected()

        if index != -1:
            self.mrules = self.rules[index]
            self.mmode = index

            edit_rule_event.signal(filename=self.filename, id_=self.id_,
                    parent=self.parent.rule_editor.scwindow, ruled=self.mrules)

        self.parent.show_editor()

    def remove_rule(self, event):
        index = self.listview.GetFirstSelected()

        if index != -1:
            self.listview.DeleteItem(index)
            self.listview.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            del self.rules[index]

    def move_rule_up(self, event):
        index = self.listview.GetFirstSelected()

        if index not in (-1, 0):
            self.listview.InsertStringItem(index - 1,
                                            self.listview.GetItemText(index))
            self.listview.DeleteItem(index + 1)
            self.listview.Select(index - 1)

            rule = self.rules.pop(index)
            self.listview.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.rules.insert(index - 1, rule)

    def move_rule_down(self, event):
        index = self.listview.GetFirstSelected()

        if index not in (-1, self.listview.GetItemCount() - 1):
            self.listview.InsertStringItem(index + 2,
                                            self.listview.GetItemText(index))
            self.listview.DeleteItem(index)
            # Select *after* DeleteItem because DeleteItem deselects the
            # currently selected item (this doesn't happen in move_rule_up)
            self.listview.Select(index + 1)

            rule = self.rules.pop(index)
            self.listview.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.rules.insert(index + 1, rule)

    def insert_rule(self, ruled, label):
        if self.mmode == 'append':
            self.listview.InsertStringItem(sys.maxint, label)

            # append relies on the use of sys.maxint in InsertStringItem
            self.rules.append(ruled)

        elif isinstance(self.mmode, int):
            self.listview.DeleteItem(self.mmode)
            self.listview.InsertStringItem(self.mmode, label)

            self.rules[self.mmode] = ruled

        self.listview.SetColumnWidth(0, wx.LIST_AUTOSIZE)


class RuleEditor():
    parent = None
    filename = None
    id_ = None
    panel = None
    choice = None
    scwindow = None
    scbox = None
    rmaker_ref = None
    mpanel = None

    def __init__(self, parent, filename, id_):
        self.parent = parent
        self.filename = filename
        self.id_ = id_
        self.panel = wx.Panel(parent.panel)

        self.panel.Show(False)

        mbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(mbox)

        mbox2 = wx.BoxSizer(wx.HORIZONTAL)
        mbox.Add(mbox2, flag=wx.EXPAND | wx.BOTTOM, border=4)

        self.choice = wx.Choice(self.panel, size=(-1, 24), choices=())
        mbox2.Add(self.choice, 1, flag=wx.EXPAND)

        button_cancel = wx.Button(self.panel, label='Cancel', size=(60, 24))
        mbox2.Add(button_cancel, flag=wx.LEFT | wx.RIGHT, border=4)

        button_ok = wx.Button(self.panel, label='OK', size=(60, 24))
        mbox2.Add(button_ok)

        self.scwindow = wx.ScrolledWindow(self.panel, style=wx.BORDER_NONE)
        self.scwindow.SetScrollRate(20, 20)
        self.scbox = wx.BoxSizer(wx.VERTICAL)
        self.scwindow.SetSizer(self.scbox)
        mbox.Add(self.scwindow, 1, flag=wx.EXPAND)

        self.panel.Bind(wx.EVT_CHOICE, self.choose_rule, self.choice)
        self.panel.Bind(wx.EVT_BUTTON, self.cancel, button_cancel)
        self.panel.Bind(wx.EVT_BUTTON, self.check, button_ok)

    def post_init(self):
        self.choice.SetSelection(0)

    def display_rule(self, description, rule):
        self.choice.Append(description, clientData=rule)

    def select_rule(self, interface_name):
        for i in range(self.choice.GetCount()):
            if self.choice.GetClientData(i) == interface_name:
                self.choice.SetSelection(i)
                break

    def init_rule(self, rule):
        self.rmaker_ref = rule

    def choose_rule(self, event):
        choose_rule_event.signal(filename=self.filename, id_=self.id_,
                            parent=self.scwindow, choice=event.GetClientData(),
                            ruled=self.parent.rule_list.mrules)

    def change_rule(self, window):
        if self.mpanel:
            self.scbox.Clear(True)

        self.mpanel = window
        self.scbox.Add(self.mpanel, 1, flag=wx.EXPAND)
        # Do not allocate space for the horizontal scroll bar, otherwise
        # when/if the user expands the window and the scroll bar disappears,
        # an ugly gap would be left shown in place of the scroll bar, unless
        # some complicated size-updating algorithm is used (which is not the
        # case of this application)
        self.scwindow.SetMinSize((-1,
                                self.mpanel.GetBestVirtualSize().GetHeight()))
        self.parent.resize()

    def cancel(self, event):
        self.parent.show_list()

    def check(self, event):
        check_editor_event.signal(filename=self.filename, id_=self.id_,
                    rule=self.choice.GetClientData(self.choice.GetSelection()),
                    object_=self.rmaker_ref)

    def apply_(self, ruled, label):
        self.parent.rule_list.insert_rule(ruled, label)
        self.parent.show_list()


def handle_open_editor(kwargs):
    filename = kwargs['filename']
    id_ = kwargs['id_']

    if filename in organism_api.get_supported_open_databases():
        itemid = Scheduler.make_itemid(filename, id_)

        global items
        items[itemid] = Scheduler(filename, id_)

        items[itemid].post_init()


def main():
    wxgui_api.bind_to_open_editor(handle_open_editor)
