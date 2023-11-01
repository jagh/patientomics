import logging
import argparse

import sys, os, shutil
import glob
import pandas as pd
import numpy as np



###################################
## Get unique subjects
## Metadat path
input_dir_path = "/data/01_multiomics/02_long_covid_study/00_data_indexing/00_Bern/01_csv_to_process/"
input_file_name = "herkus_manual_selection_group1_230818-all.csv"
input_file_path = os.path.join(input_dir_path, input_file_name)
df = pd.read_csv(input_file_path, sep=';')

## Get unique subjects
unique_subjects = df['PID'].unique()
print("+ unique_subjects: ", unique_subjects.shape)


## Drop duplicates
df_unique_subjects = df.drop_duplicates(subset=['PID'])
print("+ df_unique_subjects: ", df_unique_subjects.shape)

## Save unique subjects

output_dir_path = "/data/01_multiomics/02_long_covid_study/00_data_indexing/00_Bern/02_csv_with_unique_PID/"
output_file_name =  "herkus_manual_selection_group1_230818-all-uniquePIDs.csv"
output_file_path =  os.path.join(output_dir_path, output_file_name)

unique_subjects_output_file =  os.path.join(output_file_path)
df_unique_subjects.to_csv(unique_subjects_output_file, sep=';', index=False)
print("+ unique_subjects_output_file: ", unique_subjects_output_file)