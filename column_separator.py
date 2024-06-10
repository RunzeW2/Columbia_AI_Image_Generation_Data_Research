import csv

# Define the input and output CSV file names
input_csv = 'engagement_2.csv'  # Replace with your actual input file name
output_csv = 'engagement_2_fixed.csv'  # The file name for the output CSV

# Open the input CSV file for reading
with open(input_csv, mode='r', newline='') as infile:
    # Open the output CSV file for writing
    with open(output_csv, mode='w', newline='') as outfile:
        # Create a CSV reader object to read from the input file
        reader = csv.reader(infile)
        # Create a CSV writer object to write to the output file
        writer = csv.writer(outfile)

        # Read the first row and split it to create the column headers
        headers = next(reader)[0].split()  # Splits on any whitespace
        # Write the column headers to the output file
        writer.writerow(headers)

        # Iterate over the remaining rows in the input file
        for row in reader:
            # Split the merged data into separate columns based on any whitespace
            data = row[0].split()  # Splits on any whitespace
            # Write the separated data to the output file
            writer.writerow(data)

print(f'Data has been split and saved to {output_csv}')
