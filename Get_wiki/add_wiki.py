from mediawikiapi import MediaWikiAPI
from wikidata.client import Client
import json
import penman
from tqdm import tqdm
import pandas as pd
from itertools import chain
from collections import Counter
import concurrent.futures
from collections import defaultdict
import urllib.parse
import re
import time
import argparse


def find_wiki_names(graph,amr_string):
    wiki_names = []
    wiki_idx= []
    nodes_list = []
    roles = []
    rel_nodes = {}
    Salutations_list =[ "mr.", "mrs.", "ms.", "miss" , "sir" , "madam" , "mr", "mrs", "ms"]
    for i, triple in enumerate(graph.triples):

        if triple[1] == ':wiki':
            wiki_idx.append(i)
            node = triple[0]
            name_parts = []
            current_mod = []
            pointer = 1
            state_1 = False
            for idx , triple in enumerate(graph.triples):
                if triple[0] == node and triple[1] == ':instance':
                    # replace any '-' or '_' characters with a space
                    nodes_list.append(triple[2])
                    instance_node = triple[2]

                    top_node = triple[0]
                    if ":mod" in amr_string: # consider if :location as well
                        for triple in graph.triples:
                            if triple[1] == ':mod' and triple[0] == top_node:
                                rel_nodes[triple[2]] = None
                                state_1 = True  
                    if instance_node == 'person' :
                        if 'have-org-role-91' in amr_string:
                            # instance_node=''
                            pass
                        elif 'government-organization' in amr_string:
                            # if government-organization is the instance node, then we should not include the name of the government organization
                            # As it is the most well known name and government-organization will increase its perplexity
                            # instance_node=''
                            pass
                        elif 'country' in amr_string:
                            # if government-organization is the instance node, then we should not include the name of the government organization
                            # As it is the most well known name and government-organization will increase its perplexity
                            # instance_node=''
                            pass
                        else:
                            instance_node = '#del#'
                            continue

                state = False
                name_nodes = {}
                name= []
                # rel_nodes = []
                # rel_nodes = {}
                switch = False
                
                if triple[0] == node and triple[1] == ':name':
                    name_node = triple[2]
                    for k ,name_triple in enumerate(graph.triples[idx:]):
                        if name_triple[0] == name_node and name_triple[1].startswith(':op'):
                            name_parts.append(name_triple[2].strip('"'))
                            if state_1:
                                state = True
                            if idx+ k+2 < len(graph.triples):
                                if graph.triples[idx+k+2][2] == "have-org-role-91" and graph.triples[idx+k+1][2] == top_node:
                                    state = True
                                    switch = False
                                    # name_node_2 = name_triple[0]
                                    # rel_nodes.append(graph.triples[k+2][0])
                                    rel_nodes = {graph.triples[idx+ k+2][0]: None}
                                    roles.append(graph.triples[idx+k+2][0])
                                    continue
                                if graph.triples[idx + k+1][0] in roles and graph.triples[idx + k+1][1].startswith(':ARG') and graph.triples[idx + k+1][2] != graph.triples[idx + k+2][0]:
                                    state = True
                                    switch = False
                                    rel_nodes = {graph.triples[idx+ k+1][0]: None}
                                    continue
                                continue

                        if switch:
                            break
                        if state and name_triple[1].startswith(':ARG'):
                            if name_triple[0] in rel_nodes.keys() and name_triple[2] == graph.triples[k+1][0]:
                                if name_triple[2] in rel_nodes:
                                    continue
                                # rel_nodes.append(name_triple[2])
                                rel_nodes[name_triple[2]] = None
                            if top_node in rel_nodes.keys():
                                rel_nodes.pop(top_node)
                        # new attempt
                        if state:
                            for j ,name_triple_j in enumerate(graph.triples): 
                                # switch = True
                                if name_triple_j[1] == ':instance' and name_triple_j[0] in rel_nodes.keys():
                                    rel_nodes[name_triple_j[0]] = re.sub(r'-\d+$', '', name_triple_j[2])
                                    
                                    continue

                                if name_triple_j[1].startswith(':ARG'):
                                    if j+1 < len(graph.triples):
                                        if name_triple_j[2] != graph.triples[j+1][0]:
                                            continue

                                    if name_triple_j[0] in rel_nodes.keys():
                                        if name_triple_j[2] in rel_nodes.keys():
                                            continue
                                        # rel_nodes.append(name_triple_j[2])
                                        rel_nodes[name_triple_j[2]] = None
                                    if top_node in rel_nodes.keys():
                                        rel_nodes.pop(top_node)
                                        
                                if name_triple_j[0] in rel_nodes.keys() and name_triple_j[1] == ':name':
                                    if name_triple_j[2] in name_nodes.keys():
                                        continue
                                    name_nodes[name_triple_j[2]] = name_triple_j[0]

                                if name_triple_j[0] in name_nodes.keys() and name_triple_j[1].startswith(':op') :
                                    # if name_triple_j[2].strip('"') in name_parts:
                                    #     # print('test')
                                    #     continue
                                    # name_parts.append(name_triple_j[2].strip('"'))
                                    if j+1 != len(graph.triples):
                                        name.append(name_triple_j[2].strip('"'))
                                        if graph.triples[j+1][1].startswith(':op'):
                                            pass
                                        else:
                                            rel_nodes[name_nodes[name_triple_j[0]]] = ' '.join(name)
                                        # if graph.triples[j+1][1].startswith(':ARG'):
                                        #     switch = True
                                        #     break
                                    # switch = True
                                        name = []
                                    continue
                                if j+1 != len(graph.triples):
                                    continue
                                else:
                                    switch = True
                                    break
            for key , value in rel_nodes.items():
                if key in roles:
                    continue
                if value == None:
                    continue
                name_parts.append(value)
            for name_part in name_parts:
                if name_part.lower() in Salutations_list:
                    name_parts.remove(name_part)

            rel_nodes = {}
            # reverse the current_mod list
            current_mod = current_mod[::-1]
            full_name = instance_node + ' ' + ' '.join(current_mod +name_parts)
            wiki_names.append(full_name)
    return wiki_names , wiki_idx , nodes_list


def add_wiki_tag(graph, wiki_idx, wiki_names, nodes_list, entities_dict, mediawikiapi, client):
      """
      get the parent-child relationships
      """
      # Build parent-child relationship
      
      for i, content in enumerate(wiki_names):
            switch = True
            if '#del#' in content:
                continue
            try:
                if nodes_list[i] not in entities_dict.keys():
                    result = mediawikiapi.search(str(content), results=3)
                    # result = result.replace(' ', '_')
                    # print(result)
                    if result == []:
                        continue
                    try:
                        if result == mediawikiapi.page(str(list([result]))).title:
                            result = str(list([result]))
                        elif result == mediawikiapi.page(str([result])).title:
                            result = str([result])
                    except:
                        if result == mediawikiapi.page(str([result])).title:
                            result = str([result])
                        elif result == mediawikiapi.page(str(list([result]))).title:
                            result = str(list([result]))
                    copy = list(graph.triples[wiki_idx[i]])
                    try:
                        copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'
                    except:
                        copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'     
                    # copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(str(list([result]))).url.split('/wiki/')[1]) + '"'
                    graph.triples[wiki_idx[i]] = tuple(copy)
                    continue
                query = ' '.join(content.split()[1:])
                results0 = mediawikiapi.search(str(query), results=5)
                # print(results0)

                if results0 == []:
                    query = content.replace('-', ' ').replace('_', ' ')
                    switch = False
                    results0 = mediawikiapi.search(str(query), results=3)
                    if results0 == []:
                    #     if nodes_list[i] != 'person':
                    #         results0.append(nodes_list[i])
                        continue

                for result in results0:
                    # result = result.replace(' ', '_')
                    try:
                        if result == mediawikiapi.page(str(list([result]))).title:
                            result = str(list([result]))
                        elif result == mediawikiapi.page(str([result])).title:
                            result = str([result])
                        else:
                            continue
                    except:
                        if result == mediawikiapi.page(str([result])).title:
                            result = str([result])
                        elif result == mediawikiapi.page(str(list([result]))).title:
                            result = str(list([result]))
                        else:
                            continue
                    entities, count = get_wikidata_tags(result, mediawikiapi, client)
                    # if any entities in the entities_dict[nodes_list[i]] then pass
                    if any(entity in entities_dict[nodes_list[i]] for entity in entities):
                        copy = list(graph.triples[wiki_idx[i]]) 
                        try:
                            copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'
                        except:
                            copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'         
                        # copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(str(list([result]))).url.split('/wiki/')[1]) + '"'
                        graph.triples[wiki_idx[i]] = tuple(copy)
                        switch = False
                        break
                if switch:
                    query = content.replace('-', ' ').replace('_', ' ')
                    results0 = mediawikiapi.search(str(query), results=3)
                    if results0 == []:
                        print('Error wiki: ', content)
                        continue
                    for result in results0:
                        # result = result.replace(' ', '_')
                        try:
                            if result == mediawikiapi.page(str(list([result]))).title:
                                result = str(list([result]))
                            elif result == mediawikiapi.page(str([result])).title:
                                result = str([result])
                            else:
                                continue
                        except:
                            if result == mediawikiapi.page(str([result])).title:
                                result = str([result])
                            elif result == mediawikiapi.page(str(list([result]))).title:
                                result = str(list([result]))
                            else:
                                continue
                        entities, count = get_wikidata_tags(result, mediawikiapi, client)
                        if any(entity in entities_dict[nodes_list[i]] for entity in entities):

                            copy = list(graph.triples[wiki_idx[i]])
                            try:
                                copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'
                            except:
                                copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(result).url.split('/wiki/')[1]) + '"'     
                            # copy[2] = '"' + urllib.parse.unquote(mediawikiapi.page(str(list([result]))).url.split('/wiki/')[1]) + '"'
                            graph.triples[wiki_idx[i]] = tuple(copy)
                            break
                    continue
            except:
                print('Error wiki: ', content)
                continue
      return graph

def get_wikidata_tags(query, mediawikiapi, client,count=0):
    statement_list = ["P31", "P279","P10241","P361","P16","P3450", "P5138","P289","P452","P571", "P366" , "P1269"]
    entities= []
    try:
        
        wikidata_id = mediawikiapi.page(query).pageprops["wikibase_item"]

    except:
        print("Error wikidata: ", query)
        # the true value is to indicate that the no wikidata link was found 
        # as this is a very rare case, we can assume that the wiki tag is correct
        entities.append('true')
        return entities , count
    entity = client.get(wikidata_id, load=True)
    # check if any entity has the statement_list keys
    target = None
    for statement in statement_list:
        if statement in entity.data['claims'].keys():
            target = statement
            break
    if target == None:
        return entities , count
    if target == "P31":
        for value in entity.data['claims'][target]:
            entities.append(value["mainsnak"]["datavalue"]["value"]["id"])
    else:
        try:
            subclass_entity = client.get(entity.data['claims'][target][0]["mainsnak"]["datavalue"]["value"]["id"], load=True)
            entities.append(subclass_entity.data['claims']["P31"][0]["mainsnak"]["datavalue"]["value"]["id"])
        except:
            try:
                entities.append(entity.data['claims'][target][0]["mainsnak"]["datavalue"]["value"]["id"])
            except:
                return [] , count
    return entities , count

def get_wiki(amr, dict_entities, mediawikiapi, client):
    if ':wiki' in amr:
        graph = penman.decode(amr)
        wiki_names , wiki_idx , nodes_list = find_wiki_names(graph,amr)
        graph = add_wiki_tag(graph, wiki_idx, wiki_names, nodes_list, dict_entities, mediawikiapi, client)
        amr = penman.encode(graph)
        # data[i] = amr_string
    return amr 
# Function to process each AMR
def get_wiki_with_index(index, amr, dict_entities, mediawikiapi, client):
    result = get_wiki(amr, dict_entities, mediawikiapi, client)
    return index, result

def add_wiki(input_path,output_path,dict_entities,mediawikiapi= MediaWikiAPI(),client = Client()):
    with open(input_path, 'r') as file:
        dataset = file.read()
    dataset = dataset.split('\n\n')
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks with indices
        futures = [executor.submit(get_wiki_with_index, i, amr, dict_entities, mediawikiapi, client) for i, amr in enumerate(dataset)]
        results = []
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            results.append(future.result())

    # Sort results based on the original indices
    results.sort(key=lambda x: x[0])
    ordered_results = [result for _, result in results]

    # Now ordered_results is in the same order as val_dataset
    with open(output_path, 'w') as file:
        file.write('\n\n'.join(ordered_results))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='data/amr/test.txt', help='Path to the input AMR file')
    parser.add_argument('--output_path', type=str, default='data/amr/test_wiki.txt', help='Path to the output AMR file')

    input_path = parser.parse_args().input_path
    output_path = parser.parse_args().output_path
    # Load the entities dictionary
    with open('dict_entities.json', 'r') as file:
        dict_entities = json.load(file)
    add_wiki(input_path,output_path,dict_entities)

if __name__ == '__main__':
    main()