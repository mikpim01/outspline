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

import time as _time
import wx

import organism.plugins.wxscheduler_api as wxscheduler_api

_RULE_NAME = 'except_once'
_RULE_DESC = 'Except from date until date'


class Rule():
    mwidgets = None

    def __init__(self, kwargs):
        parent = kwargs['parent']

        # Create rule interface

        self.mwidgets = {}
        mwidgets = self.mwidgets

        mpanel = wx.Panel(parent)

        pgrid = wx.GridBagSizer(4, 4)
        mpanel.SetSizer(pgrid)

        slabel = wx.StaticText(mpanel, label='From:')
        pgrid.Add(slabel, (0, 1), flag=wx.ALIGN_CENTER_VERTICAL)

        mwidgets['start_date'] = wx.DatePickerCtrl(mpanel, size=(-1, 21))
        # Add a 1px top border because DatePickerCtrl cuts 1px at top and left
        pgrid.Add(mwidgets['start_date'], (0, 2),
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP, border=1)

        mwidgets['start_hour'] = wx.SpinCtrl(mpanel, min=0, max=23,
                                           size=(40, 21),
                                           style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        pgrid.Add(mwidgets['start_hour'], (0, 3),
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
                  border=12)

        slabel = wx.StaticText(mpanel, label=':')
        pgrid.Add(slabel, (0, 4), flag=wx.ALIGN_CENTER_VERTICAL)

        mwidgets['start_minute'] = wx.SpinCtrl(mpanel, min=0, max=59,
                                           size=(40, 21),
                                           style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        pgrid.Add(mwidgets['start_minute'], (0, 5),
                  flag=wx.ALIGN_CENTER_VERTICAL)

        elabel = wx.StaticText(mpanel)
        pgrid.Add(elabel, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL)

        slabel = wx.StaticText(mpanel, label='Until:')
        pgrid.Add(slabel, (1, 1), flag=wx.ALIGN_CENTER_VERTICAL)

        mwidgets['end_date'] = wx.DatePickerCtrl(mpanel, size=(-1, 21))
        # Add a 1px top border because DatePickerCtrl cuts 1px at top and left
        pgrid.Add(mwidgets['end_date'], (1, 2),
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP, border=1)

        mwidgets['end_hour'] = wx.SpinCtrl(mpanel, min=0, max=23,
                                           size=(40, 21),
                                           style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        pgrid.Add(mwidgets['end_hour'], (1, 3), flag=wx.ALIGN_CENTER_VERTICAL |
                  wx.ALIGN_RIGHT)

        slabel = wx.StaticText(mpanel, label=':')
        pgrid.Add(slabel, (1, 4), flag=wx.ALIGN_CENTER_VERTICAL)

        mwidgets['end_minute'] = wx.SpinCtrl(mpanel, min=0, max=59,
                                           size=(40, 21),
                                           style=wx.SP_ARROW_KEYS | wx.SP_WRAP)
        pgrid.Add(mwidgets['end_minute'], (1, 5),
                  flag=wx.ALIGN_CENTER_VERTICAL)

        mwidgets['inclusive_chbox'] = wx.CheckBox(mpanel)
        pgrid.Add(mwidgets['inclusive_chbox'], (2, 0))

        slabel = wx.StaticText(mpanel, label='Inclusive')
        pgrid.Add(slabel, (2, 1), span=(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)

        # Initialize values in interface

        # dict.get() returns None if key is not in dictionary, and it happens
        # when the interface is being set up for a new rule
        start = kwargs['ruled'].get('start')
        end = kwargs['ruled'].get('end')
        inclusive = kwargs['ruled'].get('inclusive')

        if start == None:
            start = (int(_time.time()) // 3600 + 1) * 3600

        sdate = wx.DateTime()
        sdate.Set(year=int(_time.strftime('%Y', _time.localtime(start))),
                  month=int(_time.strftime('%m', _time.localtime(start))) - 1,
                  day=int(_time.strftime('%d', _time.localtime(start))))
        shour = int(_time.strftime('%H', _time.localtime(start)))
        smin = int(_time.strftime('%M', _time.localtime(start)))

        mwidgets['start_date'].SetValue(sdate)
        mwidgets['start_hour'].SetValue(shour)
        mwidgets['start_minute'].SetValue(smin)

        if end == None:
            end = start + 3600

        edate = wx.DateTime()
        edate.Set(year=int(_time.strftime('%Y', _time.localtime(end))),
                   month=int(_time.strftime('%m', _time.localtime(end))) - 1,
                   day=int(_time.strftime('%d', _time.localtime(end))))
        ehour = int(_time.strftime('%H', _time.localtime(end)))
        emin = int(_time.strftime('%M', _time.localtime(end)))

        mwidgets['end_date'].SetValue(edate)
        mwidgets['end_hour'].SetValue(ehour)
        mwidgets['end_minute'].SetValue(emin)

        if inclusive == None:
            mwidgets['inclusive_chbox'].SetValue(False)
        else:
            mwidgets['inclusive_chbox'].SetValue(inclusive)

        wxscheduler_api.change_rule(kwargs['filename'], kwargs['id_'], mpanel)


    def apply_rule(self, kwargs):
        sdate = self.mwidgets['start_date'].GetValue().GetTicks()
        shour = self.mwidgets['start_hour'].GetValue()
        sminute = self.mwidgets['start_minute'].GetValue()

        start = sdate + shour * 3600 + sminute * 60

        edate = self.mwidgets['end_date'].GetValue().GetTicks()
        ehour = self.mwidgets['end_hour'].GetValue()
        eminute = self.mwidgets['end_minute'].GetValue()

        end = edate + ehour * 3600 + eminute * 60

        inclusive = self.mwidgets['inclusive_chbox'].GetValue()

        self.create_rule(filename=kwargs['filename'], id_=kwargs['id_'],
                         start=start, end=end, inclusive=inclusive)

    @classmethod
    def insert_rule(cls, kwargs):
        start = kwargs['rule']['start']
        end = kwargs['rule']['end']
        inclusive = kwargs['rule']['inclusive']

        start = int(start)
        end = int(end)

        if inclusive == 'True':
            inclusive = True
        else:
            inclusive = False

        cls.create_rule(filename=kwargs['filename'], id_=kwargs['id_'],
                        start=start, end=end, inclusive=inclusive)

    @staticmethod
    def create_rule(filename, id_, start, end, inclusive):
        start = int(start)
        end = int(end)
        label = ' '.join(('Except', _time.strftime('from %a %d %b %Y at %H:%M',
                           _time.localtime(start)),
                           _time.strftime('until %a %d %b %Y at %H:%M',
                           _time.localtime(end))))

        if inclusive:
            label += ', inclusive'

        ruled = {'rule': _RULE_NAME,
                 'start': start,
                 'end': end,
                 'inclusive': inclusive}

        wxscheduler_api.insert_rule(filename, id_, ruled, label)
