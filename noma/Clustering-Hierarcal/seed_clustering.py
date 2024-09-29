# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 17:51:26 2024

@author: abhis
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
import numpy as np

#print(df.head())
#print(df.columns)

df = pd.read_csv('final_dataset_normalized.csv')
clean_df = df.drop(columns=['Company_Name', 'Ticker', 'Market Cap Normalized', 'Industry_Encoded', 'Company_Name_Encoded'])
#print(clean_df.columns)
#print(clean_df.iloc)
# Generate the linkage matrix
Z = linkage(clean_df, method='ward', metric='euclidean')


#Determining the Threshold for merges

last_20_merge_distances = Z[-20:, 2]  # Last 20 distances
# Prepare the x-axis indices for plotting
merge_indices = np.arange(1, len(last_20_merge_distances) + 1)
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(merge_indices, last_20_merge_distances, marker='o', linestyle='-')
plt.title('Merge Distances for the Last 20 Merges')
plt.xlabel('Merge Step (from the last 20 merges)')
plt.ylabel('Merge Distance')
plt.grid(True)

# Calculate the mean of the last 10 merge distances (excluding the last one for this mean)
mean_threshold = np.mean(last_20_merge_distances[:-1])
plt.axhline(y=mean_threshold, color='r', linestyle='--', label=f'Mean Threshold: {mean_threshold:.2f}')
plt.legend()

plt.show()
#Threshold comes to about 15


# Plotting the dendrogram with the threshold for 10 clusters highlighted
plt.figure(figsize=(15, 10))
threshold_for_10_clusters = 10
dendrogram(Z, no_labels=True, color_threshold=threshold_for_10_clusters)
plt.title('Hierarchical Clustering Dendrogram with 10 Clusters Highlighted')
plt.xlabel('Sample index')
plt.ylabel('Distance')
plt.axhline(y=threshold_for_10_clusters, c='k', ls='--', lw=0.8)
plt.text(x=0, y=threshold_for_10_clusters, s=' 10 Cluster Threshold', va='bottom', ha='left')
plt.show()

#Model fitting after dendrogram assessed
agg_clustering = AgglomerativeClustering(n_clusters=10, affinity='euclidean', linkage='ward')
labels = agg_clustering.fit_predict(clean_df)

# Adding cluster labels to the OG dataframe
df['Cluster_Labels'] = labels

for i in range(10):  # Plotted for 10 clusters
    cluster_points = df[df['Cluster_Labels'] == i]
    print(f"Cluster {i} contains points:", len(cluster_points))  
#print(df.columns)
exported_df = df.drop(columns=['Market Cap Normalized'])
exported_df.to_csv('clusters_added_clean_data_revised.csv', index=False)