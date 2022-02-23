import combination_builder as Combine


# 1. Set Values and Initialize a Combinations Object
map_filepath = "Example_Files\\ExamplePlatemap.txt"
concentration_file = "Example_Files\\Example_Final_Concs.csv"
save_filepath = "Example_Files\\ExampleOutput3.csv"
cmt_filepath = "Example_Files\\ExampleOutput4.cmt"

backfill_wells = Combine.generate_well_range("A21", "P24")
control_wells = Combine.generate_well_range("A1","P2")
control_wells.extend(Combine.generate_well_range("A13","P14"))

static_transfer_volume = 100
assay_volume = 30
combination_max = 3
substance_id_regex = r'SJ[0-9-]+'

# Initialize the object
exp = Combine.Combinations()


# 2. Load the plate map
exp.load_platemap(map_filepath, substance_id_regex)


# 3. Setup the backfill wells - Comment/Uncomment as needed
# Option 1: Manually supply a list of wells
#           This is fine for a small number of wells
# wells = ["A21", "A22", "A23", "A24", "B21", "B22", "B23", "B24"]

# Option 2: Generate well list from start and stop wells
#           This option is good for a large number of wells
#           List comprehension is required to get well alphas
wells = [x[0] for x in backfill_wells]

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
exp.generate_combinations(combination_max)


# 5. Set transfer volume or assay conditions
# Option 1: Set a static volume for all substances
#           Volume is in nanoliters - All combinations will be 
#           the 1:1:1 volume ratios
# exp.set_transfer_volume(static_transfer_volume)

# Option 2: Set assay volume and assay concentration
#           Assay volume is in microliters
#           Assay concentration(s) must be supplied
exp.set_assay_volume(assay_volume)
# Set a constant concentration for all substances
# exp.set_assay_concentration(conc=50, unit="mM")
# Or set each concentration idependently with a csv file
exp.set_assay_concentration(file=concentration_file)


# 6. Configure assay plate layout
exp.reserve_control_wells([w[0] for w in control_wells])


# 7. Create the transfer list
exp.create_transfers()


# 8. Sort transfer list for optimized transfer speed
exp.sort_transfers()


# 9. Save transfer list - Echo formatted CSV file
exp.save_transfers(save_filepath)


# 10. Save *.cmt file - Screener Mapping File
#     OPTIONAL - Set replicate number to create replicate 
#     plates with the same plate mapping and concentrations
exp.save_cmt(cmt_filepath, 3)



# IN A NEW SESSION
# After using the Echo CSV to transfer samples
#
# 11. Update CMT with barcodes after performing transfers
import src.combination_builder.Combinations as Combine

cmt_filepath = "Example_Files\\ExampleOutput4.cmt"
barcode_filepath = "Example_Files\\Barcode_List.csv"

# Update barcodes
Combine.update_CMT_barcodes(cmt_filepath, barcode_filepath)
