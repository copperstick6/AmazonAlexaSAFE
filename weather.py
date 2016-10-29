import keys
import urllib.request
import json
import codecs


#format of the returned list:
#dayPartName (nights and days), grassPollenIndex, grassPollenCategory, treePollenIndex, treePollenCategory,
#Ragweed PollenIndex, RagweedPollenCategory
def getPollen(days, lat, lon):
    if(((days == 3)or(days == 5)or(days == 7)or(days == 10)or(days == 15))==False):
        raise ValueError("Days must be 3,5,7,10,or 15")
    s = "https://api.weather.com/v2/indices/pollen/daypart/"
    s+= str(days) + "day?geocode="
    s+= str(lat) + "," + str(lon) + "&language=en-US&format=json&apiKey="
    s+= keys.blueChasmKey()
    webUrl = urllib.request.urlopen(s)
    list1 = []
    list2 = []
    if(webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        i = 0
        while i < (len(obj["pollenForecast12hour"]["daypartName"])):
            list2.append(obj["pollenForecast12hour"]["daypartName"][i])
            list2.append(obj["pollenForecast12hour"]["grassPollenIndex"][i])
            list2.append(obj["pollenForecast12hour"]["grassPollenCategory"][i])
            list2.append(obj["pollenForecast12hour"]["treePollenIndex"][i])
            list2.append(obj["pollenForecast12hour"]["treePollenCategory"][i])
            list2.append(obj["pollenForecast12hour"]["ragweedPollenIndex"][i])
            list2.append(obj["pollenForecast12hour"]["ragweedPollenCategory"][i])
            list1.append(list2)
            list2 = []
            i+=1
    return list1


#format of returned list:
#day, breathingIndex, breathingCategory
def getBreathing(days, lat, lon):
    if(((days == 3)or(days == 5)or(days == 7)or(days == 10)or(days == 15))==False):
        raise ValueError("Days must be 3,5,7,10,or 15")
    s = "https://api.weather.com/v2/indices/breathing/daypart/"
    s+= str(days) + "day?geocode="
    s+= str(lat) + "," + str(lon) + "&language=en-US&format=json&apiKey="
    s+= keys.blueChasmKey()
    webUrl = urllib.request.urlopen(s)
    list1 = []
    list2 = []
    if(webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        i = 0
        while i < (len(obj["breathingIndex12hour"]["daypartName"])):
            list2.append(obj["breathingIndex12hour"]["daypartName"][i])
            list2.append(obj["breathingIndex12hour"]["breathingIndex"][i])
            list2.append(obj["breathingIndex12hour"]["breathingCategory"][i])
            list1.append(list2)
            list2 = []
            i+=1
    return list1

#format of returned list:
#dat, achePain index, achePain category
def getAches(days,lat,lon):
    if(((days == 3)or(days == 5)or(days == 7)or(days == 10)or(days == 15))==False):
        raise ValueError("Days must be 3,5,7,10,or 15")
    s = "https://api.weather.com/v2/indices/achePain/daypart/"
    s+= str(days) + "day?geocode="
    s+= str(lat) + "," + str(lon) + "&language=en-US&format=json&apiKey="
    s+= keys.blueChasmKey()
    webUrl = urllib.request.urlopen(s)
    list1 = []
    list2 = []
    if(webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        i = 0
        while i < (len(obj["achesPainsIndex12hour"]["daypartName"])):
            list2.append(obj["achesPainsIndex12hour"]["daypartName"][i])
            list2.append(obj["achesPainsIndex12hour"]["achesPainsIndex"][i])
            list2.append(obj["achesPainsIndex12hour"]["achesPainsCategory"][i])
            list1.append(list2)
            list2 = []
            i+=1
    return list1

#list object is as follows:
#min temp, max temp, pressure, humidity, weather, cloudiness %, wind speeds
def getWeather(lat,lon):
    s = "http://api.openweathermap.org/data/2.5/forecast?lat="
    s+= str(lat) + "&lon=" + str(lon) + "&APPID=" + keys.openWeatherMap()
    webUrl = urllib.request.urlopen(s)
    list1 = []
    list2 = []
    if(webUrl.getcode() == 200):
        str_response = webUrl.read().decode('utf-8')
        obj = json.loads(str_response)
        i = 0;
        while(i<obj["cnt"]):
            a=obj["list"][i]["main"]["temp_min"]
            a=a*9/5 - 459.67
            list2.append(round(a,2))
            b = obj["list"][i]["main"]["temp_max"]
            b=b*9/5 - 459.67
            list2.append(round(b,2))
            list2.append(obj["list"][i]["main"]["humidity"])
            list2.append(obj["list"][i]["weather"][0]["description"])
            list2.append(obj["list"][i]["clouds"]["all"])
            list2.append(obj["list"][i]["wind"]["speed"])
            list1.append(list2)
            i+=1
        return list1
print(getWeather(33.74,-84.39))
print(getPollen(3,33.74,-84.39))
print(getBreathing(3,33.74,-84.39))
print(getAches(3,33.74,-84.39))
