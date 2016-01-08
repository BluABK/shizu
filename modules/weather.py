#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import cPickle

import requests

__author__ = 'BluABK <abk@blucoders.net>'

station_loc_url = 'http://fil.nrk.no/yr/viktigestader/noreg.txt'
station_world_loc_url = 'http://fil.nrk.no/yr/viktigestader/verda.txt'
#stations = {}
time_format = "%a, %d %b %Y %H:%M:%S +0000"


class Buffer:
    """Lazy evaluation Buffer class"""

    def __init__(self, func, timestamp=-1.0, debug=False):
        """Takes a function argument to be buffered"""
        self.func = func
        self.debug = debug

        if timestamp != -1.0:
            self.timestamp = float(timestamp)
            if self.debug:
                print "setting age to custom value: %s (%s)" % (timestamp, time.ctime(timestamp))
                print "self.timestamp: %f" % self.timestamp
        else:
            self.timestamp = time.mktime(time.localtime())

        self.age = float(timestamp)

        try:
            with open('cache.dat', 'rb') as f:
                self.buffer = cPickle.load(f)
            self.age = self.buffer.get("age")
            if self.debug:
                print "Loaded buffer from file with size %s and age %s (%s)" % (
                    len(self.buffer), self.age, time.ctime(self.age))
        except (IOError, EOFError) as e:
            if self.debug:
                print "No cache detected, buffer is empty: %s" % e.message
            self.buffer = {"age": self.timestamp}

    def __call__(self, arg):
        """Checks current argument against the local buffer and saves it if no such entry exists"""
        # If buffer age is > 6 hours, it is obsolete and must be reset
        if self.debug:
            print "Seconds in the past: %s" % (self.timestamp - self.age)
        if (self.timestamp - self.age) >= 21600:
            self.reset()

        if arg in self.buffer:
            return self.buffer[arg]
        retval = self.func(arg)
        self.buffer[arg] = retval
        self.save()
        return retval

    def save(self):
        """Saves buffer to file"""
        if self.debug:
            print "Saving buffer with size %s and age %s" % (len(self.buffer), self.age)
        cPickle.dump(self.buffer, open('cache.dat', 'wb'))

    def reset(self):
        """Wipes buffer and file"""
        if self.debug:
            print "Wiping local buffer"
        t = time.time()
        self.buffer = {"age": t}
        self.age = t
        self.save()


class Station:
    """Weather station class containing all relevant information"""

    def __init__(self, my_id, cid, place, priority, type_nn, type_nb, type_en, county,
                 province, latitude, longitude, height, xml_nn, xml_nb, xml_en):
        self.my_id = my_id
        self.cid = cid
        self.place = place
        self.priority = priority
        self.type_nn = type_nn
        self.type_nb = type_nb
        self.type_en = type_en
        self.county = county
        self.province = province
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.xml_nn = xml_nn
        self.xml_nb = xml_nb
        self.xml_en = xml_en

    def about_me(self):
        """Returns all information about a Station, mostly used for debugging."""
        return "Station %05d:    cid=%s, place=%s, priority=%s, type_nn=%s, type_nb=%s, type_en=%s, county=%s," \
               " province=%s, latitude=%s, longitude=%s, height=%s, xml_nn=%s, xml_nb=%s, xml_en=%s" % \
               (self.my_id, self.cid, self.place, self.priority, self.type_nn, self.type_nb, self.type_en, self.county,
                self.province, self.latitude, self.longitude, self.height, self.xml_nn, self.xml_nb, self.xml_en)


def download(url, coding="", limit=0, debug=False):
    """Downloads a file from the internet, if limit is set only download that amount of lines"""
    try:
        r = requests.get(url)
    except requests.exceptions.MissingSchema:
        print "download: This is not a url: %s" % url
        return False
    if limit != 0:
        doc = ""
        count = 0

        for line in r.text:
            if count == limit:
                break
            if debug:
                print "%s: %s" % (count, line)
            doc += line
            count += 1
    else:
        doc = r.text.encode(r.encoding)
    if coding is not "":
        doc = doc.decode(coding)
    return doc


# Wrap download in a Buffer
download_buf = Buffer(download)


def regexify(normal_string, symbol='*'):
    """Takes a string containing characters with regex properties, inserts a leading period and returns the modified
     string
     """
    pos = normal_string.index(symbol)
    return normal_string[:pos] + '.' + normal_string[pos:]


def create_stations(sl, method=0, debug=False):
    """Creates a dictionary of weather stations (object) from a list and returns the dictionary"""
    # global stations
    stations = {}
    id_count = 0
    for line in sl.split('\r\n'):
        # Skip junk lines
        if len(line) < 1:
            continue
        n = line.split('\t')
        if method == 0:
            stations.update(
                {id_count: Station(my_id=id_count, cid=n[0], place=n[1], priority=n[2], type_nn=n[3], type_nb=n[4],
                                    type_en=n[5], county=n[6], province=n[7], latitude=n[8], longitude=n[9],
                                    height=n[10], xml_nn=n[11], xml_nb=n[12], xml_en=n[13])})
        elif method == 1:
            stations.update(
                {id_count: Station(my_id=id_count, cid=n[0], place=n[3], priority=n[4], type_nn=n[5], type_nb=n[6],
                                    type_en=n[7], county=n[10], province=n[10], latitude=n[12], longitude=n[13],
                                    height=n[14], xml_nn=n[15], xml_nb=n[16], xml_en=n[17])})
        if debug:
            print stations.get(id_count).about_me()
        id_count += 1
    return stations


#station_list = download_buf(station_loc_url)
#stations = dict(stations, **create_stations(station_list))
#def generate_defaults():
stations_norway = create_stations(download_buf(station_loc_url))
stations_world = create_stations(download_buf(station_world_loc_url), method=1)

default_stations = [stations_norway, stations_world]


def get_location_xml(place, limit=0, debug=False):
    """Takes a place (string) and returns all matching xml (English) urls"""
    global default_stations
    results = list()
    # If empty string, return all xml_en entries
    if place == "":
        for station in default_stations:
            for key, st in station.iteritems():
                results.append(st.xml_en)
        return results

    # If wildcard specified, reformat location into regex compliant
    if '*' in place:
        place = regexify(place)

    # Find and append unique xml_en entries
    for station in default_stations:
        for key, st in station.iteritems():
            if len(results) >= limit != 0:
                if debug:
                    print "get_location_xml: Exceeded limit (%s), ending job." % limit
                    break
            # Strip any duplicate entries
            if st.xml_en not in results:
                if re.search(place, st.place, re.I):
                    results.append(st.xml_en)
                elif re.search(place, st.county, re.I):
                    results.append(st.xml_en)
                elif re.search(place, st.province, re.I):
                    results.append(st.xml_en)

    return results


def get_station(xml_en=""):
    """Takes a xml (English) url and returns the corresponding weather station (object)"""
    global default_stations
    if xml_en == "":
        return None
    # Find station based on xml_en
    for station in default_stations:
        for key, st in station.iteritems():
            if re.search(xml_en, st.xml_en):
                return station.get(key)

    return None


def weather_info(xml_url, place, terrible=False, debug=False):
    """Retrieves and returns weather information from a xml url"""
    entries = list()
    if debug:
        print "Got url: %s" % xml_url
    xml = download_buf(xml_url)
    if xml is False:
        return []
    # Parse it using regex
    if terrible:
        # Skip leading junk data
        junk = True
        new_xml = ""
        for line in xml.split('\r\n'):
            if junk:
                if "<tabular>" in line:
                    junk = False
                continue
            else:
                new_xml += line + '\r\n'
        xml = new_xml

        # times = print(re.findall('<time.*from="(.*?)" to="(.*?)">', xml))
        # times_from = times.
        times_from = (re.findall('<time.*from="(.*?)" .*>', xml))
        times_to = (re.findall('<time.*to="(.*?)" .*>', xml))
        temps = (re.findall('<temperature.*value="(.*?)" .*>', xml))
        winds = (re.findall('<windSpeed.*mps="(.*?)" .*>', xml))
        rain = (re.findall('<precipitation.*value="(.*?)" .*>', xml))
        names = (re.findall('<symbol .* name="(.*?)" .*/>', xml))

        if debug:
            print "to:   %s" % times_from
            print "from: %s" % times_to
            print "temp: %s" % temps
            print "wind: %s" % winds
            print "rain: %s" % rain
            print "name: %s" % names

        entries = []
        for i in range(len(times_from)):
            times_from[i] = time.strptime(times_from[i], '%Y-%m-%dT%H:%M:%S')
            times_to[i] = time.strptime(times_to[i], '%Y-%m-%dT%H:%M:%S')
            if debug:
                print "\tPlace:               %s" % place
                print "\tTime from:           %s" % time.strftime(time_format, times_from[i])
                print "\tTime to:             %s" % time.strftime(time_format, times_to[i])
            summary = {'time_from': times_from[i], 'time_to': times_to[i], 'place': place, 'name': None, 'rain': None,
                       'wind': None, 'temperature': None}

            summary.update({"time_from": times_from[i]})
            summary.update({"time_to": times_to[i]})
            summary.update({"place": place})
            summary.update({"temperature": temps[i]})
            summary.update({"wind": winds[i]})
            summary.update({"rain": rain[i]})
            summary.update({"name": names[i]})
            entries.append(summary)
        if debug:
            print entries
    # Parse it using XML etree
    else:
        try:
            import xml.etree.ElementTree as ET
            xml_root = ET.fromstring(xml)
        except:
            if debug:
                if "<!DOCTYPE html>" in xml.split('\n')[0]:
                    print "weather_info: Expected xml, got html, dropping request."
                else:
                    print "weather_info: An invalid xml was given, dropping request: %s" % xml.split('\n')[0]
            return []
        try:
            for child in xml_root.find("forecast/tabular"):
                if debug:
                    print child
                time_from = time.strptime(child.get('from'), '%Y-%m-%dT%H:%M:%S')
                time_to = time.strptime(child.get('to'), '%Y-%m-%dT%H:%M:%S')
                if debug:
                    print "\tPlace:               %s" % place
                    print "\tTime from:           %s" % time.strftime(time_format, time_from)
                    print "\tTime to:             %s" % time.strftime(time_format, time_to)
                summary = {'time_from': time_from, 'time_to': time_to, 'place': place, 'name': None, 'rain': None,
                           'wind': None, 'temperature': None}
                for elem in child.iter():
                    if elem.tag == "symbol":
                        if debug:
                            print "\tName:                %s" % elem.attrib.get('name')
                        summary.update({'name': elem.attrib.get('name')})
                    if elem.tag == "precipitation":
                        if debug:
                            print "\tPrecipitation value: %s" % elem.attrib.get('value')
                        summary.update({'rain': elem.attrib.get('value')})
                    if elem.tag == "windSpeed":
                        if debug:
                            print "\tWind speed:          %s" % elem.attrib.get('mps')
                        summary.update({'wind': elem.attrib.get('mps')})
                    if elem.tag == "temperature":
                        if debug:
                            print "\tTemperature:         %s" % elem.attrib.get('value')
                        summary.update({'temperature': elem.attrib.get('value')})
                entries.append(summary)
        except TypeError as e:
            print e.message
        if debug:
            print entries

    return entries


def weather_update(place, hour=-1, minute=-1, return_raw=False, limit=100, debug=False):
    """Weather forecast, takes place (string), hour and minute and returns weather info for the given time.
    If no hour and/or minute is given they will be set to current local time"""
    lim_cnt = 0
    if hour == -1:
        hour = time.localtime().tm_hour
    if minute == -1:
        minute = time.localtime().tm_min
    for elem in get_location_xml(place):
        if lim_cnt >= limit != 0:
            if debug:
                print "weather_update: Exceeded limit (%s), ending job." % limit
            break

        forecasts = weather_info(elem, get_station(elem).place)
        current_time = time.localtime()

        t = list(time.localtime())
        t[3] = hour
        t[4] = minute
        t = time.mktime(t)

        if hour < current_time.tm_hour or (hour == current_time.tm_hour and minute < current_time.tm_min):
            t += 3600*24

        for f in forecasts:
                if debug:
                    print "Checking time:\t\t %02d - %02d" % (f.get("time_from").tm_hour, f.get("time_to").tm_hour) +\
                          " [%d <= %d <= %s]" % (time.mktime(f.get("time_from")), t, time.mktime(f.get("time_to")))

                if time.mktime(f.get("time_from")) <= t <= time.mktime(f.get("time_to")):
                    date_stamp = "%02d.%02d.%s %02d:%02d" % (
                        f.get("time_from").tm_mday, f.get("time_from").tm_mon, f.get("time_from").tm_year,
                        f.get("time_from").tm_hour, f.get("time_from").tm_min)
                    if debug:
                        print "\tMatched Time:\t %02d - %02d" % (f.get("time_from").tm_hour, f.get("time_to").tm_hour)

                    if return_raw:
                        return f
                    else:
                        return "%s (%s): %s, rain:%s mm, wind:%s mps, temp:%s deg C" % (
                            f.get("place"), date_stamp, f.get("name"), f.get("rain"), f.get("wind"),
                            f.get("temperature"))
        lim_cnt += 1


def find_coldest(hour=13, limit=100, debug=False, info=False):
    """Prints Norway's coldest place on the given hour (default=13)"""
    score = 999999
    forecasts = []
    place = ""
    if info:
        if limit == 0:
            print "Locating place with coldest temperature... (no entry limit, this will take a long time!)"
        else:
            print "Locating place with coldest temperature... (%s entries)" % limit
    for url in get_location_xml("", limit=limit):
        if len(forecasts) >= limit != 0:
            break
        if debug:
            print url
        # Skip static junk entry
        if url == "Engelsk":
            continue
        forecasts.append(weather_info(url, get_station(url).place))

    for f in forecasts:
        for itm in f:
            if itm.get("time_from").tm_hour < hour < itm.get("time_to").tm_hour:
                current = int(itm.get("temperature"))
                if current < score:
                    if debug:
                        print "New record: %s --> %s" % (score, current)
                    score = current
                    place = itm.get("place")
    if debug:
        print "Final score: %s" % score
    return [place, score]


def find_warmest(hour=13, limit=100, debug=False, info=False):
    """Prints Norway's warmest place on the given hour (default=13)"""
    score = -999999
    forecasts = []
    place = ""
    if info:
        if limit == 0:
            print "Locating place with warmest temperature... (no entry limit, this will take a long time!)"
        else:
            print "Locating place with warmest temperature... (%s entries)" % limit
    for url in get_location_xml("", limit=limit):
        if len(forecasts) >= limit != 0:
            break
        if debug:
            print url
        # Skip static junk entry
        if url == "Engelsk":
            continue
        forecasts.append(weather_info(url, get_station(url).place))

    for f in forecasts:
        for itm in f:
            if itm.get("time_from").tm_hour < hour < itm.get("time_to").tm_hour:
                current = int(itm.get("temperature"))
                if current > score:
                    if debug:
                        print "New record: %s --> %s" % (score, current)
                    score = current
                    place = itm.get("place")
    if debug:
        print "Final score: %s" % score
    return [place, score]


def find_extreme_places(hour=13, limit=100, debug=False, info=False):
    """Prints Norway's warmest and coldest place on the given hour (default=13)"""
    warmest = find_warmest(hour=hour, limit=limit, debug=debug, info=info)
    coldest = find_coldest(hour=hour, limit=limit, debug=debug, info=info)
    print "Norway's extreme places at %02d:00:" % hour
    if not warmest[0]:
        print "\tWarmest: Not found (!?)"
    else:
        print "\tWarmest: %s, %02d deg C" % (warmest[0], warmest[1])
    if not coldest[0]:
        print "\tColdest: Not found (!?)"
    else:
        print "\tColdest: %s, %02d deg C" % (coldest[0], coldest[1])

    return [warmest, coldest]