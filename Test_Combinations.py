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
        Combinations.Platemap.wells = dict()
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
    



class Combinations_TestingMethods(unittest.TestCase):
   
    def setUp(self):
        self.mapfile = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\Platemap.csv"
        self.combine_file = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder\\Combination Template.csv"
        self.wrkdir = "C:\\Users\\dcurrier\\OneDrive - St. Jude Children's Research Hospital\\Codes\\Python\\Echo Combination Builder"
        return

    def tearDown(self):
        Combinations.Combinations.clist = list()
        Combinations.Combinations.platemap = None
        Combinations.Combinations.transfers = list()
        Combinations.Combinations.destinations = dict()
        Combinations.Combinations.transfer_vol = "0.0"
        Combinations.Platemap.wells = dict()
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
    
    def test_05_Combinations_build_combination_matrix(self):
        test = Combinations.Combinations()
        cmpd_list = ["cmpd1", "cmpd2", "cmpd3"]
        combine_list = test.build_combination_matrix(cmpd_list)
        self.assertEqual(7, len(combine_list))
        self.assertIn([cmpd_list[0]], combine_list)
        self.assertIn([cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[1],cmpd_list[2]], combine_list)
        self.assertIn([cmpd_list[0],cmpd_list[1],cmpd_list[2]], combine_list)
        return
    
    def test_06_Combinations_generate_combinations(self):
        test = Combinations.Combinations()
        test.load_platemap(self.mapfile)
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        return

    def test_09_Combinations_add_empty_plate(self):
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
    
    def test_10_Combinations_find_next_dest(self):
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
    
    def test_11_Combinations_format_transfer(self):
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

    def test_12_Combinations_create_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Create the transfer list
        self.assertEqual(1, len(test.transfers))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers))
        self.assertEqual(377, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        return

    def test_13_Combinations_print_transfers(self):
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
        self.assertIn("source1,2,1,destination1,3,1,0.0", capturedOutput.getvalue())
        self.assertIn("source1,3,1,destination1,7,1,0.0", capturedOutput.getvalue())
        return

    def test_14_Combinations_save_transfers(self):
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
        return


