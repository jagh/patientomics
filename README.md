# Description

This project aims to predict long-term outcomes and chronic risk factors in long COVID patients by integrating clinical time series data and medical images.

Steps:

1. Data Harmonization: Combine clinical data with medical images.
2. Patient Selection: Identify long COVID patients and negative controls.
3. Time Series Structuring: Organize patient event data.
4. Model Development: Create a time series data embedding model.


# Pipeline structuring

Step 1: Use `template_2_extract_clinical_data.py` to synchronize clinical data, compute time intervals from the first COVID-19 hospitalization day, and save the data for each patient in a CSV file.

Step 2: Use `long_covid_patient_selection.py` and `severe_covid_patients_selection.py` to select potential long COVID patients and negative controls based on specific criteria from medical images. Save the list of potential long COVID patients to a CSV file and store additional ris information in another CSV file.

Step 3: Utilize `long_covid_data_exploration.ipynb` and `negative_controls_data_exploration.ipynb` to determine quartile ranges for medical images, find acute and chronic stage CT scan pairs, and create histograms for each patient group.

Step 4: Employ `analyzing_labmarkers_for_long_covid.ipynb` to create a matrix of clinical features for N patients at a single-time-point (n_day=1 or n_day=7) and save it as a CSV file.

Step 5. Use `analyzing_labmarkers_for_long_covid.ipynb` to visualize correlations among laboratory features for potential long COVID patients using a single-time-point matrix by: a. Grouping features by laboratory families. b. Sorting features by average similarity distances. c. Creating a clustering map to visualize data patterns among potential long COVID patients.


### Tasks to Do:
- [+] Develop a script to retrieval the right examinition at the acute and chronic stages per patients include
    - Harmonize the index tables from RIS post-processed and the table from SCAN 

- [ ] Create a script to identify NII files based on specific parameters such as Thorax, LF, 1.0mm, kernel, and others, depending on the type of medical images (CTA, CTTH, CTTHABD, TH, etc.) they belong to.
   - For **CTA images**, look for files like:
     - Thorax_LE_WT_1.0_I26f_3_PE_xxxx.nii
     - Thorax_LF_1.0_I70f_3_LCAD_xxxx.nii

   - For **CTTHABD**, look for files like:
     - ThAbd_nat_LF_1.0_I70f_3_LCAD_xxxx.nii
     - ThAbd_nat_WT_1.0_I31f_3__xxxx.nii


### Repository tech stack to be implemented
- [ ] Actions Importer
- [ ] SLSA Generic Generator
- [ ] Python Application