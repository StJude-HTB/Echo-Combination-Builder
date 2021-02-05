from os import path
import string, warnings, re


class Platemap(object):
    wells = dict()

    def __init__(self, filepath):
        raise_warning = False
        basic_pattern = r'^([a-zA-Z0-9-_ ]+),([0-9]{1,2}),([0-9]{1,2})$'
        mosaic_pattern = r'\s(SJ[0-9-]+)\s([A-Z]+[0-9]{1,2})\s'
        # Import the plate map
        if(path.exists(filepath)):
            with open(filepath, 'r') as map_file:
                for line in map_file:
                    basic = re.search(basic_pattern, line)
                    mosaic = re.search(mosaic_pattern, line)
                    if((not basic) and (not mosaic)):
                        continue
                    if(basic):
                        # Expects 3 columns: Compound ID, Row, Column
                        [cmpd, row, col] = [basic.group(1), basic.group(2), basic.group(3)]
                    if(mosaic):
                        # Expects > 9 columns: Compound ID (8), Well Alpha (9)
                        # Parses Well Alpha to numeric Row/Column
                        [cmpd, well] = [mosaic.group(1), mosaic.group(2)]
                        row = str(string.ascii_uppercase.find(well[0])+1)
                        col = well[1:3]
                    # Ensure that this Compound ID has not already been recorded
                    if(cmpd not in self.wells):
                        self.wells[cmpd] = [row, col]
                    # Raise a warning about duplicates if it has
                    else:
                        raise_warning = True
            if(len(self.wells) == 0):
                raise Exception("File Parse Error: File contents could not be parsed")
            if(raise_warning):
                warnings.warn("Duplicate Compounds Detected: Duplicate compounds were detected in the map file")
        return


class Combinations(object):
    clist = list()
    platemap = None
    transfers = list()
    destinations = dict()
    transfer_vol = "0.0"
    trns_str_tmplt = "<SRC_NAME>,<SRC_COL>,<SRC_ROW>,<DEST_NAME>,<DEST_COL>,<DEST_ROW>,<TRS_VOL>\n"
    trns_header = "Source Barcode,Source Column,Source Row,Destination Barcode,Destination Column,Destination Row,Volume\n"
    plate_dims = {96: [8,12], 384: [16,24], 1536:[32,48]}
    plt_format = 384

    # TODO: Refactor code so that init does not parse the combinations or mapfile
    #       New flow should be: Init -> Load Map -> Load or Calculate Combinations ->
    #       Set Volume -> Create Transfer File

    def __init__(self, format=384):
        # Set the transfer file header as the first element of the transfer list
        self.transfers.append(self.trns_header)
        # Set the destination plate format
        self.plt_format = format
        # Load the platemap file data if a filepath was supplied - TEMP
        # if(map_file is not None):
        #    self.load_platemap(map_file)
        # Load the combine file data if a filepath was supplied - TEMP
        # if(map_file is not None):
        #    self.load_combinations(combine_file)
        # Set combination list as all possible combinations if a combination matrix
        # was not supplied and the platemap was supplied 
        # elif(self.platemap is not None):
        #    cmpds = [name for name in self.platemap.wells]
        #    self.clist = self.generate_combinations(cmpds)

    def load_platemap(self, filepath):
        if(filepath is not None and path.exists(filepath)):
            self.platemap = Platemap(filepath)
        return

    def load_combinations(self, combine_file):
        # Load the combination matrix if a filepath was supplied
        #  --> Keep this to support manually curating combinations if all possible 
        #      combinations are not desired
        if(combine_file is not None and path.exists(combine_file)):
            with open(combine_file, 'r') as combine:
                # Skip the header
                # TODO: Try to do a Regex match on the first line to determine
                #       if there is a header at all
                # next(combine)
                for line in combine:
                    # Remove any empty and "-" entries
                    temp = [c for c in line.strip().split(",") if c not in ["", "-"]]
                    # Check that all compounds are in the platemap
                    if(all([(t in self.platemap.wells) for t in temp])):
                        self.clist.append(temp)

    def set_volume(self, volume):
        if(volume is not None):
            self.transfer_vol = str(2.5 * round(float(volume)/2.5))
        return

    def generate_combinations(self):
        compounds = [name for name in self.platemap.wells]
        self.clist = self.build_combination_matrix(compounds)
        return

    def build_combination_matrix(self, compounds):
        combination_list = []
        if(compounds is not None and len(compounds) > 0):
            # TODO: Try to find a way to support any number of compounds in combination
            for cmpd in compounds:
                # Add single
                combination_list.append([cmpd])
                remain1 = [name for name in compounds if name is not cmpd]
                for cmpd2 in remain1:
                    # Add double combination
                    if(all([set([cmpd, cmpd2]) != set(c) for c in combination_list])):
                        combination_list.append([cmpd, cmpd2])
                    remain2 = [name for name in remain1 if name is not cmpd2]
                    for cmpd3 in remain2:
                        # Add triple combination
                        if(all([set([cmpd, cmpd2, cmpd3]) != set(c) for c in combination_list])):
                            combination_list.append([cmpd, cmpd2, cmpd3])
        return combination_list

    def add_empty_plate(self):
        wells = dict()
        # Set plate dimmensions from format
        [rows, cols] = self.plate_dims[self.plt_format]
        row = 1
        while row <= rows:
            col = 1
            while col <= cols:
                # Generate well alphanumeric name
                LETTERS = [l for l in string.ascii_uppercase]
                LETTERS.extend([l1 + l2 for l1 in string.ascii_uppercase for l2 in string.ascii_uppercase])
                name = LETTERS[row-1] + ("0" + str(col))[-2:]
                # Set numeric coordinates
                coord = [row, col]
                # Record well
                wells[name] = {"coord": coord}
                col += 1
            row += 1
        # Store wells dictionary
        self.destinations["destination"+str(len(self.destinations)+1)] = wells
        return

    def find_next_dest(self):
        # Get the number of empty wells on the plate
        empty_wells = len([w for p in self.destinations for w in self.destinations[p] if "transfers" not in self.destinations[p][w]])
        if(len(self.destinations) == 0 or empty_wells == 0):
            # Create a new plate if the current one if full
            self.add_empty_plate()
        # Iterate over plates then wells to find one that has not been used
        for plate in self.destinations:
            for well in self.destinations[plate]:
                if ("transfers" not in self.destinations[plate][well]):
                    return [plate, well]

    def format_transfer(self, sname, srow, scol, dname, drow, dcol, vol):
        if(all([sname, scol, srow, dname, dcol, drow, vol])):
            trs_str = self.trns_str_tmplt.replace("<SRC_NAME>", sname)
            trs_str = trs_str.replace("<SRC_ROW>", str(srow))
            trs_str = trs_str.replace("<SRC_COL>", str(scol))
            trs_str = trs_str.replace("<DEST_NAME>", dname)
            trs_str = trs_str.replace("<DEST_ROW>", str(drow))
            trs_str = trs_str.replace("<DEST_COL>", str(dcol))
            trs_str = trs_str.replace("<TRS_VOL>", str(vol))
            return trs_str

    # TODO: Add support for sorting transfers by source well or by destination well

    def create_transfers(self):
        if(self.platemap is not None):
            for combination in self.clist:
                [dest_plt, dest_well] = self.find_next_dest()
                [dest_row, dest_col] = self.destinations[dest_plt][dest_well]['coord']
                for compound in combination:
                    if(compound in self.platemap.wells):
                        if("transfers" not in self.destinations[dest_plt][dest_well]):
                            self.destinations[dest_plt][dest_well]["transfers"] = list()
                        row = self.platemap.wells[compound][0]
                        col = self.platemap.wells[compound][1]
                        src_name = "source1"
                        trans_str = self.format_transfer(src_name, row, col, dest_plt, dest_row, dest_col, self.transfer_vol)
                        if trans_str is not None:
                            self.transfers.append(trans_str)
                            self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
        return
    
    def print_transfers(self):
        print("\n".join(self.transfers))

    # TODO: Add check for *.csv extension

    def save_transfers(self, saveas):
        if(len(self.transfers) > 1):
            with open(saveas, 'w') as output:
                output.writelines(self.transfers)
        return

