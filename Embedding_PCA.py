#UMAP analysis of the data
import umap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#load the csv data
data = pd.read_csv('generated_content_metadata.csv')
selected_data = data['prompt_embedding']
# Initiate the reducer

from sklearn.cluster import KMeans

# Assume 'n_clusters' is the number of clusters you want to create
n_clusters = 1400

# Reshape your data if it's a 1D array
selected_data = selected_data.values.reshape(-1, 1)

# Create an instance of KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=0)

# Fit the model to your data and predict the cluster assignments
clusters = kmeans.fit_predict(selected_data)

# Add the cluster assignments to your DataFrame
data['cluster'] = clusters
# Assume 'selected_data' is your DataFrame
# Do not reshape your data to (-1, 1) if you want to cluster based on the values of the entire vector

# Create an instance of KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=0)

# Fit the model to your data and predict the cluster assignments
clusters = kmeans.fit_predict(selected_data)

# Create a DataFrame that shows the column ID number and the corresponding cluster assignment
cluster_df = pd.DataFrame({'Column_ID': selected_data.columns, 'Cluster': clusters})

# If you want to add the cluster assignments to your original DataFrame, you can do so like this:
for i in range(n_clusters):
    data['cluster_' + str(i)] = clusters == i