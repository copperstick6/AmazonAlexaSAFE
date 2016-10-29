import keys
import urllib.request
import json
import codecs
import latLong
import googleMapsDistance

#list1 is a list of a list of strings, where each element in the original list is
#the list of elements
#each element's list's elements are as follows: (All elements in array are string)
#(title, date, coordinates, disaster type, description, affected countries)

def getNaturalEvents():
	list1 = []
	s = "https://api.sigimera.org/v1/crises?auth_token="
	s+= keys.sigimeraAuth()
	webUrl  = urllib.request.urlopen(s)
	if(webUrl.getcode() == 200):
		counter = 0
		response = webUrl.read().decode('utf-8')
		theJSON = json.loads(response)
		for i in theJSON:
			list2 = []
			list2.append(i["dc_title"])
			list2.append(i["dct_modified"])
			s = str(i["foaf_based_near"][1]) + " , " + str(i["foaf_based_near"][0])
			list2.append(s)
			list2.append(i["dc_subject"][0])
			list2.append(i["dc_description"])
			k = ""
			if(i["gn_parentCountry"]!=" "):
				for j in i["gn_parentCountry"]:
					k+=str(i["gn_parentCountry"])
				list2.append(k)
			else:
				list2.append("N/A, no affected countries")
			list1.append(list2)

	return list1


def getCloseCrimes(address):
	s= 'http://api.spotcrime.com/crimes.json?lat='
	s+=str(googleMapsDistance.getUnFormattedLongLat(address)[0]) + "&"
	s+="lon=" + str(googleMapsDistance.getUnFormattedLongLat(address)[1])
	s+="&radius=2&key=."
	list1=[]
	list2 = []
	webUrl = urllib.request.urlopen(s)
	if(webUrl.getcode() == 200):
		response = webUrl.read().decode('utf-8')
		theJSON = json.loads(response)["crimes"]
		for i in theJSON:
			if(i["type"]!="Shooting" and i["type"]!="Other"):
				list2.append(i["address"])
				list2.append(i["lat"])
				list2.append(i["lon"])
				list2.append(i["type"])
				list2.append(i["date"])
				list1.append(list2)
				list2=[]
	return list1


def getAllCloseEvents(address):
	a = getCloseCrimes(address)
	s = ""
	try:
		s+="The closest event is a " +  str(a[0][3]) + " on " + str(a[0][0]) + " at " + str(a[0][4]) + "\n"
	except:
		s= "There was no event."
	return s

def getAllFarEvents(address):
	a = getFarCrimes(address)
	s = ""
	try:
		s+="The closest event is a " +  str(a[0][3]) + " on " + str(a[0][0]) + " at " + str(a[0][4]) + "\n"
	except:
		s= "There was no event."
	return s



#objects within list, in order: address, lat and long of activity, type, date,
def getFarCrimes(address):
	s= 'http://api.spotcrime.com/crimes.json?lat='
	s+=str(googleMapsDistance.getUnFormattedLongLat(address)[0]) + "&"
	s+="lon=" + str(googleMapsDistance.getUnFormattedLongLat(address)[1])
	s+="&radius=2&key=."
	list1=[]
	list2 = []
	webUrl = urllib.request.urlopen(s)
	if(webUrl.getcode() == 200):
		response = webUrl.read().decode('utf-8')
		theJSON = json.loads(response)["crimes"]
		for i in theJSON:
			if(i["type"]=="Shooting"):
				list2.append(i["address"])
				list2.append(i["lat"])
				list2.append(i["lon"])
				list2.append(i["type"])
				list2.append(i["date"])
				list1.append(list2)
				list2 = []
	return list1
