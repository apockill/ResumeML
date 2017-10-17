import os
from time import time
from collections import Counter

from linkedin.profile_manager import ProfileManager
from feature_handling.feature_creation import create_features, create_lexicon


if __name__ == "__main__":
    # Inputs
    print("Loading all profiles...")
    start = time()
    reader = ProfileManager(load_pickle="./cached_dataset.pickle", pre_cache_profiles=False)
    print("Loaded and processed in ", time() - start)


    data = create_features(reader,
                           ["skills"],
                           "industry",
                           min_input_samples=100,
                           min_output_samples=2500,
                           save_to="skills_to_industry.pickle")

    print("in: ", len(data["inputs"]), "out: ", len(data["outputs"]), "in lex", len(data["input_lexicon"]), "out lex", len(data["output_lexicon"]))

