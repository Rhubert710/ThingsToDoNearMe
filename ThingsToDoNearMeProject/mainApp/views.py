from django.shortcuts import render, get_list_or_404
from django.http import HttpResponse, JsonResponse

from mainApp.models import *
import json, requests , datetime

from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

def indexDemo(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@ensure_csrf_cookie
def index(request):
    context={ 'pageTitle' : pageTitle} 
    # print(request.__dict__)
    # print(request.headers)
    return render(request, "mainApp/index.html", context)








def getEvents(request):

    lat , lon = get_my_user_Lat_Lon(request)
    print(lat , lon)
    if (lat == 0 and lon == 0 ):
        return JsonResponse( {'status' : 'error' , 'errorMessage': render_to_string('mainApp/modal_noLocation.html') }, safe=False)
    ## Get lat, lon from client ip
    # rl = requests.get(f'https://api.seatgeek.com/2/events?geoip={client_ip}&rnage=1mi&per_page=1&client_id=MzcwNDI1NTB8MTY5NTg3NDM1My4wNjYwMDU1')

    # datal = rl.json()
    # print(datal)
    # print(datal['meta']['geolocation']['lat'], data['meta']['geolocation']['lon'])
    ## Get Events from OUR DB
    myDbJson = list( Event.objects.filter(date__gte = datetime.date.today()).values() ) #Time on db seems to be three hours ahead of local time.(its UTC)
    # print(datetime.date.today()+datetime.timedelta(days=6))

    
    ## Get from seat geek api
    results_page_number, seatGeekJson = 0, []
    while(True):
        results_page_number += 1
        r = requests.get(f'https://api.seatgeek.com/2/events?lat={lat}&lon={lon}&datetime_local.gt={datetime.date.today()}&datetime_local.lte={datetime.date.today()+datetime.timedelta(days=6)}&per_page=50&page={results_page_number}&client_id=MzcwNDI1NTB8MTY5NTg3NDM1My4wNjYwMDU1')
        data = r.json()

        for o in data['events']:
            temp_obj = {}
            temp_obj['title'] = ''.join(o["title"].split('-')[:-1]) if len(o["title"].split('-')) > 2 else o["title"].split('-')[0]
            temp_obj['date'] = o["datetime_local"][:10]
            temp_obj['address'] = o["venue"]["name"]
            temp_obj['latitude'] = o['venue']["location"]["lat"]
            temp_obj['longitude'] = o['venue']['location']['lon']
            temp_obj['url'] = o['performers'][0]["url"]
            seatGeekJson.append(temp_obj)

        # seatGeekJson += list ( data['events'] )
        if len(data['events']) == 0:
            break
    # print(seatGeekJson)


    #Combine All Results
    response = { 'events' : list(myDbJson + seatGeekJson)}
    response['location'] = {'lat' : lat , 'lon' : lon}

    print(len(response))
    return JsonResponse( response , safe=False)

def addEventForm(request):
    return render(request, "mainApp/addEventForm.html", { 'pageTitle' : pageTitle})

def postEvent(request):
    
    p = request.POST.dict()
    newEvent = Event(title=p['titleInput'], description=p['descriptionInput'], date=p['dateInput'], address=p['addressInput'])

    #get geocode
    geocode = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={p["addressInput"]}&key=AIzaSyBsjbLLe2RaAjIzUe5lxKb7wLFvebnX2gY')
    # print(r.text)
    geocode_json= json.loads(geocode.text)
    # print(rj['results'][0]['geometry']['location'])
    # print(rj['results'][0]['geometry']['location']['lat'])

    newEvent.latitude = geocode_json['results'][0]['geometry']['location']['lat']
    newEvent.longitude = geocode_json['results'][0]['geometry']['location']['lng']

    newEvent.save()
    return render(request, "mainApp/index.html")











#### variables ####
pageTitle = 'Things-to-do-near-me!'


## FUNC GET CLIENT IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
    else:
       ip = request.META.get('REMOTE_ADDR')
    return ip

## FUNC GET USER LAT LON
def get_my_user_Lat_Lon(request):

    requestBody = json.loads(request.body)

    # if lat, lon
    try:
        
        lat, lon = requestBody['lattitude'] , requestBody['longitude']
        return lat, lon
    
    except: pass

    # if address
    try:
        
        geocode = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={requestBody["props"]["addressInput"]}&key=AIzaSyBsjbLLe2RaAjIzUe5lxKb7wLFvebnX2gY')
        # print(geocode.text)
        geocode_json= json.loads(geocode.text)
        print(geocode.text)
        # print(rj['results'][0]['geometry']['location'])
        # print(rj['results'][0]['geometry']['location']['lat'])
        try:
            lat = geocode_json['results'][0]['geometry']['location']['lat']
            lon = geocode_json['results'][0]['geometry']['location']['lng']
        except: return 0, 0 , 'mainApp/modal_noLocation.html'

        return lat, lon
    
    except: pass

    # else try ip
    try:
        print(3)
        client_ip = get_client_ip(request)
        r = requests.get(f'https://api.seatgeek.com/2/events?geoip={client_ip}&datetime_local={datetime.date.today()}&per_page=1&client_id=MzcwNDI1NTB8MTY5NTg3NDM1My4wNjYwMDU1')
        r_JSON = r.json()
        print(client_ip)
        print(r.json)
        lat = r_JSON['meta']['geolocation']['lat']
        lon = r_JSON['meta']['geolocation']['lon']

        return lat, lon

    #catch all
    except:
        return 0 , 0
        

