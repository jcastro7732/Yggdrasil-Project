import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import re
from sklearn.cluster import KMeans
import numpy as np
import csv

# ==========================
# Utility Functions
# ==========================

# Atomic and Overlap Charges Handling
# -----------------------

# Increment indices in the atomic charges column to match the database's 1-based indexing.
# This is necessary because Python uses 0-based indexing, but the database uses 1-based indexing.
def increment_indices_atomic_charges(entry):
    components = entry.split()
    modified_components = []
    for component in components:
        if component.isdigit():
            modified_components.append(str(int(component) + 1))
        else:
            modified_components.append(component)
    return ' '.join(modified_components)

# Increment indices in the overlap charges column to match the database's 1-based indexing.
def increment_indices_overlap_charges(entry):
    bond_charge_pairs = entry.split('B(')
    for i in range(1, len(bond_charge_pairs)):
        bond_info = bond_charge_pairs[i].split(')')[0]
        atoms = [atom.split('-') for atom in bond_info.split(',')]
        atoms[0][0] = str(int(atoms[0][0]) + 1)
        atoms[1][0] = str(int(atoms[1][0]) + 1)
        bond_info = '-'.join(atoms[0]) + ',' + '-'.join(atoms[1])
        bond_charge_pairs[i] = 'B(' + bond_info +')'+ bond_charge_pairs[i].split(')')[1]
    return ' '.join(bond_charge_pairs)

# Extract atomic charges from the atomic charges column.
# This function uses regex to capture the atomic number, atom type, and its charge.
def extract_atomic_charges(entry):
    pattern = re.compile(r'(\d+)\s+([A-Z][a-z]*)\s*:\s+(-?\d+\.\d+)')
    matches = pattern.findall(entry)
    atomic_charges = {}
    for match in matches:
        index = int(match[0])
        atom = match[1]
        charge = float(match[2])
        atomic_charges[index] = {'atom': atom, 'charge': charge}
    return atomic_charges

# Bond Length Handling
# --------------------

# Extract relevant bonds from the bond length column.
# This function captures bonds by identifying atom types and their indices.
def extract_relevant_bonds(bond_length_entry):
    pattern = re.compile(r'([A-Z][a-z]*)(\d+)-([A-Z][a-z]*)(\d+)')
    matches = pattern.findall(bond_length_entry)
    relevant_bonds = set()
    for match in matches:
        atom1 = match[0]
        index1 = int(match[1])
        atom2 = match[2]
        index2 = int(match[3])
        bond_key = (index1, atom1, index2, atom2)
        relevant_bonds.add(bond_key)
    return relevant_bonds

# Extract overlap charges from the overlap charges column.
# This function captures the overlap charges for bonds that are deemed relevant.
def extract_overlap_charges(overlap_entry, relevant_bonds):
    overlap_data = {}
    bond_charge_pairs = overlap_entry.split('B(')[1:]
    for bond in relevant_bonds:
        for pair in bond_charge_pairs:
            bond_info, charge = pair.split(') :')
            atoms = [atom.strip() for atom in bond_info.split(',')]
            bond1 = (int(atoms[0].split('-')[0]), atoms[0].split('-')[1], int(atoms[1].split('-')[0]), atoms[1].split('-')[1])
            bond2 = (int(atoms[1].split('-')[0]), atoms[1].split('-')[1], int(atoms[0].split('-')[0]), atoms[0].split('-')[1])
            if bond1 in relevant_bonds:
                overlap_data[bond1] = float(charge.strip())
            elif bond2 in relevant_bonds:
                overlap_data[bond2] = float(charge.strip())
    return overlap_data

# Extract atomic charge columns from the atomic charges dictionary.
# This function creates a structured representation of atomic charges.
def extract_atomic_charge_columns(row):
    data = {}
    for key, value in row.items():
        atom_type = value['atom']
        charge = value['charge']
        column_name = f"{atom_type}_{key}_charge"
        data[column_name] = charge
    return data
    
# Extract overlap charge columns from the overlap charges dictionary.
# This function creates a structured representation of overlap charges.
def extract_overlap_charge_columns(row):
    data = {}
    for key, charge in row.items():
        atom1, index1, atom2, index2 = key
        column_name = f"{atom1}_{index1}_{atom2}_{index2}_charge"
        data[column_name] = charge
    return data

# Nearest Neighbors Handling
# --------------------------

# Extract the number of neighbors and replace "- 0" with numerical zero.
# This function processes the NEAREST_NEIGHBORS column to capture the count of each atom type.
#def extract_neighbors(value):
#    if value == "- 0":
#        return "0"
#    else:
#        return ' '.join([part.split()[-1] for part in value.split() if part])
 
 # Transform NEAREST_NEIGHBORS column to create a structured representation.
# This function captures the count of each atom type and its occurrences.
#def transform_neighbors(row):
#    atoms = row.split()
#    atom_dict = {}
#    for i in range(0, len(atoms) - 1, 2):  # Adjusted the range to avoid out of range error
#        atom_type = atoms[i].split('(')[0]  # Remove index numbers
#        count = int(atoms[i+1])
#        column_name = f"{atom_type}_{count}"
#        atom_dict[column_name] = atom_dict.get(column_name, 0) + 1
#    return atom_dict

# Process BOND_LENGTH column to extract bond lengths
def process_bond_length(row):
    bond_data = row.split()
    bond_dict = {}
    for i in range(0, len(bond_data) - 1, 2):
        bond_atoms = bond_data[i]
        bond_length = float(bond_data[i+1])
        bond_dict[bond_atoms] = bond_length  # Use bond with index for dictionary key
    return bond_dict
    
# Bond Order Handling
#--------------------

# Increment indices in the bond orders column to match the database's 1-based indexing.
def increment_indices_bond_orders(entry):
    bond_order_pairs = entry.split('B(')[1:]
    for i in range(len(bond_order_pairs)):
        bond_info, order = bond_order_pairs[i].split(') :')
        atoms = [atom.strip() for atom in bond_info.split(',')]
        atoms[0] = str(int(atoms[0].split('-')[0]) + 1) + '-' + atoms[0].split('-')[1]
        atoms[1] = str(int(atoms[1].split('-')[0]) + 1) + '-' + atoms[1].split('-')[1]
        bond_order_pairs[i] = 'B(' + atoms[0] + ',' + atoms[1] + ') :' + order
    return ' '.join(bond_order_pairs)

# Extract bond orders from the bond orders column.
def extract_bond_orders(entry):
    pattern = re.compile(r'B\(\s*(\d+)-([A-Z][a-z]*),\s*(\d+)-([A-Z][a-z]*)\s*\)\s*:\s*(\d+\.\d+)')
    matches = pattern.findall(entry)
    bond_orders = {}
    for match in matches:
        atom1_index = int(match[0])
        atom1_type = match[1]
        atom2_index = int(match[2])
        atom2_type = match[3]
        bond_order = float(match[4])
        bond_key = (atom1_index, atom1_type, atom2_index, atom2_type)
        bond_orders[bond_key] = bond_order
    return bond_orders

# Extract bond order columns from the bond orders dictionary.
def extract_bond_order_columns(row):
    data = {}
    for key, order in row.items():
        atom1, index1, atom2, index2 = key
        column_name = f"{atom1}_{index1}_{atom2}_{index2}_order"
        data[column_name] = round(order)  # Round the bond order to the nearest integer
    return data
    
# Main Code Execution
# -------------------


# Load the data
data_path = "/home/jc/Desktop/TESIS/DATABASE/database(1500).csv"

# Load the data with pandas, excluding the NEAREST_NEIGHBORS column
df = pd.read_csv(data_path, usecols=lambda column: column not in ["NEAREST_NEIGHBORS", "COORDINATES"])


# Separate the NEAREST_NEIGHBORS column and convert it to a list of strings
#nearest_neighbors = df['NEAREST_NEIGHBORS'].tolist()
#df.drop('NEAREST_NEIGHBORS', axis=1, inplace=True)
# Handle missing values for all columns
df.fillna("- 0", inplace=True)
#df['NEAREST_NEIGHBORS'] = df['NEAREST_NEIGHBORS'].apply(extract_neighbors)
#df['NEAREST_NEIGHBORS'] = df['NEAREST_NEIGHBORS'].replace("- 0", "0")

# Check for duplicate rows and remove them
duplicates = df.duplicated()
if duplicates.sum() > 0:
    df.drop_duplicates(inplace=True)

# One-hot encoding for MOLECULE_TYPE with explicit categories
categories = [['reactant', 'product', 'intermediate']]
encoder = OneHotEncoder(sparse_output=False, categories=categories)
encoded_features = encoder.fit_transform(df[['MOLECULE_TYPE']])
encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(['MOLECULE_TYPE']))

# Concatenate the original dataframe with the encoded dataframe
df = pd.concat([df, encoded_df], axis=1)

# Drop the original MOLECULE_TYPE column
df.drop('MOLECULE_TYPE', axis=1, inplace=True)


# Transform NEAREST_NEIGHBORS column
#neighbors_data = df['NEAREST_NEIGHBORS'].apply(transform_neighbors).tolist()
#neighbors_df = pd.DataFrame(neighbors_data).fillna(0).astype(int)
# Concatenate the new columns to the original dataframe
#df = pd.concat([df, neighbors_df], axis=1)
# Drop the original NEAREST_NEIGHBORS column
#df.drop('NEAREST_NEIGHBORS', axis=1, inplace=True)


# Process BOND_LENGTH column
bond_data = df['BOND_LENGTH'].apply(process_bond_length).tolist()
bond_df = pd.DataFrame(bond_data).fillna(0)
# Concatenate the new columns to the original dataframe
df = pd.concat([df, bond_df], axis=1)

# Handle ATOMIC_CHARGES column
df['ATOMIC_CHARGES'] = df['ATOMIC_CHARGES'].apply(increment_indices_atomic_charges)
df['ATOMIC_CHARGES_DICT'] = df['ATOMIC_CHARGES'].apply(extract_atomic_charges)

# Replace "- 0" in the OVERLAP_CHARGES column with an empty string
df['OVERLAP_CHARGES'] = df['OVERLAP_CHARGES'].replace("- 0", "")

# Handle OVERLAP_CHARGES column
df['OVERLAP_CHARGES'] = df['OVERLAP_CHARGES'].apply(increment_indices_overlap_charges)
df['RELEVANT_BONDS'] = df['BOND_LENGTH'].apply(extract_relevant_bonds)
df['OVERLAP_CHARGES_DICT'] = df.apply(lambda row: extract_overlap_charges(row['OVERLAP_CHARGES'], row['RELEVANT_BONDS']), axis=1)

# Drop the original BOND_LENGTH column
df.drop('BOND_LENGTH', axis=1, inplace=True)

# Drop the original ATOMIC_CHARGES, OVERLAP_CHARGES, and RELEVANT_BONDS columns
df.drop(columns=['ATOMIC_CHARGES', 'OVERLAP_CHARGES', 'RELEVANT_BONDS'], inplace=True)

# Handle ATOMIC_CHARGES dictionary
atomic_charges_data = df['ATOMIC_CHARGES_DICT'].apply(extract_atomic_charge_columns).tolist()
atomic_charges_df = pd.DataFrame(atomic_charges_data).fillna(0)
df = pd.concat([df, atomic_charges_df], axis=1)
df.drop('ATOMIC_CHARGES_DICT', axis=1, inplace=True)

# Handle OVERLAP_CHARGES dictionary
overlap_charges_data = df['OVERLAP_CHARGES_DICT'].apply(extract_overlap_charge_columns).tolist()
overlap_charges_df = pd.DataFrame(overlap_charges_data).fillna(0)
df = pd.concat([df, overlap_charges_df], axis=1)
df.drop('OVERLAP_CHARGES_DICT', axis=1, inplace=True)

# Handle BOND_ORDERS column
df['BOND_ORDERS'] = df['BOND_ORDERS'].apply(increment_indices_bond_orders)
df['BOND_ORDERS_DICT'] = df['BOND_ORDERS'].apply(extract_bond_orders)

# Extract bond order columns
bond_order_data = df['BOND_ORDERS_DICT'].apply(extract_bond_order_columns).tolist()
bond_order_df = pd.DataFrame(bond_order_data).fillna(0)
df = pd.concat([df, bond_order_df], axis=1)
df.drop('BOND_ORDERS_DICT', axis=1, inplace=True)

# Drop the original BOND_ORDERS column
df.drop('BOND_ORDERS', axis=1, inplace=True)

# Reassign the original NEAREST_NEIGHBORS column
#df['NEAREST_NEIGHBORS'] = nearest_neighbors

# Save the processed dataframe
df.to_csv("/home/jc/Desktop/TESIS/DATABASE/processed_database(1500).csv", index=False)                                     

