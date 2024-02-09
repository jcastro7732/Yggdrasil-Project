import csv

# Define the paths for the input and output CSV files.
input_path = "/home/jorge316/Desktop/Yggdrasil/script/USPTO_MIT.csv"
output_path = "/home/jorge316/Desktop/Yggdrasil/smiles(15000).csv"

# Initialize counters to keep track of the maximum number of reactants, intermediates, and products 
# across all reactions in the input file.
max_reactants = 0
max_intermediates = 0
max_products = 0

# Create an empty list to store detailed information about each parsed reaction.
reactions = []

# Open the input CSV file in read mode.
with open(input_path, 'r') as infile:
    reader = csv.reader(infile)  # Create a CSV reader object to read rows from the file.
    next(reader)  # Skip the header row, which typically contains column names.

    # Loop through each row in the CSV file.
    for idx, row in enumerate(reader):
        reaction_str = row[0]  # The reaction string is assumed to be the first column in the CSV.
        
        # Initialize empty lists to store the reactants, intermediates, and products for the current reaction.
        reactants, intermediates, products = [], [], []

        # Parse the reaction string. Reactions can be of the form "A.B>>C.D" or "A.B>C.X>D.Y"
        if '>>' in reaction_str:  # Check for the ">>" delimiter which indicates no intermediates.
            reactants_str, products_str = reaction_str.split('>>')  # Split the string into reactants and products.
            reactants = reactants_str.split('.')  # Split the reactants string further using '.' to get individual reactants.
            products = products_str.split('.')    # Similarly, split the products string.
        else:  # If ">>" is not present, then there are intermediates in the reaction.
            reactants_str, intermediates_str, products_str = reaction_str.split('>')  # Split the reaction string into reactants, intermediates, and products.
            reactants = reactants_str.split('.')
            intermediates = intermediates_str.split('.')
            products = products_str.split('.')

        # Update the maximum count values based on the current reaction's counts.
        max_reactants = max(max_reactants, len(reactants))
        max_intermediates = max(max_intermediates, len(intermediates))
        max_products = max(max_products, len(products))

        # Construct a dictionary with the parsed data for the current reaction and add it to the reactions list.
        reactions.append({
            'id': idx + 1,  # A unique identifier for the reaction.
            'reactants': reactants,
            'intermediates': intermediates,
            'products': products
        })

# Sort the reactions list based on the total character length of all reactants' SMILES strings.
# This might be useful for some post-processing or analysis.
reactions.sort(key=lambda x: sum(len(reactant) for reactant in x['reactants']))

# Open the output CSV file in write mode.
with open(output_path, 'w', newline='') as outfile:
    # Create a list of column headers for the output CSV.
    # This dynamically creates column names based on the maximum counts observed.
    fieldnames = ['REACTION_ID'] + [f'REACTANT_{i+1}' for i in range(max_reactants)] + [f'INTERMEDIATE_{i+1}' for i in range(max_intermediates)] + [f'PRODUCT_{i+1}' for i in range(max_products)]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)  # Create a CSV writer object.
    writer.writeheader()  # Write the column headers to the CSV.

    # Loop through each reaction in the sorted reactions list and write its details to the CSV.
    for idx, reaction in enumerate(reactions):
        if idx >= 15000:  # limit the output to the first 10 reactions.
            break
        row = {'REACTION_ID': idx + 1}  # Initialize the row with the reaction ID.
        
        # Populate the row with reactants, intermediates, and products.
        # If there are fewer entities than the maximum count, fill the remaining columns with empty strings.
        for i in range(max_reactants):
            row[f'REACTANT_{i+1}'] = reaction['reactants'][i] if i < len(reaction['reactants']) else ''
        for i in range(max_intermediates):
            row[f'INTERMEDIATE_{i+1}'] = reaction['intermediates'][i] if i < len(reaction['intermediates']) else ''
        for i in range(max_products):
            row[f'PRODUCT_{i+1}'] = reaction['products'][i] if i < len(reaction['products']) else ''
        
        writer.writerow(row)  # Write the constructed row to the CSV
