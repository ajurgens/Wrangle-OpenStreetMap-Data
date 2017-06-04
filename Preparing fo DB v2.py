# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 14:23:39 2017

@author: alina83s
"""




import csv
import codecs
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "oahu_data.osm"

NODES_PATH = "nodes_05jan.csv"
NODE_TAGS_PATH = "nodes_tags_05jan.csv"
WAYS_PATH = "ways_05jan.csv"
WAY_NODES_PATH = "ways_nodes_05jan.csv"
WAY_TAGS_PATH = "ways_tags_05jan.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
state_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
city_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Honolulu", "Hawaii", "Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Highway", "Way", "Loop", "Walk", "King"]

# UPDATE THIS VARIABLE
mapping = {
            "HI": "Hawaii",
            "hi": "Hawaii",
            "Hi": "Hawaii",
            "Honolulu, Hawaii": "Honolulu",
            "HI": " ",
            "honolulu": "Honolulu",
            "Honlulu": "Honolulu",
            "Honolulu": "Honolulu",
            "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Ave." : "Avenue",
            "Rd" : "Road",
            "Rd." : "Road",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Cir" : "Circle",
            "Cir." : "Circle",
            "Ct" : "Court",
            "Ct." : "Court",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "Pl" : "Place",
            "Pl." : "Place",
            "Hwy" : "Highway",
            "Pkwy" : "Parkway",
            "highway": "Highway",
            "king" : "King"
        }

badzip = { "HI ": " "
           }



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def update_name(name, mapping):
    for a in mapping:
        if a == street_type_re.search(name).group():
            name = re.sub(street_type_re, mapping[a],name)
    return name
    
    
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
       


#update the postcodes

# create the dict to put zipcodes into
def add_to_dict(data_dict, item):
    data_dict[item] += 1



# find the zipcodes
def get_postcode(element):
    if (element.attrib['k'] == "addr:postcode"):
        postcode = element.attrib['v']
        return postcode


def update_postal(postcode):
    for v in badzip:
        if postcode is None:
            continue
        else:
            if re.match(v,postcode):
                postcode = postcode.replace(v,badzip[v])
    return postcode



# put the list of zipcodes into dict
def audit(osmfile):
    osm_file = open(osmfile, "r")
    data_dict = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                
                if get_postcode(tag):
                    postcode = get_postcode(tag)
                    #print postcode
                    postcode = update_postal(postcode)
                    add_to_dict(data_dict, postcode)
    
    return data_dict
        
 


# test the zipcode audit and dict creation
def test():
    cleanzips = audit(osmfile)
    pprint.pprint(dict(cleanzips))
            

            

    
    
#update city name
def audit_city_type(city_types, city_name):
    m = city_type_re.search(city_name)
    if m:
        city_type = m.group()
        if city_type not in expected:
            city_types[city_type].add(city_name)


def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    city_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city_name(tag):
                    audit_city_type(city_types, tag.attrib['v'])
    osm_file.close()
    return city_types
    
    


def update_city_name(name, mapping):
    m = city_type_re.search(name)
    if m:
        city_type = m.group()
        if city_type in mapping.keys():
            if m not in expected:
                name = re.sub(m.group(), mapping[m.group()], name)
    return name

  


#update state
def audit_state_type(state_types, state_name):
    m = state_type_re.search(state_name)
    if m:
        state_type = m.group()
        if state_type not in expected:
            state_types[state_type].add(state_name)


def is_state_name(elem):
    return (elem.attrib['k'] == "addr:state")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    state_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_state_name(tag):
                    audit_state_type(state_types, tag.attrib['v'])
    osm_file.close()
    return state_types
    
    


def update_state_name(name, mapping):
    m = state_type_re.search(name)
    if m:
        state_type = m.group()
        if state_type in mapping.keys():
            if m not in expected:
                name = re.sub(m.group(), mapping[m.group()], name)
    return name

def test():
    st_types = audit(OSM_PATH)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    if element.tag == 'node':
        node_attribs = {}    
        tags = []
        
        for item in NODE_FIELDS:
            try:
                node_attribs[item] = element.attrib[item]
            except:
                node_attribs[item] = "0000000"

        for tag in element.iter("tag"):  
 
            match_prob = PROBLEMCHARS.search(tag.attrib['k'])
            if not match_prob:
                global node_tag_dict
                node_tag_dict = {} 
                node_tag_dict['id'] = element.attrib['id'] 
                node_tag_dict['value'] = tag.attrib['v']  

                m = LOWER_COLON.search(tag.attrib['k'])
                if not m:
                    node_tag_dict['type'] = 'regular'
                    node_tag_dict['key'] = tag.attrib['k']
                else:
                    chars_before_colon = re.findall('^(.+):', tag.attrib['k'])
                    chars_after_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])

                    node_tag_dict['type'] = chars_before_colon[0]
                    node_tag_dict['key'] = chars_after_colon[0]
                    if node_tag_dict['type'] == "addr" and node_tag_dict['key'] == "street":
                        node_tag_dict['value'] = update_name(tag.attrib['v'], mapping) 
                    elif node_tag_dict['type'] == "addr" and node_tag_dict['key'] == "postcode":
                        node_tag_dict['value'] = update_postal(tag.attrib['v']) 
                    elif node_tag_dict['type'] == "addr" and node_tag_dict['key'] == "state":
                        node_tag_dict['value'] = update_state_name(tag.attrib['v'], mapping)
                    elif node_tag_dict['type'] == "addr" and node_tag_dict['key'] == "city":
                        node_tag_dict['value'] = update_city_name(tag.attrib['v'], mapping)
            tags.append(node_tag_dict)
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        way_attribs = {}
        way_nodes = []
        tags = []  
    
        for item in WAY_FIELDS:
            way_attribs[item] = element.attrib[item]
    
        for tag in element.iter("tag"):  
 
            match_prob = PROBLEMCHARS.search(tag.attrib['k'])
            if not match_prob:
                way_tag_dict = {}
                way_tag_dict['id'] = element.attrib['id'] 
                way_tag_dict['value'] = tag.attrib['v']  

                m = LOWER_COLON.search(tag.attrib['k'])
                if not m:
                    way_tag_dict['type'] = 'regular'
                    way_tag_dict['key'] = tag.attrib['k']
                else:
                    chars_before_colon = re.findall('^(.+?):+[a-z]', tag.attrib['k'])
                    chars_after_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])

                    way_tag_dict['type'] = chars_before_colon[0]
                    way_tag_dict['key'] = chars_after_colon[0]
                    if way_tag_dict['type'] == "addr" and way_tag_dict['key'] == "street":
                        way_tag_dict['value'] = update_name(tag.attrib['v'], mapping) 
                    elif way_tag_dict['type'] == "addr" and way_tag_dict['key'] == "postcode":
                        way_tag_dict['value'] = update_postal(tag.attrib['v'])
                    elif way_tag_dict['type'] == "addr" and way_tag_dict['key'] == "state":
                        way_tag_dict['value'] = update_state_name(tag.attrib['v'], mapping)
                    elif way_tag_dict['type'] == "addr" and way_tag_dict['key'] == "city":
                        way_tag_dict['value'] = update_city_name(tag.attrib['v'], mapping)    
            tags.append(way_tag_dict)
        count = 0
        for tag in element.iter("nd"):  
            way_nd_dict = {}
            way_nd_dict['id'] = element.attrib['id'] 
            way_nd_dict['node_id'] = tag.attrib['ref'] 
            way_nd_dict['position'] = count  
            count += 1
            
            way_nodes.append(way_nd_dict)
    
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)