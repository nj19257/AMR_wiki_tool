import json
import penman
from penman.graph import Graph
import multiprocessing
import argparse



def inject_wiki(data):
    if ':name' in data:
        amr = penman.decode(data)
        list_amr = list(amr.triples)
        pointer = 0
        for idx ,triple in enumerate(amr.triples):
            if triple[1] == ":name":
                if amr.triples[idx-1][1] == ':wiki':
                    print("wiki already exists")
                    copy = list(list_amr[idx+pointer-1])
                    copy[2] = '-'
                    list_amr[idx+pointer-1] = tuple(copy)
                    pass
                # insert wiki before :name at list_amr[pointer]
                else:
                    list_amr.insert(idx+pointer, (list_amr[idx+pointer][0], ':wiki', '-' ))
                    pointer += 1
        amr.triples = list_amr
        data = penman.encode(amr)
        return data

    else:
        return data

def inject_wiki_file(input_file, output_dir, output_name):
    with open(input_file, 'r') as file:
        dataset = file.read()

    dataset = dataset.split('\n\n')
    print(len(dataset))

    amr_dataset = []
    for data in dataset:

        if ":name" in data:
            data = inject_wiki(data)
        amr_dataset.append(data)

    print(len(amr_dataset))

    # save the data 
    # /mnt/e/workspace/UCL_master_project/Get_wiki/AMR_without_wiki
    with open('/'.join([output_dir, output_name]), 'w') as file:
        file.write('\n\n'.join(amr_dataset))

def main():
    parser = argparse.ArgumentParser(description='Inject wiki into AMR')
    parser.add_argument('--input_file', type=str, default='data/amr.txt', help='input file path')
    parser.add_argument('--output_dir', type=str, default='data', help='output file directory')
    parser.add_argument('--output_name', type=str, default='amr_with_wiki.txt', help='output file name')
    args = parser.parse_args()

    inject_wiki_file(args.input_file, args.output_dir, args.output_name)