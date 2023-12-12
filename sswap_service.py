from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse
import json
import uvicorn
from rdflib import Graph
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import random
import re
from utils import rdf_query

HOST = "127.0.0.3"
PORT = 8000


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/")
async def view_page(request: Request):
    file_path = "static/turtle_files/RDG.ttl"
    return FileResponse(path=file_path, media_type='application/octet-stream', filename="RDG.ttl")

@app.post("/parse_rig")
async def rig_parse(request: Request):
    received_rig = await request.body()
    print(received_rig)
    name = re.findall(r'cot:bookedBy\s*"([^"]+)"', str(received_rig))[0]
    bookingday = re.findall(r'cot:bookingStartDate\s*"([^"]+)"', str(received_rig))[0]
    places = int(re.findall(r'cot:hasPlaces\s*"([^"]+)"', str(received_rig))[0])
    ndays = int(re.findall(r'cot:bookingDuration\s*"([^"]+)"', str(received_rig))[0])
    maxshift = int(re.findall(r'cot:maxShift\s*"([^"]+)"', str(received_rig))[0])
    bedrooms = int(re.findall(r'cot:hasBedrooms\s*"([^"]+)"', str(received_rig))[0])
    lakedist = int(re.findall(r'cot:distanceToLake\s*"([^"]+)"', str(received_rig))[0])
    city = re.findall(r'cot:nearestCity\s*"([^"]+)"', str(received_rig))[0]
    citydist = int(re.findall(r'cot:distanceToCity\s*"([^"]+)"', str(received_rig))[0])
    print(name,places,bedrooms,lakedist,city,citydist,bookingday,ndays,maxshift)
    results,bookingendday = rdf_query(name,places,bedrooms,lakedist,city,citydist,bookingday,ndays,maxshift)
    print(results)
    booking_id = random.randint(0,10000)
    cottages = []
    cottage_images = []
    cottage_addresses = []
    BASE_RRG = """
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix sswap: <http://sswapmeet.sswap.info/sswap/> .
    @prefix cot: <http://www.semanticweb.org/dell/ontologies/2023/9/cottageOntology/> .
    @prefix resource: <http://localhost:8080/getCottageBookingService/> . 


    resource:getCottageBookingService
        rdf:type sswap:Resource ,
                cot:CottageBookingService;
        sswap:providedBy resource:resourceProvider ;
        sswap:name "Cottage Booking Service" ;
        sswap:oneLineDescription "A service that perform a search in a
        database of the cottages and return a set of bookings for the 
        cottages that fit the requirements set as input to the service“ ;
        sswap:operatesOn [
            rdf:type sswap:Graph ;
            sswap:hasMapping [
                rdf:type sswap:Subject, cot:Booking ;
                cot:bookedBy "Mr X" ;
                cot:bookingStartDate "2023-12-01"^^xsd:date ;
                cot:bookingDuration  "3"^^xsd:integer ;
                cot:maxShift "1"^^xsd:integer:
                
                rdf:type cot:Cottage ; 
                cot:hasPlaces "2"^^xsd:integer ;
                cot:hasBedrooms "2"^^xsd:integer ;
                cot:distanceToLake "300"^^xsd:integer ; 
                cot:nearestCity "Helsinki" ;
                cot:distanceToCity "6.5"^^xsd:float ; 
    """
    for row in results:
        # Each 'row' is a tuple of matched RDF terms
        # Accessing elements using the variable names from your SELECT clause
        temp_rrg = f"""
        sswap:mapsTo [
				rdf:type sswap:Object, cot:Cottage ;
				cot:hasName {str(row.cottageName)} ;
				cot:hasAddress {str(row.cottageAddress)} ;
				cot:hasImage {str(row.cottageImage)} ;
				cot:hasPlaces {places} ;
				cot:hasBedrooms {bedrooms} ;
				cot:distanceToLake {lakedist} ;
				cot:nearestCity {city} ;
				cot:distanceToCity {citydist} ;
                rdf:type cot:Booking ;
				cot:bookingNumber {random.randint(0,1000)} ;
				cot:bookedBy {name} ;
				cot:bookingStartDate {bookingday} ;
				cot:bookingEndDate  {bookingendday} .
            ]
        """
        BASE_RRG+=temp_rrg
        # BASE_RRG+="\n"
        
    print("hello_rrg",BASE_RRG.replace("\n", "").replace("\t", ""),"RRG END")
    return str(BASE_RRG)


    



if __name__ == '__main__':
    uvicorn.run("sswap_service:app",reload=True, port=PORT, host=HOST)