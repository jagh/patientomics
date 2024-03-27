
"""
Step 4.2: The aim for this script is to visualize the cluster analysis results from time series clinical matrix.
"""


import sys
print(sys.path)

import os
import pandas as pd
import numpy as np



def hierarchical_clustering_OLD(df, method='average', metric='euclidean', figsize=(12, 8), center=10):
    # Set NaN values to 0
    df = df.fillna(0)

    # Extract the feature columns and sample data
    feature_names = df.columns
    samples = df.values

    # Extract patients ids
    patient_ids = df.index.values

    # Standardize the data before calculating distances
    scaler = StandardScaler()
    scaled_samples = scaler.fit_transform(samples)

    # Calculate pairwise Euclidean distances
    similarities = hierarchy.linkage(scaled_samples, method=method, metric=metric)

    # Create a hierarchical clustering dendrogram
    plt.figure(figsize=figsize)
    hierarchy.dendrogram(similarities, labels=patient_ids, orientation='left', leaf_font_size=8)
    plt.title(f'Hierarchical Clustering Dendrogram ({method}, {metric})')
    plt.xlabel('Distance')
    plt.ylabel('Patients')
    plt.show()

    # Create a dendroheatmap
    plt.figure(figsize=figsize)
    heatmap = dhm.DendroHeatMap(df, row_linkage=similarities, col_linkage=similarities)
    heatmap.plot(cbar=True, scale_axis='row', cmap='coolwarm', center=center)
    plt.title(f'Hierarchical Clustering DendroHeatMap ({method}, {metric})')
    plt.xlabel('Features')
    plt.show()


def hierarchical_clustering(df, method='average', metric='euclidean', figsize=(12, 8), center=10):

    import matplotlib
    matplotlib.use('TkAgg')  # Or another backend like 'Qt5Agg'


    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from scipy.cluster import hierarchy
    from sklearn.preprocessing import StandardScaler

    # Set NaN values to 0
    df = df.fillna(0)

    # Extract the feature columns and sample data
    feature_names = df.columns
    samples = df.values

    # Extract patients ids
    patient_ids = df.index.values

    # Standardize the data before calculating distances
    scaler = StandardScaler()
    scaled_samples = scaler.fit_transform(samples)

    # Calculate pairwise Euclidean distances
    similarities = hierarchy.linkage(scaled_samples, method=method, metric=metric)

    # Create a hierarchical clustering dendrogram
    plt.figure(figsize=figsize)
    hierarchy.dendrogram(similarities, labels=patient_ids, orientation='left', leaf_font_size=8)
    plt.title(f'Hierarchical Clustering Dendrogram ({method}, {metric})')
    plt.xlabel('Distance')
    plt.ylabel('Patients')
    plt.show()
    # plt.savefig('dendrogram.png')

    # Create a dendroheatmap
    plt.figure(figsize=figsize)
    ordered_df = df.iloc[np.argsort(hierarchy.leaves_list(similarities))]
    ordered_samples = scaled_samples[np.argsort(hierarchy.leaves_list(similarities))]
    ordered_similarity = hierarchy.linkage(ordered_samples, method=method, metric=metric)
    
    plt.imshow(ordered_df, aspect='auto', cmap='coolwarm')
    plt.colorbar(label='Value')
    plt.title(f'Hierarchical Clustering DendroHeatMap ({method}, {metric})')
    plt.xlabel('Features')
    plt.ylabel('Patients')
    plt.show()
    # plt.savefig('dendroheatmap.png')
    # print("Dendroheatmap saved path: ", os.path.abspath('dendroheatmap.png'))


# # Set the day range to be selected
# init_day = 0
# end_day = 2

# # Load the list of laboratory features
# dir_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/05_data_exploration/01_preprocessing_116_PLCP/'
# filename = os.path.join(dir_path, 'lab_parameter_grouping.csv')
# df_lab_features = pd.read_csv(filename, sep=',', header=0)

# # Load data
# dir_path = '/home/jagh/Documents/01_UB/MultiOmiX/patientomics/data/05_data_exploration/01_preprocessing_116_PLCP/'
# filename = os.path.join(dir_path, f'116_plcp_lab_markers_day-{init_day}.csv')
# df = pd.read_csv(filename, sep=',', header=0, index_col=0)

# # Set the 'df' columns in the order of the 'df_lab_features'
# df = df.reindex(columns=df_lab_features['lab_parameter'].tolist())

# # Set the df without the first two columns
# df = df.iloc[:, 2:].copy()

# # Set NaN values to 0
# df = df.fillna(-1)

# # Call the hierarchical_clustering function
# hierarchical_clustering(df, method='average', metric='euclidean', figsize=(12, 30), center=10)
    






#################################################################
#################################################################
#################################################################
    

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