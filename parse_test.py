from rdflib import Graph
import rdflib
import re
import copy

f = open("static/turtle_files/RDG.ttl", "r")
rdg = f.read()
rdg_copy = copy.deepcopy(rdg)
print("hello",rdg)
# Define a mapping of properties to their expected values
mapping_values = {
    "cot:bookedBy": "Example Person",
    "cot:bookingStartDate": "2023-01-01",
    "cot:bookingDuration": "7",  # Duration in days
    "cot:maxShift": "3",  # Max shift in days
    "cot:hasPlaces": "5",  # Number of places
    "cot:hasBedrooms": "2",  # Number of bedrooms
    "cot:distanceToLake": "100",  # Distance in meters
    "cot:nearestCity": "Example City",
    "cot:distanceToCity": "10.5",  # Distance in kilometers
}

mapping_section = rdg.split('sswap:hasMapping [')[1].split(']')[0].split("sswap:mapsTo")[0]
mapping_section_prev = copy.copy(mapping_section)
print(mapping_section)
for key, value in mapping_values.items():
    mapping_section = re.sub(f'{key} ""', f'{key} "{value}"', mapping_section)
print("-----------------------------------")    
print(mapping_section)

fin_rdg = rdg_copy.replace(mapping_section_prev,mapping_section)

print("hola",fin_rdg)