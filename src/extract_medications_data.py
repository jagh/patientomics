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


def categorize_data(df, lab_categories):
    """
    Adds lab_categories column to the DataFrame based on lab_name.

    Args:
        df (pd.DataFrame): The input DataFrame.
        lab_categories (dict): Dictionary mapping lab categories to their corresponding lab names.

    Returns:
        pd.DataFrame: The DataFrame with the lab_categories column added.
    """
    df_lab_categorized = df.copy()
    df_lab_categorized['lab_categories'] = df_lab_categorized['lab_name'].map(
        lambda lab_name: next((category for category, features in lab_categories.items() if lab_name in features), 'Unknown')
    )
    return df_lab_categorized


def save_categorized_data(df, file_path):
    """
    Saves the categorized data to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to be saved.
        file_path (str): Path to save the CSV file.
    """
    df.to_csv(file_path, index=False)


def group_and_plot_data(df, patient_id, max_days):
    """
    Groups the DataFrame by patient pseudoid_pid and plots the lab values.

    Args:
        df (pd.DataFrame): The input DataFrame.
        patient_id (int): The ID of the patient to filter the data.
        max_days (int): Maximum number of days to consider for plotting.

    """
    patient_data = df[df['pseudoid_pid'] == patient_id]
    unique_lab_categories = patient_data['lab_categories'].unique()

    for lab_category in unique_lab_categories:
        category_data = patient_data[patient_data['lab_categories'] == lab_category]
        unique_lab_names = category_data['lab_name'].unique()
        num_rows = len(unique_lab_names)
        num_cols = 1

        fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(8, 10), sharex=True)
        axes = axes.flatten()

        for i, lab_name in enumerate(unique_lab_names):
            ax = axes[i]
            ax.set_title(lab_name)
            lab_data = category_data[category_data['lab_name'] == lab_name]
            lab_data['lab_req_date'] = pd.to_datetime(lab_data['lab_req_date'])
            lab_data['lab_req_date'] = (lab_data['lab_req_date'] - lab_data['lab_req_date'].min()).dt.days
            lab_data = lab_data[lab_data['lab_req_date'] <= max_days]
            lab_data = lab_data.sort_values(by='lab_nval')
            ax.scatter(lab_data['lab_req_date'], lab_data['lab_nval'], marker='o')

            for x, y, val in zip(lab_data['lab_req_date'], lab_data['lab_nval'], lab_data['lab_nval']):
                ax.text(x, y, str(val), ha='center', va='bottom')

        fig.suptitle(f'Patient ID: {patient_id} - Lab Category: {lab_category}')
        plt.tight_layout()
        plt.show()


def csv_lab_per_patient(df, output_dir):
    grouped_df = df.groupby('pseudoid_pid')

    for patient, data in grouped_df:
        patient_csv = pd.DataFrame()

        for lab_name, lab_data in data.groupby('lab_name'):
            min_date = lab_data['lab_req_date'].min()
            lab_data['days'] = (lab_data['lab_req_date'] - min_date).dt.days

            # Convert lab_nval to numeric, handling non-numeric values
            lab_data['lab_nval'] = pd.to_numeric(lab_data['lab_nval'], errors='coerce')

            lab_data = lab_data.pivot_table(index='lab_name', columns='days', values='lab_nval', aggfunc='mean')
            lab_data.columns = [f'day-{day}' for day in lab_data.columns]

            patient_csv = pd.concat([patient_csv, lab_data])

        patient_csv_file = os.path.join(output_dir, f'patient_{patient}.csv')
        patient_csv.to_csv(patient_csv_file)


def csv_med_per_patient_old(df, output_dir):
    grouped_df = df.groupby('pseudoid_pid')

    for patient, data in grouped_df:
        patient_csv = pd.DataFrame()

        for med_name, med_data in data.groupby('med_atc'):
            min_date = med_data['med_date'].min()
            med_data['days'] = (med_data['med_date'] - min_date).dt.days

            # Convert med_given_dose to numeric, handling non-numeric values
            med_data['med_given_dose'] = pd.to_numeric(med_data['med_given_dose'], errors='coerce')

            med_data = med_data.pivot_table(index='med_atc', columns='days', values='med_given_dose', aggfunc='mean')
            med_data.columns = [f'day-{day}' for day in med_data.columns]

            patient_csv = pd.concat([patient_csv, med_data])

        patient_csv_file = os.path.join(output_dir, f'patient_{patient}.csv')
        patient_csv.to_csv(patient_csv_file)


def save_medications_dict_to_csv(medications_dict, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['med_act', 'med_medication'])  # Write header row
        for code, name in medications_dict.items():
            writer.writerow([code, name])
    print(f"Medications dictionary saved to {output_file}")


def csv_med_per_patient(df, output_dir):
    grouped_df = df.groupby('pseudoid_pid')

    for patient, data in grouped_df:
        patient_csv = pd.DataFrame()

        for med_name, med_data in data.groupby('med_atc'):
            min_date = med_data['med_date'].min()
            med_data['days'] = (med_data['med_date'] - min_date).dt.days

            # Check if any value in 'med_given_dose' column is null
            if med_data['med_given_dose'].isnull().any():
                # Convert 'med_given_dose' to numeric, handling non-numeric values
                med_data['med_given_dose'] = pd.to_numeric(med_data['med_given_dose'], errors='coerce')
            else:
                # Convert 'med_dose' to numeric, handling non-numeric values
                med_data['med_dose'] = pd.to_numeric(med_data['med_dose'], errors='coerce')

            med_data = med_data.pivot_table(index='med_atc', columns='days', values='med_given_dose', aggfunc='mean')
            med_data.columns = [f'day-{day}' for day in med_data.columns]

            patient_csv = pd.concat([patient_csv, med_data])

        patient_csv_file = os.path.join(output_dir, f'patient_{patient}.csv')
        patient_csv.to_csv(patient_csv_file)




# Step 1: Read the CSV file into a DataFrame
dir_CDA_features = "/home/jagh/Documents/01_UB/10_Conferences_submitted/11_Second_paper/00_dataset/03_Insel_dataset/01_Preprocessing_IDSC202101463_data_v13_20221214/"
file_name = "medications"
csv_file_path = os.path.join(dir_CDA_features, file_name + ".csv")
df = read_csv(csv_file_path, sep=';')

# Step 2: Preprocess and categorize the data
df = preprocess_data(df, 'med_date')

# print("df.head():", df.head())

# Step 3: Categorize the data
# Filter unique laboratory codes 'med_atc' with respective laboratory feature names 'med_medication'
medications_data = df[['med_atc', 'med_medication']].drop_duplicates()

# Create a dictionary to store the unique laboratory codes as keys and their respective feature names as values
medications_dict = {code: name for code, name in medications_data.values}

# Extract the unique laboratory codes
medications_codes = list(medications_dict.keys())
# Extract the unique laboratory feature names
medications_names = list(medications_dict.values())

print('medications_names:', medications_codes)
print('medications_names count:', len(medications_names))

## Step 4: Save the data per patient in a CSV file
medications_file_name = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/dicts/medications.csv"
save_medications_dict_to_csv(medications_dict, medications_file_name)

## Step 5: Save the data per patient in a CSV file
output_dir = "/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/medication_features/"
csv_med_per_patient(df, output_dir)

