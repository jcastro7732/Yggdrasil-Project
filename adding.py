import csv

# Paths to the files
input_file_path = "/home/jc/Desktop/TESIS/DATABASE/database(1500).csv"
output_file_path = "/home/jc/Desktop/TESIS/DATABASE/processed_database(1500).csv"

# Open the input CSV file
with open(input_file_path, mode='r', newline='', encoding='utf-8') as input_file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(input_file)
    
    # Find the index of the "NEAREST_NEIGHBORS" column
    if "NEAREST_NEIGHBORS" in csv_reader.fieldnames:
        nearest_neighbors_data = [row["NEAREST_NEIGHBORS"] for row in csv_reader]
    else:
        print("Column 'NEAREST_NEIGHBORS' not found in the input file.")
        exit()

# Read existing data from the output file
with open(output_file_path, mode='r', newline='', encoding='utf-8') as output_file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(output_file)
    
    # Read existing data
    existing_data = [row for row in csv_reader]
    fieldnames = csv_reader.fieldnames

# Add the new column to the existing data
fieldnames.append("NEAREST_NEIGHBORS")
for i, row in enumerate(existing_data):
    row["NEAREST_NEIGHBORS"] = nearest_neighbors_data[i] if i < len(nearest_neighbors_data) else ""

# Write everything back to the output file
with open(output_file_path, mode='w', newline='', encoding='utf-8') as output_file:
    # Create a CSV writer object
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    
    # Write the header
    csv_writer.writeheader()
    
    # Write the data
    csv_writer.writerows(existing_data)

print("NEAREST_NEIGHBORS column has been added to the output file.")
