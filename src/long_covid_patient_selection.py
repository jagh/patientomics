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


def feature_extractor_per_patient_OLD(df, output_dir, feature_column_name, date_column_name, value_column_name):
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


def feature_extractor_per_patient(df, output_dir, feature_column_name, date_column_name, value_column_name):
    grouped_df = df.groupby('pseudoid_pid')


    ## Read the hospitalization timeline csv file
    general_data_file_name = "general_data"
    hosp_timeline_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/" + general_data_file_name + "_hosp_timeline.csv" 
    hosp_timeline_df = read_csv(hosp_timeline_file_name, sep=',')
    # hosp_timeline = hosp_timeline_df[['pseudoid_pid', 'date_admission_hosp', 'date_discharge_hosp']]

    ## Preprocess the date column
    hosp_timeline_data = preprocess_data(hosp_timeline_df, 'date_admission_hosp')


    for patient, data in grouped_df:
        patient_df = pd.DataFrame()

        ## Get the hospitalization timeline for the patient
        patient_hosp_timeline = hosp_timeline_data[hosp_timeline_data['pseudoid_pid'] == patient]

        ## Get the first hospitalization date
        first_hosp_date = patient_hosp_timeline['date_admission_hosp'].min()

        # ## Get the last hospitalization date
        # last_hosp_date = patient_hosp_timeline['date_discharge_hosp'].max()

        # ## Get the first and last hospitalization dates for the patient
        # patient_hosp_timeline = patient_hosp_timeline[(patient_hosp_timeline['date_admission_hosp'] == first_hosp_date) | (patient_hosp_timeline['date_discharge_hosp'] == last_hosp_date)]
        # print("patient_hosp_timeline: ", patient_hosp_timeline)

        ## Function 
        for feature_name, feature_data in data.groupby(feature_column_name):
            min_date = first_hosp_date
            ## derive the days from the first hospitalization date
            feature_data['days'] = (feature_data[date_column_name] - min_date).dt.days

            ## Convert value to numeric, handling non-numeric values
            feature_data[value_column_name] = pd.to_numeric(feature_data[value_column_name], errors='coerce')

            feature_data = feature_data.pivot_table(index=feature_column_name, columns='days', values=value_column_name, aggfunc='mean')
            feature_data.columns = [f'{day}' for day in feature_data.columns]

            patient_df = pd.concat([patient_df, feature_data])

        patient_df_file = os.path.join(output_dir, f'patient_{patient}.csv')
        patient_df.to_csv(patient_df_file)


def sort_dataframe_columns(dataframe):

    # print("dataframe: ", dataframe)
    print("dataframe: ", dataframe.head())


    # Get the header row and remove the 'lab_name' column
    header = dataframe.columns[1:].tolist()
    table_data = dataframe.values.tolist()

    print("header: ", header)
    print("table_data: ", table_data)

    # # Filter and sort the header based on the day number
    # sorted_header = sorted([col for col in header if '-' in col], key=lambda col: int(col.split('-')[1]))

    # # Reconstruct the table data with sorted columns
    # sorted_table_data = [[str(row[0])] + [str(row[header.index(col) + 1]) for col in sorted_header] for row in table_data]

    # # # Print the sorted table
    # # for row in sorted_table_data:
    # #     print('\t'.join(row))

    # # Write the sorted table to a new CSV file
    # output_file = file_name + '_sorted.csv'
    # dataframe_sorted = pd.DataFrame(sorted_table_data, columns=['lab_name'] + sorted_header)
    
    # return dataframe_sorted






##############################################################################################################
def launcher_pipeline(file_name, sep, feature_column_name, date_column_name, value_column_name):
    """
    Script to select the potential long covid patients from the dataset.

    Step 1: Filter the patients with the following criteria: 
        - Patients with 'ris_examination_begin' after 2020-03-01
        - Patients with 'ris_examination_type' == 'CTA, CTTH, TH'
    
    Step 2: Calculate the days from the first hospitalization date

    Step 3: Filter the patients medical imaging ('ris_examination_type') follow-up with the following criteria:
        - At least 2 medical imaging in the first 60 days from the first hospitalization date
        - At least 1 medical imaging after 120 days from the first hospitalization date
    """

    # # Step 1: Read the CSV file into a DataFrame
    dir_CDA_features = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/"
    csv_file_path = os.path.join(dir_CDA_features, file_name + ".csv")
    df = read_csv(csv_file_path, sep=sep)

    ## Step 2: Preprocess and categorize the data
    df = preprocess_data(df, date_column_name)
    # print("df: ", df.head())

    ##############################################################
    ##############################################################
    ## Step 3: Filter the patients with the following criteria: 
    ##    - Patients with 'ris_examination_begin' after 2020-03-01
    ##    - Patients with 'ris_examination_type' == 'CTA, CTTH, TH'

    ## Step 3.1: Filter the patients with 'ris_examination_begin' after 2020-03-01
    df = df[df['ris_examination_begin'] >= '2020-03-01']

    ## Step 3.2: Filter the patients with 'ris_examination_type' == 'CTA, CTTH, TH'
    df = df[df['ris_examination_type'].isin(['CTA', 'CTHATHAB', 'CTHATHOB', 'CTHTH', 'CTHTHABD', 'CTTH', 'CTTHABD', 'CTTHOB', 'CTUB', 'IMPCTTH', 'IMPCTTHAB', 'TH'])]
    # print("df: ", df.head())


    ##############################################################
    ##############################################################
    ## Step 4: Calculate the days from the first hospitalization date
    grouped_df = df.groupby('pseudoid_pid')

    ## Read the hospitalization timeline csv file
    general_data_file_name = "general_data"
    hosp_timeline_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/" + general_data_file_name + "_hosp_timeline.csv" 
    hosp_timeline_df = read_csv(hosp_timeline_file_name, sep=',')

    ## Preprocess the date column
    hosp_timeline_data = preprocess_data(hosp_timeline_df, 'date_admission_hosp')


    ##############################################################
    ## Set the store list
    potential_long_covid_patients = []
    potential_long_covid_patients.append('pseudoid_pid')

    ## Set the full data list
    long_covid_selected = pd.DataFrame()

    for patient, data in grouped_df:
        patient_df = pd.DataFrame()
        full_data = pd.DataFrame()

        ## Get the hospitalization timeline for the patient
        patient_hosp_timeline = hosp_timeline_data[hosp_timeline_data['pseudoid_pid'] == patient]

        ## Get the first hospitalization date
        first_hosp_date = patient_hosp_timeline['date_admission_hosp'].min()

        ## Filter the patients medical imaging ('ris_examination_type') follow-up with the following criteria:
        for feature_name, feature_data in data.groupby(feature_column_name):
            min_date = first_hosp_date

            ## derive the days from the first hospitalization date
            feature_data['days'] = (feature_data[date_column_name] - min_date).dt.days

            # ## derive the days from the first hospitalization date
            # feature_data['days'] = (feature_data[date_column_name] - min_date).dt.days

            ##############
            ## Get the additional data
            full_data = pd.concat([full_data, feature_data])
            ##############

            ## Convert value to numeric, handling non-numeric values
            feature_data[value_column_name] = pd.to_numeric(feature_data[value_column_name], errors='coerce')

            feature_data = feature_data.pivot_table(index=feature_column_name, columns='days', values=value_column_name, aggfunc='mean')
            feature_data.columns = [f'{day}' for day in feature_data.columns]

            patient_df = pd.concat([patient_df, feature_data])

            ## sort the columns
            # patient_df = patient_df.reindex(sorted(patient_df.columns), axis=1)
            patient_df = patient_df.reindex(sorted(patient_df.columns, key=lambda x: int(x) if x.isdigit() else float('inf')), axis=1)


        # ##############################################################
        # ## Step 5: Save patients containing at least 1 colume with header name => 120 days
        # other_df = patient_df[patient_df.columns[patient_df.columns.str.contains('30')]]
        # # print("other_df: ", other_df.head())


        # ##############################################################
        patient_df.columns = pd.to_numeric(patient_df.columns, errors='coerce')

        ###############
        ## Criteria 1: Filter columns based on column headers greater than 120
        filtered_criteria_1 = [col for col in patient_df.columns if col > 150]
        
        # Check if any columns meet the criteria
        if filtered_criteria_1:
            # filtered_df = patient_df[filtered_criteria_1]
            # print("Filtered dataframe saved successfully.")

            ###############
            ## Criteria 2: Check if there are more that two CTs between 0 and 60
            filtered_criteria_2 = [col for col in patient_df.columns if col > -15]

            if len(filtered_criteria_2) >= 1:
                # print("patient_df: ", patient_df.head())

                ###############
                ## Criteria 3: Check if there are more that two images labaled as 'CTA' or 'CTTH in the patient_df
                patient_df_t = patient_df.T
                # print("patient_df_t: ", patient_df_t.head())

                total_count = 0
                columns = patient_df_t.columns.tolist()

                ##  List of items to count
                items_to_count = [
                    'CTA', 'CTHATHAB', 'CTHATHOB', 'CTHTH', 'CTHTHABD',
                    'CTTH', 'CTTHABD', 'CTTHOB', 'IMPCTTH', 'IMPCTTHAB'
                ]

                ## Count the items in the columns
                for item in items_to_count:
                    item_count = columns.count(item)
                    total_count += item_count

                # ## Print the total count
                # if total_count > 0:
                #     print("+ Positive total_count:", total_count)
                # else:
                #     print("+ Negative total_count:", total_count)
                

                ## Parameter to include at least 2 CTA or CTTH in total
                if total_count >= 1:
                    # Save filtered dataframe to a CSV file
                    output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/03_long_covid_potential_patients/"
                    patient_df_file = os.path.join(output_dir, f'patient_{patient}.csv')

                    # Create the directory if it doesn't exist
                    os.makedirs(output_dir, exist_ok=True)
                    
                    ## Transpose the patient_df dataframe
                    patient_df_t2 = patient_df.T

                    # set the patient_df_t2 index with the column name 'days' in the first column
                    patient_df_t2.index.name = 'days'
                    patient_df_t2.to_csv(patient_df_file)

                    ####################
                    # ## Save the additional data to the dataframe
                    # full_patient_df_t = full_data
                    # full_patient_df_t.to_csv(patient_df_file, index=False)

                    ## Add selected patient to the long covid selected dataframe
                    long_covid_selected = pd.concat([long_covid_selected, full_data])
                
                    ####################
                    ## Added the patient to the list of potential long covid patients
                    potential_long_covid_patients.append(patient)

        else:
            # print("No columns with headers greater than 5 found.")
            pass

    ## Save the list of potential long covid patients to a CSV file
    potential_long_covid_patients_file = os.path.join(output_dir, f'potential_long_covid_patients_pseudoid_pid.csv')
    potential_long_covid_patients_df = pd.DataFrame(potential_long_covid_patients)
    potential_long_covid_patients_df.to_csv(potential_long_covid_patients_file, index=False)

    ####################
    ## Save the additional data to the dataframe
    long_covid_selected_file = os.path.join(output_dir, f'potential_long_covid_patients_ris_information.csv')
    long_covid_selected.to_csv(long_covid_selected_file, index=False)


################################################################################################################
file_name = "ris_data"
sep=','
feature_column_name = 'ris_examination_type'
date_column_name = 'ris_examination_begin'
value_column_name = 'value'



launcher_pipeline(file_name, sep, feature_column_name, date_column_name, value_column_name)

