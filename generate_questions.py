import json

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import MetadataMode
import pandas as pd

df = pd.read_json('results.json')


shuffled_df = df.sample(frac=1)[['content']].reset_index(drop=True)

# separate into train_df and validation_df, 


train_df = shuffled_df.iloc[0:4500].copy()
validation_df = shuffled_df.iloc[4500:].copy()

train_df.to_csv('data/processed/train.csv', index=False)
validation_df.to_csv('data/processed/validation.csv', index=False)

TRAIN_FILES = ["data/processed/train.csv"]
VAL_FILES = ["data/processed/validation.csv"]

TRAIN_CORPUS_FPATH = "./data/processed/train_corpus.json"
VAL_CORPUS_FPATH = "./data/processed/val_corpus.json"

def load_corpus(files, verbose=False):
    if verbose:
        print(f"Loading files {files}")

    reader = SimpleDirectoryReader(input_files=files)
    docs = reader.load_data()
    if verbose:
        print(f"Loaded {len(docs)} docs")

    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(docs, show_progress=verbose)

    if verbose:
        print(f"Parsed {len(nodes)} nodes")

    return nodes