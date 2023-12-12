import rdflib

# Create a new graph
g = rdflib.Graph()

# Load the Turtle file
turtle_file = 'static/turtle_files/RDG.ttl'
g.parse(turtle_file, format='turtle')

# Dictionary to hold properties and their values
properties = {}

# Find hasMapping
for subject, predicate, object in g:
    # Convert subject, predicate, object to strings for easier handling
    subj_str = str(subject)
    pred_str = str(predicate)
    obj_str = str(object)
    if pred_str.split("/")[-1]=="hasMapping":
        hasMapping_Sub = obj_str
    # print("hello",subj_str,"--",pred_str,"--",obj_str)
properties = []
for subject, predicate, object in g:
    # Convert subject, predicate, object to strings for easier handling
    subj_str = str(subject)
    pred_str = str(predicate)
    obj_str = str(object)
    if subj_str == hasMapping_Sub and obj_str=='':
        print("helo",subj_str,"---",pred_str,"--",obj_str)
        properties.append(pred_str.split('/')[-1])
    
print(len(properties))