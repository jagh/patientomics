
"""
Step 4.2: The aim for this script is to visualize the cluster analysis results from time series clinical matrix.
"""    

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances
from sklearn.manifold import MDS


## Set the day range to be selected
init_day = 6
# end_day = 2

## Load data
dir_path = '/data/01_multiomics/02_long_covid_study/04_lung_function_tests/03_FirstAnalysis/02_time_series_matrices'
# filename = os.path.join(dir_path, 'lab_data_exploration.csv')
filename = os.path.join(dir_path, f'04_LongCovid_IDS_keys_clinical_data-{init_day}_original_sorted_normalized_filled.csv')
# filename = os.path.join(dir_path, f'116_plcp_lab_markers_day_Imputed-{init_day}_to_{end_day}_starting.csv')
df = pd.read_csv(filename, sep=',', header=0, index_col=0)


# ## Load the list of laboratory features
# dir_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/05_data_exploration/01_preprocessing_116_PLCP/'
# filename = os.path.join(dir_path, 'lab_parameter_grouping.csv')
# df_lab_features = pd.read_csv(filename, sep=',', header=0)

# ## Set the 'df' columns in the order of the 'df_lab_features'
# df = df.reindex(columns=df_lab_features['lab_parameter'].tolist())

## Set the df without the first two columns
df = df.iloc[:, 2:].copy()

## Set NaN values to 0
df = df.fillna(-1)

# Standardize the data before calculating distances
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)

# Calculate pairwise distances using Euclidean distance
similarities = pairwise_distances(scaled_data, metric='euclidean')

# Multidimensional scaling
seed = np.random.RandomState(seed=3)
mds = MDS(n_components=2, max_iter=5000, eps=1e-12, random_state=seed, dissimilarity='precomputed', n_jobs=1, metric=False)
pos = mds.fit_transform(similarities)

# Features as a heatmap
corr = df.corr()

# Set up the matplotlib figure, adjust size
plt.figure(figsize=(12, 8))

# Draw the heatmap using seaborn
sns.heatmap(corr, cmap='coolwarm', annot=False, fmt=".2f", center=0)

plt.show()