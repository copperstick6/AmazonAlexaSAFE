import urllib.request
import json
import pprint
import sys
import codecs


def getLatLong():
    send_url = 'http://freegeoip.net/json'
    webUrl = urllib.request.urlopen(send_url)
    if (webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        a = []
        a.append(obj["latitude"])
        a.append(obj["longitude"])
    return a
