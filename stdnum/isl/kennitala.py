# kennitala.py - functions for handling Icelandic identity codes
# coding: utf-8
#
# Copyright (C) 2011 Jussi Judin
# Copyright (C) 2012, 2013 Arthur de Jong
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

"""Kennitala (Icelandic personal and organisation identity code).

Module for handling Icelandic personal and organisation identity codes
(kennitala).

>>> compact('530575-0209')  # organisation
'5305750209'
>>> compact('120174-3399')  # individual
'1201743399'
>>> validate('530575-0209')  # organisation
'5305750209'
>>> validate('120174-3399')  # individual
'1201743399'
>>> validate('530575-0299')
Traceback (most recent call last):
    ...
InvalidChecksum: ...
>>> validate('320174-3399')
Traceback (most recent call last):
    ...
InvalidComponent: ...
>>> compact('530575-0209')
'5305750209'
"""

import re
import datetime

from stdnum.exceptions import *
from stdnum.util import clean


# Icelandic personal and organisation identity codes are composed of
# date part, a dash, two random digits, a checksum, and a century
# indicator where '9' for 1900-1999 and '0' for 2000 and beyond. For
# organisations instead of birth date, the registration date is used,
# and number 4 is added to the first digit.
_kennitala_re = re.compile(r'^(?P<day>[01234567]\d)(?P<month>[01]\d)(?P<year>\d\d)'
                           r'(?P<random>\d\d)(?P<control>\d)'
                           r'(?P<century>[09])$')


def compact(number):
    """Convert the kennitala to the minimal representation. This
    strips surrounding whitespace and separation dash, and converts it
    to upper case."""
    return clean(number, '-').upper().strip()


def checksum(number):
    """Calculate the checksum."""
    weights = (3, 2, 7, 6, 5, 4, 3, 2)
    return (11 - sum(weights[i] * int(n) for i, n in enumerate(number))) % 11


def validate(number):
    """Checks to see if the number provided is a valid kennitala. It
    checks the format, whether a valid date is given and whether the
    check digit is correct."""
    number = compact(number)
    match = _kennitala_re.search(number)
    if not match:
        raise InvalidFormat()
    day = int(match.group('day'))
    month = int(match.group('month'))
    year = int(match.group('year'))
    century = int(match.group('century'))
    if century == 9:
        century = 1900
    else:
        century = 2000
    # check if birth date or registration data is valid
    try:
        if day >= 40:  # organisation
            datetime.date(century + year, month, day-40)
        else:  # individual
            datetime.date(century + year, month, day)
    except ValueError:
        raise InvalidComponent()
    # validate the checksum
    if checksum(number[:8]) != int(number[8]):
       raise InvalidChecksum()
    return number


def is_valid(number):
    """Checks to see if the number provided is a valid HETU. It checks the
    format, whether a valid date is given and whether the check digit is
    correct."""
    try:
        return bool(validate(number))
    except ValidationError:
        return False


# This is here just for completeness as there are no different length forms
# of Finnish personal identity codes:
format = compact
