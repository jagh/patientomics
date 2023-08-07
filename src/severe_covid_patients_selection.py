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


    ## Step 3.3: Filter the patients with 'ris_examination_type' == 'Altersheim, Verstorben'



    ##############################################################
    ##############################################################
    ## Step 4: Calculate the days from the first hospitalization date
    grouped_df = df.groupby('pseudoid_pid')

    ## Read the hospitalization timeline csv file
    general_data_file_name = "general_data"
    # hosp_timeline_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/" + general_data_file_name + "_hosp_timeline.csv" 
    hosp_timeline_file_name = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/" + general_data_file_name + ".csv" 
    hosp_timeline_df = read_csv(hosp_timeline_file_name, sep=';')

    # ## Filter the hosp_timeline_df by patients that was discharged 'discharge_type' as Verstorben or Zuhause
    # hosp_timeline_df = hosp_timeline_df[hosp_timeline_df['discharge_type'].isin(['Verstorben', 'Zuhause'])]

    ## Preprocess the date column
    hosp_timeline_data = preprocess_data(hosp_timeline_df, 'date_admission_hosp')

    # ## Set the store list
    # potential_long_covid_patients = []
    # potential_long_covid_patients.append('pseudoid_pid')

    # ## Set the full data list
    # long_covid_selected = pd.DataFrame()

    ## Set the store list for pseudoid_pid and discharge_type
    deceased_patients = []
    deceased_patients.append('pseudoid_pid, discharge_type')
    ## Set the dataframe to store the ris_information
    ris_deceased_patients_selected = pd.DataFrame()


    ## Set the store list for pseudoid_pid and discharge_type
    discharged_patients_home = []
    discharged_patients_home.append('pseudoid_pid, discharge_type')
    ## Set the dataframe to store the ris_information
    ris_discharged_patients_selected = pd.DataFrame()

    
    for patient, data in grouped_df:
        patient_df = pd.DataFrame()
        full_data = pd.DataFrame()

        ## Get the hospitalization timeline for the patient
        patient_hosp_timeline = hosp_timeline_data[hosp_timeline_data['pseudoid_pid'] == patient]

        ## Get the first hospitalization date
        first_hosp_date = patient_hosp_timeline['date_admission_hosp'].min()

        ###########################################################
        ## Get the discharge_tye for the pseudoid_pid == patient
        row = hosp_timeline_df[hosp_timeline_df['pseudoid_pid'] == patient]
        discharge_type = row[['discharge_type']]

        ## Get the date_death for the pseudoid_pid == patient
        date_death = row[['date_death']]
        ## Normalize the date_death column
        date_death = pd.to_datetime(date_death['date_death'], errors='coerce')
        delta_date_death = (date_death - first_hosp_date).dt.days
        # print("delta_date_death: ", delta_date_death.values[0])
        #############################################################
        

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



        ##############################################################
        patient_df.columns = pd.to_numeric(patient_df.columns, errors='coerce')

        ## Add the discharge_type to the full_data dataframe
        try:
            if discharge_type.values[0][0] == 'Verstorben':
                ## check if the patient died before 60 days of the first day of hospitalization
                if delta_date_death.values[0] < 60:
                    ## Added the patient to the list of deceased_patients
                    deceased_patients.append((patient, discharge_type.values[0][0]))
                    # print("+ delta_date_death: ", delta_date_death.values[0])

                    ## Add selected patient to the ris_deceased_patients_selected dataframe
                    ris_deceased_patients_selected = pd.concat([ris_deceased_patients_selected, full_data])
                
            elif discharge_type.values[0][0] == 'Entlassung':

                ## Criteria 1: Filter columns based on column headers greater than 120
                filtered_criteria_1 = [col for col in patient_df.columns if col > 60]

                if filtered_criteria_1:
                    print("Potential long covid patient: ", patient)
                    
                else:
                    print("Control patient: ", patient)
                    ## Added the patient to the list of discharged_patients_home
                    discharged_patients_home.append((patient, discharge_type.values[0][0]))   
                    # print("+ delta MI: ", patient_df.columns[-1])

                    ## Add selected patient to the ris_discharged_patients_selected dataframe
                    ris_discharged_patients_selected = pd.concat([ris_discharged_patients_selected, full_data])
                


                # if len(filtered_criteria_1) > 0:
                # ## check if the patient has not medical imaging after 120 days of the first day of hospitalization
                # if patient_df.columns[-1] > 60:
                #     print("+ delta MI: ", patient_df.columns[-1])
                # elif patient_df.columns[-2] > 60:
                #     print("+ delta MI: ", patient_df.columns[-2])
                # else:
                #     ## Added the patient to the list of discharged_patients_home
                #     discharged_patients_home.append((patient, discharge_type.values[0][0]))   
                #     # print("+ delta MI: ", patient_df.columns[-1])

                #     ## Add selected patient to the ris_discharged_patients_selected dataframe
                #     ris_discharged_patients_selected = pd.concat([ris_discharged_patients_selected, full_data])
                
        except IndexError:
            # full_data['discharge_type'] = 'NaN'
            pass

        
    output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/05_data_exploration/02_preprocessing_NC/"                  
    # ## Save the list of potential long covid patients to a CSV file
    # potential_long_covid_patients_file = os.path.join(output_dir, f'potential_severe_pseudoid_pid.csv')
    # potential_long_covid_patients_df = pd.DataFrame(potential_long_covid_patients)
    # potential_long_covid_patients_df.to_csv(potential_long_covid_patients_file, index=False)

    # ####################
    # ## Save the additional data to the dataframe
    # long_covid_selected_file = os.path.join(output_dir, f'potential_long_covid_patients_ris_information.csv')
    # long_covid_selected.to_csv(long_covid_selected_file, index=False)
    
    # ## Save the list of deceased_patients to a CSV file
    # deceased_patients_file = os.path.join(output_dir, f'deceased_patients_pseudoid_pid.csv')
    # deceased_patients_df = pd.DataFrame(deceased_patients)
    # deceased_patients_df.to_csv(deceased_patients_file, index=False)

    # ## Save the ris information of the deceased_patients to a CSV file
    # ris_deceased_patients_selected_file = os.path.join(output_dir, f'deceased_patients_ris_information.csv')
    # ris_deceased_patients_selected.to_csv(ris_deceased_patients_selected_file, index=False)

    ## Save the list of discharged_patients_home to a CSV file
    discharged_patients_home_file = os.path.join(output_dir, f'discharged_patients_home_pseudoid_pid.csv')
    discharged_patients_home_df = pd.DataFrame(discharged_patients_home)
    discharged_patients_home_df.to_csv(discharged_patients_home_file, index=False)

    ## Save the ris information of the discharged_patients_home to a CSV file
    ris_discharged_patients_selected_file = os.path.join(output_dir, f'discharged_patients_home_ris_information.csv')
    ris_discharged_patients_selected.to_csv(ris_discharged_patients_selected_file, index=False)



################################################################################################################
file_name = "ris_data"
sep=','
feature_column_name = 'ris_examination_type'
date_column_name = 'ris_examination_begin'
value_column_name = 'value'



launcher_pipeline(file_name, sep, feature_column_name, date_column_name, value_column_name)

