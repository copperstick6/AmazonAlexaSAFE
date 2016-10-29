#given to addresses, return the distance in meters.

import keys
import urllib.request
import json
import pprint
import sys
import codecs

def getWebUrl(address1, address2):
    s = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
    tempS = ""
    tempS2 = ""
    for i in str(address1):
        if(i == " "):
            tempS+="+"
        elif (i == ","):
            tempS+=""
        else:
            tempS+= i
    s+= tempS + "&destinations="
    for i in str(address2):
        if(i == " "):
            tempS2+="+"
        else:
            tempS2+= i
    tempKey = keys.GoogleMapsKey()
    s+=tempS2 + "&key=" + tempKey
    return s

def getDistance(address1, address2):
    webUrl = urllib.request.urlopen(getWebUrl(address1, address2))
    if (webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        s =obj["rows"][0]["elements"][0]["distance"]["value"]
        return s
def getUnFormattedLongLat(address1):
    s = "https://maps.googleapis.com/maps/api/geocode/json?address="
    tempString = ""
    for i in str(address1):
        if(i == " "):
            tempString+="+"
        else:
            tempString+=i
    s+=tempString + "&key=" + keys.GoogleMapsKey()
    webUrl = urllib.request.urlopen(s)
    if(webUrl.getcode()==200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        list1 = []
        list1.append(obj["results"][0]["geometry"]["location"]["lat"])
        list1.append(obj["results"][0]["geometry"]["location"]["lng"])
    return list1

def getFormattedLat(list1):
    return list1[0]
def getFormattedLong(list1):
    return list1[1]
