from os import path
import string, warnings


class Platemap(object):
    wells = dict()

    def __init__(self, filepath, file_format="basic"):
        raise_warning = False
        # Validate file_format
        if(file_format not in ["basic", "mosaic"]):
            raise Exception("Argument Error: Argument file_format must be one of 'basic' or 'mosaic'")
        # Import the plate map
        if(path.exists(filepath)):
            with open(filepath, 'r') as map_file:
                next(map_file)
                for line in map_file:
                    if(file_format == "basic"):
                        [cmpd, row, col] = line.strip().split(",")
                    if(file_format == "mosaic"):
                        [cmpd, well] = line.strip().split("\t")[7:9]
                        row = str(string.ascii_uppercase.find(well[0])+1)
                        col = well[1:3]
                    if(cmpd not in self.wells):
                        self.wells[cmpd] = [row, col]
                    else:
                        raise_warning = True
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

    def __init__(self, combine_file=None, map_file=None, volume=None):
        # Raise Exception if one type of file is not supplied
        if(combine_file is None and map_file is None):
            raise Exception("Missing Argument: Combinations class must be initialized with combine_file and/or map_file")
        # Set the transfer volume if a value is supplied
        if(volume is not None):
            self.transfer_vol = str(2.5 * round(float(volume)/2.5))
        # Set the transfer file header as the first element of the transfer list
        self.transfers.append(self.trns_header)
        # Load the platemap file data if a filepath was supplied
        if(map_file is not None):
            self.load_platemap(map_file)
        # Load the combination matrix if a filepath was supplied
        #  --> Keep this to support manually curating combinations if all possible 
        #      combinations are not desired
        if(combine_file is not None and path.exists(combine_file)):
            with open(combine_file, 'r') as combine:
                next(combine)
                for line in combine:
                    [cpd1, cpd2, cpd3] = line.strip().split(",")
                    temp = [cpd1]
                    if cpd2 not in ["", "-"]:
                        temp.append(cpd2)
                    if cpd3 not in ["", "-"]:
                        temp.append(cpd3)
                    self.clist.append(temp)
        # Set combination list as all possible combinations if a combination matrix
        # was not supplied and the platemap was supplied 
        elif(self.platemap is not None):
            cmpds = [name for name in self.platemap.wells]
            self.clist = self.generate_combinations(cmpds)

    def generate_combinations(self, compounds):
        combination_list = []
        if(compounds is not None and len(compounds) > 0):
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
        row = 1
        while row <= 16:
            col = 1
            while col <= 24:
                name = string.ascii_uppercase[row-1] + ("0" + str(col))[-2:]
                coord = [row, col]
                wells[name] = {"coord": coord}
                col += 1
            row += 1
        self.destinations["destination"+str(len(self.destinations)+1)] = wells
        return

    def load_platemap(self, filepath):
        if(filepath is not None and path.exists(filepath)):
            self.platemap = Platemap(filepath)
        return

    def find_next_dest(self):
        empty_wells = len([w for p in self.destinations for w in self.destinations[p] if "transfers" not in self.destinations[p][w]])
        if(len(self.destinations) == 0 or empty_wells == 0):
            self.add_empty_plate()
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
                             
    def save_transfers(self, saveas):
        if(len(self.transfers) > 1):
            with open(saveas, 'w') as output:
                output.writelines(self.transfers)
        return

