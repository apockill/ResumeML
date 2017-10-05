import os
from time import time
from collections import Counter

from linkedin.profile_manager import ProfileManager


if __name__ == "__main__":
    # Inputs

    print("Loading all profiles...")
    start = time()
    reader = ProfileManager(load_pickle="./cached_dataset.pickle", pre_cache_profiles=False)

    # Future goals
    # train_in, train_out, test_in, test_out = feature_create_custom(reader)
