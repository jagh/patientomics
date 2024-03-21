
"""
Step 4.1: The aim for this script is to create a time series clinical matrix from the clinical data.
"""


import os
import pandas as pd



def impute_missing_values(df_lab_selected_day, df_lab_days, columns_to_impute):
    """Function for data imputation using substitution method"""

    imputed_values = []  # Store imputed values
    
    for column in columns_to_impute:
        if not df_lab_selected_day[column].isna().all():
            for index, row in df_lab_selected_day.iterrows():
                if pd.isna(row[column]):
                    # Find the nearest available value from days after the missing day
                    next_day_values = df_lab_days[df_lab_days['days'] > row['days']].sort_values(by='days')
                    if not next_day_values.empty:
                        next_day_value = next_day_values.iloc[0][column]
                        df_lab_selected_day.at[index, column] = next_day_value
                        imputed_values.append(next_day_value)
                    else:
                        # If no values are available from days after, use the nearest available value from days before
                        prev_day_values = df_lab_days[df_lab_days['days'] < row['days']].sort_values(by='days', ascending=False)
                        if not prev_day_values.empty:
                            prev_day_value = prev_day_values.iloc[0][column]
                            df_lab_selected_day.at[index, column] = prev_day_value
                            imputed_values.append(prev_day_value)
    
    return df_lab_selected_day, imputed_values



##########################################
##########################################
## Read the list of unique patient IDs
dir_path = '/data/01_multiomics/02_long_covid_study/04_lung_function_tests/03_FirstAnalysis/01_pairing_long_covid_clinical_data'
filename = os.path.join(dir_path, '03_LongCovid_IDS_keys_clinical_data_OnlyLabDATA.csv')
df = pd.read_csv(filename, sep=',', header=0)



# Initialize an empty list to store patient DataFrames
patient_dfs = []

# Set the day range to be selected
init_day = 0
end_day = 60

# Initialize a list to store all imputed values
all_imputed_values = []

# Iterate through the patient IDs
for patient_id in df['pseudoid_pid']:
    dir_lab_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/06_clinical_data/lab_data_features/'
    filename = os.path.join(dir_lab_path, f'patient_{patient_id}.csv')

    try:
        # Read the CSV file into a DataFrame for each patient
        df_lab = pd.read_csv(filename, sep=',', header=0)

        # Get the row features from 'df_lab' for the selected day range
        df_lab_days = df_lab[df_lab['days'].between(init_day, end_day)].copy()

        # Get the columns to impute from the dataframe df_lab_days
        columns_to_impute = df_lab_days.columns[2:-1].tolist()

        # Iterate through the selected days
        for selected_day in range(init_day, end_day + 1):
            # Get the row features for a specific day in 'days' column
            df_lab_day_selected = df_lab_days[df_lab_days['days'] == selected_day].copy()

            # Apply data imputation for the selected day
            df_lab_day_selected, imputed_values = impute_missing_values(df_lab_day_selected, df_lab_days, columns_to_impute)
            all_imputed_values.extend(imputed_values)  # Append imputed values to the list

            # Add a column 'patient_id' into the df_lab_day_selected
            df_lab_day_selected['patient_id'] = patient_id

            # Append the patient DataFrame to the list
            patient_dfs.append(df_lab_day_selected)

    except Exception as e:
        print(f"Error reading patient {patient_id}: {str(e)}")
        continue

# Concatenate all patient DataFrames into one
collection_df = pd.concat(patient_dfs, ignore_index=True)


#####################################################
## Save the time series clinical matrix to a CSV file
output_csv_path = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_to_{end_day}.csv')
collection_df.to_csv(output_csv_path, index=False)

## Save the imputed values to a separate file if needed
imputed_values_file = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data_.csv')
print(f"Imputed values saved to: {type(all_imputed_values)}")   
print(f"Imputed values saved to: {all_imputed_values}")   




# pd.Series(all_imputed_values).to_csv(imputed_values_file, index=False) #, header=['Imputed_Values'])

