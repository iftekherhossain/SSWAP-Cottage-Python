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
    "cot:bookedBy": name,
    "cot:bookingStartDate": bookingday,
    "cot:bookingDuration": ndays,  # Duration in days
    "cot:maxShift": maxshift,  # Max shift in days
    "cot:hasPlaces": places,  # Number of places
    "cot:hasBedrooms": bedrooms,  # Number of bedrooms
    "cot:distanceToLake": lakedist,  # Distance in meters
    "cot:nearestCity": city,
    "cot:distanceToCity": citydist,  # Distance in kilometers
    }   
    response = requests.get(url)
    # rdg_file =
    rdg = response.text
    print("rdg_val",rdg)
    
    with open('temp_rdg.ttl', 'wb') as file:  # Replace 'filename.ext' with the desired file name
        file.write(response.content)
    # print("jjjjjjjjjjjjjjjjjjjj",response)
    # rdg = rdg.replace("\\", "")
    # print("hello_rdg",rdg)
    properties = get_rdg_properties("temp_rdg.ttl")
    print("Hello Properties",properties)
    rig = make_rig(rdg,mapping_values)
    print("hello_rig",rig)
    rig_send_url = f"{url}/parse_rig"
    rig_send_response = requests.post(url=rig_send_url, data=rig)
    rrg_text = rig_send_response.text.replace("\\n", "").replace("\\t", "").replace("\\\\","")
    parsed_cottages = re.findall(r'sswap:mapsTo \[(.*?)\]', rrg_text)
    
    cottages = []
    cottage_images = []
    cottage_addresses = []
    booking_ids = []
    for parsed_cottage in parsed_cottages:
        cottage = re.findall(r'cot:hasName (.*?) ;', parsed_cottage)[0]
        address = re.findall(r'cot:hasAddress (.*?) ;', parsed_cottage)[0]
        image = re.findall(r'cot:hasImage (.*?) ;', parsed_cottage)[0]
        book_id = re.findall(r'cot:bookingNumber (.*?) ;', parsed_cottage)[0]
        cottages.append(cottage)
        cottage_images.append(image)
        cottage_addresses.append(address)
        booking_ids.append(book_id)
    
    all_cottage_info = zip(cottages,cottage_images,cottage_addresses,booking_ids) 
    # name = re.findall(r'cot:bookedBy\s*"([^"]+)"', rig)
    return templates.TemplateResponse("index_sswap.html", {"request": request,
                                                     "booker_name":name,
                                                     "all_cottage_info":all_cottage_info})


@app.get("/")
async def view_page(request: Request):
    return templates.TemplateResponse("index_sswap.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run("mediatorold:app",reload=True, port=PORT, host=HOST)