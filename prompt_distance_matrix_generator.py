import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform, cdist
import ast
from tqdm import tqdm
import h5py

# Read in the data.
data = pd.read_csv('generated_content_metadata.csv')

# Convert the 'prompt_embedding' column to a list of lists of floats
embeddings = [ast.literal_eval(embedding) for embedding in data['prompt_embedding'].tolist()]

# Convert the list to a 2D numpy array
embeddings = np.array(embeddings)

# Get the unique IDs
unique_ids = data['id'].unique()

# Create a new HDF5 file
with h5py.File('distance_matrix.hdf5', 'w') as f:
    # Create a dataset in the file
    distance_matrix = f.create_dataset("distance_matrix", (len(unique_ids), len(unique_ids)), dtype='float16')

    # Calculate the pairwise distances for each chunk of embeddings
    for i in tqdm(range(len(unique_ids))):
        for j in range(i+1):
            # Calculate the distance between the two embeddings
            distance = np.linalg.norm(embeddings[i] - embeddings[j])

            # Store the distance in the dataset
            distance_matrix[i, j] = distance

    # Flush the data to disk
    f.flush()
