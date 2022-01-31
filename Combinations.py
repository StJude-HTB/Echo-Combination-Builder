from os import path
import string, warnings, re, itertools, os, math


def parse_well_alpha(well_alpha):
    if(type(well_alpha) is not str):
        raise Exception("Argument Error: Argument 'well_alpha' must be of type 'str'")
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

def parse_well_coord(well_coord):
    # Check argument
    if(len(well_coord) != 2 and all([type(x) is not int for x in well_coord])):
        raise Exception("Argument Error: Argument 'well_coord' must be list of 2 integers")
    # Set up letters
    LETTERS = [l for l in string.ascii_uppercase]
    LETTERS.extend([l1 + l2 for l1 in string.ascii_uppercase for l2 in string.ascii_uppercase])
    # Construct well_alpha
    well_alpha = LETTERS[well_coord[0]-1] + ("0" + str(well_coord[1]))[-2:]
    return well_alpha

def generate_well_range(start, stop):
    st = parse_well_alpha(start)
    ed = parse_well_alpha(stop)
    # Calculate the number of well in the range
    r_dif = (ed[1][0] - st[1][0]) + 1
    c_dif = abs(ed[1][1] - st[1][1]) + 1
    w_dif = r_dif * c_dif
    # print("Number of rows: " + str(r_dif) + " [" + str(st[1][0]) + ":" + str(ed[1][0]) + "]")
    # print("Number of colums: " + str(c_dif) + " [" + str(st[1][1]) + ":" + str(ed[1][1]) + "]")
    # print("Number of wells in range: " + str(w_dif))
    # Calculate the ranges
    if(w_dif > 1):
        # This is the normal condition
        wells = [(parse_well_coord([r, c]), [r,c]) 
                    for r in range(st[1][0], ed[1][0]+1) 
                    for c in range(st[1][1], ed[1][1]+1)]
    elif(w_dif < 1):
        # This is where the stop is before the start
        wells = [(parse_well_coord([r, c]), [r,c]) 
                    for r in range(ed[1][0], st[1][0]+1) 
                    for c in range(ed[1][1], st[1][1]+1)]
    else:
        # This is where the stop == start -> one well
        wells = [(parse_well_coord(st[1]), st[1])]
    return wells

def conc_unit_conversion(conc, unit):
    if(unit not in ["pM", "nM", "uM", "mM", "M"]):
        raise Exception("Calculation Error: Concentration units must be one of 'pM', 'nM', 'uM', 'mM', 'M'")
    unit_conversion = {"M":1, "mM":1000, "uM":1000000, "nM":1000000000, "pM":1000000000000}
    return float(conc)/unit_conversion[unit]

def update_CMT_barcodes(cmt_file, barcode_file):
    # Expects barcodes supplied as a csv with two columns: generic name, barcode
    # Replaces all instances of generic name in cmt with barcode
    replacements = dict()
    pattern = re.compile(r'^(?P<name><destination[0-9]+[_A-Z]*>)')
    if(os.path.exists(barcode_file)):
        with open(barcode_file, 'r') as barcodes:
            for line in barcodes:
                [name, bc] = line.split(',')
                replacements[name] = bc.strip()
    print(" * Imported " + str(len(replacements)) + " replacement barcodes")
    counter = 0
    if(os.path.exists(cmt_file)):
        new_cmt_file = cmt_file.replace(".cmt", "-Updated.cmt")
        with open(cmt_file, 'r') as cmt:
            with open(new_cmt_file, 'w') as new_cmt:
                for line in cmt:
                    if(line[0] == "#"):
                        new_cmt.write(line)
                    else:
                        match = pattern.match(line)
                        if(match):
                            # print("MATCH     -  " + line)
                            d = match.groupdict()
                            new_line = line.replace(d["name"], replacements[d["name"].replace("<", "").replace(">", "")])
                            counter += 1
                            new_cmt.write(new_line)
                        else:
                            # print("NO MATCH  -  " + line)
                            new_cmt.write(line)
    print(" * Replaced " + str(counter) + " barcodes in " + new_cmt_file)
    return 


class Platemap(object):

    def __init__(self):
        self.wells = dict()
        self.backfill = dict()
        self.controls = dict()
        return
    
    def set_backfill_wells(self, wells):
        # Accepts wells in the format of a list of strings
        if(any([w in [parse_well_coord(self.wells[c]["location"]) for c in self.wells] for w in wells])):
            raise Exception("Well Definition Error: One or more specified backfill wells are compound source wells")
        unq_wells = list(set(wells))
        unq_wells.sort()
        for w in unq_wells:
            well_coord = parse_well_alpha(w)
            self.backfill[well_coord[0]] = {"location": well_coord[1], "usage": 0}
        return

    def set_controls(self, compounds, volume, times_used=16):
        if(len(compounds) != len(volume)) and (len(volume) > 1):
            raise Exception("Argument Error: Length of 'compounds' must equal length of 'volume' unless 'volume' has a length of 1") 
        # Volume can be a list corresponding to the compounds list
        if(any([x not in self.wells for x in compounds])):
            raise Exception("Control Compound Error: One or more control compounds specified are not in the mapped wells")
        unq_cmpds = list(set(compounds))
        for cmpd in unq_cmpds:
            well = self.wells.pop(cmpd)
            loc = well['location']
            use = well['usage']
            if(len(volume) == 1):
                vol = volume[0]
            else:
                vol = volume[compounds.index(cmpd)]
            self.controls[cmpd] = {"location": [loc[0], loc[1]], "times_used": times_used, "volume": vol, "usage": use}
        print(" * Moved " + str(len(self.controls)) + " controls from wells")
        print(" * Wells now contains " + str(len(self.wells)) + " compounds")
        return


class SourcePlates(object):

    def __init__(self, filepath):
        self.plates = dict()
        raise_warning = False
        basic_pattern = re.compile(r'^(?P<id>[a-zA-Z0-9-_ ]+),(?P<row>[0-9]{1,2}),(?P<col>[0-9]{1,2}),?(?P<conc>[0-9]+\.?[0-9]*)?$')
        mosaic_pattern = re.compile(r'^(?P<bc>[a-zA-Z0-9]+)\s.+\s(?P<id>SJ[0-9-]+)\s(?P<well>[A-Z]+[0-9]{1,2})\s[0-9]+\s(?P<conc>[0-9]+\.?[0-9]*)\s')
        # Import the plate map
        if(path.exists(filepath)):
            with open(filepath, 'r') as map_file:
                for line in map_file:
                    basic = basic_pattern.match(line)
                    mosaic = mosaic_pattern.match(line)
                    if((not basic) and (not mosaic)):
                        continue
                    if(basic):
                        # Basic only supports 1 source plate
                        plt = "source1"
                        d = basic.groupdict()
                        # Expects 3 columns: Compound ID, Row, Column
                        [cmpd, row, col, conc] = [d["id"], int(d["row"]), int(d["col"]), d["conc"]]
                    if(mosaic):
                        # Expects > 9 columns: Compound ID (8), Well Alpha (9)
                        # Parses Well Alpha to numeric Row/Column
                        d = mosaic.groupdict()
                        [plt, cmpd, well, conc] = [d["bc"], d["id"], d["well"], d["conc"]]
                        row = string.ascii_uppercase.find(well[0])+1
                        col = int(well[1:3])
                    # Convert Conc to Float
                    if(conc):
                        # All Concentrations are expected in mM units
                        # TODO: consider adding support for additional concentration units
                        conc = conc_unit_conversion(conc, "mM")
                    # Ensure that the plate is in the list of platemaps
                    if(plt not in self.plates):
                        self.plates[plt] = Platemap()
                    # Ensure that this Compound ID has not already been recorded
                    if(len(self.find(cmpd)) == 0):
                        self.plates[plt].wells[cmpd] = {"location": [row, col], "volume": 0.0, "conc": conc, "usage": 0}
                    # Raise a warning about duplicates if it has
                    else:
                        raise_warning = True
            if(sum([len(self.plates[p].wells) for p in self.plates]) == 0):
                raise Exception("File Parse Error: File contents could not be parsed")
            if(raise_warning):
                warnings.warn("Duplicate Compounds Detected: Duplicate compounds were detected in the map file")
        return
    
    def get_all_compounds(self):
        return [cmpd for plt in self.plates for cmpd in self.plates[plt].wells]
    
    def find(self, compound):
        found = [(plt, cmpd, self.plates[plt].wells[cmpd]) 
                    for plt in self.plates 
                    for cmpd in self.plates[plt].wells 
                    if cmpd == compound]
        return found
    
    def mark_use(self, plt, compound):
        self.plates[plt].wells[compound]["usage"] += 1
        return
    
    def has_backfills(self):
        return (sum([len(self.plates[p].backfill) for p in self.plates]) > 0)
    
    def get_backfill_wells(self, plate=None):
        if(plate):
            return [(plate, well, self.plates[plate].backfill[well]) for well in self.plates[plate].backfill]
        else:
            return [(plt, well, self.plates[plt].backfill[well]) for plt in self.plates for well in self.plates[plt].backfill]

    def has_controls(self):
        return (sum([len(self.plates[p].controls) for p in self.plates]) > 0)
    
    def get_control_wells(self):
        return [(plt, ctl, self.plates[plt].controls[ctl]) for plt in self.plates for ctl in self.plates[plt].controls]


class Combinations(object):
    clist = list()                  # List of all combinations, each element is a list of substances to combine
    platemap = None                 # Storage of Platemap object
    transfers = {"all": list()}     # Lists of transfers - defaults to single list in 'all', by sorting with split multiple lists are possible
    destinations = dict()           # Destination plates keyed on destination plate name
    trns_str_tmplt = "<SRC_NAME>,<SRC_COL>,<SRC_ROW>,<DEST_NAME>,<DEST_COL>,<DEST_ROW>,<TRS_VOL>,<NOTE>\n"
    trns_header = "Source Barcode,Source Column,Source Row,Destination Barcode,Destination Column,Destination Row,Volume\n"
    map_tmplt = "<DEST_NAME>\t<ROW>\t<COL>\t<ID1>\t<CONC1>\t<ID2>\t<CONC2>\t<ID3>\t<CONC3>\n"
    map_header1 = "# Genedata Screener Compound Mapping Table - Created by Echo Combinations Builder\n"
    map_header2 = "# <MAPPING_PARAMETERS>\n"
    map_header3 = "# PlateFormat\t<ROWS>\t<COLUMNS>\n"
    map_header4 = "# ConcentrationUnit\tuM\n"
    map_header5 = "# PlateID\tRow\tCol\tCompound ID\tConcentration\tCONDENSING_PROPERTY:Compound ID2\tWELL_PROPERTY:Conc.2 [uM]\tCONDENSING_PROPERTY:Compound ID3\tWELL_PROPERTY:Conc.3 [uM]\n"
    plate_dims = {96: [8,12], 384: [16,24], 1536:[32,48]}
    plt_format = 384                # Format of plate - defaults to 384, can also be 96 or 1536
    used_backfills = list()         # List of backfill wells that have been used - is populated and cleared automatically
    control_wells = dict()          # Wells to use as controls - keyed on well alpha
    transfer_vol = 0.0              # Volume of compounds to tranfer, is overidden by compound specific volumes
    assay_volume = 0.0              # Assay Volume in uL
    assay_concentrations = dict()   # Assay Concentrations keyed on compound ids - missing compounds will use the global volume
    factor = 1                      # Dead volume factor, default is 1 or no dead volume adjustment, Volumes and concentrations are adjusted

    # Workflow: Init -> Load Map -> Setup Control Compounds -> 
    #           Reserve Control Wells -> Setup Backfill Wells -> 
    #           Set Volume -> Load or Calculate Combinations ->  
    #           Create Transfer File -> Create *.cmt File

    def __init__(self, format=384):
        # Set the transfer file header as the first element of the transfer list
        self.transfers["all"].append(self.trns_header)
        # Set the destination plate format
        self.plt_format = format

    def load_platemap(self, filepath):
        if(filepath is not None and path.exists(filepath)):
            self.platemap = SourcePlates(filepath)
            print(" * Loaded " + str(sum([len(x) for x in self.platemap.plates])) + " mapped wells")
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
                    if(all([(t in self.platemap.get_all_compounds()) for t in temp])):
                        self.clist.append(temp)
            print(" * Loaded " + str(len(self.clist)) + " combinations")

    def set_transfer_volume(self, volume=None, file=None):
        if(volume is not None):
            self.transfer_vol = 2.5 * round(float(volume)/2.5)
            print(" * Set transfer volume to: " + str(self.transfer_vol))
        if(file is not None) and (path.exists(file)):
            with open(file, 'r') as volumes:
                i = 0
                # Expects a csv with two columns: Compound ID, Volume to use
                pattern = re.compile(r'^(?P<id>[a-zA-Z0-9_\-() ]+),(?P<vol>[0-9]+\.?[0-9]+)$')
                for line in volumes:
                    match = pattern.match(line)
                    if(match):
                        d = match.groupdict()
                        loc = self.platemap.find(d["id"])
                        for l in loc:
                            self.platemap.plates[l[0]].wells[d["id"]]["volume"] = float(d["vol"])
                        i += 1
            print(" * Set transfer volume for: " + str(i) + " compounds")
        return
    
    def set_assay_volume(self, volume):
        self.assay_volume = float(volume)
        return
    
    # def conc_unit_conversion(self, conc, unit):
    #     if(unit not in ["pM", "nM", "uM", "mM", "M"]):
    #         raise Exception("Calculation Error: Concentration units must be one of 'pM', 'nM', 'uM', 'mM', 'M'")
    #     unit_conversion = {"M":1, "mM":1000, "uM":1000000, "nM":1000000000, "pM":1000000000000}
    #     return float(conc)/unit_conversion[unit]

    def set_assay_concentration(self, conc=None, unit="mM", file=None):
        if(self.assay_volume <= 0):
            raise Exception("Calculation Error: Concentrations cannot be set before setting assay volume")
        if(unit not in ["pM", "nM", "uM", "mM", "M"]):
            raise Exception("Calculation Error: Concentration units must be one of 'pM', 'nM', 'uM', 'mM', 'M'")
        if(not self.platemap) or (len(self.platemap.plates) == 0):
            raise Exception("Calculation Error: Concentrations cannot be set before source plates are loaded")
        if(conc is not None):
            adj_conc = conc_unit_conversion(conc, unit)
            [self.assay_concentrations.update({w: adj_conc}) for p in self.platemap.plates for w in self.platemap.plates[p].wells]
            #[self.platemap.plates[p].wells[w].update({'conc': adj_conc}) for p in self.platemap.plates for w in self.platemap.plates[p].wells]
            print(" * Set all compound concentrations to: " + str(conc))
        elif(file is not None) and (path.exists(file)):
            with open(file, 'r') as concs:
                i = 0
                # Expects a csv with three columns: Compound ID, Concentration to use, and Concentration unit
                pattern = re.compile(r'^(?P<id>[a-zA-Z0-9_\-() ]+),(?P<conc>[0-9]+\.?[0-9]*),(?P<unit>[pnum]?[M])$')
                for line in concs:
                    match = pattern.match(line)
                    if(match):
                        d = match.groupdict()
                        loc = self.platemap.find(d["id"])
                        adj_conc = conc_unit_conversion(d["conc"], d["unit"])
                        for l in loc:
                            self.assay_concentrations.update({d["id"]: adj_conc})
                            #self.platemap.plates[l[0]].wells[d["id"]]["conc"] = adj_conc
                        i += 1
            print(" * Set compound concentrations for: " + str(i) + " compounds")
        else:
            raise Exception("File Parse Error: The file supplied does not exist")
        return

    def reserve_control_wells(self, wells):
        # Accepts wells in the format of a list of strings
        unq_wells = list(set(wells))
        unq_wells.sort()
        for w in unq_wells:
            well_coord = parse_well_alpha(w)
            self.control_wells[well_coord[0]] = well_coord[1]
        return

    def generate_combinations(self, nmax=3):
        compounds = self.platemap.get_all_compounds()
        self.clist = self.build_combination_matrix(compounds, nmax)
        print(" * Saved " + str(len(self.clist)) + " combinations")
        return

    def build_combination_matrix(self, compounds, nmax):
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
        self.destinations["destination"+("0"+str(len(self.destinations)+1))[-2:]] = wells
        return

    def find_next_dest(self):
        # Get the number of empty wells on the plate
        empty_wells = len([w for p in self.destinations for w in self.destinations[p] 
                            if "transfers" not in self.destinations[p][w] and 
                            w not in self.control_wells])
        if(len(self.destinations) == 0 or empty_wells == 0):
            # Create a new plate if the current one if full
            self.add_empty_plate()
        # Iterate over plates then wells to find one that has not been used
        for plate in self.destinations:
            for well in self.destinations[plate]:
                if ("transfers" not in self.destinations[plate][well] and 
                    well not in self.control_wells):
                    return [plate, well]
    
    def get_next_backfill(self, plate=None):
        if(self.platemap and self.platemap.has_backfills()):
            # Get the keys of all of the backfill wells in a list
            backfill_wells = self.platemap.get_backfill_wells(plate)
            # Find the well with the lowest usage
            min_use = min([p[2]["usage"] for p in backfill_wells])
            well = [p for p in backfill_wells if p[2]["usage"] == min_use][0]
            # Format of well: (plt, well, {location: [r,c], usage:0})
            # Update usage and return
            self.platemap.plates[well[0]].backfill[well[1]]["usage"] += 1
            return well
        else:
            return None   
    
    def sort_wells(self, wells, mode):
        if(mode not in ["column", "row"]):
            raise Exception("Argument Error: Argument 'mode' must be one of 'column' or 'row'")
        if(wells is not None and len(wells) > 0):
            if(mode == "row"):
                wells.sort()
            if(mode == "column"):
                pattern1 = r"([a-zA-Z]{1,2})([0-9]{2})"
                pattern2 = r"([0-9]{2})([a-zA-Z]{1,2})"
                st = [re.sub(pattern1, r'\2\1', w) for w in wells]
                st.sort()
                wells = [re.sub(pattern2, r'\2\1', w) for w in st]
            return wells

    def find_next_ctrl(self, fill_mode="column"):
        # Get the number of empty control wells on the plate
        empty_wells = len([w for p in self.destinations for w in self.destinations[p] 
                            if "transfers" not in self.destinations[p][w] and 
                            w in self.control_wells])
        if(len(self.destinations) == 0 or empty_wells == 0):
            # Create a new plate if the current one if full
            self.add_empty_plate()
        # Iterate over plates then wells to find one that has not been used
        for plate in self.destinations:
            # Sort wells
            sorted_wells = self.sort_wells(list(self.destinations[plate].keys()), fill_mode)
            for well in sorted_wells:
                if ("transfers" not in self.destinations[plate][well] and 
                    well in self.control_wells):
                    return [plate, well]

    def format_transfer(self, sname, srow, scol, dname, drow, dcol, vol, note=""):
        if(all([sname, scol, srow, dname, dcol, drow, vol])):
            trs_str = self.trns_str_tmplt.replace("<SRC_NAME>", sname)
            trs_str = trs_str.replace("<SRC_ROW>", str(srow))
            trs_str = trs_str.replace("<SRC_COL>", str(scol))
            trs_str = trs_str.replace("<DEST_NAME>", dname)
            trs_str = trs_str.replace("<DEST_ROW>", str(drow))
            trs_str = trs_str.replace("<DEST_COL>", str(dcol))
            trs_str = trs_str.replace("<TRS_VOL>", str(vol))
            trs_str = trs_str.replace("<NOTE>", str(note))
            return trs_str

    def sort_transfers(self, priority="source", split=False):
        if(priority not in ["source", "destination"]):
            raise Exception("Invalid Argument: Argument priority must be one of 'source' or 'destination'")
        else:
            n = [self.transfers["all"][0]]
            x = self.transfers["all"][1:]
            match_pattern1 = re.compile(r'^(?P<sn>[a-zA-Z0-9_-]+),(?P<sr>[0-9]{1,2}),(?P<sc>[0-9]{1,2}),(?P<dn>[a-zA-Z0-9_-]+),(?P<dr>[0-9]{1,2}),(?P<dc>[0-9]{1,2}),(?P<tv>[0-9\.]+),(?P<tn>.+)$')
            sorting_dict = dict()
            g = list()
            for t in x:
                m = match_pattern1.match(t)
                if(m):
                    d = m.groupdict()
                    if(priority == "source"):
                        s = d["sn"] + d["dn"] + ("0" + d["sr"])[-2:] + ("0" + d["sc"])[-2:] + ("0" + d["dr"])[-2:] + ("0" + d["dc"])[-2:]
                        sorting_dict[s] = dict()
                        sorting_dict[s]["transfer"] = t
                        sorting_dict[s]["group"] = d["sn"] + "-" + d["dn"]
                    if(priority == "destination"):
                        s = d["sn"] + d["dn"] + ("0" + d["dr"])[-2:] + ("0" + d["dc"])[-2:] + ("0" + d["sr"])[-2:] + ("0" + d["sc"])[-2:]
                        sorting_dict[s] = dict()
                        sorting_dict[s]["transfer"] = t
                        sorting_dict[s]["group"] = d["sn"] + "-" + d["dn"]
            refs = list(sorting_dict.keys())
            refs.sort()
            [n.append(sorting_dict[k]["transfer"]) for k in refs]
            if(split):
                [g.append(sorting_dict[k]["group"]) for k in refs]
                t = dict()
                [t.update({i:[n[0]]}) for i in set(g)]
                [t[g[i-1]].append(a) for i,a in enumerate(n) if i != 0]
                self.transfers = t
            else:
                self.transfers = {"all": n}
        return
    
    def calculate_transfer_volume(self, stock_conc, assay_conc):
        if(not stock_conc or not assay_conc) or (float(stock_conc) <= 0 or float(assay_conc) <= 0):
            raise Exception("Argument Error: Arguments 'stock_conc' and 'assay_conc' bust be greater than 0")
        if(self.assay_volume <= 0):
            raise Exception("Calculation Error: Assay Volume must be set before transfer volumes can be calulated from concentrations")
        vol = float(assay_conc) * float(self.assay_volume) / float(stock_conc) * 1000 * self.factor
        return 2.5 * round(vol/2.5, 0)
    
    def get_max_volume(self, factor=1):
        max_vol = 0.0
        max_combination = None
        for comb in self.clist:
            comb_vol = 0.0
            for c in comb:
                if c not in self.assay_concentrations:
                    comb_vol += self.transfer_vol
                else:
                    stock = self.platemap.find(c)[0][2]['conc']
                    assay = self.assay_concentrations[c]
                    comb_vol += self.calculate_transfer_volume(stock, assay)
            if comb_vol > max_vol:
                max_vol = comb_vol
                max_combination = ",".join(comb)
        return (2.5 * round(max_vol/2.5, 0), max_combination)

    def create_transfers(self, scale_factor=1):
        self.factor = scale_factor
        if(self.platemap is not None):
            max_vol = self.get_max_volume()[0]
            for combination in self.clist:
                [dest_plt, dest_well] = self.find_next_dest()
                [dest_row, dest_col] = self.destinations[dest_plt][dest_well]['coord']
                sources = list()
                running_vol = 0
                for compound in combination:
                    # Check that the compound is in the source plates
                    if(compound in self.platemap.get_all_compounds()):
                        if("transfers" not in self.destinations[dest_plt][dest_well]):
                            self.destinations[dest_plt][dest_well]["transfers"] = list()
                            self.destinations[dest_plt][dest_well]["mapping"] = list()
                        # Get the location(s) of this compound on all sources
                        loc = self.platemap.find(compound)
                        if(len(loc) > 1):
                            # Set the location to use based on lowest usage
                            # TODO: Is this a good idea??  Maybe check if its on the last source plate...
                            min_use = min([c[1]["usage"] for c in loc])
                            loc = [c for c in loc if c[1]['usage'] == min_use][0]
                        else:
                            loc = loc[0]
                        # Parse the location of the compound source
                        row = loc[2]["location"][0]
                        col = loc[2]["location"][1]
                        src = loc[0]
                        cid = loc[1]
                        conc = loc[2]["conc"]
                        # Store the source plate
                        sources.append(src)
                        # Calculate transfer volume
                        if(cid not in self.assay_concentrations):
                            # There is no assay concentration for this substance, use global volume
                            if(self.transfer_vol <= 0):
                                warnings.warn("Transfer volume used for {0} is 0".format(str(cid)))
                            vol = self.transfer_vol
                        elif(cid in self.assay_concentrations):
                            vol = self.calculate_transfer_volume(conc, self.assay_concentrations[cid])
                        running_vol += vol
                        # Save the transfer details
                        note = loc[1]
                        trans_str = self.format_transfer(src, row, col, dest_plt, dest_row, dest_col, vol, note)
                        if trans_str is not None:
                            if conc and vol and self.assay_volume > 0:
                                assay_conc = float(conc) * float(vol) / (self.assay_volume * 1000) * 1000 / self.factor
                            else:
                                assay_conc = 0
                            self.transfers["all"].append(trans_str)
                            self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
                            self.destinations[dest_plt][dest_well]["mapping"].append([cid, assay_conc])
                # Set up backfills for this well if needed
                if(running_vol < max_vol) and self.platemap.has_backfills():
                    backfill_vol = str( 2.5 * round(float((max_vol-running_vol))/2.5))
                    # Format of well: (plt, well, {location: [r,c], usage:0})
                    well = self.get_next_backfill()
                    if well is not None:
                        src = well[0]
                        row = well[2]["location"][0]
                        col = well[2]["location"][1]
                        trans_str = self.format_transfer(src, row, col, dest_plt, dest_row, dest_col, backfill_vol, "Backfill")
                        if trans_str is not None:
                            self.transfers["all"].append(trans_str)
                            self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
            # Set up the control transfers
            if(self.platemap.has_controls()):
                # Format of controls: (plt, name, {location: [r,c], times_used:16, volume:100, usage:0})
                controls = self.platemap.get_control_wells()
                for compound in controls:
                    # Set up a transfer for each time the control is to be used
                    for _ in range(0,compound[2]["times_used"]):
                        [dest_plt, dest_well] = self.find_next_ctrl()
                        [dest_row, dest_col] = self.destinations[dest_plt][dest_well]['coord']
                        if("transfers" not in self.destinations[dest_plt][dest_well]):
                                self.destinations[dest_plt][dest_well]["transfers"] = list()
                                #self.destinations[dest_plt][dest_well]["mapping"] = list()
                        row = compound[2]["location"][0]
                        col = compound[2]["location"][1]
                        src = compound[0]
                        ctl_vol = compound[2]["volume"]
                        note = compound[1]
                        trans_str = self.format_transfer(src, row, col, dest_plt, dest_row, dest_col, str(ctl_vol), note)
                        if trans_str is not None:
                            self.transfers["all"].append(trans_str)
                            self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
                            # self.destinations[dest_plt][dest_well]["mapping"].append([note, self.assay_concentrations[cid]])
                        # Setup a backfill if the control is below the level of combinations
                        if(ctl_vol < max_vol) and self.platemap.has_backfills():
                            backfill_vol = max_vol-ctl_vol
                            # Format of well: (plt, well, {location: [r,c], usage:0})
                            well = self.get_next_backfill()
                            if well is not None:
                                src = well[0]
                                row = well[2]["location"][0]
                                col = well[2]["location"][1]
                                trans_str = self.format_transfer(src, row, col, dest_plt, dest_row, dest_col, backfill_vol, "backfill")
                                if trans_str is not None:
                                    self.transfers["all"].append(trans_str)
                                    self.destinations[dest_plt][dest_well]["transfers"].append(trans_str)
            print(" * Saved " + str(len(self.transfers["all"])) + " transfers")
            print("    * Maximum substance volume was " + str(max_vol))
        return
    
    def print_transfers(self):
        print("".join(["{0}: {1}".format(i, j) for i in self.transfers for j in self.transfers[i]]))

    def save_transfers(self, saveas):
        if(saveas[-4:].lower() != ".csv"):
            saveas = saveas + ".csv"
        if(not path.dirname(saveas)):
            saveas = path.join(os.getcwd(), saveas)
        if(not path.exists(path.dirname(saveas))):
            raise Exception("Invalid Save Path: The directory " + path.dirname(saveas) + "does not exist")
        if(len(self.transfers) >= 1):
            for g in self.transfers:
                if(g == "all"):
                    new_saveas = saveas
                else:
                    new_saveas = path.join(path.dirname(saveas), ("{0}_{1}".format(g,path.basename(saveas))))
                with open(new_saveas, 'w') as output:
                    output.writelines(self.transfers[g])
                if(os.path.exists(saveas)):
                    print(" * Transfer list saved to: " + saveas)
        return

    def create_cmt_header(self):
        # Update the header with actual values
            params = "Combinations: " + str(len(self.clist)) + " | Default Volume: " + str(self.transfer_vol) + "nl"
            self.map_header2 = self.map_header2.replace("<MAPPING_PARAMETERS>", params)
            self.map_header3 = self.map_header3.replace("<ROWS>", str(self.plate_dims[self.plt_format][0]))
            self.map_header3 = self.map_header3.replace("<COLUMNS>", str(self.plate_dims[self.plt_format][1]))
            content = [self.map_header1, self.map_header2, self.map_header3, self.map_header4, self.map_header5]
            return content
    
    def create_mapping_line(self, line, mapping):
        if not line:
            raise Exception("Invalid Argument: line must be supplied as a string")
        if not mapping:
            raise Exception("Invalid Argument: mapping must be supplied as a list")
        for i in range(3):
            if len(mapping) >= (i+1):
                line = line.replace("<ID" + str(i+1) + ">", str(mapping[i][0]))
                # Convert the concentration to uM and add to CMT line
                line = line.replace("<CONC" + str(i+1) + ">", str(mapping[i][1]*1000))
            else:
                line = line.replace("<ID" + str(i+1) + ">", "")
                line = line.replace("<CONC" + str(i+1) + ">", "")
        return line

    # TODO: Add support for replicates in the CMT file
    def save_cmt(self, saveas, replicates=1):
        if(saveas[-4:].lower() != ".cmt"):
            saveas = saveas + ".cmt"
        if(not path.dirname(saveas)):
            saveas = path.join(os.getcwd(), saveas)
        if(not path.exists(path.dirname(saveas))):
            raise Exception("Invalid Save Path: The directory " + path.dirname(saveas) + "does not exist")
        if(len(self.destinations) >= 1):
            content = self.create_cmt_header()
            destination_table = set()
            # Iterate over destinations and add mapped transfers to the content
            for p in self.destinations:
                for w in self.destinations[p]:
                    if "mapping" in self.destinations[p][w] and \
                       len(self.destinations[p][w]["mapping"]) > 0:
                        (_, [row, col]) = parse_well_alpha(w)
                        line = self.map_tmplt.replace("DEST_NAME", p)
                        line = line.replace("<ROW>", str(row))
                        line = line.replace("<COL>", str(col))
                        try:
                            line = self.create_mapping_line(line, self.destinations[p][w]["mapping"])
                        except:
                            print("Exception: create_mapping_line error")
                            print("P: " + p + "  W: " + w)
                            print("Line: " + line)
                            print("Mapping: " + ",".join(self.destinations[p][w]["mapping"]))
                        if(replicates > 1):
                            for r in range(replicates):
                                rep_name =  p + "_" + list(string.ascii_uppercase)[r]
                                destination_table.add(rep_name + ",\n")
                                content.append(line.replace(p, rep_name))
                        else:
                            destination_table.add(p + ",\n")
                            content.append(line)
            with open(saveas, 'w') as output:
                output.writelines(content)
            # Write the destinations table to a file
            destinations_file = saveas.replace(".cmt", "_Destinations.csv")
            with open(destinations_file, 'w') as dest_table:
                dest_table.writelines(destination_table)
            if(os.path.exists(saveas) and os.path.exists(destinations_file)):
                print(" * Screener *.cmt saved to: " + saveas)
                print(" * Destination Plate List saved to: " + destinations_file)
        return
