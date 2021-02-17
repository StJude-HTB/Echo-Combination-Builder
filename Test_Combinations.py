import Combinations
import unittest, os, json, requests, io, warnings
import sys
if sys.version_info[0] < 3:
    import mock
else:
    from unittest import mock

class Platemap_TestingMethods(unittest.TestCase):
    def setUp(self):
        self.mapfile = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\Platemap.csv"
        self.mosaicfile = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\PlateSummary.txt"
        self.echofile = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\ECHO CSV.csv"
        warnings.simplefilter('ignore', category=UserWarning)

        return

    def tearDown(self):
        # Clear the Platemap object
        Combinations.Platemap.wells = dict()
        Combinations.Platemap.backfill = dict()
        Combinations.Platemap.controls = dict()
        # Clear the other Combinations attributes
        Combinations.Combinations.clist = list()
        Combinations.Combinations.platemap = None
        Combinations.Combinations.transfers = list()
        Combinations.Combinations.destinations = dict()
        Combinations.Combinations.used_backfills = list()
        Combinations.Combinations.control_wells = dict()
        Combinations.Combinations.transfer_vol = "0.0"
        Combinations.Combinations.plt_format = 384
        return
    
    def test_00_TestEngineStarts(self):
        self.assertEqual(0, 0)
        return
    
    def test_01_Platemap_Initializes_with_basic_file(self):
        test = Combinations.Platemap(self.mapfile)
        self.assertIsNotNone(test.wells)
        self.assertEqual(3, len(test.wells))
        self.assertIn("Dasatinib", test.wells)
        self.assertIn("Bortezomib", test.wells)
        self.assertIn("Topotecan", test.wells)
        self.assertEqual(2, len(test.wells["Dasatinib"]))
        self.assertEqual(2, len(test.wells["Bortezomib"]))
        self.assertEqual(2, len(test.wells["Topotecan"]))
        return
    
    def test_02_Platemap_Initializes_with_mosaic_file(self):
        test = Combinations.Platemap(self.mosaicfile)
        self.assertIsNotNone(test.wells)
        self.assertEqual(16, len(test.wells))
        self.assertIn("SJ000312343-2", test.wells)
        self.assertIn("SJ000312327-8", test.wells)
        self.assertIn("SJ000982892-2", test.wells)
        self.assertEqual(2, len(test.wells["SJ000312343-2"]))
        self.assertEqual(2, len(test.wells["SJ000312327-8"]))
        self.assertEqual(2, len(test.wells["SJ000982892-2"]))
        return
    
    def test_03_Platemap_Initializes_raises_warning(self):
        self.assertWarns(UserWarning, Combinations.Platemap, self.mosaicfile)
        return
    
    def test_03_Platemap_Initializes_raises_exception(self):
        self.assertRaises(Exception, Combinations.Platemap, self.echofile)
        return
    
    def test_04_Platemap_parse_well_alpha(self):
        test = Combinations.Platemap(self.mapfile)
        self.assertIsNotNone(test.wells)
        # Test the method
        well = test.parse_well_alpha("A01")
        self.assertEqual(("A01", [1,1]), well)
        well = test.parse_well_alpha("A24")
        self.assertEqual(("A24", [1,24]), well)
        well = test.parse_well_alpha("P01")
        self.assertEqual(("P01", [16,1]), well)
        well = test.parse_well_alpha("P24")
        self.assertEqual(("P24", [16,24]), well)
        well = test.parse_well_alpha("I12")
        self.assertEqual(("I12", [9,12]), well)
        # Test for exception
        self.assertRaises(Exception, test.parse_well_alpha, [1,1])
        return
    
    def test_05_Platemap_parse_well_coord(self):
        test = Combinations.Platemap(self.mapfile)
        self.assertIsNotNone(test.wells)
        # Test the method
        well = test.parse_well_coord([1,1])
        self.assertEqual("A01", well)
        well = test.parse_well_coord([1,24])
        self.assertEqual("A24", well)
        well = test.parse_well_coord([16,1])
        self.assertEqual("P01", well)
        well = test.parse_well_coord([16,24])
        self.assertEqual("P24", well)
        well = test.parse_well_coord([9,12])
        self.assertEqual("I12", well)
        # Test for exception
        self.assertRaises(Exception, test.parse_well_coord, "A01")
        return
    
    def test_06_Platemap_generate_well_range(self):
        test = Combinations.Platemap(self.mapfile)
        self.assertIsNotNone(test.wells)
        # Try something simple
        wells = test.generate_well_range("A01", "B02")
        self.assertEqual(4, len(wells))
        self.assertIn(("A01", [1,1]), wells)
        self.assertIn(("A02", [1,2]), wells)
        self.assertIn(("B01", [2,1]), wells)
        self.assertIn(("B02", [2,2]), wells)
        # Try something longer
        wells = test.generate_well_range("A10", "P12")
        self.assertEqual(16*3, len(wells))
        self.assertIn(("A10", [1,10]), wells)
        self.assertIn(("P12", [16,12]), wells)
        self.assertIn(("D11", [4,11]), wells)
        self.assertIn(("K12", [11,12]), wells)
        # Try putting them in backwards
        wells = test.generate_well_range("P12", "A10")
        self.assertEqual(16*3, len(wells))
        self.assertIn(("A10", [1,10]), wells)
        self.assertIn(("P12", [16,12]), wells)
        self.assertIn(("D11", [4,11]), wells)
        self.assertIn(("K12", [11,12]), wells)
        # Try a single well
        wells = test.generate_well_range("P12", "P12")
        self.assertEqual(1, len(wells))
        self.assertIn(("P12", [16,12]), wells)
        return
    
    def test_07_Platemap_set_backfill_wells(self):
        test = Combinations.Platemap(self.mapfile)
        self.assertIsNotNone(test.wells)
        # Try a short list
        test.set_backfill_wells(["A01", "A02", "A03"])
        self.assertIn("A01", test.backfill)
        self.assertEqual([1,1], test.backfill["A01"])
        self.assertIn("A02", test.backfill)
        self.assertEqual([1,2], test.backfill["A02"])
        self.assertIn("A03", test.backfill)
        self.assertEqual([1,3], test.backfill["A03"])
        return
    
    def test_08_Platemap_set_controls(self):
        test = Combinations.Platemap(self.mosaicfile)
        self.assertIsNotNone(test.wells)
        self.assertEqual(16, len(test.wells))
        # Try adding a couple of compounds to controls
        controls = ["SJ000285696-8", "SJ000312317-9"]
        test.set_controls(controls, [50, 82.5])
        self.assertEqual(2, len(test.controls))
        self.assertEqual(14, len(test.wells))
        self.assertIn("SJ000285696-8", test.controls)
        self.assertIn("location", test.controls["SJ000285696-8"])
        self.assertEqual(["16","01"], test.controls["SJ000285696-8"]["location"])
        self.assertIn("times_used", test.controls["SJ000285696-8"])
        self.assertEqual(16, test.controls["SJ000285696-8"]["times_used"])
        self.assertIn("volume", test.controls["SJ000285696-8"])
        self.assertEqual(50, test.controls["SJ000285696-8"]["volume"])
        self.assertIn("SJ000312317-9", test.controls)
        self.assertIn("location", test.controls["SJ000312317-9"])
        self.assertEqual(["15","01"], test.controls["SJ000312317-9"]["location"])
        self.assertIn("times_used", test.controls["SJ000312317-9"])
        self.assertEqual(16, test.controls["SJ000312317-9"]["times_used"])
        self.assertIn("volume", test.controls["SJ000312317-9"])
        self.assertEqual(82.5, test.controls["SJ000312317-9"]["volume"])
        # Test that supplying controls not in the wells list raises and exception
        self.assertRaises(Exception, test.set_controls, ["ABCDEFG"], [50])
        # Test that supplying different numbers of compounds and volumes raises and exception
        controls = ["SJ000285696-8", "SJ000312317-9", "SJ000541096-3"]
        self.assertRaises(Exception, test.set_controls, controls, [50, 82.5])
        return


class Combinations_TestingMethods(unittest.TestCase):
   
    def setUp(self):
        self.mapfile = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\Platemap.csv"
        self.combine_file = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\Combination Template.csv"
        self.wrkdir = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder"
        return

    def tearDown(self):
        # Clear the Platemap object
        Combinations.Platemap.wells = dict()
        Combinations.Platemap.backfill = dict()
        Combinations.Platemap.controls = dict()
        # Clear the other Combinations attributes
        Combinations.Combinations.clist = list()
        Combinations.Combinations.platemap = None
        Combinations.Combinations.transfers = list()
        Combinations.Combinations.destinations = dict()
        Combinations.Combinations.used_backfills = list()
        Combinations.Combinations.control_wells = dict()
        Combinations.Combinations.transfer_vol = "0.0"
        Combinations.Combinations.plt_format = 384
        return
    
    def test_00_TestEngineStarts(self):
        self.assertEqual(0, 0)
        return

    def test_01_Combinations_Initializes(self):
        test = Combinations.Combinations()
        self.assertIsNone(test.platemap)
        self.assertEqual(0, len(test.clist))
        self.assertEqual(1, len(test.transfers))
        self.assertEqual(0, len(test.destinations))
        self.assertEqual("0.0", test.transfer_vol)
        self.assertEqual(3, len(test.plate_dims))
        self.assertEqual(384, test.plt_format)
        self.assertIsNotNone(test.trns_str_tmplt)
        self.assertIsNotNone(test.trns_header)
        # Test setting a different plate format
        test = Combinations.Combinations(96)
        self.assertEqual(96, test.plt_format)
        test = Combinations.Combinations(1536)
        self.assertEqual(1536, test.plt_format)
        return
    
    def test_02_Combinations_load_platemap(self):
        test = Combinations.Combinations()
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        self.assertEqual(3, len(test.platemap.wells))
        return

    def test_03_Combinations_load_combinations(self):
        test = Combinations.Combinations()
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        # Now we can test the combinations load
        test.load_combinations(self.combine_file)
        self.assertIsNotNone(test.platemap)
        self.assertEqual(7, len(test.clist))
        return
    
    def test_04_Combinations_set_volume(self):
        test = Combinations.Combinations()
        # Test with a number that is not rounded
        test.set_volume(120)
        self.assertEqual("120.0", test.transfer_vol)
        # Test with a number that is rounded
        test.set_volume(122)
        self.assertEqual("122.5", test.transfer_vol)
        # Test with a number supplied as a string
        test.set_volume("122")
        self.assertEqual("122.5", test.transfer_vol)
        return
    
    def test_05_Combinations_reserve_control_wells(self):
        test = Combinations.Combinations()
        test.load_platemap(self.mapfile)
        # Make a list of wells
        ctrl_wells = ['A21', 'A22', 'A23', 'A24', 'B21', 'B22', 'B23', 'B24']
        # Test method
        self.assertEqual(0, len(test.control_wells))
        test.reserve_control_wells(ctrl_wells)
        self.assertEqual(len(ctrl_wells), len(test.control_wells))
        self.assertEqual([1,21], test.control_wells["A21"])
        self.assertEqual([1,24], test.control_wells["A24"])
        self.assertEqual([2,21], test.control_wells["B21"])
        self.assertEqual([1,24], test.control_wells["A24"])
        return

    def test_06_Combinations_generate_combinations(self):
        test = Combinations.Combinations()
        test.load_platemap(self.mapfile)
        test.generate_combinations(3)
        self.assertEqual(7, len(test.clist))
        return

    def test_07_Combinations_build_combination_matrix(self):
        # Test with nmax = 3
        test = Combinations.Combinations()
        cmpd_list = ["cmpd1", "cmpd2", "cmpd3"]
        combine_list = test.build_combination_matrix(cmpd_list, 3)
        self.assertEqual(7, len(combine_list))
        self.assertIn([cmpd_list[0]], combine_list)
        self.assertIn([cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1],cmpd_list[2]], combine_list)
        # Test with nmax = 2
        combine_list = test.build_combination_matrix(cmpd_list, 2)
        self.assertEqual(6, len(combine_list))
        self.assertIn([cmpd_list[0]], combine_list)
        self.assertIn([cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[2]], combine_list)
        # Test with nmax = 4
        cmpd_list = ["cmpd1", "cmpd2", "cmpd3", "cmpd4"]
        combine_list = test.build_combination_matrix(cmpd_list, 4)
        self.assertEqual(15, len(combine_list))
        self.assertIn([cmpd_list[0]], combine_list)
        self.assertIn([cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[2],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[2],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[2],cmpd_list[3]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1],cmpd_list[2],cmpd_list[3]], combine_list)
        return
    
    def test_08_Combinations_add_empty_plate(self):
        test = Combinations.Combinations()
        self.assertEqual(0, len(test.destinations))
        # Use default format -> 384
        test.add_empty_plate()
        self.assertEqual(1, len(test.destinations))
        self.assertIn("destination1", test.destinations)
        self.assertEqual(384, len(test.destinations["destination1"]))
        self.assertIn("A01", test.destinations["destination1"])
        self.assertIn("P24", test.destinations["destination1"])
        for w in test.destinations["destination1"]:
            well = test.destinations["destination1"][w]
            self.assertIn("coord", well)
            self.assertNotIn("transfers", well)
            self.assertEqual(2, len(well['coord']))
        # Reset and use 96 format
        test.plt_format = 96
        test.destinations = dict()
        test.add_empty_plate()
        self.assertEqual(1, len(test.destinations))
        self.assertIn("destination1", test.destinations)
        self.assertEqual(96, len(test.destinations["destination1"]))
        self.assertIn("A01", test.destinations["destination1"])
        self.assertIn("H12", test.destinations["destination1"])
        for w in test.destinations["destination1"]:
            well = test.destinations["destination1"][w]
            self.assertIn("coord", well)
            self.assertNotIn("transfers", well)
            self.assertEqual(2, len(well['coord']))
        # Reset and use 384 format
        test.plt_format = 384
        test.destinations = dict()
        test.add_empty_plate()
        self.assertEqual(1, len(test.destinations))
        self.assertIn("destination1", test.destinations)
        self.assertEqual(384, len(test.destinations["destination1"]))
        self.assertIn("A01", test.destinations["destination1"])
        self.assertIn("P24", test.destinations["destination1"])
        for w in test.destinations["destination1"]:
            well = test.destinations["destination1"][w]
            self.assertIn("coord", well)
            self.assertNotIn("transfers", well)
            self.assertEqual(2, len(well['coord']))
        # Reset and use 1536 format
        test.plt_format = 1536
        test.destinations = dict()
        test.add_empty_plate()
        self.assertEqual(1, len(test.destinations))
        self.assertIn("destination1", test.destinations)
        self.assertEqual(1536, len(test.destinations["destination1"]))
        self.assertIn("A01", test.destinations["destination1"])
        self.assertIn("AF48", test.destinations["destination1"])
        for w in test.destinations["destination1"]:
            well = test.destinations["destination1"][w]
            self.assertIn("coord", well)
            self.assertNotIn("transfers", well)
            self.assertEqual(2, len(well['coord']))
        return
    
    def test_09_Combinations_find_next_dest(self):
        test = Combinations.Combinations()
        self.assertEqual(0, len(test.destinations))
        next_well = test.find_next_dest()
        self.assertEqual(1, len(test.destinations))
        self.assertEqual(["destination1", "A01"], next_well)
        # Iteratively fill a well and test again
        while next_well[1] != "P24":
            prev_well = next_well[1]
            test.destinations[next_well[0]][next_well[1]]["transfers"] = []
            next_well = test.find_next_dest()
            self.assertEqual(1, len(test.destinations))
            self.assertEqual("destination1", next_well[0])
            self.assertNotEqual(prev_well, next_well[1])
        return
    
    def test_10_Combinations_get_next_backfill(self):
        test = Combinations.Combinations()
        # Test that method returns None with no platemap set
        well = test.get_next_backfill()
        self.assertIsNone(well)
        # Set a platemap and add a backfill well
        test.load_platemap(self.mapfile)
        self.assertEqual(3, len(test.platemap.wells))
        test.platemap.set_backfill_wells(["P20", "P21", "P22", "P23", "P24"])
        self.assertEqual(5, len(test.platemap.backfill))
        well = test.get_next_backfill()
        self.assertEqual([16,20], well)
        self.assertTrue("P20" in test.used_backfills)
        self.assertEqual(1, len(test.used_backfills))
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual([16,21], well)
        self.assertTrue("P21" in test.used_backfills)
        self.assertEqual(2, len(test.used_backfills))
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual([16,22], well)
        self.assertTrue("P22" in test.used_backfills)
        self.assertEqual(3, len(test.used_backfills))
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual([16,23], well)
        self.assertTrue("P23" in test.used_backfills)
        self.assertEqual(4, len(test.used_backfills))
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual([16,24], well)
        self.assertTrue("P24" in test.used_backfills)
        self.assertEqual(5, len(test.used_backfills))
        return
    
    def test_11_Combinations_sort_wells(self):
        test = Combinations.Combinations()
        # Setup a list of wells to test with
        wells = ['A21', 'A22', 'A23', 'A24', 'B21', 'B22', 'B23', 'B24']
        # Test column mode first
        sort = test.sort_wells(wells, "column")
        column_sorted = ['A21', 'B21', 'A22', 'B22', 'A23', 'B23', 'A24', 'B24']
        self.assertEqual(column_sorted, sort)
        # Test row mode next - use column sorted list as input
        sort = test.sort_wells(column_sorted, "row")
        self.assertEqual(wells, sort)
        # Test for exception
        self.assertRaises(Exception, test.sort_wells, wells, "random")
        return
    
    def test_12_Combinations_find_next_ctrl(self):
        test = Combinations.Combinations()
        test.load_platemap(self.mapfile)
        # Make a list of wells
        ctrl_wells = ['A21', 'A22', 'A23', 'A24', 'B21', 'B22', 'B23', 'B24']
        # Test method
        self.assertEqual(0, len(test.control_wells))
        test.reserve_control_wells(ctrl_wells)
        self.assertEqual(len(ctrl_wells), len(test.control_wells))
        # Use default fill_mode
        well = test.find_next_ctrl()
        self.assertEqual(["destination1", "A21"], well)
        test.destinations["destination1"]["A21"]["transfers"] = ""
        well = test.find_next_ctrl()
        self.assertEqual(["destination1", "B21"], well)
        test.destinations["destination1"]["B21"]["transfers"] = ""
        well = test.find_next_ctrl()
        self.assertEqual(["destination1", "A22"], well)
        test.destinations["destination1"]["A22"]["transfers"] = ""
        well = test.find_next_ctrl()
        self.assertEqual(["destination1", "B22"], well)
        test.destinations["destination1"]["B22"]["transfers"] = ""
        # Reset
        test.destinations = dict()
        # Test with row fill_mode
        well = test.find_next_ctrl("row")
        self.assertEqual(["destination1", "A21"], well)
        test.destinations["destination1"]["A21"]["transfers"] = ""
        well = test.find_next_ctrl("row")
        self.assertEqual(["destination1", "A22"], well)
        test.destinations["destination1"]["A22"]["transfers"] = ""
        well = test.find_next_ctrl("row")
        self.assertEqual(["destination1", "A23"], well)
        test.destinations["destination1"]["A23"]["transfers"] = ""
        well = test.find_next_ctrl("row")
        self.assertEqual(["destination1", "A24"], well)
        test.destinations["destination1"]["A24"]["transfers"] = ""
        well = test.find_next_ctrl("row")
        self.assertEqual(["destination1", "B21"], well)
        test.destinations["destination1"]["B21"]["transfers"] = ""
        # Reset
        test.destinations = dict()
        # Test with column fill_mode
        well = test.find_next_ctrl("column")
        self.assertEqual(["destination1", "A21"], well)
        test.destinations["destination1"]["A21"]["transfers"] = ""
        well = test.find_next_ctrl("column")
        self.assertEqual(["destination1", "B21"], well)
        test.destinations["destination1"]["B21"]["transfers"] = ""
        well = test.find_next_ctrl("column")
        self.assertEqual(["destination1", "A22"], well)
        test.destinations["destination1"]["A22"]["transfers"] = ""
        well = test.find_next_ctrl("column")
        self.assertEqual(["destination1", "B22"], well)
        test.destinations["destination1"]["B22"]["transfers"] = ""
        return

    def test_13_Combinations_format_transfer(self):
        test = Combinations.Combinations()
        # Test 1
        test_str = test.format_transfer("Source1", "1", "1", "Destination1", "1", "1", "100")
        expected_str = "Source1,1,1,Destination1,1,1,100\n"
        self.assertEqual(expected_str, test_str)
        # Test 2
        test_str = test.format_transfer("Source1", "2", "1", "Destination1", "2", "1", "100")
        expected_str = "Source1,1,2,Destination1,1,2,100\n"
        self.assertEqual(expected_str, test_str)
        # Test 3
        test_str = test.format_transfer("Source1", "1", "3", "Destination1", "3", "1", "150")
        expected_str = "Source1,3,1,Destination1,1,3,150\n"
        self.assertEqual(expected_str, test_str)
        return
    
    def test_14_Combinations_sort_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        self.assertIsNotNone(test.platemap.wells)
        self.assertTrue(len(test.platemap.wells) > 0)
        print(test.platemap.backfill)
        self.assertFalse(len(test.platemap.backfill) > 0)
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Create the transfer list
        self.assertEqual(1, len(test.transfers))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers))
        # Add a second group that goes to a second destination
        d2 = [x.replace("destination1", "destination2") for x in test.transfers if test.trns_header not in x]
        test.transfers.extend(d2)
        # Check that they are not sorted
        self.assertEqual(test.transfers[1], "source1,1,1,destination1,1,1,0.0\n")
        self.assertEqual(test.transfers[2], "source1,2,1,destination1,2,1,0.0\n")
        self.assertEqual(test.transfers[3], "source1,3,1,destination1,3,1,0.0\n")
        self.assertEqual(test.transfers[11], "source1,2,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[12], "source1,3,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[13], "source1,1,1,destination2,1,1,0.0\n")
        self.assertEqual(test.transfers[14], "source1,2,1,destination2,2,1,0.0\n")
        self.assertEqual(test.transfers[15], "source1,3,1,destination2,3,1,0.0\n")
        self.assertEqual(test.transfers[23], "source1,2,1,destination2,7,1,0.0\n")
        self.assertEqual(test.transfers[24], "source1,3,1,destination2,7,1,0.0\n")
        # Sort by source -> default
        test.sort_transfers()
        self.assertEqual(test.transfers[1], "source1,1,1,destination1,1,1,0.0\n")
        self.assertEqual(test.transfers[2], "source1,1,1,destination1,4,1,0.0\n")
        self.assertEqual(test.transfers[3], "source1,1,1,destination1,5,1,0.0\n")
        self.assertEqual(test.transfers[11], "source1,3,1,destination1,6,1,0.0\n")
        self.assertEqual(test.transfers[12], "source1,3,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[13], "source1,1,1,destination2,1,1,0.0\n")
        self.assertEqual(test.transfers[14], "source1,1,1,destination2,4,1,0.0\n")
        self.assertEqual(test.transfers[15], "source1,1,1,destination2,5,1,0.0\n")
        self.assertEqual(test.transfers[23], "source1,3,1,destination2,6,1,0.0\n")
        self.assertEqual(test.transfers[24], "source1,3,1,destination2,7,1,0.0\n")
        # Sort by destination
        test.sort_transfers("destination")
        self.assertEqual(test.transfers[1], "source1,1,1,destination1,1,1,0.0\n")
        self.assertEqual(test.transfers[2], "source1,2,1,destination1,2,1,0.0\n")
        self.assertEqual(test.transfers[3], "source1,3,1,destination1,3,1,0.0\n")
        self.assertEqual(test.transfers[11], "source1,2,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[12], "source1,3,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[13], "source1,1,1,destination2,1,1,0.0\n")
        self.assertEqual(test.transfers[14], "source1,2,1,destination2,2,1,0.0\n")
        self.assertEqual(test.transfers[15], "source1,3,1,destination2,3,1,0.0\n")
        self.assertEqual(test.transfers[23], "source1,2,1,destination2,7,1,0.0\n")
        self.assertEqual(test.transfers[24], "source1,3,1,destination2,7,1,0.0\n")
        # Sort by source explicitly
        test.sort_transfers("source")
        self.assertEqual(test.transfers[1], "source1,1,1,destination1,1,1,0.0\n")
        self.assertEqual(test.transfers[2], "source1,1,1,destination1,4,1,0.0\n")
        self.assertEqual(test.transfers[3], "source1,1,1,destination1,5,1,0.0\n")
        self.assertEqual(test.transfers[11], "source1,3,1,destination1,6,1,0.0\n")
        self.assertEqual(test.transfers[12], "source1,3,1,destination1,7,1,0.0\n")
        self.assertEqual(test.transfers[13], "source1,1,1,destination2,1,1,0.0\n")
        self.assertEqual(test.transfers[14], "source1,1,1,destination2,4,1,0.0\n")
        self.assertEqual(test.transfers[15], "source1,1,1,destination2,5,1,0.0\n")
        self.assertEqual(test.transfers[23], "source1,3,1,destination2,6,1,0.0\n")
        self.assertEqual(test.transfers[24], "source1,3,1,destination2,7,1,0.0\n")
        return

    def test_15_Combinations_create_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Create the transfer list, without backfills
        self.assertEqual(1, len(test.transfers))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers))
        self.assertEqual(377, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        # Add some backfill wells and repeat with backfills
        test.transfers = [test.trns_header]
        test.destinations = dict()
        backfill_wells = test.platemap.generate_well_range("A21", "P24")
        test.platemap.set_backfill_wells([x[0] for x in backfill_wells])
        self.assertEqual(64, len(test.platemap.backfill))
        test.create_transfers()
        self.assertEqual(22, len(test.transfers))
        # Count wells that are not used ()
        self.assertEqual(377, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        # Add some controls and test again
        test.transfers = [test.trns_header]
        test.destinations = dict()
        test.reserve_control_wells(['A21', 'A22', 'A23', 'A24', 'B21', 'B22', 'B23', 'B24'])
        test.platemap.wells["Control1"] = [1,24]
        test.platemap.wells["Control2"] = [2,24]
        test.platemap.set_controls(["Control1", "Control2"], [125], 4)
        test.set_volume(100)
        test.create_transfers()
        self.assertEqual(38, len(test.transfers))
        # Count wells that are not used ()
        self.assertEqual(369, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        return
    
    def test_16_Combinations_print_transfers(self):
        # This test is based on:
        # https://stackoverflow.com/questions/33767627/python-write-unittest-for-console-print
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Set up transfers
        self.assertEqual(1, len(test.transfers))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers))
        # Capture the Output
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        # Run the method
        test.print_transfers()
        # Reset the stdout
        sys.stdout = sys.__stdout__
        self.assertIn("source1,1,1,destination1,1,1,0.0", capturedOutput.getvalue())
        self.assertIn("source1,2,1,destination1,2,1,0.0", capturedOutput.getvalue())
        self.assertIn("source1,3,1,destination1,7,1,0.0", capturedOutput.getvalue())
        return

    def test_17_Combinations_save_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Set up transfers
        self.assertEqual(1, len(test.transfers))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers))
        # Set an output filepath
        filepath = os.path.join(self.wrkdir, "TestCSV.csv")
        # Save the file
        test.save_transfers(filepath)
        self.assertTrue(os.path.exists(filepath))
        # Test contents
        with open(filepath, 'r') as csv:
            line = csv.readline()
            exp_header = "Source Barcode,Source Column,Source Row,Destination Barcode,Destination Column,Destination Row,Volume\n"
            self.assertEqual(exp_header, line)
            line_regex = r'[a-zA-Z0-9]+,[0-9]{1,2},[0-9]{1,2},[a-zA-Z0-9]+,[0-9]{1,2},[0-9]{1,2},[0-9]{1,3}.[0-9]?'
            line = csv.readline()
            while line:
                self.assertRegex(line, line_regex)
                line = csv.readline()
        # Delete test file
        os.remove(filepath)
        # Test with a filepath that does not have an extension
        # Save the file
        test.save_transfers(os.path.join(self.wrkdir, "TestCSV"))
        self.assertTrue(os.path.exists(filepath))
        # Delete test file
        os.remove(filepath)
        # Test with a bogus path
        self.assertRaises(Exception, test.save_transfers, os.path.join("C:\\Some\\bogus\\path", "TestCSV"))
        return



