
"""
Step 4.1: The aim for this script is to create a time series clinical matrix from the clinical data.
        This script include the following steps:
            - Read the list of unique patient IDs
            - Initialize an empty list to store patient DataFrames
            - Set the day range to be selected
            - Iterate through the patient IDs
            - Read patient data
            - Get the row features from 'df_lab' for the selected day range
            - Get the columns to impute
            - Process patient data
            - Append processed patient DataFrames
            - Concatenate all patient DataFrames into one
            - Save the time series clinical matrices to CSV files
"""


import os
import pandas as pd
from sklearn.impute import KNNImputer

def read_patient_data(patient_id, dir_lab_path):
    """Read patient data from CSV file"""
    filename = os.path.join(dir_lab_path, f'patient_{patient_id}.csv')
    return pd.read_csv(filename, sep=',', header=0)

def impute_missing_values(df, columns_to_impute, n_neighbors=1):
    """Impute missing values using KNNImputer"""
    imputer = KNNImputer(n_neighbors=n_neighbors)
    for column in columns_to_impute:
        column_values = df[[column]].values
        imputed_values = imputer.fit_transform(column_values)
        df[column] = imputed_values
    return df

def process_patient(patient_id, df_lab_days, columns_to_impute, n_neighbors=1):
    """Process patient data for each selected day"""
    patient_dfs_imputed = []
    patient_dfs_original = []
    for selected_day in df_lab_days['days'].unique():
        df_lab_day_selected = df_lab_days[df_lab_days['days'] == selected_day].copy()
        df_lab_day_original = df_lab_day_selected.copy()
        
        df_lab_day_imputed = impute_missing_values(df_lab_day_selected, columns_to_impute, n_neighbors)
        
        df_lab_day_imputed.insert(0, 'patient_id', patient_id)
        df_lab_day_original.insert(0, 'patient_id', patient_id)
        
        patient_dfs_imputed.append(df_lab_day_imputed)
        patient_dfs_original.append(df_lab_day_original)
        
    return pd.concat(patient_dfs_imputed, ignore_index=True), pd.concat(patient_dfs_original, ignore_index=True)

def sort_clinical_features(collection_df, df_lab_features):
    """Sort clinical features based on the list of laboratory features"""
    sorted_columns = ['patient_id'] + df_lab_features['lab_parameter'].tolist()
    return collection_df.reindex(columns=sorted_columns)

def main():
    # Read the list of unique patient IDs
    dir_path = '/data/01_multiomics/02_long_covid_study/04_lung_function_tests/03_FirstAnalysis/02_time_series_matrices/'
    filename = os.path.join(dir_path, '03_LongCovid_IDS_keys_clinical_data_OnlyLabDATA.csv')
    df = pd.read_csv(filename, sep=',', header=0)

    # Initialize an empty list to store patient DataFrames
    patient_dfs_imputed = []
    patient_dfs_original = []

    # Set the day range to be selected
    init_day = 0
    end_day = 60

     # Set path for lab data
    dir_lab_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/06_clinical_data/lab_data_features/'


    # Load the list of laboratory features
    lab_features_filename = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/lab_parameter_grouping.csv'
    df_lab_features = pd.read_csv(lab_features_filename, sep=',', header=0)

    # Iterate through the patient IDs
    for patient_id in df['pseudoid_pid']:
        try:
            # Read patient data
            df_lab = read_patient_data(patient_id, dir_lab_path)

            # Get the row features from 'df_lab' for the selected day range
            df_lab_days = df_lab[df_lab['days'].between(init_day, end_day)].copy()

            # Get the columns to impute
            columns_to_impute = df_lab_days.columns[2:-1].tolist()

            # Process patient data
            df_imputed, df_original = process_patient(patient_id, df_lab_days, columns_to_impute, n_neighbors=7)

            # Append processed patient DataFrames
            patient_dfs_imputed.append(df_imputed)
            patient_dfs_original.append(df_original)
        except Exception as e:
            print(f"Error reading patient {patient_id}: {str(e)}")
            continue

    # Concatenate all patient DataFrames into one
    collection_df_imputed = pd.concat(patient_dfs_imputed, ignore_index=True)
    collection_df_original = pd.concat(patient_dfs_original, ignore_index=True)

    # Save the time series clinical matrices to CSV files
    output_csv_path_imputed = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_to_{end_day}_imputed.csv')
    output_csv_path_original = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_to_{end_day}_original.csv')
    collection_df_imputed.to_csv(output_csv_path_imputed, index=False)
    collection_df_original.to_csv(output_csv_path_original, index=False)


    # Sort clinical features based on the list of laboratory features
    collection_df_imputed_sorted = sort_clinical_features(collection_df_imputed, df_lab_features)
    collection_df_original_sorted = sort_clinical_features(collection_df_original, df_lab_features)

    # Save the time series clinical matrices to CSV files
    output_csv_path_imputed = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_to_{end_day}_imputed_sorted.csv')
    output_csv_path_original = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_to_{end_day}_original_sorted.csv')
    collection_df_imputed_sorted.to_csv(output_csv_path_imputed, index=False)
    collection_df_original_sorted.to_csv(output_csv_path_original, index=False)

if __name__ == "__main__":
    main()