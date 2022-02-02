# Echo Combination Builder #
A Python module for creating large-scale combination work list files.


## Summary ##
The intended purpose of this module is to provide a framework for easily constructing work list files for import to Echo acoustic liquid handlers (Beckman Coulter) that create combinations of substances for high throughput screening assays.  The original application was for small molecule screening, but additional applications should be possible without modification.  There are a series of steps involved in creating the work list files and this module provides the methods needed to perform these steps.


## Installation ##
**Dependency:** Python 3.8+

The simplest way to install and use the module is to clone the repository and place a copy in a project directory on the local PC.  From a command line navigate to the directory where the module is located and launch python. For example:   
`C:\> cd Foo\Bar`  
`C:\Foo\Bar> python`  

## Use And Examples ##

`# Import Combinations Module`  
`import Combinations as Combine`


### 1. Set Values and Initialize a Combinations Object ###
`# Set variables to indicate locations of input and output files`  
`map_filepath = "Example_Files\\ExamplePlatemap.txt"`  
`concentration_file = "Example_Files\\Example_Final_Concs.csv"`  
`save_filepath = "Example_Files\\ExampleOutput3.csv"`  
`cmt_filepath = "Example_Files\\ExampleOutput4.cmt"`  
  
`# Set variables to control the locations of special wells`  
`backfill_wells = Combine.generate_well_range("A21", "P24")`  
`control_wells = Combine.generate_well_range("A1","P2")`  
`control_wells.extend(Combine.generate_well_range("A13","P14"))`  
  
`# Set varaibles that specify assay conditions`  
`static_transfer_volume = 100`  
`assay_volume = 30`  
`combination_max = 3`  
  
`# Initialize the object - This creates the bucket to store all the data in`  
`exp = Combine.Combinations()`  

### 2. Load the plate map ###
`# Import the source plate map - were the source substances are on the source plate`  
`exp.load_platemap(map_filepath)`  


### 3. Setup the backfill wells - Comment/Uncomment as needed
`# There are two ways to set the backfill source wells: manually create`  
`# Option 1: Manually supply a list of wells`  
`#           This is fine for a small number of wells`  
`wells = ["A21", "A22", "A23", "A24", "B21", "B22", "B23", "B24"]`  
  
`# Option 2: Generate well list from start and stop wells`  
`#           This option is good for a large number of wells`  
`#           List comprehension is required to get well alphas`  
`wells = [x[0] for x in backfill_wells]`  
  
`# Set backfill wells is specific to individual plates`  
`# Repeat for all plates with backfill wells`  
`exp.platemap.plates["E3P00000776"].set_backfill_wells(wells)`  
  
### 4. Set up Combinations - Comment/Uncomment as needed
`# Option 1: Supply a manually curated list of combinations`  
`#           List compounds in separate columns, any number of`   
`#           columns is supported, header and any compound not`   
`#           in the platemap are skipped`  
`combinations_filepath = "Combination Template.csv"`  
`exp.load_platemap(combinations_filepath)`  
  
`# Option 2: Calculate all permutations in the script`  
`#           Specify how many compounds to include in each combination`  
`exp.generate_combinations(combination_max)`  

### 5. Set transfer volume or assay conditions
`# Option 1: Set a static volume for all substances`  
`#           Volume is in nanoliters - All combinations will be`  
`#           the 1:1:1 volume ratios`  
`exp.set_transfer_volume(static_transfer_volume)`  
  
`# Option 2: Set assay volume and assay concentration`  
`#           Assay volume is in microliters`  
`#           Assay concentration(s) must be supplied`  
`exp.set_assay_volume(assay_volume)`  
`# Set a constant concentration for all substances`  
`# exp.set_assay_concentration(conc=50, unit="mM")`  
`# Or set each concentration idependently with a csv file`  
`exp.set_assay_concentration(file=concentration_file)`  
  
### 6. Configure assay plate layout
`exp.reserve_control_wells([w[0] for w in control_wells])`  
  
### 7. Create the transfer list
`exp.create_transfers()`  
  
### 8. Sort transfer list for optimized transfer speed
`exp.sort_transfers()`  
  
### 9. Save transfer list - Echo formatted CSV file
`exp.save_transfers(save_filepath)`  
  
### 10. Save *.cmt file - Screener Mapping File
`#     OPTIONAL - Set replicate number to create replicate`  
`#     plates with the same plate mapping and concentrations`  
`exp.save_cmt(cmt_filepath, 3)`  



### IN A NEW SESSION
This must be done after using the Echo CSV to transfer samples
  
### 11. Update CMT with barcodes after performing transfers
`# This is a new python session - initialize the module again`  
`import Combinations as Combine`  
  
`cmt_filepath = "Example_Files\\ExampleOutput4.cmt"`  
`barcode_filepath = "Example_Files\\Barcode_List.csv"`  
  
`# Update barcodes`  
`Combine.update_CMT_barcodes(cmt_filepath, barcode_filepath)`  

