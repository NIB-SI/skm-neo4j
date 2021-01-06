import numpy as np
import pandas as pd

def component_node_query(file_name, labels, 
                         n_name="line.NodeName"
                        ):
    
    if type(labels) == list:
        node_label = ':' + ':'.join(labels)
    else:
        node_label = ':' + labels
    
    key = {"file_name":file_name, 
           "node_label":node_label, 
           "name":n_name}

    species_str = ""
    for species in ['ath', 'nbe', 'nta', 'stu', 'osa']:
        species_str += "{species}_homologues:split(line.{species}_homolog, ','),\n".format(species=species)

    
    
    q = '''USING PERIODIC COMMIT 500
           LOAD CSV WITH HEADERS FROM  'file:///{file_name}' AS line FIELDTERMINATOR '\t'
           CREATE (p{node_label}   {{ 
                name:{name}, 
                added_by:line.AddedBy,
                family:line.Family, 
                clade:line.Clade, 
                description:line.NodeDescription, 
                additional_information: line.AdditionalInfo, 
                
                {species_str}

                gmm_ocd:line.GMM_OCD1,
                gmm_description:line.GMM_Description,
                gmm_link:line.GMM_OCD, 
                gmm_shortname:line.GMM_ShortName, 
                gmm_synonyms:split(line.GMM_Synonyms, ","),
                
                external_database:line.ExternalDB,
                chebi_identifier:line.chebi_identifier,
                pubchem_identifier:line.pubchem_identifier,
                
                process:line.Process,
                model_version:line.ModelV,
               
                classification:line.classification
            }})'''.format(**key, species_str=species_str)
    
    return q



def make_create_edge_query(file_name, edge_type,
                           source_label="", target_label="",
                           source_name="line.source_name", target_name="line.target_name",
                           source_compartment="line.source_compartment", target_compartment="line.target_compartment",
                           source_form="line.source_form", target_form="line.target_form"
                          ):

    if not source_label == "":
        source_label = ':' + source_label
        
    if not target_label == "":
        target_label = ':' + target_label
                
    key ={"file_name":file_name, "edge_type":edge_type,
          "source_label":source_label, "target_label":target_label,
          "source_name":source_name, "target_name":target_name, 
          "source_compartment":source_compartment, "target_compartment":target_compartment,
          "source_form":source_form, "target_form":target_form}
    
    q = '''USING PERIODIC COMMIT 500
           LOAD CSV WITH HEADERS FROM  'file:///{file_name}' AS line FIELDTERMINATOR '\t'
           
           MATCH (source{source_label} {{ name:{source_name}}}),
                 (target{target_label} {{ name:{target_name}}})
           
           CREATE (source)-[:{edge_type} {{
                        added_by:line.AddedBy,
                        observed_species:line.observed_species, 
                        also_observed_in:split(line.also_observed_in, ","),
                        additional_information: line.AdditionalInfo, 
                        comment:line.Comment,
                        process:line.Process, 
                        reaction_effect:line.ReactionEffect,
                        trust_level:line.trust_level, 
                        literature_sources:line.literature_sources,
                        reaction_type:line.reaction_type,
                        reaction_mechanism:line.Modifications, 
                        model_version:line.ModelV,
                    
                        source_compartment:{source_compartment},
                        target_compartment:{target_compartment},                        
                        source_form:{source_form},
                        target_form:{target_form}
                        }}]->(target)'''.format(**key)

    return q


def pseudo_node_query(file_name, name="line.RxID", reaction_id="line.RxID"):
    
    key = {"file_name":file_name, 
           "name":name, 
          "reaction_id":reaction_id, 
          "label":"PseudoNode"}
    
    q = '''USING PERIODIC COMMIT 500
           LOAD CSV WITH HEADERS FROM  'file:///{file_name}' AS line FIELDTERMINATOR '\t'
           CREATE (p:{label}   {{ 
                name:{name}, 
                reaction_id:{reaction_id}, 

                added_by:line.AddedBy,
                process:line.Process,
                model_version:line.ModelV,
                additional_information:line.AdditionalInfo
            }})'''.format(**key)    

    return q





all_species = ['ath', 'stu', 'osa']
homologue_cols = [f"_{x}_homologues" for x in all_species]
substrate_cols = [ f'substrate{x}' for x in ['_newID', '_label', '_form', '_localisation']] +\
                [f"substrate{x}" for x in homologue_cols]
catalyst_cols = [ f'catalyst{x}' for x in ['_newID', '_label', '_form', '_localisation']] +\
                [f"catalyst{x}" for x in homologue_cols] 
product_cols = [ f'product{x}' for x in ['_newID', '_label', '_form', '_localisation']] +\
                [f"product{x}" for x in homologue_cols]                


def dict_to_str(d):
    s = ""
    i = 0
    for key, value in d.items():
        s += " "*24*i + f"{key}:{value},\n"
        i = 1
    return s


def get_keys(key_prefix, line_prefix):
    keys = {}
    for value in ["form", "localisation"]: 
        keys[f"{key_prefix}_{value}"] = f"line.{line_prefix}_{value}"
    for species in all_species:
        keys[f"{key_prefix}_{species}_homologues"] = f"split(line.{line_prefix}_{species}_homologues, ',')"
    
    return keys

def make_create_reaction_edge_query(file_name, edge_type, 
                                    source_prefix, target_prefix, 
                                    source_label="", target_label="", 
                                    source_name=None, 
                                    target_name=None):

    if not source_label == "":
        source_label = ':' + source_label
        
    if not target_label == "":
        target_label = ':' + target_label
                
    key ={"file_name":file_name, "edge_type":edge_type,
          "source_label":source_label, "target_label":target_label}
    
    
    source_str = dict_to_str(get_keys("source", source_prefix))
    target_str = dict_to_str(get_keys("target", target_prefix))

    if source_name:
        key['source_name'] = source_name
    else:
        key['source_name'] = f"line.{source_prefix}_name"
    if target_name:
        key['target_name'] = target_name
    else:
        key['target_name'] = f"line.{target_prefix}_name"                
    
    q = '''USING PERIODIC COMMIT 500
           LOAD CSV WITH HEADERS FROM  'file:///{file_name}' AS line FIELDTERMINATOR '\t'
           
           MATCH (source{source_label} {{ name:{source_name}}}),
                 (target{target_label} {{ name:{target_name}}})
           
           CREATE (source)-[:{edge_type} {{

                        {source_str}
                        {target_str}

                        added_by:line.AddedBy,
                        reaction_id:line.RxID,
                        observed_species:line.observed_species, 
                        also_observed_in:split(line.also_observed_in, ","),
                        additional_information: line.AdditionalInfo, 
                        comment:line.Comment,
                        process:line.Process, 
                        reaction_effect:line.ReactionEffect,
                        trust_level:line.trust_level, 
                        literature_sources:line.literature_sources,
                        reaction_type:line.reaction_type,
                        reaction_mechanism:line.Modifications, 
                        reaction_kinetics:line.kinetics, 
                        model_version:line.ModelV
                        }}]->(target)'''.format(**key, source_str=source_str, target_str=target_str)

    return q


def make_create_requlatory_edge_query(file_name, edge_type, 
                                    source_prefix, target_prefix, 
                                    source_label="", target_label="", 
                                    source_name=None, 
                                    target_name=None):

    if not (edge_type in ['ACTIVATES', 'INHIBITS']):
        return 
    
    if not source_label == "":
        source_label = ':' + source_label
        
    if not target_label == "":
        target_label = ':' + target_label
                
    key ={"file_name":file_name, "edge_type":edge_type,
          "source_label":source_label, "target_label":target_label}
    
    
    source_str = dict_to_str(get_keys("source", source_prefix))
    target_str = dict_to_str(get_keys("target", target_prefix))

    if source_name:
        key['source_name'] = source_name
    else:
        key['source_name'] = f"line.{source_prefix}_name"
    if target_name:
        key['target_name'] = target_name
    else:
        key['target_name'] = f"line.{target_prefix}_name"                
    
    q = '''USING PERIODIC COMMIT 500
           LOAD CSV WITH HEADERS FROM  'file:///{file_name}' AS line FIELDTERMINATOR '\t'
           
           MATCH (source{source_label} {{ name:{source_name}}}),
                 (target{target_label} {{ name:{target_name}}})
           
           CREATE (source)-[:{edge_type} {{

                        {source_str}
                        {target_str}

                        added_by:line.AddedBy,
                        reaction_id:line.RxID,
                        observed_species:line.observed_species, 
                        also_observed_in:split(line.also_observed_in, ","),
                        additional_information: line.AdditionalInfo, 
                        comment:line.Comment,
                        process:line.Process, 
                        reaction_effect:line.ReactionEffect,
                        trust_level:line.trust_level, 
                        literature_sources:line.literature_sources,
                        reaction_type:line.reaction_type,
                        reaction_mechanism:line.Modifications, 
                        reaction_kinetics:line.kinetics, 
                        model_version:line.ModelV
                        }}]->(target)'''.format(**key, source_str=source_str, target_str=target_str)

    return q




empty_strings = ["-", "?", "[empty]", "nan", "n.a.", np.nan, '[undefined]', '']


def only_asci(x):
    return "".join([character for character in x if character.isascii()])


def string_to_nice_string(x, delim="|"):
    if not (x in empty_strings):
        nice_list = [y.strip() for y in str(x).split(delim)]
        return ",".join(nice_list)
    else:
        return ""

def lower_string(x):
    if not (x in empty_strings):
        return x.lower().strip()
    else:
        return ""   
    
def get_latest_model(x):
    if x.shape[0] == 1:
        m = x.iloc[0]
    else:
        prev_v = (0, 0)
        m = ''
        for _, r in x.iteritems():
            v = tuple((int(i) for i in r[1:].split('.') if i != 'NA'))
            if v > prev_v:
                m = r
            prev_v = v
    if m == 'vNA':
        m = 'v0.0'
    return m


def list_to_string(x):
    l = []
    for s in x:
        s = str(s)
        if not s in empty_strings:
            l.append(s)
    
    return ",".join(l)

def get_second_item(x, delim="/"):
    if not (x in empty_strings):
        nice_list = [y.strip().lower() for y in str(x).split(delim)]
        if len(nice_list) == 1:
            return nice_list[0]
        else:
            return nice_list[1]
    else:
        return ""

def rest_of_items(x, delim="/"):
    if not (x in empty_strings):
        nice_list = [y.strip().lower() for y in str(x).split(delim)]
        if len(nice_list) > 1:
            return nice_list[0]
        else:
            return ""
    else:
        return ""
    
def unnesting(df, explode):
    idx = df.index.repeat(df[explode[0]].str.len())
    df1 = pd.concat([
        pd.DataFrame({x: np.concatenate(df[x].values)}) for x in explode], axis=1)
    df1.index = idx

    return df1.join(df.drop(explode, 1), how='left')


def reorder_ids(x):
    # reorder ids for complexes
    if type(x) == np.float:
        return np.nan
    else:
        return '|'.join(sorted(x.split("|")))
    
def get_unique_entries(df, column):
    s = set()
    for x in ['input1', 'input2', 'input3', 'output1']:
        s = s | set(df[f"{x}_{column}"].dropna(how="all"))
    return s    