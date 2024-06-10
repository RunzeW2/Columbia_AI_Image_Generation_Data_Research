import pandas as pd
import numpy as np

# Methodology explanation:
# 1.	Load the “generated_content_metadata” and “engagement” csv files.
# 2.    For the "engagement" csv file, filter DataFrame for the value in "engagement_type" is "Like".
#       Then find the sum of the "engagement_value" column for each "content_id".
# 3.	Create a new Dataframe called "processed_engagement" that contains only the following columns:"content_id", "total_engagement_value" 
#       and put the total engagement value for each content_id in the "total_engagement_value" column. matching the content_id.
# 2.	Merge the "generated_content_metadata" and "processed_engagement" DataFrames based on the 'content_id' column
#       by placing the "total_engagement_value" column on the right side of the "generated_content_metadata" DataFrame with matching "content_id".
# 4.	Group rows with same “num_inference_steps” and same “guidance_scale” and same "artist_style"
#       Do correlation analysis for column “seed” against the "total_engagement_value" column. 
#       Then average out the correlation value for all groups.
# 5.	Group rows with same “seed” and same “guidance_scale” and same "artist_style"
#       Do correlation analysis for column “num_inference_steps” against the "total_engagement_value" column. 
#       Then average out the correlation value for all groups.
# 6.	Group rows with same “num_inference_steps” and same “seed” and same "artist_style"
#       Do correlation analysis for column “guidance_scale” against the "total_engagement_value" column. 
#       Then average out the correlation value for all groups.


# Now let's get started!

# Load the CSV files
generated_content_metadata = pd.read_csv('generated_content_metadata.csv')
engagement = pd.read_csv('engagement.csv')

# Filter the "engagement" DataFrame
filtered_engagement_like = engagement[engagement['engagement_type'] == 'Like']
filtered_engagement_time = engagement[engagement['engagement_type'] == 'MillisecondsEngagedWith']

# Calculate the sum of engagement value for each content_id
total_engagement_like = filtered_engagement_like.groupby('content_id')['engagement_value'].sum().reset_index()
total_engagement_time = filtered_engagement_time.groupby('content_id')['engagement_value'].sum().reset_index()
total_engagement_like.columns = ['content_id', 'total_engagement_like']
total_engagement_time.columns = ['content_id', 'total_engagement_time']

# Create the "processed_engagement" DataFrames
processed_engagement_like = total_engagement_like[['content_id', 'total_engagement_like']]
processed_engagement_time = total_engagement_time[['content_id', 'total_engagement_time']]

# Merge the DataFrames on 'content_id'
merged_data = pd.merge(generated_content_metadata, processed_engagement_like, on='content_id', how='left')
merged_data = pd.merge(merged_data, processed_engagement_time, on='content_id', how='left')

# Add a column to track the prompt word count
merged_data['prompt_word_count'] = merged_data['prompt'].str.split().str.len()

# Add a column to track the number of items in each group
def track_group_items(group_df):
    return len(group_df)
    
# Ensure numeric columns are of the correct type
numeric_cols = ['prompt_word_count','seed', 'guidance_scale', 'num_inference_steps', 'total_engagement_like', 'total_engagement_time']
merged_data[numeric_cols] = merged_data[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values in the columns of interest
merged_data.dropna(subset=numeric_cols, inplace=True)

# Define the safe_corr function if not already defined
def safe_corr(df, col1, col2):
    if df[col1].nunique() > 1 and len(df) > 1:
        stddev1 = df[col1].std()
        stddev2 = df[col2].std()
        if stddev1 != 0 and stddev2 != 0:
            return df[col1].corr(df[col2])
    return None  # Return None to indicate that the correlation couldn't be computed
# Define the number of bins you want
num_bins = len(merged_data['guidance_scale'].unique()) // 3

# Bin the 'guidance_scale' and 'num_inference_steps' columns
merged_data['guidance_scale_bins'] = pd.cut(merged_data['guidance_scale'], bins=num_bins)
merged_data['num_inference_steps_bins'] = pd.cut(merged_data['num_inference_steps'], bins=num_bins)
# Group by the binned columns instead of the original columns
grouped = merged_data.groupby(['num_inference_steps_bins', 'guidance_scale_bins', 'seed', 'artist_style', 'prompt_word_count'])
test_correlations = grouped.apply(lambda df: safe_corr(df, 'guidance_scale', 'total_engagement_like'))

# Print out the test correlations
print("Test correlations for each group (Like):")
print(test_correlations)

# Check for any groups that returned a non-null correlation
non_null_correlations = test_correlations[test_correlations.notnull()]
print("\nGroups with non-null correlations (Like):")
print(non_null_correlations)

# If there are no non-null correlations, print out some diagnostics
if non_null_correlations.empty:
    print("\nNo non-null correlations found (Like). Diagnostics:")
    for name, group in grouped:
        print(f"Group: {name}")
        print(f"Unique values in 'guidance_scale': {group['guidance_scale'].nunique()}")
        print(f"Number of rows: {len(group)}")
        print(f"Correlation: {safe_corr(group, 'guidance_scale', 'total_engagement_like')}")
        print("-" * 40)

# Test code for diagnosing the num_inference_steps correlation issue
grouped = merged_data.groupby(['num_inference_steps', 'seed', 'artist_style', 'prompt_word_count'])
test_correlations = grouped.apply(lambda df: safe_corr(df, 'guidance_scale', 'total_engagement_time'))

# Print out the test correlations
print("Test correlations for each group (Time):")
print(test_correlations)

# Check for any groups that returned a non-null correlation
non_null_correlations = test_correlations[test_correlations.notnull()]
print("\nGroups with non-null correlations (Time):")
print(non_null_correlations)

# If there are no non-null correlations, print out some diagnostics
if non_null_correlations.empty:
    print("\nNo non-null correlations found (Time). Diagnostics:")
    for name, group in grouped:
        print(f"Group: {name}")
        print(f"Unique values in 'guidance_scale': {group['guidance_scale'].nunique()}")
        print(f"Number of rows: {len(group)}")
        print(f"Correlation: {safe_corr(group, 'guidance_scale', 'total_engagement_time')}")
        print("-" * 40)

# Group and compute correlations for different combinations
groupings = {
    'num_inference_steps': ['guidance_scale', 'seed'],
    'guidance_scale': ['num_inference_steps', 'seed', 'artist_style'],
    'prompt_word_count': ['num_inference_steps', 'guidance_scale', 'seed', 'artist_style']
}

# Initialize a dictionary to store correlation results
correlation_results = {}

# Calculate correlations for each grouping and save the individual group correlations
for target_col, group_cols in groupings.items():
    grouped = merged_data.groupby(group_cols)
    # Apply the safe_corr function to each group
    correlations = grouped.apply(lambda df: safe_corr(df, target_col, 'total_engagement_like'))
    
    # Convert the Series to a DataFrame if it's not already one
    if isinstance(correlations, pd.Series):
        correlations_df = correlations.reset_index()
        correlations_df.rename(columns={0: f'{target_col}_correlation_like'}, inplace=True)
    else:
        correlations_df = correlations

    # Ensure the column exists before attempting to drop NaN values
    if f'{target_col}_correlation_like' in correlations_df.columns:
        correlations_df.dropna(subset=[f'{target_col}_correlation_like'], inplace=True)
    
    # Add a column indicating the number of items used to calculate the correlation
    correlations_df['num_items'] = correlations_df.apply(track_group_items, axis=1)
    
    # Save the DataFrame to a CSV file
    correlations_df.to_csv('Correlations/' + f'{target_col}_correlations_like.csv', index=False)
    
    # Calculate and print the average correlation, excluding NaN values
    average_correlation = correlations.mean()
    print(f'Average correlation for {target_col} (Like): {average_correlation}')

# Calculate correlations for each grouping and save the individual group correlations
for target_col, group_cols in groupings.items():
    grouped = merged_data.groupby(group_cols)
    # Apply the safe_corr function to each group
    correlations = grouped.apply(lambda df: safe_corr(df, target_col, 'total_engagement_time'))
    
    # Convert the Series to a DataFrame if it's not already one
    if isinstance(correlations, pd.Series):
        correlations_df = correlations.reset_index()
        correlations_df.rename(columns={0: f'{target_col}_correlation_time'}, inplace=True)
    else:
        correlations_df = correlations

    # Ensure the column exists before attempting to drop NaN values
    if f'{target_col}_correlation_time' in correlations_df.columns:
        correlations_df.dropna(subset=[f'{target_col}_correlation_time'], inplace=True)
    
    # Add a column indicating the number of items used to calculate the correlation
    correlations_df['num_items'] = correlations_df.apply(track_group_items, axis=1)
    
    # Save the DataFrame to a CSV file
    correlations_df.to_csv('Correlations/' + f'{target_col}_correlations_time.csv', index=False)
    
    # Calculate and print the average correlation, excluding NaN values
    average_correlation = correlations.mean()
    print(f'Average correlation for {target_col} (Time): {average_correlation}')
