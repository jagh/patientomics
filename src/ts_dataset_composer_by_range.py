
import os
import pandas as pd

def impute_missing_values(df_lab_selected_day, df_lab_days, columns_to_impute):
    """Function for data imputation using substitution method"""
    
    imputed_values = []  # Store imputed values
    
    for column in columns_to_impute:
        missing_values = df_lab_selected_day[column].isna()
        
        if not missing_values.all():
            for index, row in df_lab_selected_day[missing_values].iterrows():
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

def process_patient_data(patient_id, init_day, end_day, dir_lab_path):
    """Process data for a single patient."""
    filename = os.path.join(dir_lab_path, f'patient_{patient_id}.csv')
    
    try:
        df_lab = pd.read_csv(filename, sep=',', header=0)
        df_lab_days = df_lab[df_lab['days'].between(init_day, end_day)].copy()
        columns_to_impute = df_lab_days.columns[2:-1].tolist()
        
        patient_dfs = []
        all_imputed_values = []
        
        for selected_day in range(init_day, end_day + 1):
            df_lab_day_selected = df_lab_days[df_lab_days['days'] == selected_day].copy()
            df_lab_day_selected, imputed_values = impute_missing_values(df_lab_day_selected, df_lab_days, columns_to_impute)
            all_imputed_values.extend(imputed_values)
            df_lab_day_selected['patient_id'] = patient_id
            patient_dfs.append(df_lab_day_selected)
        
        collection_df = pd.concat(patient_dfs, ignore_index=True)
        return collection_df, all_imputed_values
    
    except Exception as e:
        print(f"Error reading patient {patient_id}: {str(e)}")
        return None, None


##########################################
# Set the day range to be selected
init_day = 0
end_day = 60

# Read the list of unique patient IDs
dir_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/05_data_exploration/01_preprocessing_116_PLCP/'
filename = os.path.join(dir_path, 'deceased_patients_pseudoid_pid.csv')
df = pd.read_csv(filename, sep=',', header=0)

# Initialize an empty list to store patient DataFrames
all_patient_dfs = []
all_imputed_values = []

# Iterate through the patient IDs
for patient_id in df['pseudoid_pid']:
    dir_lab_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/06_clinical_data/lab_data_features/'
    collection_df, imputed_values = process_patient_data(patient_id, init_day, end_day, dir_lab_path)
    
    if collection_df is not None:
        all_patient_dfs.append(collection_df)
        all_imputed_values.extend(imputed_values)

# Concatenate all patient DataFrames into one
collection_df = pd.concat(all_patient_dfs, ignore_index=True)

# Save the resulting DataFrame as a CSV file
output_csv_path = os.path.join(dir_path, f'deceased_lab_markers_day_Imputed-{init_day}_to_{end_day}.csv')
collection_df.to_csv(output_csv_path, index=False)

# Save the imputed values to a separate file if needed
imputed_values_file = os.path.join(dir_path, f'deceased_lab_imputed_values.csv')
pd.Series(all_imputed_values).to_csv(imputed_values_file, index=False, header=['Imputed_Values'])