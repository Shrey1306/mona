# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 19:08:03 2024

@author: abhis
"""

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd

clean_df = pd.read_csv('clusters_added_clean_data_revised.csv')
features_for_pca = clean_df.drop(columns=['Cluster_Labels', 'Company_Name', 'Ticker', 'Company_Name_Encoded', 'Industry_Encoded'])

# Initialize PCA for 2D reduction
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(features_for_pca)

# Assuming 'cluster_labels' contains your cluster labels
cluster_labels = clean_df['Cluster_Labels']

# Plotting the 2D PCA-reduced space
plt.figure(figsize=(10, 8))
plt.scatter(X_pca_2d[:, 0], X_pca_2d[:, 1], c=cluster_labels, cmap='viridis', marker='o', alpha=0.7, edgecolor='k')
plt.title('Clusters Visualized in PCA-Reduced 2D Space')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.colorbar(label='Cluster Label')
plt.show()

pca_3d = PCA(n_components=3)
X_pca_3d = pca_3d.fit_transform(features_for_pca)

# Creating a 3D plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot in 3D PCA-reduced space
scatter = ax.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2], 
                     c=cluster_labels, cmap='viridis', marker='o', alpha=0.7, edgecolor='k')

# Labeling the axes
ax.set_title('Clusters Visualized in PCA-Reduced 3D Space')
ax.set_xlabel('Principal Component 1')
ax.set_ylabel('Principal Component 2')
ax.set_zlabel('Principal Component 3')

# Adding a color bar to indicate cluster labels
cbar = plt.colorbar(scatter, ax=ax, pad=0.1)
cbar.set_label('Cluster Label')

plt.show()
