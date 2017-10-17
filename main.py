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

    #
    # count = 0
    # for profile in reader:
    #     if len(profile.skills) > 0 and profile.current_company is not None:
    #         if profile.current_company.lower() == "google":
    #             count += 1
    #             print(count)

    data = create_features(reader,
                           ["skills"],
                           "current_company",
                           output_lexicon=None,
                           save_to="skills_to_comp.pickle")

    print("in: ", len(data["inputs"]), "out: ", len(data["outputs"]), "in lex", len(data["input_lexicon"]), "out lex", len(data["output_lexicon"]))
    #
