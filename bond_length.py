from openbabel import openbabel, pybel
import os

# Define a function to read the contents of an .xyz file
def read_xyz(filename):
    with open(filename, 'r') as f:  # Open the file in read mode
        lines = f.readlines()  # Read all lines of the file
        content = lines[2:]    # Skip the first two lines (usually atom count and comment)
    num_atoms = len(content)   # Count the number of atoms from the remaining lines
    return str(num_atoms) + "\n\n" + "".join(content)  # Return the formatted content

# Define a function to calculate bond lengths using Open Babel
def ob_calculate_bond_lengths(mol):
    bond_lengths = []
    ob_mol = mol.OBMol  # Extract the OBMol object from Pybel's Molecule object
    # Loop through each bond in the molecule
    for bond in openbabel.OBMolBondIter(ob_mol):
        atom1 = ob_mol.GetAtom(bond.GetBeginAtomIdx())  # Get the starting atom of the bond
        atom2 = ob_mol.GetAtom(bond.GetEndAtomIdx())    # Get the ending atom of the bond
        bond_length = atom1.GetDistance(atom2)          # Calculate the bond length

        # Retrieve atomic symbols for the two bonded atoms
        atom1_symbol = openbabel.GetSymbol(atom1.GetAtomicNum())
        atom2_symbol = openbabel.GetSymbol(atom2.GetAtomicNum())
        
        # Include atom indices in the bond type description
        bond_type = f"{atom1_symbol}{atom1.GetIdx()}-{atom2_symbol}{atom2.GetIdx()}"  # Format the bond type (e.g., "C1-H2")

        bond_lengths.append((bond_type, bond_length))  # Store bond type and length as a tuple in the list
    return bond_lengths

# Define a function to write bond lengths to an output file
def write_to_file(bond_lengths, output_file):
    with open(output_file, 'w') as f:  # Open the file in write mode
        f.write("Bond\tBond Length\n")
        if not bond_lengths:
            f.write("-\t0\n")  # Write a default value if bond_lengths list is empty
        else:
            # Loop through each bond type and length pair and write to the file
            for bond_type, bond_length in bond_lengths:
                f.write(f"{bond_type}\t{bond_length}\n")

def main():
    main_path = "/home/titi/Desktop/JONNATHAN/INPUTS"
    # List only directories in main_path that are purely numeric
    numbered_folders = [dir for dir in os.listdir(main_path) if dir.isnumeric()]

    # Loop through each numbered folder
    for numbered_folder in numbered_folders:
        numbered_path = os.path.join(main_path, numbered_folder)
        molecule_folders = os.listdir(numbered_path)

        # Loop through each sub-folder (molecule folder) inside the numbered folder
        for molecule_folder in molecule_folders:
            molecule_path = os.path.join(numbered_path, molecule_folder)
            xyz_found = False
            # Loop through each file in the molecule folder
            for file in os.listdir(molecule_path):
                if file.endswith(".xyz"):  # Check if the file is an .xyz file
                    xyz_found = True
                    input_file = os.path.join(molecule_path, file)
                    output_file = os.path.join(molecule_path, molecule_folder + "_bl.txt")

                    xyz_data = read_xyz(input_file)
                    ob_mol = pybel.readstring("xyz", xyz_data)  # Convert the .xyz data to a Pybel Molecule object
                    bond_lengths = ob_calculate_bond_lengths(ob_mol)
                    write_to_file(bond_lengths, output_file)  # Write bond lengths to the output file

                    print(f"{molecule_folder} bond length calculated.")

            # If no .xyz file was found in the molecule folder, write default values to the output file
            if not xyz_found:
                output_file = os.path.join(molecule_path, molecule_folder + "_bl.txt")
                write_to_file([], output_file)
                print(f"No .xyz file found for {molecule_folder}. Writing default values.")

# Run the main function when the script is executed directly
if __name__ == "__main__":
    main()