# coding=utf-8
# -*- coding: utf-8 -*-

"""
This is a port to python of a few LUA functions from
http://en.wikipedia.org/wiki/Module:Coordinates

"""
from __future__ import unicode_literals
import re
import math
import math_mod


class ParseException(Exception):
    pass


class table(object):
    @staticmethod
    def insert(tbl, obj):
        tbl.append(obj)


def optionalArg(arg, suplement):
    """
    Helper function, handle optional args
    """
    if arg:
        return arg + suplement
    return ""


def parseDec(lat, long_, format_):
    """
    Transforms decimal format latitude and longitude into the a
    structure to be used in displaying coordinates
    """
    coordinateSpec = {}

    if long_ == "" or long_ is None:
        raise ParseException('Missing longitude')
        # return None, {{"parseDec", "Missing longitude"}}

    errors = validate(lat, None, None, long_, None, None, 'parseDec', False)
    coordinateSpec["dec-lat"] = lat
    coordinateSpec["dec-long"] = long_

    mode = coordinates_determineMode(lat, long_)
    coordinateSpec["dms-lat"] = convert_dec2dms(
        lat, "N", "S", mode)  # {{coord/dec2dms|{{{1}}}|N|S|{{coord/prec dec|{{{1}}}|{{{2}}}}}}}
    coordinateSpec["dms-long"] = convert_dec2dms(
        long_, "E", "W", mode)  # {{coord/dec2dms|{{{2}}}|E|W|{{coord/prec dec|{{{1}}}|{{{2}}}}}}}

    if format_:
        coordinateSpec['default'] = format_
    else:
        coordinateSpec['default'] = "dec"

    return coordinateSpec, errors


# --[[ Helper function, handle optional args. ]]
# function optionalArg(arg, suplement)
#     if arg ~= None and arg ~= "":
#         return arg .. suplement
#     end
#     return ""
# end


def convert_dec2dms(coordinate, firstPostfix, secondPostfix, precision):
    """
    Helper function, convert decimal latitude or longitude to
    degrees, minutes, and seconds format based on the specified precision.
    """
    coord = _float_or_value(coordinate)

    if coord >= 0:
        postfix = firstPostfix
    else:
        postfix = secondPostfix

    precision = precision.lower()
    if precision == "dms":
        return convert_dec2dms_dms(abs(coord)) + postfix
    elif precision == "dm":
        return convert_dec2dms_dm(abs(coord)) + postfix
    elif precision == "d":
        return convert_dec2dms_d(abs(coord)) + postfix


def convert_dec2dms_d(coordinate):
    """
    Helper function, convert decimal to degrees
    """
    return math_mod._round(coordinate, 0) + "°"


def convert_dec2dms_dm(coordinate):
    """
    Helper function, convert decimal to degrees and minutes
    """
    coordinate = math_mod._round(coordinate * 60, 0)
    m = coordinate % 60
    coordinate = int(math.floor((coordinate - m) / 60))
    d = "%d°" % (coordinate % 360)

    return u"%s%02d′" % (d, m,)


def convert_dec2dms_dms(coordinate):
    """
    Helper function, convert decimal to degrees, minutes, and seconds
    """
    coordinate = math_mod._round(coordinate * 60 * 60, 0)
    s = coordinate % 60
    coordinate = int(math.floor((coordinate - s) / 60))
    m = coordinate % 60
    coordinate = int(math.floor((coordinate - m) / 60))
    d = "%d°" % (coordinate % 360)

    return u"%s%02d′%02d″" % (d, m, s)


def coordinates_determineMode(value1, value2):
    """
    Helper function to determine whether to use D, DM, or DMS
    format depending on the precision of the decimal input.
    """
    precision = max(math_mod._precision(
        value1), math_mod._precision(value2))
    if precision <= 0:
        return 'd'
    elif precision <= 2:
        return 'dm'
    else:
        return 'dms'


def parseDMS(lat_d, lat_m, lat_s, lat_f, long_d, long_m, long_s, long_f,
             format_=None):
    """
    Transforms degrees, minutes, seconds format latitude and longitude
    into the a structure to be used in displaying coordinates
    """
    coordinateSpec = {}

    lat_f = lat_f.upper()
    long_f = long_f.upper()

    # Check if specified backward
    if lat_f == 'E' or lat_f == 'W':
        t_d = lat_d
        t_m = lat_m
        t_s = lat_s
        t_f = lat_f
        lat_d = long_d
        lat_m = long_m
        lat_s = long_s
        lat_f = long_f
        long_d = t_d
        long_m = t_m
        long_s = t_s
        long_f = t_f

    errors = validate(
        lat_d, lat_m, lat_s, long_d, long_m, long_s, 'parseDMS', True)
    if not long_d:
        raise Exception('Missing longitude')

    if lat_m is None and lat_s is None and long_m is None and long_s is None and not len(errors):
        if math_mod._precision(lat_d) > 0 or math_mod._precision(long_d) > 0:
            if lat_f.upper() == 'S':
                lat_d = '-' + lat_d
            if long_f.upper() == 'W':
                long_d = '-' + long_d

            return parseDec(lat_d, long_d, format_)

    coordinateSpec["dms-lat"] = lat_d + "°" + optionalArg(
        lat_m, "′") + optionalArg(lat_s, "″") + lat_f
    coordinateSpec["dms-long"] = long_d + "°" + optionalArg(
        long_m, "′") + optionalArg(long_s, "″") + long_f
    # {{coord/dms2dec|{{{4}}}|{{{1}}}|0{{{2}}}|0{{{3}}}}}
    coordinateSpec["dec-lat"] = convert_dms2dec(
        lat_f, lat_d, lat_m, lat_s)
    # {{coord/dms2dec|{{{8}}}|{{{5}}}|0{{{6}}}|0{{{7}}}}}
    coordinateSpec["dec-long"] = convert_dms2dec(
        long_f, long_d, long_m, long_s)

    if format_:
        coordinateSpec['default'] = format_
    else:
        coordinateSpec['default'] = "dms"

    return coordinateSpec, errors


def convert_dms2dec(direction, degrees_str, minutes_str, seconds_str):
    """
    Convert DMS format into a N or E decimal coordinate
    """
    degrees = _float_or_value(degrees_str)
    minutes = _float_or_value(minutes_str)
    seconds = _float_or_value(seconds_str)

    print '=== DIRECTION', direction
    ## lua version is:
    # direction = mw.ustring.gsub(direction, '^[ ]*(.-)[ ]*$', '%1')

    ## a plain translation would be:
    # direction_match = re.match(r'^[ ]*(.)[ ]*$', direction)
    # if direction_match and direction_match.group(1) in "NE":

    ## but it can also be done with:
    direction = direction.strip()
    if direction in "NE":
        factor = 1
    else:
        factor = -1

    if seconds_str:
        precision = 5 + max(math_mod._precision(seconds_str), 0)
    elif minutes_str:
        precision = 3 + max(math_mod._precision(minutes_str), 0)
    else:
        precision = max(math_mod._precision(degrees_str), 0)

    decimal = factor * (degrees + (minutes + seconds / 60) / 60)

    # not float since this whole thing is string based.
    return ("%%.%df" % (precision,)) % (decimal,)


def _float_or_value(s, default=0.):
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def validate(lat_d, lat_m, lat_s, long_d, long_m, long_s, source, strong):
    """
    Checks input values to for out of range errors.
    """
    errors = []
    lat_d = _float_or_value(lat_d)
    lat_m = _float_or_value(lat_m)
    lat_s = _float_or_value(lat_s)
    long_d = _float_or_value(long_d)
    long_m = _float_or_value(long_m)
    long_s = _float_or_value(long_s)

    if strong:
        if lat_d < 0:
            table.insert(errors, [
                         source, "latitude degrees < 0 with hemisphere flag"])
        if long_d < 0:
            table.insert(errors, [
                         source, "longitude degrees < 0 with hemisphere flag"])

        # coordinates is inconsistent about whether this is an error.  If globe: is
        # specified, it won't error on this condition, but otherwise it will.
        #
        # For not simply disable this check.
        #
        # if long_d > 180:
        #     table.insert(errors, {source, "longitude degrees > 180 with hemisphere flag"})
        # end

    if lat_d > 90:
        table.insert(errors, [source, "latitude degrees > 90"])
    if lat_d < -90:
        table.insert(errors, [source, "latitude degrees < -90"])
    if lat_m >= 60:
        table.insert(errors, [source, "latitude minutes >= 60"])
    if lat_m < 0:
        table.insert(errors, [source, "latitude minutes < 0"])
    if lat_s >= 60:
        table.insert(errors, [source, "latitude seconds >= 60"])
    if lat_s < 0:
        table.insert(errors, [source, "latitude seconds < 0"])
    if long_d >= 360:
        table.insert(errors, [source, "longitude degrees >= 360"])
    if long_d <= -360:
        table.insert(errors, [source, "longitude degrees <= -360"])
    if long_m >= 60:
        table.insert(errors, [source, "longitude minutes >= 60"])
    if long_m < 0:
        table.insert(errors, [source, "longitude minutes < 0"])
    if long_s >= 60:
        table.insert(errors, [source, "longitude seconds >= 60"])
    if long_s < 0:
        table.insert(errors, [source, "longitude seconds < 0"])

    return errors
