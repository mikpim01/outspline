# Organism - A highly modular and extensible outliner.
# Copyright (C) 2011-2013 Dario Giovannetti <dev@dariogiovannetti.net>
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

import wx


class HourCtrl():
    panel = None
    hourctrl = None
    minutectrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.hourctrl = wx.SpinCtrl(self.panel, min=0, max=23, size=(40, 21),
                                            style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        box.Add(self.hourctrl, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)

        slabel = wx.StaticText(self.panel, label=':')
        box.Add(slabel, flag=wx.ALIGN_CENTER_VERTICAL)

        self.minutectrl = wx.SpinCtrl(self.panel, min=0, max=59, size=(40, 21),
                                            style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        box.Add(self.minutectrl, flag=wx.ALIGN_CENTER_VERTICAL)

    def set_values(self, hour, minute):
        self.hourctrl.SetValue(hour)
        self.minutectrl.SetValue(minute)

    def get_main_panel(self):
        return self.panel

    def get_hour(self):
        return self.hourctrl.GetValue()

    def get_minute(self):
        return self.minutectrl.GetValue()

    def get_relative_time(self):
        hour = self.hourctrl.GetValue()
        minute = self.minutectrl.GetValue()

        return hour * 3600 + minute * 60


class DateHourCtrl():
    panel = None
    datectrl = None
    hourctrl = None
    minutectrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.datectrl = wx.DatePickerCtrl(self.panel, size=(-1, 21))
        box.Add(self.datectrl, flag=wx.ALIGN_CENTER_VERTICAL)

        self.hourctrl = wx.SpinCtrl(self.panel, min=0, max=23, size=(40, 21),
                                            style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        box.Add(self.hourctrl, flag=wx.ALIGN_CENTER_VERTICAL |
                                            wx.ALIGN_RIGHT | wx.LEFT, border=12)

        slabel = wx.StaticText(self.panel, label=':')
        box.Add(slabel, flag=wx.ALIGN_CENTER_VERTICAL)

        self.minutectrl = wx.SpinCtrl(self.panel, min=0, max=59, size=(40, 21),
                                            style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        box.Add(self.minutectrl, flag=wx.ALIGN_CENTER_VERTICAL)

    def set_values(self, year, month, day, hour, minute):
        sdate = wx.DateTime()
        sdate.Set(year=year, month=month, day=day)
        self.datectrl.SetValue(sdate)

        self.hourctrl.SetValue(hour)
        self.minutectrl.SetValue(minute)

    def get_main_panel(self):
        return self.panel

    def get_unix_time(self):
        date = self.datectrl.GetValue().GetTicks()
        hour = self.hourctrl.GetValue()
        minute = self.minutectrl.GetValue()

        return date + hour * 3600 + minute * 60


class TimeSpanCtrl():
    panel = None
    numberctrl = None
    unitctrl = None

    def __init__(self, parent, min_number):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.numberctrl = wx.SpinCtrl(self.panel, min=min_number, max=99,
                                          size=(40, 21), style=wx.SP_ARROW_KEYS)
        box.Add(self.numberctrl, flag=wx.ALIGN_CENTER_VERTICAL)

        self.unitctrl = wx.ComboBox(self.panel, value='minutes', size=(100, 21),
                                   choices=('minutes', 'hours', 'days', 'weeks',
                                       'months', 'years'), style=wx.CB_READONLY)
        box.Add(self.unitctrl, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT |
                                                             wx.LEFT, border=12)

    def set_values(self, number, unit):
        self.numberctrl.SetValue(number)
        self.unitctrl.Select(self.unitctrl.FindString(unit))

    def get_main_panel(self):
        return self.panel

    def get_time_span(self):
        number = self.numberctrl.GetValue()
        unit = self.unitctrl.GetValue()

        return self._compute_relative_time(number, unit)

    def get_number(self):
        return self.numberctrl.GetValue()

    def get_unit(self):
        return self.unitctrl.GetValue()

    @staticmethod
    def _compute_relative_time(number, unit):
        mult = {'minutes': 60,
                'hours': 3600,
                'days': 86400,
                'weeks': 604800,
                'months': 2592000,
                'years': 31536000}

        return number * mult[unit]

    @staticmethod
    def _compute_widget_values(diff):
        adiff = abs(diff)

        if adiff > 0:
            for (number, unit) in ((31536000, 'years'),
                                   (2592000, 'months'),
                                   (604800, 'weeks'),
                                   (86400, 'days'),
                                   (3600, 'hours'),
                                   (60, 'minutes')):
                if adiff % number == 0:
                    return (adiff // number, unit)
            else:
                return (adiff // 60, 'minutes')
        else:
            return (0, 'minutes')


class WidgetChoiceCtrl():
    panel = None
    box = None
    choicectrl = None
    activectrl = None

    def __init__(self, parent, choices, initchoice, rborder):
        self.panel = wx.Panel(parent)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(self.box)

        self.choices = choices

        self.choicectrl = wx.Choice(self.panel, size=(-1, 21),
                                      choices=[choice[0] for choice in choices])
        self.choicectrl.Select(initchoice)
        self.box.Add(self.choicectrl, flag=wx.ALIGN_CENTER_VERTICAL |
                                           wx.EXPAND | wx.RIGHT, border=rborder)
        # Do not call self._update here, in fact classcall will very likely have
        # to use this very object, which at this stage hasn;'t been instantiated
        # yet; call self.force_update after the object is created, instead

        self.panel.Bind(wx.EVT_CHOICE, self._update, self.choicectrl)

    def _update(self, event=None):
        # self.activectrl may not exist yet
        if self.activectrl:
            self.activectrl.Destroy()

        classcall = self.choices[self.choicectrl.GetSelection()][1]

        if classcall:
            self.activectrl = classcall()

        # self.activectrl is None if sel == 0
        if self.activectrl:
            self.box.Add(self.activectrl)

        # self.panel.Layout() isn't enough...
        self.panel.GetParent().Layout()

    def force_update(self):
        self._update()

    def set_choice_min_width(self, width):
        minh = self.choicectrl.GetMinHeight()
        self.choicectrl.SetMinSize((width, minh))

    def get_main_panel(self):
        return self.panel

    def get_selection(self):
        return self.choicectrl.GetSelection()

    def get_choice_width(self):
        return self.choicectrl.GetSizeTuple()[0]