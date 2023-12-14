from fastapi import FastAPI, Request, Form
import json
import uvicorn
from rdflib import Graph
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import random
import requests
from utils import make_rig, get_rdg_properties
import re

HOST = "127.0.0.2"
PORT = 5000


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.post("/")
async def query(request: Request,
                url: str = Form(...),
                name: str = Form(...), 
                places: str = Form(...),
                bedrooms: str = Form(...),
                lakedist: str = Form(...),
                city: str = Form(...),
                citydist:int = Form(...),
                bookingday: str = Form(...),
                ndays: int = Form(...),
                maxshift: int = Form(...)):
    print(url,name, places, bedrooms, lakedist,city, citydist, bookingday,ndays,maxshift)
    mapping_values = {
    "bookedBy": name,
    "bookingStartDate": bookingday,
    "bookingDuration": ndays,  # Duration in days
    "maxShift": maxshift,  # Max shift in days
    "hasPlaces": places,  # Number of places
    "hasBedrooms": bedrooms,  # Number of bedrooms
    "distanceToLake": lakedist,  # Distance in meters
    "nearestCity": city,
    "distanceToCity": citydist, 
    # "numDays" : ndays #Extra Parameter
    }   
    response = requests.get(url)
    rdg = response.text
    print("rdg_val",rdg)
    
    with open('temp_rdg.ttl', 'wb') as file:  # Replace 'filename.ext' with the desired file name
        file.write(response.content)
    
    properties = get_rdg_properties("temp_rdg.ttl")
    print("Hello Properties",properties)
    rig = make_rig(rdg,mapping_values,properties)
    print("hello_rig",rig)
    rig_send_url = f"{url}/parse_rig"
    rig_send_response = requests.post(url=rig_send_url, data=rig)
    rrg_text = rig_send_response.text.replace("\\n", "").replace("\\t", "").replace("\\\\","")
    parsed_cottages = re.findall(r'sswap:mapsTo \[(.*?)\]', rrg_text)
    print("recieved RRG",parsed_cottages)
    cottage_images = []
    cottage_addresses = []
    booking_ids = []
    places = []
    bedrooms = []
    distlakes = []
    cities = []
    distcities = []
    bookernames = []
    stdates = []
    endates = []
    
    for parsed_cottage in parsed_cottages:
        address = re.findall(r'cot:hasAddress (.*?) ;', parsed_cottage)[0]
        image = re.findall(r'cot:hasImage (.*?) ;', parsed_cottage)[0]
        book_id = re.findall(r'cot:bookingNumber (.*?) ;', parsed_cottage)[0]
        place = re.findall(r'cot:hasPlaces (.*?) ;', parsed_cottage)[0]
        bedroom = re.findall(r'cot:hasBedrooms (.*?) ;', parsed_cottage)[0]
        distlake = re.findall(r'cot:distanceToLake (.*?) ;', parsed_cottage)[0]
        city = re.findall(r'cot:nearestCity (.*?) ;', parsed_cottage)[0]
        distcity = re.findall(r'cot:bookingNumber (.*?) ;', parsed_cottage)[0]
        bookername = re.findall(r'cot:bookedBy (.*?) ;', parsed_cottage)[0]
        book_id = re.findall(r'cot:bookingNumber (.*?) ;', parsed_cottage)[0]
        stdate = re.findall(r'cot:bookingStartDate (.*?) ;', parsed_cottage)[0]
        endate = re.findall(r'cot:bookingEndDate (.*?) ', parsed_cottage)[0]
        cottage_images.append(image)
        cottage_addresses.append(address)
        booking_ids.append(book_id)
        places.append(place)
        bedrooms.append(bedroom)
        distlakes.append(distlake)
        cities.append(city)
        distcities.append(distcity)
        bookernames.append(bookername)
        stdates.append(stdate)
        endates.append(endate)
    
    all_cottage_info = zip(cottage_images, cottage_addresses, booking_ids, places, bedrooms, distlakes, cities, distcities, bookernames, stdates, endates) 
    # name = re.findall(r'cot:bookedBy\s*"([^"]+)"', rig)
    return templates.TemplateResponse("index_sswap.html", {"request": request,
                                                     "booker_name":name,
                                                     "all_cottage_info":all_cottage_info})


@app.get("/")
async def view_page(request: Request):
    return templates.TemplateResponse("index_sswap.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run("mediator:app",reload=True, port=PORT, host=HOST)