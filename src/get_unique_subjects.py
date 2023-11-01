import os
import pandas as pd

def get_unique_subjects(input_file_path, output_file_path, column_name):
    try:
        # Read the input CSV file
        df = pd.read_csv(input_file_path, sep=';')

        # Get unique subjects
        unique_subjects = df[column_name].unique()
        print("+ unique_subjects:", len(unique_subjects))

        # Drop duplicates
        df_unique_subjects = df.drop_duplicates(subset=[column_name])
        print("+ df_unique_subjects:", df_unique_subjects.shape)

        # Save unique subjects
        unique_subjects_output_file = os.path.join(output_file_path)
        df_unique_subjects.to_csv(unique_subjects_output_file, sep=';', index=False)
        print("+ unique_subjects_output_file:", unique_subjects_output_file)

    except Exception as e:
        print("An error occurred:", str(e))


if __name__ == "__main__":
    input_dir_path = "/data/01_multiomics/02_long_covid_study/00_data_indexing/00_Bern/01_csv_to_process/"
    input_file_name = "herkus_manual_selection_group2_230913-elegibles.csv"
    input_file_path = os.path.join(input_dir_path, input_file_name)

    output_dir_path = "/data/01_multiomics/02_long_covid_study/00_data_indexing/00_Bern/02_csv_with_unique_PID/"
    output_file_name = "herkus_manual_selection_group2_230913-elegibles-uniquePIDs.csv"
    output_file_path = os.path.join(output_dir_path, output_file_name)

    get_unique_subjects(input_file_path, output_file_path, column_name='PID')