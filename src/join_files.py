import logging
import argparse

import sys, os, shutil
import glob
import pandas as pd
import numpy as np


###################################
# Join to csv files
## Metadat path
# metadata_path = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/00_ManualDataset_Selection/new_list_20230809/"
# metadata_path = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/00_ManualDataset/"
metadata_path = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/50_imaging_data/01_ids_from_scan/"


first_file_path = os.path.join(metadata_path, "general_data--IDSC_to_second_request.csv")
second_file_path = os.path.join(metadata_path, "IDSC202101463_data_v13_keys_20221214.csv")

first_metadata = pd.read_csv(first_file_path, sep=';', header=0)
second_metadata = pd.read_csv(second_file_path, sep=',', header=0)

# print("who_metadata: ", who_metadata)
# print("seg_metadata: ", seg_metadata)


joined_metadata = first_metadata.join(second_metadata.set_index('pseudoid_pid'), on='pseudoid_pid', how='left')
print("+ joined_metadata: ", joined_metadata)


joined_metadata_output_file =  os.path.join(metadata_path, "full_covid_list_CD_and_PFTs_request_to_IDSC-20231023.csv")
joined_metadata.to_csv(joined_metadata_output_file, sep=',', index=False)