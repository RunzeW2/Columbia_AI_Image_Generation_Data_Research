import h5py
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd

# Read ids
data = pd.read_csv('generated_content_metadata.csv')
ids = data['id']
prompt = data['prompt']
# Number of random distances to pick
num_samples = 100

prompt_1 = []
prompt_2 = []
id_1 = []
id_2 = [] 
distance = []
# Open the HDF5 file
with h5py.File('distance_matrix.hdf5', 'r') as f:
    # Get the dataset from the file
    distance_matrix = f["distance_matrix"]

    # Calculate the number of rows in the matrix
    num_rows = distance_matrix.shape[0]

    # Generate random row and column indices
    rows = np.random.randint(0, num_rows, num_samples)
    cols = np.random.randint(0, rows, num_samples)  # Ensure cols <= rows for lower triangular part

    # Read the randomly picked distances from the file
    random_distances = np.array([distance_matrix[i, j] for i, j in zip(rows, cols)])
    prompt_1 = np.array([prompt[i] for i in rows])
    prompt_2 = np.array([prompt[j] for j in cols])
    id_1 = np.array([ids[i] for i in rows])
    id_2 = np.array([ids[j] for j in cols])
    
# Export prompt_1 and prompt_2 and their distances in three columns in an excel
df = pd.DataFrame({'id_1':id_1,'id_2':id_2, 'prompt_1': prompt_1, 'prompt_2': prompt_2, 'distance': random_distances})
df.to_excel('prompt_sample_distances_comparison.xlsx', index=False)

# Calculate the mean and variance of the distances
mean = np.mean(random_distances)
variance = np.var(random_distances, dtype=np.float64)

# Create a histogram of the distances
plt.hist(random_distances, bins=30, edgecolor='black')

# Display the mean and variance on the plot
plt.title(f'Mean: {mean:.2f}, Variance: {variance:.2f}')

# Display the plot
plt.show()