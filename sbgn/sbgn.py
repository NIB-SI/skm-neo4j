#!/usr/bin/env python
# coding: utf-8

'''
Requires:
---------

Connect to neo4j via py2neo
Read family-to-og-ID.json
Import sbgn_options.py
Create sqllite db

Sources:
--------
- Python libray:
https://libsbgn-python.readthedocs.io/en/latest/
- SBGN specifications:
https://sbgn.github.io/downloads/specifications/pd_level1_version2.pdf
- Examples:
https://github.com/sbgn/sbgn/tree/gh-pages/examples
'''


# import libsbgn and important SBGN types
import libsbgnpy.libsbgn as libsbgn
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass, Orientation
from libsbgnpy import render, utils
import random
import os
import json

from py2neo import Graph, RelationshipMatcher


import sqlite3

##############################################################
# Connect, load stuff
##############################################################

graph = Graph("http://localhost:7474")

from sbgn_options import *

with open("family-to-og-ID-v0.0.4.json", "r") as file_in:
    translate = json.load(file_in)

##############################################################
# neo4j helper stuff
##############################################################

def clean_labels(labels):
    if 'Family' in labels:
        labels.remove('Family') 
    return labels[0]

def get_complex_components(name):
    cy = '''MATCH (n)-[:COMPONENT_OF]->(:Complex {name:$name}) RETURN n.name AS name, labels(n) as label'''
    data = graph.run(cy, name=name).data()
    
    for d in data:
        d['label'] = clean_labels(d['label'])
    return data

##############################################################
# Sqllite stuff
##############################################################

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_db(db_file):
    conn  = create_connection(db_file)
    cur = conn.cursor()

    # Create table
    cur.execute('''CREATE TABLE specie_identifier(
                       identifier INTEGER PRIMARY KEY, 
                       name TEXT, 
                       form TEXT, 
                       location TEXT,
                       x REAL, 
                       y REAL,
                       UNIQUE(name, form, location)
                   )'''
               )

    cur.execute('''CREATE TABLE arc_identifier(
                       identifier INTEGER PRIMARY KEY, 
                       reaction_id TEXT, 
                       source_id TEXT, 
                       target_id TEXT,
                       UNIQUE(reaction_id, source_id, target_id)
                       )'''
               )

    cur.execute('''CREATE TABLE compartment_identifier(
                      identifier INTEGER PRIMARY KEY, 
                      name TEXT,
                      x REAL, 
                      y REAL,
                      UNIQUE(name)
                      )'''
               )

    cur.execute('''CREATE TABLE reaction_identifier(
                      identifier INTEGER PRIMARY KEY, 
                      reaction_id TEXT,
                      x REAL, 
                      y REAL,
                      UNIQUE(reaction_id)
                      )'''
               )

    conn.commit()
    conn.close()
    

def add_row(conn, data, super_class):
    #print(super_class, data)

    cur = conn.cursor()    
    
    if super_class == 'specie':
        sql = '''INSERT OR IGNORE 
                 INTO specie_identifier (name, form, location)
                 VALUES (?,?,?)'''
    
    elif super_class == 'arc':
        sql = '''INSERT OR IGNORE 
                 INTO arc_identifier (reaction_id, source_id, target_id)
                 VALUES (?,?,?)'''
    
    elif super_class == 'compartment':
        sql = '''INSERT OR IGNORE 
                 INTO compartment_identifier (name)
                 VALUES (?)'''
    
    elif super_class == 'reaction':
        sql = '''INSERT OR IGNORE 
                 INTO reaction_identifier (reaction_id)
                 VALUES (?)'''
    
    else:
        return
    
    cur.execute(sql, data)
    
    # this is not safe 
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.rowcount
    status = cur.rowcount 
    
    conn.commit()
    
    # cur.lastrowid would work if not also dealing with already entered
    identifier = get_identifier(conn, data, super_class)
    return identifier, status

def get_identifier(conn, data, super_class):
    #print(super_class, data)
    cur = conn.cursor()

    if super_class == 'arc':
        sql = '''SELECT identifier
                 FROM arc_identifier 
                 WHERE reaction_id = ?
                 AND source_id = ?
                 AND target_id = ?'''

    elif super_class == 'compartment':
        sql = '''SELECT identifier
                 FROM compartment_identifier 
                 WHERE name = ?'''

    elif super_class == 'reaction':
        sql = '''SELECT identifier
                 FROM reaction_identifier
                 WHERE reaction_id = ?'''        

    elif super_class == 'specie':
        sql = '''SELECT identifier
                 FROM specie_identifier
                 WHERE name = ?
                 AND form = ?
                 AND  location = ?'''

    else:
        return

    cur.execute(sql, data)

    try:
        row = next(iter(cur))
    except Exception as e:
        print(data, super_class, 'no identifier')
        raise e

    row_identifier = row[0]
    return f'{super_class[0]}{row_identifier}'

def set_coords(conn, data, super_class): 
    cur = conn.cursor()    
    
    if super_class == 'specie':
        sql = '''UPDATE specie_identifier
                 SET x = ?,
                     y = ?
                 WHERE name = ?
                   AND form = ?
                   AND location = ?'''
    
    elif super_class == 'compartment':
        sql = '''UPDATE compartment_identifier
                 SET x = ?,
                     y = ?
                 WHERE name = ?'''
    
    elif super_class == 'reaction':
        sql = '''UPDATE reaction_identifier 
                 SET x = ?,
                     y = ?
                 WHERE reaction_id = ?'''
    
    else:
        return
    
    #print(data)
    #print(sql)
    
    cur.execute(sql, data)
    conn.commit()
    return 

def get_coords(conn, identifier, super_class=None): 
    cur = conn.cursor()    
    
    
    if not super_class:
        super_class = {
            's':'specie',
            'c':'compartment',
            'r':'reaction'
        }[identifier[0]]
        
    data = (int(identifier[1:]), )
    
    if super_class == 'specie':
        sql = '''SELECT x, y
                 FROM specie_identifier
                 WHERE identifier = ?'''
    
    elif super_class == 'compartment':
        sql = '''SELECT x, y
                 FROM compartment_identifier
                 WHERE identifier = ?'''
    
    elif super_class == 'reaction':
        sql = '''SELECT x, y
                 FROM reaction_identifier 
                 WHERE identifier = ?'''
    
    else:
        return
    
    cur.execute(sql, data)
    try:
        row = next(iter(cur))
    except Exception as e:
        print(identifier, super_class, 'no identifier')
        raise e
    return row[0], row[1]

##############################################################
# SBGN stuff
##############################################################

def create_glyph(libsbgn_map, conn, 
                 name, class_, super_class, data, 
                 inside=None, state=None, children=None):
    '''Creates glyph (including sub-glyphs) and adds to libsbgn map
    
    Parameters
    ----------
    libsbgn_map : libsbgn.map
    
    conn : 
        sqllite
    name : str
        name of species (e.g. Water)
    class_ : 
        Glyph class
    super_class : 
        sqllite
    data : tuple
        sqllite
    inside : None or glyph
        optional containing compartment
    state : str
        state variable value
    children : list or None, default None
        (only applicalbe to complex, but will not complain)
    Returns
    -------
    identifier : str
        unique identifier of created glyph
    '''
    # make/get unique glyph id

    #print(super_class, data)
    identifier, status =  add_row(conn, data, super_class)

    if status != 0:
        #print(super_class, data)
        # it was added to the db, now add the glyph as well
        g = libsbgn.glyph(class_=class_, id=identifier)

        if name:
            g.set_label(libsbgn.label(text=name))

        if inside:
            inside_identifier = compartment_glyph(libsbgn_map, conn, inside)
            if inside_identifier is not None:
                g.set_compartmentRef(inside_identifier)

        if state:
            state_identifier = f'{identifier}.state'
            state_var = libsbgn.glyph(class_=GlyphClass.STATE_VARIABLE, id=state_identifier)
            state_var.set_state(libsbgn.stateType(state))
            g.add_glyph(state_var)

        add_h = 0
        if (children is None):
            children = []
        for i, (child_name, child_class) in enumerate(children):
            child_identifier = f'{identifier}.c{i}'
            child = libsbgn.glyph(class_=child_class, id=child_identifier)
            child.set_label(libsbgn.label(text=child_name))
            child_w, child_h = class_to_size[child_class] 
            child.set_bbox(libsbgn.bbox(x=110, y=25, w=100, h=40))
            g.add_glyph(child)
            add_h += child_h

        # if children, adjust h
        w, h = class_to_size[class_]
        if len(children) > 0:
            h = h + add_h + class_to_size['complex_btw_h'] * (len(children)-1)

        if class_ == GlyphClass.COMPARTMENT:
            w, h = compartment_to_size[name]
            x, y = compartment_to_xy[name]

        else:
            # x ~ w, y~ h
            parent_x0, parent_y0 = compartment_to_xy[inside]
            parent_delta_x, parent_delta_y = compartment_to_size[inside]
            parent_x1, parent_y1 = parent_x0 + parent_delta_x, parent_y0 + parent_delta_y

            x = random.randint(parent_x0, parent_x1 - w)
            y = random.randint(parent_y0, parent_y1 - h)

        g.set_bbox(libsbgn.bbox(w=w, h=h, x=x, y=y))

        libsbgn_map.add_glyph(g)

        data = (x, y, *data)
        set_coords(conn, data, super_class)

    return identifier

    
def compartment_glyph(libsbgn_map, conn, name):
    '''Create a glyph representing a cellular compartment
    
    Parameters
    ----------
    name : str
        name of new compartmant
    inside : None or str
        optional name of containing apartment
    
    Returns
    -------
    identifier : int
    '''
    
    if name == 'extracellular':
        return None

    class_ = GlyphClass.COMPARTMENT
    data = (name,)

    inside = None if name == 'cytoplasm' else 'cytoplasm'
    return create_glyph(
        libsbgn_map, conn, name, class_, 'compartment', data, inside=inside
    )
    
def node_glyph(libsbgn_map, conn, name, form, location):
    '''Create a glyph representing a model species
    
    Parameters
    ----------
    node_name : str
        name of species (e.g. Water)
    node_form : str
        molecular form (e.g. protein, complex, metabolite)
    inside : None or glyph
        optional containing apartment
    
    Returns
    -------
    g : glyph
    '''
    
    class_ = form_to_glyph[form]
    state = form_to_state[form]

    children = []
    if class_ == GlyphClass.COMPLEX:
        components = get_complex_components(name)
        children.extend(
            (child['name'], label_to_class[child['label']])
            for child in components
        )
    if location is None:
        #print('location was none', end='\t')
        location = 'cytoplasm'
        #print(f'now location is {location}')
    location = location.replace("putative:", "")

    data = (name, form, location)
    return create_glyph(
        libsbgn_map,
        conn,
        name,
        class_,
        'specie',
        data,
        inside=location,
        state=state,
        children=children,
    )


def reaction_glyph(libsbgn_map, conn, reaction_id, class_, location):
    '''Create a glyph representing a reaction (process)
    
    Parameters
    ----------
    node_name : str
        name of species (e.g. Water)
    node_form : str
        molecular form (e.g. protein, complex, metabolite)
    inside : None or glyph
        optional containing apartment
    
    Returns
    -------
    g : glyph
    '''
    
    #TODO ports

    if location is None:
        location = 'cytoplasm'
    location = location.replace("putative:", "")


    data = (reaction_id,)
    return create_glyph(
        libsbgn_map, conn, None, class_, 'reaction', data, inside=location
    )


def reaction_arc(libsbgn_map, conn, source_id, target_id, reaction_id, class_):
    '''Create an arc representing (part of) a reaction
    
    Parameters
    ----------
    source_id : str
        source glyph identifier
    target_id : str
        target glyph identifier

    Returns
    -------
    g : glyph
    '''
    
    data = (reaction_id, source_id, target_id)
    identifier, status =  add_row(conn, data, 'arc')

    if status != 0:
        # make unique arc id
        a = libsbgn.arc(class_=class_, 
                        source=source_id, target=target_id, 
                        id=identifier)

        source_x, source_y = get_coords(conn, source_id)
        a.set_start(libsbgn.startType(x=source_x+5, y=source_y+5))

        target_x, target_y = get_coords(conn, target_id)
        a.set_end(libsbgn.endType(x=target_x+5, y=target_y+5))

        libsbgn_map.add_arc(a)

    return identifier


def add_reaction(libsbgn_map, conn, reaction_id, edge_list):
   
    # each reaction has> >=~4 nodes and >=3 arcs
    # substrate 1/+, product 1/+, process 1, modifier 1/+ nodes
    # consumption, production and modulation arcs

    substrates = set()
    products = set()
    modifiers = set()  

    reaction_type = edge_list[0]['reaction_type']
    process_glyph_class = reaction_type_to_process[reaction_type]

    for edge in edge_list:
        
        edge_type = next(iter(edge.types())) # edges only have 1 type     

        if edge_type in ['SUBSTRATE', 'TRANSLOCATE_FROM']:
            
            # (1) source is SUBSTRATE
            key = 'source'
            name = translate[reaction_id][edge.start_node['name']]
            location = edge[f'{key}_location']
            form = edge[f'{key}_form']
            substrates.update([(name, form, location)])

            # (2) target is MODIFIER if not Pseudo node
            if "PseudoNode" not in edge.end_node.labels:
                key = 'target'
                name = translate[reaction_id][edge.end_node['name']]
                location = edge[f'{key}_location']
                form = edge[f'{key}_form']        
                modifiers.update([(name, form, location)])

        elif edge_type in ['PRODUCT', 'TRANSLOCATE_TO']:
            
            # (1) source is MODIFIER if not Pseudo node
            if "PseudoNode" not in edge.start_node.labels:
                key = 'source'
                name = translate[reaction_id][edge.start_node['name']]
                location = edge[f'{key}_location']
                form = edge[f'{key}_form']        
                modifiers.update([(name, form, location)])

            # (2) target is PRODUCT
            key = 'target'
            name = translate[reaction_id][edge.end_node['name']]
            location = edge[f'{key}_location']
            form = edge[f'{key}_form']
            products.update([(name, form, location)])

        elif edge_type in  ['INHIBITS',  'ACTIVATES']:
            # (1) source is MODIFIER
            key = 'source'
            name = translate[reaction_id][edge.start_node['name']]
            location = edge[f'{key}_location']
            form = edge[f'{key}_form']
            modifiers.update([(name, form, location)])

            # (1) target is SUBSTRATE
            key = 'target'
            name = translate[reaction_id][edge.end_node['name']]
            location = edge[f'{key}_localisation']
            form = edge[f'{key}_form']        
            substrates.update([(name, form, location)])

            # (2) product_property is PRODUCT
            key = 'product'
            location = edge[f'{key}_location']
            form = edge[f'{key}_form']        
            products.update([(name, form, location)])

    print(reaction_id, reaction_type, substrates, products, modifiers)

    base_location = next(iter(substrates))[2]        

    if reaction_type == 'degradation/secretion':
        name = "empty set"
        form = 'na'
        products.update([(name, form, base_location)])

    elif reaction_type == 'undefined':
        print("undefined reaction")
        return

    # FINALLY enter the reaction

    '''
                    (modifier)
                         |
                         |
                        \|/
    (substrate)----[process/reaction]---->(product)
    '''   

    # (1) process glyph   
    process_identifier = reaction_glyph(libsbgn_map, conn, reaction_id, 
                                                              process_glyph_class, base_location)

    # (2) substrate glyphs and arcs
    for (name, form, location) in substrates:
        #print('substrate:  ',   name, form, location)
        substrate_identifier = node_glyph(libsbgn_map, conn, name, form, location)

        arc_class = edge_to_arc[reaction_type]['SUBSTRATE']
        reaction_arc(libsbgn_map, conn, substrate_identifier, process_identifier,reaction_id, arc_class)

    # (3) product glyphs and arcs
    for (name, form, location) in products:
        #print('product:  ', name, form, location)
        product_identifier = node_glyph(libsbgn_map, conn, name, form, location)

        arc_class = edge_to_arc[reaction_type]['PRODUCT']
        reaction_arc(libsbgn_map, conn, process_identifier, product_identifier, reaction_id, arc_class)

    # (4) modifier glyphs and arcs 
    for (name, form, location) in modifiers:
        #print('modifier:  ',   name, form, location)
        modifier_identifier = node_glyph(libsbgn_map, conn, name, form, location)

        arc_class = edge_to_arc[reaction_type]['MODIFIER']
        reaction_arc(libsbgn_map, conn, modifier_identifier, process_identifier, reaction_id, arc_class)
    

def main():
    reactions = graph.run("MATCH ()-[r]-() WHERE EXISTS(r.reaction_id) RETURN DISTINCT r.reaction_id").data()
    reactions = {r['r.reaction_id'] for r in reactions}

    edge_matcher = RelationshipMatcher(graph)


    dbi = 0
    while os.path.exists(f"sbgn_interim_db_{dbi}.sqllite"):
        dbi += 1


    db_file = f"sbgn_interim_db_{dbi}.sqllite"
    create_db(db_file)
    conn = create_connection(db_file)

    edge_matcher = RelationshipMatcher(graph)
    # create empty sbgn
    sbgn = libsbgn.sbgn()

    # create map, set language and set in sbgn
    libsbgn_map = libsbgn.map()
    libsbgn_map.set_language(Language.PD)
    sbgn.set_map(libsbgn_map)

    # create a bounding box for the map
    box = libsbgn.bbox(x=0, y=0, w=1500, h=1000)
    libsbgn_map.set_bbox(box)

    with conn:
        for reaction_id in reactions:
            edge_list = edge_matcher.match(reaction_id=reaction_id).all()
            add_reaction(libsbgn_map, conn, reaction_id, edge_list)

    sbgn_str = utils.write_to_string(sbgn)
    sbgn.write_file("PIS-v0.0.4-sbgn.xml")

if __name__ == '__main__':
    main()