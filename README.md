# AMR Wiki Link Tool

The AMR Wiki Link Tool is a Python-based tool designed to annotate **Abstract Meaning Representation (AMR)** graphs with **Wikipedia** entity tags. It leverages the **MediaWiki API** and **Wikidata client** to identify, validate, and add relevant `:wiki` tags to AMR graphs, enhancing the semantic richness of the AMR dataset. By linking AMR entities to Wikipedia pages, the tool facilitates better semantic understanding and disambiguation of named entities within AMR structures.

## Features

- **Automated Wikipedia Tagging**: Automatically annotates AMR graphs with Wikipedia tags using the **MediaWiki API**.
- **Wikidata Entity Matching**: Validates entities through **Wikidata**, providing a robust and contextually accurate linking process.
- **Epistemic Entity Disambiguation**: Uses the structured properties of entities in **Wikidata** to resolve ambiguity and improve the accuracy of entity linking.
- **Multithreading for Efficiency**: Uses multithreading to improve processing speed for large AMR datasets.

## How to Use the AMR Wiki Tool

### Prerequisites

- Python 3.x
- Required packages: `mediawikiapi`, `wikidata.client`, `penman`, `tqdm`, `pandas`, `concurrent.futures`, `argparse`

Install all necessary packages:
```
pip install mediawikiapi wikidata pandas tqdm penman
```

### Adding Wiki Tags to Your AMR File

The tool provides an easy-to-use command line script, **`add_wiki.py`**, to annotate AMR files with Wikipedia tags.

#### Running the Tool

1. Place your AMR file in the `data/amr/` directory (or any directory of your choice).
2. Run the tool using the command below:
   
\`\`\`bash
python add_wiki.py --input_path <input_amr_file> --output_path <output_amr_file>
\`\`\`

   - `--input_path`: Path to the input file containing your AMR data.
   - `--output_path`: Path where you want the annotated AMR data to be saved.

Example:
\`\`\`bash
python add_wiki.py --input_path data/amr/test.txt --output_path data/amr/test_wiki.txt
\`\`\`

#### Viewing the Demo

For a demonstration on how the AMR Wiki Tool works, you can check the Jupyter Notebook provided:

\`\`\`bash
/Get_wiki/amr_wiki_tool_playground.ipynb
\`\`\`

This notebook provides an interactive view of how the tool annotates AMR graphs and integrates with Wikipedia and Wikidata.

## Understanding `dict_entities.json`

The tool uses a **`dict_entities.json`** file, which is a dictionary that maps **AMR entity types** to **Wikidata entity types**. This mapping plays a crucial role in determining accurate `:wiki` tags for AMR entities.

**Note**: The current `dict_entities.json` is a **first draft**. It serves as an initial mapping between AMR entity types and their corresponding Wikidata tags. Improving this dictionary is vital for enhancing the quality of the entity linking performed by the tool.

### How to Contribute to `dict_entities.json`

If you are interested in improving the mapping of AMR entities to Wikidata entities, your contributions are welcome! Enhancing `dict_entities.json` will improve the quality and accuracy of Wikipedia tagging for AMR graphs. Below are some ways you can contribute:

1. **Identify Missing or Inaccurate Mappings**: Review the current mappings and add any missing entities or correct inaccurate ones.
2. **Expand Entity Categories**: Extend the dictionary by adding more comprehensive mappings to cover a wider range of entity types.
3. **Optimize Wikidata Linking**: Provide better entity-type matches based on real-world context and AMR usage, leading to more precise Wikipedia annotations.

If you make changes or additions to `dict_entities.json`, please submit a pull request to help improve the overall quality of the tool.
