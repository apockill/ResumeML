from time import time

from linkedin.feature_creation import create_features
from linkedin.profile_manager import ProfileManager

if __name__ == "__main__":
    # Inputs
    print("Loading all profiles...")
    start = time()
    reader = ProfileManager(load_pickle="./cached_dataset.pickle", pre_cache_profiles=False)
    print("Loaded and processed in ", time() - start)


    data = create_features(reader,
                           ["skills"],
                           "industry",
                           min_inputs_per_profile=6,
                           min_input_samples=125,
                           min_output_samples=3500,
                           save_dir="./")

    print("in: ", len(data["inputs"]), "out: ", len(data["outputs"]), "in lex", len(data["input_lexicon"]), "out lex", len(data["output_lexicon"]))

