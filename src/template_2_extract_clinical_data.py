import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import csv


def read_csv(file_path, sep=','):
    """
    Reads the CSV file into a DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV file.
    """
    return pd.read_csv(file_path, sep=sep)


def preprocess_data(df, column_name):
    """
    Preprocesses the DataFrame by converting lab_req_date to datetime format and sorting by column_name.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The preprocessed DataFrame.
    """
    df[column_name] = pd.to_datetime(df[column_name])
    df = df.sort_values(column_name)
    return df


def save_pd_to_csv(df, output_file):
    df.to_csv(output_file , index=False)
    print(f"Clinical data dictionary saved to {output_file}")


def feature_extractor_per_patient(df, output_dir, feature_column_name, date_column_name, value_column_name):
    grouped_df = df.groupby('pseudoid_pid')

    for patient, data in grouped_df:
        patient_dt = pd.DataFrame()

        for feature_name, feature_data in data.groupby(feature_column_name):
            min_date = feature_data[date_column_name].min()
            feature_data['days'] = (feature_data[date_column_name] - min_date).dt.days

            ## Convert value to numeric, handling non-numeric values
            feature_data[value_column_name] = pd.to_numeric(feature_data[value_column_name], errors='coerce')

            feature_data = feature_data.pivot_table(index=feature_column_name, columns='days', values=value_column_name, aggfunc='mean')
            feature_data.columns = [f'day-{day}' for day in feature_data.columns]

            patient_dt = pd.concat([patient_dt, feature_data])

        patient_df_file = os.path.join(output_dir, f'patient_{patient}.csv')
        patient_dt.to_csv(patient_df_file)



def launcher_pipeline(file_name, sep, feature_column_name, date_column_name, value_column_name):
    # # Step 1: Read the CSV file into a DataFrame
    dir_CDA_features = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/"
    # file_name = "oxygen_supply"
    csv_file_path = os.path.join(dir_CDA_features, file_name + ".csv")
    df = read_csv(csv_file_path, sep=sep)

    # Step 2: Preprocess and categorize the data
    # date_column_name = 'date'
    df = preprocess_data(df, date_column_name)
    print("df: ", df.head())

    # Step 3: Categorize the data
    # Filter unique laboratory codes 'med_atc' with respective laboratory feature names 'med_medication'
    # feature_column_name = 'name'
    o2_feature_list = df[feature_column_name].unique().tolist()

    print('Feature_names: ', o2_feature_list)
    print('Feature_names: ', len(o2_feature_list))

    ## Step 4: Save the data per patient in a CSV file
    ## Convert the list to a dataframe

    clinical_feature_df = pd.DataFrame(o2_feature_list, columns=[file_name])
    medications_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/" + file_name + ".csv"
    save_pd_to_csv(clinical_feature_df, os.path.join(dir_CDA_features, medications_file_name))


    ## Step 5: Save the data per patient in a CSV file
    output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/" + file_name + "_features/"
    # value_column_name = 'dose'
    feature_extractor_per_patient(df, output_dir, feature_column_name, date_column_name, value_column_name)



################################################################################################################
file_name = "ris_data"
sep=','
feature_column_name = 'ris_examination_type'
date_column_name = 'ris_examination_begin'
value_column_name = 'value'

launcher_pipeline(file_name, sep, feature_column_name, date_column_name, value_column_name)




################################################################################################################
################################################  General data  ################################################
################################################################################################################

# # Step 1: Read the CSV file into a DataFrame
# dir_CDA_features = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/"
# file_name = "oxygen_supply"
# csv_file_path = os.path.join(dir_CDA_features, file_name + ".csv")
# df = read_csv(csv_file_path, sep=';')

# # Step 2: Preprocess and categorize the data
# date_column_name = 'date'
# df = preprocess_data(df, date_column_name)
# print("df: ", df.head())

# # Step 3: Categorize the data
# # Filter unique laboratory codes 'med_atc' with respective laboratory feature names 'med_medication'
# feature_column_name = 'name'
# o2_feature_list = df[feature_column_name].unique().tolist()

# print('o2_feature_names: ', o2_feature_list)
# print('o2_feature_names: ', len(o2_feature_list))

# ## Step 4: Save the data per patient in a CSV file
# ## Convert the list to a dataframe

# clinical_feature_df = pd.DataFrame(o2_feature_list, columns=[file_name])
# medications_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/" + file_name + ".csv"
# save_pd_to_csv(clinical_feature_df, medications_file_name)


# # ## Step 5: Save the data per patient in a CSV file
# # output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/" + file_name + "_features/"
# # value_column_name = 'dose'
# # csv_clinical_data_per_patient(df, output_dir, feature_column_name, date_column_name, value_column_name)


# ## Step 5: Save the data per patient in a CSV file
# output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/" + file_name + "_features/"
# value_column_name = 'dose'
# csv_clinical_data_per_patient(df, output_dir, feature_column_name, date_column_name, value_column_name)



################################################################################################################
################################################  General data  ################################################
################################################################################################################

# # Step 0: Read the CSV file into a DataFrame
# dir_CDA_features = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/"
# general_data_file_name = "general_data"
# general_data_csv_file_path = os.path.join(dir_CDA_features, general_data_file_name + ".csv")
# general_data_df = read_csv(general_data_csv_file_path, sep=';')

# ## Replace 'NULL' values with NaN
# general_data_df.replace('NULL', np.nan, inplace=True)

# ## Convert date columns to datetime type
# date_columns = ['date_admission_hosp', 'covid19_begin', 'date_discharge_hosp', 'date_recovery', 'covid19_end', 'date_death']
# for column in date_columns:
#     general_data_df[column] = pd.to_datetime(general_data_df[column])

# # Group the data by 'pseudoid_pid'
# grouped = general_data_df.groupby('pseudoid_pid')

# print("general_data_df: ", general_data_df.head())