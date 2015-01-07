#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = "Vlad Emelyanov (volshebnyi@gmail.com)"
__version__ = "2015"
__date__ = "2015-01-06"
__license__ = "CC-BY"

import datetime
import argparse


def digit_to_char(digit):
    if digit < 10:
        return chr(ord('0') + digit)
    else:
        return chr(ord('a') + digit - 10)


def str_base(number, base):
    if number < 0:
        return '-' + str_base(-number, base)
    else:
        d, m = divmod(number, base)
        if d:
            return str_base(d, base) + digit_to_char(m)
        else:
            return digit_to_char(m)


def zfill_list(a):
    max_len = max([len(i) for i in a])
    return [i.zfill(max_len) for i in a]


holidays_public_ru = {
    2015: [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
        (1, 9), (1, 10), (1, 11), (2, 21), (2, 22), (2, 23), (3, 7), (3, 8),
        (3, 9), (5, 1), (5, 2), (5, 3), (5, 4), (5, 9), (5, 10), (5, 11),
        (6, 12), (6, 13), (6, 14), (11, 4), ],
}

holidays_public = {
    2015: [
        (1, 1), (1, 6), (4, 3), (4, 6), (5, 1), (5, 14), (5, 25), (6, 4),
        (8, 15), (10, 3), (11, 1), (12, 25), (12, 26), ],
}


def is_leap(year):
    try:
        datetime.date(year, 2, 29)
    except ValueError:
        return False

    return True


def get_hoilidays(year):
    return list(holidays_public.get(year, []))


def get_specials(year):
    holidays = []

    # last Friday of July is Sysadmin's Day
    d = datetime.date(year, 7, 31)
    while True:
        if d.weekday() == 4:
            holidays.append((7, 26))
            break
        d = d - datetime.timedelta(days=1)

    # (4, 4) - Webmasters' Day
    holidays.append((4, 4))

    #  256th day of year is Programmers' Day
    if is_leap(year):
        holidays.append((9, 12))
    else:
        holidays.append((9, 13))

    return holidays


class SvgCalendar:
    def __init__(self, year, base=16):

        self.year = year

        font = 'Consolas'

        self.style = {
            'units': 'mm',

            'width': 100,
            'height': 70,

            'border-color': '#ccc',

            'year-color': '#666666',
            'year-padding-top': 5,
            'year-padding-left': 2,
            'year-font-family': font,
            'year-font-size': 5,

            'month-width': 24,
            'month-height': 21,

            'day-width': 23.0 / 7.0,
            'day-height': 12.0 / 5.0,

            'month-margin-right': 0,
            'month-margin-bottom': 0,

            'month-font-family': font,
            'month-font-size': 3,
            'month-color': '#FF9525',
            'month-padding-top': 3,

            'month-offset-top': 5,

            'week-padding-top': 6,
            'week-font-family': font,
            'week-font-size': 1.5,

            'day-padding-top': 6,
            'day-font-family': font,
            'day-font-size': 2,

            'day-color': '#000000',
            'day-holiday-color': '#79B1D4',
            'day-special-color': '#FF0000',

            'week-color': '#999',
            'week-holiday-color': '#79B1D4',
        }

        self.year_name = str_base(year, base)
        self.month_names = zfill_list(
            [str_base(i, base) for i in range(1, 13)])
        self.weekdays_names = zfill_list(
            [str_base(i, base) for i in range(1, 8)])
        self.days_names = zfill_list(
            [str_base(i, base) for i in range(1, 32)])

        # well, actually holidays depend on the production calendar
        self.holidays = get_hoilidays(year)
        self.specials = get_specials(year)
        self.not_holidays = []

    def is_holiday(self, month, day, day_of_week):
        if day_of_week in [5, 6]:
            return (month, day) not in self.not_holidays
        return (month, day) in self.holidays

    def is_special(self, month, day, day_of_week):
        return (month, day) in self.specials

    def render_day(self, x, y, month, day, day_of_week):
        svg = ''
        if self.is_special(month, day,  day_of_week):
            color = self.style['day-special-color']
        elif self.is_holiday(month, day,  day_of_week):
            color = self.style['day-holiday-color']
        else:
            color = self.style['day-color']
        svg += '<text x="%smm" y="%smm" font-family="%s" font-size="%smm" fill="%s" text-anchor="middle">' % (
            x + 0.5 * self.style['day-width'],
            y, self.style['day-font-family'],
            self.style['day-font-size'],
            color)
        svg += '%s' % self.days_names[day - 1]
        svg += '</text>'
        return svg

    def render_week(self, x, y):
        svg = ''
        svg += '<g>'
        for i in range(7):
            if i < 5:
                color = self.style['week-color']
            else:
                color = self.style['week-holiday-color']
            svg += (
                '<text x="%smm" y="%smm" font-family="%s" font-size="%smm" '
                'text-anchor="middle" fill="%s">') % (
                x + (i + 0.5) * self.style['day-width'],
                y,
                self.style['week-font-family'],
                self.style['week-font-size'],
                color)
            svg += '%s' % (self.weekdays_names[i])
            svg += '</text>'
        svg += '</g>'
        return svg

    def render_month(self, x, y, month_no):
        svg = ''

        svg += '<g>'
        svg += (
            '<text x="%smm" y="%smm" font-family="%s" font-size="%smm" '
            'text-anchor="middle" fill="%s">') % (
            x + self.style['month-width'] / 2,
            y + self.style['month-padding-top'],
            self.style['month-font-family'],
            self.style['month-font-size'],
            self.style['month-color'])
        svg += '%s' % (self.month_names[month_no - 1])
        svg += '</text>'
        svg += self.render_week(x, y + self.style['week-padding-top'])

        day_of_week = -1  # will start from Monday
        week_no = 1

        d = datetime.date(self.year, month_no, 1)
        while d.month == month_no:
            day_no = d.day
            day_of_week = d.weekday()
            d = d + datetime.timedelta(days=1)

            xx = x + self.style['day-width'] * (day_of_week)
            yy = y + self.style['day-padding-top'] + week_no * self.style['day-height']

            svg += self.render_day(xx, yy, month_no, day_no, day_of_week)

            if day_of_week == 6:
                week_no += 1

        svg += '</g>'
        return svg

    def render_year(self, x, y):
        svg = ''
        svg += '<g>'
        svg += (
            '<text x="%smm" y="%smm" font-family="%s" font-size="%smm" '
            'text-anchor="middle" fill="%s">') % (
            x + self.style['width'] / 2,
            y + self.style['year-padding-top'],
            self.style['year-font-family'],
            self.style['year-font-size'],
            self.style['year-color'])
        svg += self.year_name
        svg += '</text>'
        for i in range(12):
            xx = i % 4
            yy = i / 4
            svg += self.render_month(
                x + xx * self.style['month-width'] + xx * self.style['month-margin-right'],
                (
                    y + self.style['month-offset-top']
                    + yy * self.style['month-height']
                    + yy * self.style['month-margin-bottom']),
                i + 1)
        svg += '</g>'
        return svg

    def render(self):
        svg = ''
        svg += (
            '<?xml version="1.0" standalone="no"?>'
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
        svg += (
            '<svg width="%smm" height="%smm" version="1.1" xmlns='
            '"http://www.w3.org/2000/svg"><desc>Calendar 2012</desc>') % (
            self.style['width'], self.style['height'])
        svg += (
            '<g><rect x="0.25mm" y="0.25mm" width="%smm" height="%smm" rx='
            '"2.5mm" fill="#fff" stroke="%s" storke-width="0.5mm"/></g>') % (
            self.style['width'] - 0.75,
            self.style['height'] - 0.75,
            self.style['border-color'])
        svg += self.render_year(self.style['year-padding-left'], 0)
        svg += '</svg>'
        return svg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calendar generator.')
    parser.add_argument('year', type=int)
    parser.add_argument('--base', type=int, default=8)
    params = parser.parse_args()
    c = SvgCalendar(params.year, params.base)
    print c.render()
