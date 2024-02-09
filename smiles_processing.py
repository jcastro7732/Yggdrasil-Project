import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

# Define a function to calculate Morgan fingerprints and return as list
def calculate_fingerprints(smiles_list, radius, n_bits):
    fingerprints = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:  # Check if the molecule could be parsed
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
            fingerprints.append(list(fp))
        else:
            # Handle the case where the SMILES string could not be parsed
            fingerprints.append([0]*n_bits)  # A list of all zeros
    return fingerprints

# Load your dataset
df = pd.read_csv('/home/jc/Desktop/TESIS/DATABASE/data_featured_database(1500).csv')

# Calculate fingerprints with the specified radius and bit length
radius = 2
n_bits = 2048
smiles_list = df['SMILES'].values
fingerprints = calculate_fingerprints(smiles_list, radius, n_bits)

# Create a DataFrame from the fingerprints
fp_df = pd.DataFrame(fingerprints, columns=[f'Bit_{i+1}' for i in range(n_bits)])

# Concatenate the new fingerprint DataFrame with the original df
result_df = pd.concat([df, fp_df], axis=1)

# Drop the original 'fingerprint' column if it exists
if 'fingerprint' in result_df.columns:
    result_df = result_df.drop(columns=['fingerprint'])

# Save the DataFrame to a new CSV file
result_df.to_csv('/home/jc/Desktop/TESIS/DATABASE/data_featured_database(1500).csv', index=False, na_rep='NaN')


