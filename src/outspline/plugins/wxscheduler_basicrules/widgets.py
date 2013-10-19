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


class WeekDayCtrl():
    choices = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                                                          'Saturday', 'Sunday')
    panel = None
    dayctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)

        self.dayctrl = wx.ComboBox(self.panel, value='Monday', size=(100, 21),
                                    choices=self.choices, style=wx.CB_READONLY)

    def set_day(self, day):
        self.dayctrl.Select(self.dayctrl.FindString(day))

    def get_main_panel(self):
        return self.panel

    def get_day(self):
        return self.dayctrl.GetValue()

    def get_relative_unix_time(self):
        # Day 1 in Unix time was a Thursday
        return {
            'Thursday': 0,
            'Friday': 86400,
            'Saturday': 172800,
            'Sunday': 259200,
            'Monday': 345600,
            'Tuesday': 432000,
            'Wednesday': 518400,
        }[self.get_day()]

    @classmethod
    def _compute_widget_day(cls, timew):
        # Any check that 0 <= number <= 6 should be done outside of here
        return cls.choices[timew]

    @classmethod
    def _compute_day_label(cls, day):
        return cls.choices.index(day)


class MonthDayCtrl():
    choices = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
               '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th',
               '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th',
               '26th', '27th', '28th', '29th', '30th', '31st')
    # Defining value and size here lets derive other classes from this one more
    # easily
    value = '1st'
    size = (60, 21)
    panel = None
    dayctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)

        self.dayctrl = wx.ComboBox(self.panel, value=self.value,
                    size=self.size, choices=self.choices, style=wx.CB_READONLY)

    def set_day(self, day):
        self.dayctrl.Select(day - 1)

    def get_main_panel(self):
        return self.panel

    def get_day(self):
        return int(self.dayctrl.GetValue()[:-2])

    def get_relative_time(self):
        return self.get_day() * 86400 - 86400

    @classmethod
    def _compute_day_label(cls, day):
        return cls.choices[day - 1]


class MonthInverseDayCtrl(MonthDayCtrl):
    choices = ['last', ] + [d + ' to last' for d in ('2nd', '3rd', '4th',
               '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th',
               '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th',
               '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th',
               '29th', '30th', '31st')]
    value = 'last'
    size = (110, 21)

    def get_day(self):
        try:
            return int(self.dayctrl.GetValue()[:-10])
        except ValueError:
            return 1

    @classmethod
    def _compute_day_label(cls, day):
        return cls.choices[day - 1].replace(' ', '-')


class MonthDaySafeCtrl(MonthDayCtrl):
    choices = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
               '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th',
               '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th',
               '26th', '27th', '28th')


class MonthInverseDaySafeCtrl(MonthInverseDayCtrl):
    choices = ['last', ] + [d + ' to last' for d in ('2nd', '3rd', '4th',
               '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th',
               '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th',
               '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th')]


class MonthWeekdayNumberCtrl(MonthDayCtrl):
    choices = ('1st', '2nd', '3rd', '4th', '5th')


class MonthInverseWeekdayNumberCtrl(MonthInverseDayCtrl):
    choices = ['last', ] + [d + ' to last' for d in ('2nd', '3rd', '4th',
                                                                        '5th')]


class MonthWeekdayCtrl():
    panel = None
    mwnctrl = MonthWeekdayNumberCtrl
    numberctrl = None
    dayctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.numberctrl = self.mwnctrl(self.panel)
        box.Add(self.numberctrl.get_main_panel(),
                                                 flag=wx.ALIGN_CENTER_VERTICAL)

        self.dayctrl = WeekDayCtrl(self.panel)
        box.Add(self.dayctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL |
                                           wx.ALIGN_RIGHT | wx.LEFT, border=12)

    def set_values(self, number, day):
        self.numberctrl.set_day(number)
        self.dayctrl.set_day(day)

    def get_main_panel(self):
        return self.panel

    def get_weekday_number(self):
        return self.numberctrl.get_day()

    def get_weekday(self):
        return self.dayctrl.get_day()

    @classmethod
    def _compute_weekday_number_label(cls, number):
        return cls.mwnctrl._compute_day_label(number)

    @staticmethod
    def _compute_weekday_label(day):
        return WeekDayCtrl._compute_day_label(day)

    @staticmethod
    def _compute_widget_weekday(day):
        return WeekDayCtrl._compute_widget_day(day)


class MonthInverseWeekdayCtrl(MonthWeekdayCtrl):
    mwnctrl = MonthInverseWeekdayNumberCtrl



class DateHourCtrl():
    panel = None
    datectrl = None
    hourctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.datectrl = wx.DatePickerCtrl(self.panel, size=(-1, 21))
        box.Add(self.datectrl, flag=wx.ALIGN_CENTER_VERTICAL)

        self.hourctrl = HourCtrl(self.panel)
        box.Add(self.hourctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL |
                                           wx.ALIGN_RIGHT | wx.LEFT, border=12)

    def set_values(self, year, month, day, hour, minute):
        sdate = wx.DateTime()
        sdate.Set(year=year, month=month, day=day)
        self.datectrl.SetValue(sdate)

        self.hourctrl.set_values(hour, minute)

    def get_main_panel(self):
        return self.panel

    def get_unix_time(self):
        date = self.datectrl.GetValue().GetTicks()
        hour = self.hourctrl.get_hour()
        minute = self.hourctrl.get_minute()

        return date + hour * 3600 + minute * 60

    def get_year(self):
        return self.datectrl.GetValue().GetYear()

    def get_month(self):
        return self.datectrl.GetValue().GetMonth()

    def get_day(self):
        return self.datectrl.GetValue().GetDay()

    def get_hour(self):
        return self.hourctrl.get_hour()

    def get_minute(self):
        return self.hourctrl.get_minute()

    @staticmethod
    def _compute_month_label(month):
        # Hardcode the names since only English is supported for the moment
        # anyway
        return ('January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December')[
                                                                     month - 1]


class WeekDayHourCtrl():
    panel = None
    dayctrl = None
    hourctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.dayctrl = WeekDayCtrl(self.panel)
        box.Add(self.dayctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL)

        self.hourctrl = HourCtrl(self.panel)
        box.Add(self.hourctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL |
                                           wx.ALIGN_RIGHT | wx.LEFT, border=12)

    def set_values(self, day, hour, minute):
        self.dayctrl.set_day(day)
        self.hourctrl.set_values(hour, minute)

    def get_main_panel(self):
        return self.panel

    def get_day(self):
        return self.dayctrl.get_day()

    def get_hour(self):
        return self.hourctrl.get_hour()

    def get_minute(self):
        return self.hourctrl.get_minute()

    def get_relative_time(self):
        return self.hourctrl.get_relative_time()

    def get_relative_unix_week_time(self):
        rday = self.dayctrl.get_relative_unix_time()
        rhour = self.hourctrl.get_relative_time()

        return rday + rhour

    @staticmethod
    def _compute_widget_day(timew):
        return WeekDayCtrl._compute_widget_day(timew)


class MonthDayHourCtrl():
    # Defining mdctrl here lets derive other classes from this one more easily
    mdctrl = MonthDayCtrl
    panel = None
    dayctrl = None
    hourctrl = None

    def __init__(self, parent):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.dayctrl = self.mdctrl(self.panel)
        box.Add(self.dayctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL)

        self.hourctrl = HourCtrl(self.panel)
        box.Add(self.hourctrl.get_main_panel(), flag=wx.ALIGN_CENTER_VERTICAL |
                                           wx.ALIGN_RIGHT | wx.LEFT, border=12)

    def set_values(self, day, hour, minute):
        self.dayctrl.set_day(day)
        self.hourctrl.set_values(hour, minute)

    def get_main_panel(self):
        return self.panel

    def get_day(self):
        return self.dayctrl.get_day()

    def get_hour(self):
        return self.hourctrl.get_hour()

    def get_minute(self):
        return self.hourctrl.get_minute()

    def get_relative_time(self):
        rday = self.dayctrl.get_relative_time()
        rhour = self.hourctrl.get_relative_time()

        return rday + rhour

    @classmethod
    def _compute_day_label(cls, day):
        return cls.mdctrl._compute_day_label(day)


class MonthDayHourSafeCtrl(MonthDayHourCtrl):
    mdctrl = MonthDaySafeCtrl


class MonthInverseDayHourCtrl(MonthDayHourCtrl):
    mdctrl = MonthInverseDayCtrl

    def get_relative_time(self):
        rday = self.dayctrl.get_relative_time()
        rhour = self.hourctrl.get_relative_time()

        return rday + 86400 - rhour


class MonthInverseDayHourSafeCtrl(MonthInverseDayHourCtrl):
    mdctrl = MonthInverseDaySafeCtrl


class MonthWeekdayHourCtrl(MonthDayHourCtrl):
    mdctrl = MonthWeekdayCtrl

    def set_values(self, number, weekday, hour, minute):
        self.dayctrl.set_values(number, weekday)
        self.hourctrl.set_values(hour, minute)

    def get_relative_time(self):
        return self.hourctrl.get_relative_time()

    def get_weekday_number(self):
        return self.dayctrl.get_weekday_number()

    def get_weekday(self):
        return self.dayctrl.get_weekday()

    @classmethod
    def _compute_weekday_number_label(cls, number):
        return cls.mdctrl._compute_weekday_number_label(number)

    @classmethod
    def _compute_weekday_label(cls, day):
        return cls.mdctrl._compute_weekday_label(day)

    @classmethod
    def _compute_widget_weekday(cls, day):
        return cls.mdctrl._compute_widget_weekday(day)


class MonthInverseWeekdayHourCtrl(MonthWeekdayHourCtrl):
    mdctrl = MonthInverseWeekdayCtrl


class TimeSpanCtrl():
    panel = None
    numberctrl = None
    unitctrl = None

    def __init__(self, parent, min_number):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.numberctrl = wx.SpinCtrl(self.panel, min=min_number, max=999,
                                         size=(48, 21), style=wx.SP_ARROW_KEYS)
        box.Add(self.numberctrl, flag=wx.ALIGN_CENTER_VERTICAL)

        self.unitctrl = wx.ComboBox(self.panel, value='minutes',
                 size=(100, 21), choices=('minutes', 'hours', 'days', 'weeks'),
                                                          style=wx.CB_READONLY)
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
                'weeks': 604800}

        return number * mult[unit]

    @staticmethod
    def _compute_widget_values(diff):
        adiff = abs(diff)

        if adiff > 0:
            for (number, unit) in ((604800, 'weeks'),
                                   (86400, 'days'),
                                   (3600, 'hours'),
                                   (60, 'minutes')):
                if adiff % number == 0:
                    return (adiff // number, unit)
            else:
                return (adiff // 60, 'minutes')
        else:
            return (0, 'minutes')


class MultipleChoiceCtrl():
    panel = None
    cbctrls = None

    def __init__(self, parent, choices):
        self.panel = wx.Panel(parent)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(box)

        self.cbctrls = []

        for i, c in enumerate(choices):
            self.cbctrls.append(wx.CheckBox(self.panel))
            box.Add(self.cbctrls[i], flag=wx.ALIGN_CENTER_VERTICAL)

            label = wx.StaticText(self.panel, label=c)
            box.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT |
                                                            wx.RIGHT, border=8)

    def get_main_panel(self):
        return self.panel

    def set_values(self, values):
        for v, ctrl in enumerate(self.cbctrls):
            ctrl.SetValue(v + 1 in values)

    def get_values(self):
        return [v + 1 for v, ctrl in enumerate(self.cbctrls) if ctrl.GetValue()
                                                                              ]


class WeekdaysCtrl(MultipleChoiceCtrl):
    # Hardcode the names since only English is supported for the moment anyway
    dnames = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

    def __init__(self, parent):
        MultipleChoiceCtrl.__init__(self, parent, self.dnames)

    def set_days(self, days):
        return self.set_values(days)

    def get_days(self):
        return self.get_values()

    @classmethod
    def _compute_day_name(cls, day):
        return cls.dnames[day - 1]


class MonthsCtrl(MultipleChoiceCtrl):
    # Hardcode the names since only English is supported for the moment anyway
    mnames = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                                                           'Oct', 'Nov', 'Dec')

    def __init__(self, parent):
        MultipleChoiceCtrl.__init__(self, parent, self.mnames)

    def set_months(self, months):
        return self.set_values(months)

    def get_months(self):
        return self.get_values()

    @classmethod
    def _compute_month_name(cls, month):
        return cls.mnames[month - 1]


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