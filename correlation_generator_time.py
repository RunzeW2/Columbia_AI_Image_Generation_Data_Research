import pandas as pd
import numpy as np
# Methodology explanation:
# 1.	Load the “generated_content_metadata” and “engagement” csv files.
# 2.    For the "engagement" csv file, filter DataFrame for the value in "engagement_type" is "MillisecondsEngagedWith".
#       Then find the average of the "engagement_value" column for each "content_id".
# 3.	Create a new Dataframe called "processed_engagement" that contains only the following columns:"content_id", "average_engagement_value" 
#       and put the average engagement value for each content_id in the "average_engagement_value" column. matching the content_id.
# 2.	Merge the "generated_content_metadata" and "processed_engagement" DataFrames based on the 'content_id' column
#       by placing the "average_engagement_value" column on the right side of the "generated_content_metadata" DataFrame with matching "content_id".
# 4.	Group rows with same “num_inference_steps” and same “guidance_scale” and same "artist_style"
#       Do correlation analysis for column “seed” against the "average_engagement_value" column. 
#       Then average out the correlation value for all groups.
# 5.	Group rows with same “seed” and same “guidance_scale” and same "artist_style"
#       Do correlation analysis for column “num_inference_steps” against the "average_engagement_value" column. 
#       Then average out the correlation value for all groups.
# 6.	Group rows with same “num_inference_steps” and same “seed” and same "artist_style"
#       Do correlation analysis for column “guidance_scale” against the "average_engagement_value" column. 
#       Then average out the correlation value for all groups.


# Now let's get started!

# Load the CSV files
generated_content_metadata = pd.read_csv('generated_content_metadata.csv')
engagement = pd.read_csv('engagement.csv')

# Filter the "engagement" DataFrame
filtered_engagement = engagement[engagement['engagement_type'] == 'MillisecondsEngagedWith']

# Calculate the average engagement value for each content_id
average_engagement = filtered_engagement.groupby('content_id')['engagement_value'].mean().reset_index()
average_engagement.columns = ['content_id', 'average_engagement_value']

# Create the "processed_engagement" DataFrame
processed_engagement = average_engagement[['content_id', 'average_engagement_value']]

# Merge the DataFrames on 'content_id'
merged_data = pd.merge(generated_content_metadata, processed_engagement, on='content_id', how='left')

# Ensure numeric columns are of the correct type
numeric_cols = ['seed', 'guidance_scale', 'num_inference_steps', 'average_engagement_value']
merged_data[numeric_cols] = merged_data[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values in the columns of interest
merged_data.dropna(subset=numeric_cols, inplace=True)

# Define the safe_corr function if not already defined
def safe_corr(df, col1, col2):
    if df[col1].nunique() > 1 and len(df) > 1:
        return df[col1].corr(df[col2])
    else:
        return None  # Return None to indicate that the correlation couldn't be computed

# Test code for diagnosing the num_inference_steps correlation issue
grouped = merged_data.groupby(['num_inference_steps', 'seed', 'artist_style'])
test_correlations = grouped.apply(lambda df: safe_corr(df, 'guidance_scale', 'average_engagement_value'))

# Print out the test correlations
print("Test correlations for each group:")
print(test_correlations)

# Check for any groups that returned a non-null correlation
non_null_correlations = test_correlations[test_correlations.notnull()]
print("\nGroups with non-null correlations:")
print(non_null_correlations)

# If there are no non-null correlations, print out some diagnostics
if non_null_correlations.empty:
    print("\nNo non-null correlations found. Diagnostics:")
    for name, group in grouped:
        print(f"Group: {name}")
        print(f"Unique values in 'guidance_scale': {group['guidance_scale'].nunique()}")
        print(f"Number of rows: {len(group)}")
        print(f"Correlation: {safe_corr(group, 'guidance_scale', 'average_engagement_value')}")
        print("-" * 40)

# Group and compute correlations for different combinations
groupings = {
    'seed': ['num_inference_steps', 'guidance_scale', 'artist_style'],
    'num_inference_steps': ['guidance_scale', 'seed'],
    'guidance_scale': ['num_inference_steps', 'seed', 'artist_style']
}

# Initialize a dictionary to store correlation results
correlation_results = {}

# Calculate correlations for each grouping and save the individual group correlations
for target_col, group_cols in groupings.items():
    grouped = merged_data.groupby(group_cols)
    # Apply the safe_corr function to each group
    correlations = grouped.apply(lambda df: safe_corr(df, target_col, 'average_engagement_value'))
    
    # Convert the Series to a DataFrame if it's not already one
    if isinstance(correlations, pd.Series):
        correlations_df = correlations.reset_index()
        correlations_df.rename(columns={0: f'{target_col}_correlation'}, inplace=True)
    else:
        correlations_df = correlations

    # Ensure the column exists before attempting to drop NaN values
    if f'{target_col}_correlation' in correlations_df.columns:
        correlations_df.dropna(subset=[f'{target_col}_correlation'], inplace=True)
    
    # Save the DataFrame to a CSV file
    correlations_df.to_csv(f'{target_col}_correlations_time.csv', index=False)
    
    # Calculate and print the average correlation, excluding NaN values
    average_correlation = correlations.mean()
    print(f'Average correlation for {target_col}: {average_correlation}')
