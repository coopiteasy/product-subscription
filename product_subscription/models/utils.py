# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta
import calendar


def format_date(f):
    def format_input(d, unit):
        d = datetime.strptime(d, DEFAULT_SERVER_DATE_FORMAT)
        res = f(d, unit)
        return res.strftime(DEFAULT_SERVER_DATE_FORMAT)

    return format_input


@format_date
def add_days(d, days):
    return d + timedelta(days=days)


@format_date
def add_months(d, months):
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


@format_date
def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
