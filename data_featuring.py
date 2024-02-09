#==================================================
#*****PART 1: ELECTRON LOCALIZATION FUNCTION (ELF)*****
#==================================================

#================================================================
#*****APPROACH 1: SUMMATION AND MULTIPLICATION-BASED FEATURES*****
#================================================================

import pandas as pd
import numpy as np
import re

# Load the dataset 
file_path = '/home/jc/Desktop/TESIS/DATABASE/processed_database(1500).csv'
data = pd.read_csv(file_path)

#===============================
#******SUM OF ATOMIC CHARGES******
#===============================

# 1. Identify Atomic Charge Columns
# Atomic charges have the format: 'X_i_charge' where X is the atomic symbol and i is the index number
atomic_charge_columns = [col for col in data.columns if '_charge' in col and len(col.split('_')) == 3]
data[atomic_charge_columns] = data[atomic_charge_columns].replace(0, np.nan)

# 2. Calculate Sum of Atomic Charges
data['sum_atomic_charges'] = data[atomic_charge_columns].sum(axis=1)

# 3. Round the result to handle very small numbers close to zero
data['sum_atomic_charges'] = data['sum_atomic_charges'].round(10)

#===========================================================
#******MULTIPLICATION OF BOND ORDER AND OVERLAP CHARGES******   
#===========================================================

# 1. Identify Bond Order and Overlap Charge Columns
bond_order_columns = [col for col in data.columns if '_order' in col]
overlap_charge_columns = [col for col in data.columns if '_charge' in col]

# 2. Define Helper Functions
def decompose_bond(bond):
    parts = bond.split('_')
    if len(parts) != 4:
        return None
    try:
        return [(int(parts[i]), parts[i + 1]) for i in range(0, len(parts), 2)]
    except ValueError as e:
        print(f"Error while processing bond string '{bond}': {str(e)}")
        return None

def compare_bond_pairs(pair1, pair2):
    return sorted(pair1) == sorted(pair2)

# 3. Calculate Product of Bond Order and Overlap Charges
bond_order_overlap_products = {}
for bo_col in bond_order_columns:
    bo_pair = decompose_bond(bo_col.replace('_order', ''))
    if bo_pair is None:
        continue

    # Search for matching overlap charge column
    oc_col = None
    for col in overlap_charge_columns:
        oc_pair = decompose_bond(col.replace('_charge', ''))
        if oc_pair is not None and compare_bond_pairs(bo_pair, oc_pair):
            oc_col = col
            break
    
    if oc_col is not None:
        bond_order_overlap_products[bo_col] = data[bo_col] * data[oc_col]
    else:
        print(f"No overlap charge column found for {bo_col}")
        continue

# Convert the dictionary of Series to a DataFrame
bond_order_overlap_products = pd.DataFrame(bond_order_overlap_products)

# Replace 0 with NaN in the DataFrame to ignore them in the sum
bond_order_overlap_products.replace(0, np.nan, inplace=True)

# Check if all values in a row are NaN and if so, set the sum to NaN for that row
data['sum_bond_order_overlap'] = bond_order_overlap_products.apply(
    lambda row: row.sum(skipna=True) if not row.isna().all() else np.nan, axis=1
)

#========================================================
#*****APPROACH 2: STATISTICAL MEASURES-BASED FEATURES*****
#========================================================

#=================================================
#******STATISTICAL MEASURES OF ATOMIC CHARGES******   
#=================================================

# 1. Calculate all required statistical measures for atomic charges and store them in a dictionary
#    - Mean of Atomic Charges
#    - Median of Atomic Charges
#    - Standard Deviation of Atomic Charges
#    - Minimum of Atomic Charges
#    - Maximum of Atomic Charges
statistical_measures = {
    'mean_atomic_charges': data[atomic_charge_columns].mean(axis=1),
    'median_atomic_charges': data[atomic_charge_columns].median(axis=1),
    'std_atomic_charges': data[atomic_charge_columns].std(axis=1),
    'min_atomic_charges': data[atomic_charge_columns].min(axis=1),
    'max_atomic_charges': data[atomic_charge_columns].max(axis=1),
}

# 2. Convert the dictionary of statistical measures to a DataFrame
statistical_measures_df = pd.DataFrame(statistical_measures)

# Replace blank spaces with NaN in 'std_atomic_charges' column
statistical_measures_df['std_atomic_charges'].replace(r'^\s*$', np.nan, regex=True, inplace=True)

# 3. Calculate the range of atomic charges (Maximum - Minimum) and add it to the DataFrame
statistical_measures_df['range_atomic_charges'] = statistical_measures_df['max_atomic_charges'] - statistical_measures_df['min_atomic_charges']

# 4. Concatenate the new features (statistical measures) to the original data DataFrame
data = pd.concat([data, statistical_measures_df], axis=1)

#============================================================================
#******STATISTICAL MEASURES OF BOND ORDER AND OVERLAP CHARGES PRODUCT******   
#=============================================== =============================

# First, replace blank spaces with NaN for the entire DataFrame
bond_order_overlap_products.replace(r'^\s*$', np.nan, regex=True, inplace=True)

# Then, perform the calculations as before
# 1. Calculate Mean of Bond Order and Overlap Charges Product
data['mean_bond_order_overlap'] = bond_order_overlap_products.mean(axis=1)

# 2. Calculate Median of Bond Order and Overlap Charges Product
data['median_bond_order_overlap'] = bond_order_overlap_products.median(axis=1)

# 3. Calculate Standard Deviation of Bond Order and Overlap Charges Product
data['std_bond_order_overlap'] = bond_order_overlap_products.std(axis=1)

# 4. Calculate Minimum of Bond Order and Overlap Charges Product
data['min_bond_order_overlap'] = bond_order_overlap_products.min(axis=1)

# 5. Calculate Maximum of Bond Order and Overlap Charges Product
data['max_bond_order_overlap'] = bond_order_overlap_products.max(axis=1)

# 6. Calculate Range of Bond Order and Overlap Charges Product (Max - Min)
data['range_bond_order_overlap'] = data['max_bond_order_overlap'] - data['min_bond_order_overlap']

#====================================================
#*****PART 2: BADER'S ATOM IN MOLECULES (AIM) THEORY*****
#====================================================

#===========================
#*****ATOMIC BASIN CHARGE*****
#===========================

#1. Indentify the nearest neighbors column 
# Ensure the 'NEAREST_NEIGHBORS' column is present in the dataset
if 'NEAREST_NEIGHBORS' not in data.columns:
    raise ValueError("The 'NEAREST_NEIGHBORS' column is not present in the dataset.")

#2. Parse the nearest neighbors information
# Define a function to parse the nearest neighbors information
def parse_nearest_neighbors(nn_info):
    if pd.isnull(nn_info) or nn_info.strip() == '- 0':
        return []
    try:
        parts = nn_info.split()
        result = []
        i = 0
        while i < len(parts):
            # Extract element and index
            element_index = parts[i][:-1].split('(')
            if len(element_index) != 2:
                print(f"Unexpected format for '{parts[i]}', skipping.")
                i += 2
                continue
            element, index = element_index
            index = int(index)
            
            # Extract number of neighbors
            num_neighbors = int(parts[i + 1])
            
            # Add the information to the result list
            result.append((element, index, num_neighbors))
            
            # Move to the next atom
            i += 2
        return result
    except Exception as e:
        print(f"Error parsing '{nn_info}': {e}")
        return []

# Apply the function to the 'NEAREST_NEIGHBORS' column
data['parsed_nearest_neighbors'] = data['NEAREST_NEIGHBORS'].apply(parse_nearest_neighbors)

# 3. Calculate the weighted charge

def calculate_atomic_basin_charge(row):
    total_atomic_basin_charge = 0
    # Access the 'parsed_nearest_neighbors' list for the row
    nearest_neighbors_list = row['parsed_nearest_neighbors']
    # Iterate over each tuple in the list
    for atom_info in nearest_neighbors_list:
        # Destructure the tuple
        element, index, num_neighbors = atom_info
        # Construct the column name for the atomic charge
        column_name = f"{element}_{index}_charge"
        # Access the charge value from the column in the row, if the column exists
        if column_name in row:
            charge_value = row[column_name]
            # Multiply the charge value by the number of neighbors
            multiplied_value = charge_value * num_neighbors
            # Add the result to the total atomic basin charge
            total_atomic_basin_charge += multiplied_value
    return total_atomic_basin_charge

# Apply the function to each row of the dataset and create a new column with the results
data['atomic_basin_charge'] = data.apply(calculate_atomic_basin_charge, axis=1)

# Define a function to find the atomic basin charge for each row
def find_atomic_basin_charge(row, atomic_charge_columns):
    # Check if 'parsed_nearest_neighbors' is empty (i.e., '- 0')
    if not row['parsed_nearest_neighbors']:
        # Find the single atomic charge present and use it as the atomic basin charge
        for col in atomic_charge_columns:
            if not pd.isna(row[col]):
                # We found the atomic charge, return it
                return row[col]
        # If no charge is found, return NaN or some appropriate value
        return np.nan
    else:
        # If 'parsed_nearest_neighbors' is not empty, proceed with the normal calculation
        # (This is the part where you would multiply charges by the number of neighbors and sum them)
        # Placeholder for sum calculation
        sum_of_charges = sum(row[element + '_' + str(index) + '_charge'] * num_neighbors
                             for element, index, num_neighbors in row['parsed_nearest_neighbors']
                             if element + '_' + str(index) + '_charge' in atomic_charge_columns)
        return sum_of_charges

# Ensure the 'atomic_charge_columns' list is up-to-date
atomic_charge_columns = [col for col in data.columns if '_charge' in col]

# Apply the function to each row and create a new column for the atomic basin charge
data['atomic_basin_charge'] = data.apply(lambda row: find_atomic_basin_charge(row, atomic_charge_columns), axis=1)

#===================================
#*****BOND LENGTH DATA FEATURING*****
#===================================

#=========================================
#***** 1. WEIGHTED AVERAGE BOND LENGTH*****
#=========================================

def decompose_bond_length(bond_length):
    if pd.isna(bond_length) or not isinstance(bond_length, str):
        return None
    try:
        # Use regex to separate the atomic symbols and index numbers
        matches = re.match(r"([A-Za-z]+)(\d+)-([A-Za-z]+)(\d+)", bond_length)
        if not matches:
            return None
        atom1, index1, atom2, index2 = matches.groups()
        return (atom1, int(index1), atom2, int(index2))
    except ValueError as e:
        print(f"Error while processing bond length '{bond_length}': {str(e)}")
        return None

# Function to find the corresponding bond order for a given bond
def find_corresponding_bond_order(atom1, index1, atom2, index2, bond_order_columns, data_row):
    # Construct possible bond order column names based on the atomic symbols and their indices
    bond_order_col1 = f"{index1}_{atom1}_{index2}_{atom2}_order"
    bond_order_col2 = f"{index2}_{atom2}_{index1}_{atom1}_order"

    # Check if either column name is in the list of bond order columns
    if bond_order_col1 in bond_order_columns:
        return data_row[bond_order_col1]
    elif bond_order_col2 in bond_order_columns:
        return data_row[bond_order_col2]
    else:
        # If neither column name is present, the bond order is not available
        return None

# Function to calculate the weighted average bond length for a row in the DataFrame
def calculate_weighted_average_bond_length(row, bond_length_columns, bond_order_columns):
    total_weighted_length = 0
    total_bond_order = 0

    # For each bond length column
    for bl_col in bond_length_columns:
        # Get the bond length value
        bond_length_value = row[bl_col]

        # Ignore missing or zero values
        if not pd.isna(bond_length_value) and bond_length_value != 0:
            # Decompose the bond length column name
            decomposed = decompose_bond_length(bl_col)
            if decomposed is None:
                continue
            atom1, index1, atom2, index2 = decomposed

            # Find the corresponding bond order
            bond_order_value = find_corresponding_bond_order(atom1, index1, atom2, index2, bond_order_columns, row)

            # If a corresponding bond order is found and it's not zero
            if not pd.isna(bond_order_value) and bond_order_value != 0:
                # Add to the total weighted length
                total_weighted_length += bond_length_value * bond_order_value
                # Add to the total bond order
                total_bond_order += bond_order_value

    # Calculate the weighted average bond length
    if total_bond_order > 0:
        return total_weighted_length / total_bond_order
    else:
        return np.nan  # Return NaN if the total bond order is zero to avoid division by zero

# Get bond length columns
bond_length_columns = [col for col in data.columns if '-' in col and not '_order' in col]

# Get bond order columns
bond_order_columns = [col for col in data.columns if '_order' in col]

# Replace blank spaces with NaN for all bond length columns
for col in bond_length_columns:
    data[col] = data[col].replace(r'^\s*$', np.nan, regex=True)

# Now apply the function to calculate the weighted average bond length
data['weighted_average_bond_length'] = data.apply(
    lambda row: calculate_weighted_average_bond_length(row, bond_length_columns, bond_order_columns),
    axis=1
)

#===========================================
#***** 2. MINIMUM AND MAXIMUM BOND LENGTH*****
#===========================================

# Identify all bond length columns
bond_length_columns = [col for col in data.columns if '-' in col and not '_order' in col]

# Define a function to calculate the min and max bond lengths for a given row
def calculate_min_max_bond_length(row, bond_length_columns):
    # Filter out zero or NaN bond lengths
    valid_bond_lengths = [row[col] for col in bond_length_columns if row[col] > 0]
    
    # If there are no valid bond lengths, return None or some appropriate value for min and max
    if not valid_bond_lengths:
        return (None, None)
    
    # Calculate the minimum and maximum bond lengths
    min_bond_length = min(valid_bond_lengths)
    max_bond_length = max(valid_bond_lengths)
    return (min_bond_length, max_bond_length)

# Replace blank spaces with NaN for all bond length columns
for col in bond_length_columns:
    data[col] = data[col].replace(r'^\s*$', np.nan, regex=True)

# Apply the function to each row of the dataset
data[['min_bond_length', 'max_bond_length']] = data.apply(
    lambda row: calculate_min_max_bond_length(row, bond_length_columns), axis=1, result_type='expand'
)

#=================================
#***** 3. BOND LENGTH VARIABILITY*****
#=================================

# Function to calculate the IQR for a given array of bond lengths
def calculate_iqr(bond_lengths):
    if bond_lengths.empty:
        return np.nan
    Q3 = np.percentile(bond_lengths, 75)
    Q1 = np.percentile(bond_lengths, 25)
    return Q3 - Q1

# Replace blank spaces with NaN for all bond length columns
for col in bond_length_columns:
    data[col] = data[col].replace(r'^\s*$', np.nan, regex=True)

# Calculate the standard deviation of bond lengths for each molecule
data['std_bond_length'] = data[bond_length_columns].replace(0, np.nan).std(axis=1)

# Calculate the variance of bond lengths for each molecule
data['var_bond_length'] = data[bond_length_columns].replace(0, np.nan).var(axis=1)

# Calculate the range of bond lengths for each molecule
data['range_bond_length'] = data['max_bond_length'] - data['min_bond_length']

# Applying the IQR calculation to each row of the DataFrame
data['iqr_bond_length'] = data[bond_length_columns].replace(0, np.nan).apply(lambda row: calculate_iqr(row.dropna()), axis=1)

# List of columns to keep
columns_to_keep = [
    'REACTION_ID', 'MOLECULE_INDEX', 'SMILES', 'MOLECULE_TYPE_reactant', 'MOLECULE_TYPE_product', 'MOLECULE_TYPE_intermediate',
    'sum_atomic_charges', 'sum_bond_order_overlap', 'mean_atomic_charges', 'median_atomic_charges', 'std_atomic_charges',
    'min_atomic_charges', 'max_atomic_charges', 'range_atomic_charges', 'mean_bond_order_overlap', 'median_bond_order_overlap',
    'std_bond_order_overlap', 'min_bond_order_overlap', 'max_bond_order_overlap', 'range_bond_order_overlap', 'atomic_basin_charge',
    'weighted_average_bond_length', 'min_bond_length', 'max_bond_length', 'std_bond_length', 'var_bond_length',
    'range_bond_length', 'iqr_bond_length'
]

# Create a subset DataFrame with only the required columns
final_data = data[columns_to_keep]

# Save the final DataFrame to a CSV file
output_file_path = '/home/jc/Desktop/TESIS/DATABASE/data_featured_database(1500).csv'
final_data.to_csv(output_file_path, index=False, na_rep='NaN')