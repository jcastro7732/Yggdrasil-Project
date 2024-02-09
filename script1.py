import csv  # Module for reading and writing CSV files
from openbabel import pybel  # Open Babel is a chemical toolbox designed to convert chemical file formats
import os  # Module for interacting with the operating system
from tkinter import Tk  # GUI toolkit for Python
from tkinter.filedialog import askopenfilename  # GUI-based file dialog for opening files

# Initialize a GUI window but immediately hide it
Tk().withdraw()

# Show a file dialog to the user and allow them to select a CSV file
csv_file = askopenfilename(title='Select CSV File', filetypes=[('CSV Files', '*.csv')])

# Initialize an empty list to store molecule information
molecules = []

# Open the selected CSV file in read mode
with open(csv_file, 'r') as file:
    # Use the CSV module to read the file and interpret it as a CSV with a comma delimiter
    reader = csv.DictReader(file, delimiter=",")
    
    # Iterate over each row in the CSV file
    for row in reader:
        # Extract the REACTION_ID column value and remove any leading or trailing whitespace
        reaction_id = row['REACTION_ID'].strip()
        
        # Initialize lists to store reactants, intermediates, and products for each reaction
        reactants = []
        intermediates = []
        products = []
        
        # Extract reactants dynamically based on the number of columns in the CSV file
        for i in range(1, len(row.keys())):
            try:
                reactants.append(row[f'REACTANT_{i}'].strip())
            except KeyError:
                break
        
        # Extract intermediates dynamically based on the number of columns in the CSV file
        for i in range(1, len(row.keys())):
            try:
                intermediates.append(row[f'INTERMEDIATE_{i}'].strip())
            except KeyError:
                break
        
        # Extract products dynamically based on the number of columns in the CSV file
        for i in range(1, len(row.keys())):
            try:
                products.append(row[f'PRODUCT_{i}'].strip())
            except KeyError:
                break
        
        # Append the extracted data for each reaction to the molecules list
        molecules.append((reaction_id, reactants, intermediates, products))

# Open (or create) a CSV file to store the total charges of the molecules
with open('/home/jorge316/Desktop/Yggdrasil/molecule_charges.csv', 'w', newline='') as csvfile:
    # Define the columns (headers) for the new CSV file
    fieldnames = ['REACTION_ID', 'MOLECULE_TYPE', 'MOLECULE_INDEX', 'TOTAL_CHARGE']
    
    # Use the CSV module to write to the file
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()  # Write the column headers to the CSV file
    
    # Define the directory where the XYZ files of the molecules will be saved
    base_directory = "/home/jorge316/Desktop/Yggdrasil/moleculas"
    
    # Iterate over each molecule (from the previously created molecules list)
    for reaction_id, reactants, intermediates, products in molecules:
        # Define a sub-directory for each reaction
        reaction_directory = os.path.join(base_directory, f"{reaction_id}")
        
        # If the sub-directory doesn't exist, create it
        if not os.path.exists(reaction_directory):
            os.makedirs(reaction_directory)
        
        # Define a function to process the molecules (convert SMILES to XYZ and get their charge)
        def process_molecules(molecules, molecule_type):
            for idx, molecule in enumerate(molecules):
                # Only process non-empty molecule entries
                if molecule:
                    pb_molecule = pybel.readstring("smi", molecule)  # Convert SMILES string to a molecule object
                    pb_molecule.addh()  # Add hydrogens to the molecule
                    pb_molecule.make3D()  # Generate a 3D structure of the molecule
                    
                    # Define the filename for the XYZ file
                    molecule_file_name = f"{molecule_type}{idx+1}.xyz"
                    molecule_file_path = os.path.join(reaction_directory, molecule_file_name)
                    
                    # Save the molecule as an XYZ file
                    pb_molecule.write("xyz", molecule_file_path, overwrite=True)
                    
                    # Get the charge of the molecule
                    charge = pb_molecule.OBMol.GetTotalCharge()
                    
                    # Write the charge of the molecule to the CSV file
                    writer.writerow({'REACTION_ID': reaction_id, 'MOLECULE_TYPE': molecule_type, 'MOLECULE_INDEX': idx+1, 'TOTAL_CHARGE': charge})
        
        # Process reactants, intermediates, and products for each reaction
        process_molecules(reactants, "reactant")
        process_molecules(intermediates, "intermediate")
        process_molecules(products, "product")
        
        # Print a success message for each processed reaction
        print(f'Successfully created files for reaction: {reaction_id}')
    
    # Print a completion message once all reactions have been processed
    print('Molecule creation complete!')