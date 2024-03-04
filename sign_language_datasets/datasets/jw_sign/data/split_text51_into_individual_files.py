import pickle
import gzip
import json
from pathlib import Path
import random
import pandas as pd


def decompress_and_unpickle_dataset_file(filename):
    """
    Some of the dataset files are pickled Python objects, compressed as .tar.gz files.
    """
    with gzip.open(filename, "rb") as f:
        loaded_object = pickle.load(f)
        return loaded_object
    
if __name__ == "__main__":
    text51_dict = decompress_and_unpickle_dataset_file("text51.dict.gz")

    for spoken_language, data in text51_dict.items():
        print(spoken_language, type(data))
        out_json_path = f"text_files\{spoken_language}_text.json"
        out_compressed_path = f"text_files_compressed\{spoken_language}_text.json.gz"
        with open(out_json_path, "w") as sf:
            new_dict = {"spoken_language":spoken_language,
                        "data":data}
            json.dump(new_dict, sf)

        # with open(out_json_path, "r") as sf_in:
