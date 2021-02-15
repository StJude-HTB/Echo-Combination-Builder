from os import path
import string, warnings, re, itertools


class Platemap(object):
    wells = dict()
    backfill = dict()

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
    
    def parse_well_alpha(self, well_alpha):
        # Take well references and create a list of wells that fill the range
        well_pattern = r'([a-zA-Z]{1,2})([0-9]{1,2})'
        pat = re.compile(well_pattern)
        mtch = pat.match(well_alpha)
        if(not mtch):
            raise Exception("Argument Error: Argument 'well_alpha' must be in the format of A01")
        # Set up letters
        LETTERS = [l for l in string.ascii_uppercase]
        LETTERS.extend([l1 + l2 for l1 in string.ascii_uppercase for l2 in string.ascii_uppercase])
        # Get numeric row, col
        row = LETTERS.index(mtch.group(1))+1
        col = int(mtch.group(2))
        return (well_alpha, [row, col])

    def parse_well_coord(self, well_coord):
        # Check argument
        if(len(well_coord) != 2 and all([type(x) is not int for x in well_coord])):
            raise Exception("Argument Error: Argument 'well_coord' must be list of 2 integers")
        # Set up letters
        LETTERS = [l for l in string.ascii_uppercase]
        LETTERS.extend([l1 + l2 for l1 in string.ascii_uppercase for l2 in string.ascii_uppercase])
        # Construct well_alpha
        well_alpha = LETTERS[well_coord[0]-1] + ("0" + str(well_coord[1]))[-2:]
        return well_alpha
   
    def generate_well_range(self, start, stop):
        st = self.parse_well_alpha(start)
        ed = self.parse_well_alpha(stop)
        # Calculate the number of well in the range
        r_dif = (ed[1][0] - st[1][0]) + 1
        c_dif = abs(ed[1][1] - st[1][1]) + 1
        w_dif = r_dif * c_dif
        print("Number of rows: " + str(r_dif) + " [" + str(st[1][0]) + ":" + str(ed[1][0]) + "]")
        print("Number of colums: " + str(c_dif) + " [" + str(st[1][1]) + ":" + str(ed[1][1]) + "]")
        print("Number of wells in range: " + str(w_dif))
        # Calculate the ranges
        if(w_dif > 0):
            # This is the normal condition
            wells = [(self.parse_well_coord([r, c]), [r,c]) 
                        for r in range(st[1][0], ed[1][0]+1) 
                        for c in range(st[1][1], ed[1][1]+1)]
        elif(w_dif < 0):
            # This is where the stop is before the start
            wells = [(self.parse_well_coord([r, c]), [r,c]) 
                        for r in range(ed[1][0], st[1][0]+1) 
                        for c in range(ed[1][1], st[1][1]+1)]
        else:
            # This is where the stop == start -> one well
            wells = [(self.parse_well_coord(st[1]), st[1])]
        return wells

    
    def set_backfill_wells(self, wells):
        # Accepts wells in the format of a list of strings
        if(any([w[1] in [self.wells[c] for c in self.wells] for w in wells])):
            raise Exception("Well Definition Error: One or more specified backfill wells are compound source wells")
        unq_wells = list(set(wells))
        unq_wells.sort()
        for w in unq_wells:
            well_coord = self.parse_well_alpha(w)
            self.backfill[well_coord[0]] = well_coord[1]
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
    used_backfills = list()

    # Workflow: Init -> Load Map -> Load or Calculate Combinations ->
    #           Set Volume -> Create Transfer File

    def __init__(self, format=384):
        # Set the transfer file header as the first element of the transfer list
        self.transfers.append(self.trns_header)
        # Set the destination plate format
        self.plt_format = format

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
                for line in combine:
                    # Remove any empty and "-" entries
                    temp = [c for c in line.strip().split(",") if c not in ["", "-"]]
                    # Check that all compounds are in the platemap - this removes the header too
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

    def build_combination_matrix(self, compounds, nmax=3):
        combination_list = []
        if(compounds is not None and len(compounds) > 0):
            n=1
            while n <= nmax:
                permutations = itertools.combinations(compounds, n)
                for p in permutations:
                    # Filter out permutations that are the same combination
                    if(all([set(p) != set(c) for c in combination_list])):
                        combination_list.append(list(p))
                n += 1
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
    
    def get_next_backfill(self):
        if(self.platemap.backfill is not None and len(self.platemap.backfill) > 0):
            # Get the keys of all of the backfill wells in a list
            backfill_wells = list(self.platemap.backfill.keys())
            if(self.used_backfills is None or len(self.used_backfills) == 0):
                # No backfills have been recorded, use the first well
                self.used_backfills.append(backfill_wells[0])
                return self.platemap.backfill[backfill_wells[0]]
            else:
                # Backfills have been done, get the wells that have not been used
                unused_well_idx = [backfill_wells.index(w) for w in backfill_wells if w not in self.used_backfills]
                if(len(unused_well_idx) > 0):
                    # Use the next well that has not been used yet
                    next_well_idx = min(unused_well_idx)
                    next_well = backfill_wells[next_well_idx]
                else:
                    # All of the wells have been used, clear the list and start over
                    self.used_backfills = list()
                    next_well = backfill_wells[0]
                self.used_backfills.append(next_well)
                return self.platemap.backfill[next_well]
        else:
            return None    

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

    def sort_transfers(self, priority="source"):
        if(priority not in ["source", "destination"]):
            raise Exception("Invalid Argument: Argument priority must be one of 'source' or 'destination'")
        else:
            t = [self.transfers[0]]
            x = self.transfers[1:]
            if(priority == "source"):
                x.sort()
                t.extend(x)
            if(priority == "destination"):
                pattern1 = r'^(source[0-9]+,[0-9]{1,2},[0-9]{1,2},)(destination[0-9]+,[0-9]{1,2},[0-9]{1,2},[0-9\.]+)$'
                pattern2 = r'^(destination[0-9]+,[0-9]{1,2},[0-9]{1,2},[0-9\.]+) - (source[0-9]+,[0-9]{1,2},[0-9]{1,2},)$'
                st = [re.sub(pattern1, r'\2 - \1', t) for t in x]
                st.sort()
                t.extend([re.sub(pattern2, r'\2\1', t) for t in st])
            self.transfers = t
        return

    def create_transfers(self):
        if(self.platemap is not None):
            max_combinations = max([len(x) for x in self.clist])
            for combination in self.clist:
                [dest_plt, dest_well] = self.find_next_dest()
                [dest_row, dest_col] = self.destinations[dest_plt][dest_well]['coord']
                for compound in combination:
                    if(compound in self.platemap.wells):
                        if("transfers" not in self.destinations[dest_plt][dest_well]):
                            self.destinations[dest_plt][dest_well]["transfers"] = list()
                        row = self.platemap.wells[compound][0]
                        col = self.platemap.wells[compound][1]
                        # TODO: Get the source name from someplace else to allow multiple sources
                        src_name = "source1"
                        trans_str = self.format_transfer(src_name, row, col, dest_plt, dest_row, dest_col, self.transfer_vol)
                        if trans_str is not None:
                            self.transfers.append(trans_str)
                            self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
                if(len(combination) < max_combinations) and (self.platemap.backfill is not None):
                    for _ in range(0,max_combinations-len(combination)):
                        well = self.get_next_backfill()
                        if well is not None:
                            # TODO: Get the source name from someplace else to allow multiple sources
                            src_name = "source1"
                            trans_str = self.format_transfer(src_name, well[0], well[1], dest_plt, dest_row, dest_col, self.transfer_vol)
                            if trans_str is not None:
                                self.transfers.append(trans_str)
                                self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
        return
    
    def print_transfers(self):
        print("\n".join(self.transfers))

    def save_transfers(self, saveas, sort="source"):
        if(saveas[-4:].lower() != ".csv"):
            saveas = saveas + ".csv"
        if(not path.exists(path.dirname(saveas))):
            raise Exception("Invalid Save Path: The directory " + path.dirname(saveas) + "does not exist")
        if(len(self.transfers) > 1):
            with open(saveas, 'w') as output:
                if(sort):
                    self.sort_transfers(sort)
                output.writelines(self.transfers)
        return

