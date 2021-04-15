# This script must be run from the same folder as the module or the 
# module must be added to the system PATH

import Combinations as Combine


# 1. Initialize a Combinations Object
exp = Combine.Combinations()


# 2. Load the plate map
map_filepath = "Example_Files\\ExamplePlatemap.txt"
exp.load_platemap(map_filepath)


# 3. Setup the backfill wells - Comment/Uncomment as needed
# Option 1: Manually supply a list of wells
#           This is fine for a small number of wells
# wells = ["A21", "A22", "A23", "A24", "B21", "B22", "B23", "B24"]

# Option 2: Generate well list from start and stop wells
#           This option is good for a large number of wells
#           List comprehension is required to get well alphas
wells = [x[0] for x in Combine.generate_well_range("A21", "P24")]

# Set backfill wells is specific to individual plates
# Repeat for all plates with backfill wells
exp.platemap.plates["E3P00000776"].set_backfill_wells(wells)


# 4. Set up Combinations - Comment/Uncomment as needed
# Option 1: Supply a manually curated list of combinations
#           List compounds in separate columns, any number of 
#           columns is supported, header and any compound not 
#           in the platemap are skipped
# combinations_filepath = "Combination Template.csv"
# exp.load_platemap(combinations_filepath)

# Option 2: Calculate all permutations in the script
#           Specify how many compounds to include in each combination
exp.generate_combinations(3)


# 5. Set transfer volume or assay conditions
# Option 1: Set a static volume for all substances
#           Volume is in nanoliters - All combinations will be 
#           the 1:1:1 volume ratios
volume = 100
# exp.set_transfer_volume(volume)

# Option 2: Set assay volume and assay concentration
#           Assay volume is in microliters
#           Assay concentration(s) must be supplied
exp.set_assay_volume(25)
# Set a constant concentration for all substances
# exp.set_assay_concentration(conc=50, unit="mM")
# Or set each concentration idependently with a csv file
exp.set_assay_concentration(file="Example_Files\\Example_Final_Concs.csv")


# 7. Create the transfer list
exp.create_transfers()


# 8. Sort transfer list for optimized transfer speed
exp.sort_transfers()


# 9. Save transfer list - Echo formatted CSV file
save_filepath = "Example_Files\\ExampleOutput3.csv"
exp.save_transfers(save_filepath)


#10. Save *.cmt file - Screener Mapping File
cmt_file = "Example_Files\\ExampleOutput4.cmt"
exp.save_cmt(cmt_file)
