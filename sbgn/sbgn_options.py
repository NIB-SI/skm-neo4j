from libsbgnpy.libsbgnTypes import GlyphClass, ArcClass

'''Avalible Glyphs 

GlyphClass.UNSPECIFIED_ENTITY
GlyphClass.SIMPLE_CHEMICAL
GlyphClass.MACROMOLECULE
GlyphClass.NUCLEIC_ACID_FEATURE
GlyphClass.SIMPLE_CHEMICAL_MULTIMER
GlyphClass.MACROMOLECULE_MULTIMER
GlyphClass.NUCLEIC_ACID_FEATURE_MULTIMER
GlyphClass.COMPLEX
GlyphClass.COMPLEX_MULTIMER
GlyphClass.SOURCE_AND_SINK
GlyphClass.PERTURBATION
GlyphClass.BIOLOGICAL_ACTIVITY 
GlyphClass.PERTURBING_AGENT
GlyphClass.COMPARTMENT
GlyphClass.SUBMAP
GlyphClass.TAG
GlyphClass.TERMINAL
GlyphClass.PROCESS
GlyphClass.OMITTED_PROCESS
GlyphClass.UNCERTAIN_PROCESS
GlyphClass.ASSOCIATION
GlyphClass.DISSOCIATION
GlyphClass.PHENOTYPE
GlyphClass.AND
GlyphClass.OR
GlyphClass.NOT
GlyphClass.STATE_VARIABLE
GlyphClass.UNIT_OF_INFORMATION
GlyphClass.STOICHIOMETRY
GlyphClass.ENTITY
GlyphClass.OUTCOME
GlyphClass.OBSERVABLE
GlyphClass.INTERACTION
GlyphClass.ANNOTATION
GlyphClass.VARIABLE_VALUE
GlyphClass.IMPLICIT_XOR
GlyphClass.DELAY
GlyphClass.EXISTENCE
GlyphClass.LOCATION
GlyphClass.CARDINALITY
'''

'''Avalible Arcs

ArcClass.PRODUCTION
ArcClass.CONSUMPTION
ArcClass.CATALYSIS
ArcClass.MODULATION
ArcClass.STIMULATION
ArcClass.INHIBITION
ArcClass.ASSIGNMENT
ArcClass.INTERACTION
ArcClass.ABSOLUTE_INHIBITION
ArcClass.ABSOLUTE_STIMULATION
ArcClass.POSITIVE_INFLUENCE
ArcClass.NEGATIVE_INFLUENCE
ArcClass.UNKNOWN_INFLUENCE
ArcClass.EQUIVALENCE_ARC
ArcClass.NECESSARY_STIMULATION
ArcClass.LOGIC_ARC
'''


form_to_glyph = {
    "na": GlyphClass.SOURCE_AND_SINK,
    
    "metabolite":GlyphClass.SIMPLE_CHEMICAL,
    
    "protein":GlyphClass.MACROMOLECULE,
    "protein_active":GlyphClass.MACROMOLECULE,
    
    "gene":GlyphClass.NUCLEIC_ACID_FEATURE,
    "ncRNA":GlyphClass.NUCLEIC_ACID_FEATURE,       
    
    "process":GlyphClass.UNSPECIFIED_ENTITY,   
    "process_active":GlyphClass.UNSPECIFIED_ENTITY,
    
    "complex":GlyphClass.COMPLEX,       
    "complex_active":GlyphClass.COMPLEX, 
}


'''
These are translating complex component labels to 
SGBN glyphs. Some assumptions are made. Not all
labels included. 
'''
label_to_class = {
    "Metabolite":GlyphClass.SIMPLE_CHEMICAL,
    "MetaboliteFamily":GlyphClass.SIMPLE_CHEMICAL,
    
    "ExternalCoding":GlyphClass.MACROMOLECULE,
    "PlantCoding":GlyphClass.MACROMOLECULE,
    
    "Complex":GlyphClass.COMPLEX,        
    
    "Process":GlyphClass.UNSPECIFIED_ENTITY,           
    "PlantAbstract":GlyphClass.UNSPECIFIED_ENTITY,       
    "ExternalEntity":GlyphClass.UNSPECIFIED_ENTITY,       
}



form_to_state = {
    "na":None,
    "metabolite":None,
    
    "protein":"inactive",
    "protein_active":"active", 
    
    "gene":None,
    "ncRNA":None,         
    
    "process":"inactive",   
    "process_active":"active",
    
    "complex":"inactive",       
    "complex_active":"active", 
}


class_to_size  = { # w, h
    # reaction process nodes
    GlyphClass.PROCESS: (20, 20), 
    GlyphClass.ASSOCIATION: (20, 20),
    GlyphClass.DISSOCIATION: (20, 20),
    
    GlyphClass.SIMPLE_CHEMICAL: (60, 60),
    GlyphClass.MACROMOLECULE: (140, 60), 
    GlyphClass.NUCLEIC_ACID_FEATURE: (120, 60), 

    GlyphClass.COMPLEX: (140, 60), # h will be adjusted to fit subunits
    'complex_btw_h': 5,            # h btwn subunits
    GlyphClass.STATE_VARIABLE: (40, 15), 
    GlyphClass.UNSPECIFIED_ENTITY: (120, 120), 
    
    GlyphClass.COMPARTMENT: (500, 500), 
    
    GlyphClass.SOURCE_AND_SINK: (20, 20)
}


compartment_to_size = { # x y
    'cytoplasm': (1240, 1000),
    'chloroplast': (400, 480),
    'endoplasmic reticulum': (400, 480),
    'golgi apparatus': (400, 480),
    'nucleus': (400, 480),
    'peroxisome': (400, 480),
    'vacuole': (200, 480), 
    'mitochondrion': (200, 480), 
    'extracellular': (260, 1000) # fake
}


compartment_to_xy = {
    'cytoplasm': (0, 0),

    'chloroplast': (10, 10),
    'endoplasmic reticulum': (500, 10),

    'golgi apparatus': (10, 420),
    'nucleus': (500, 420),

    'peroxisome': (10, 830),
    'vacuole': (500, 830),

    'extracellular': (0, 1240),    # fake
    
    'mitochondrion': (200, 480), 
}


reaction_type_to_process = {
    "catalysis/auto-catalysis": GlyphClass.PROCESS,
    "cleavage/auto-cleavage": GlyphClass.PROCESS,
    "protein activation": GlyphClass.PROCESS,
    "degradation/secretion": GlyphClass.PROCESS,
    "translocation": GlyphClass.PROCESS,
    "undefined": GlyphClass.PROCESS,
    "protein deactivation": GlyphClass.PROCESS,

    "transcriptional/translational repression": GlyphClass.PROCESS,
    "transcriptional/translational induction": GlyphClass.PROCESS,

    "binding/oligomerisation": GlyphClass.ASSOCIATION,    
    "dissociation": GlyphClass.DISSOCIATION
}


''' edges between nodes and the reaction glyph'''
edge_to_arc = { 
    "catalysis/auto-catalysis": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.CATALYSIS
    },
    "cleavage/auto-cleavage": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.CATALYSIS
    },
    "protein activation": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.STIMULATION
    },
    "protein deactivation": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.STIMULATION # stimulates the deactivation
    },
    "degradation/secretion": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.CATALYSIS
    },
    "binding/oligomerisation": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.CATALYSIS        
    },
    "dissociation": {
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.CATALYSIS
    },       
    "translocation": { ##
        "PRODUCT":ArcClass.CONSUMPTION,
        "SUBSTRATE":ArcClass.PRODUCTION,        
        "MODIFIER":ArcClass.STIMULATION
    },
    "transcriptional/translational induction": { ## 
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.STIMULATION
    },
    "transcriptional/translational repression": { ##
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "MODIFIER":ArcClass.INHIBITION
    },    
    "undefined": {
        "ACTIVATES":ArcClass.STIMULATION,
        "INHIBITS":ArcClass.INHIBITION,
        "PRODUCT":ArcClass.PRODUCTION,
        "SUBSTRATE":ArcClass.CONSUMPTION,
        "TRANSLOCATE_FROM":ArcClass.CONSUMPTION,
        "TRANSLOCATE_TO":ArcClass.PRODUCTION,
        "MODIFIER":ArcClass.CATALYSIS
    },
}


