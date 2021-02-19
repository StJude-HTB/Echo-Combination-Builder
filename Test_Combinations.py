import Combinations
import unittest, os, json, requests, io, warnings
import sys
if sys.version_info[0] < 3:
    import mock
else:
    from unittest import mock

class Standalone_Methods_TestingMethods(unittest.TestCase):
    def test_01_parse_well_alpha(self):
        # Test the method
        well = Combinations.parse_well_alpha("A01")
        self.assertEqual(("A01", [1,1]), well)
        well = Combinations.parse_well_alpha("A24")
        self.assertEqual(("A24", [1,24]), well)
        well = Combinations.parse_well_alpha("P01")
        self.assertEqual(("P01", [16,1]), well)
        well = Combinations.parse_well_alpha("P24")
        self.assertEqual(("P24", [16,24]), well)
        well = Combinations.parse_well_alpha("I12")
        self.assertEqual(("I12", [9,12]), well)
        # Test for exception
        self.assertRaises(Exception, Combinations.parse_well_alpha, [1,1])
        return
    
    def test_02_parse_well_coord(self):
        # Test the method
        well = Combinations.parse_well_coord([1,1])
        self.assertEqual("A01", well)
        well = Combinations.parse_well_coord([1,24])
        self.assertEqual("A24", well)
        well = Combinations.parse_well_coord([16,1])
        self.assertEqual("P01", well)
        well = Combinations.parse_well_coord([16,24])
        self.assertEqual("P24", well)
        well = Combinations.parse_well_coord([9,12])
        self.assertEqual("I12", well)
        # Test for exception
        self.assertRaises(Exception, Combinations.parse_well_coord, "A01")
        return
    
    def test_03_generate_well_range(self):
        # Try something simple
        wells = Combinations.generate_well_range("A01", "B02")
        self.assertEqual(4, len(wells))
        self.assertIn(("A01", [1,1]), wells)
        self.assertIn(("A02", [1,2]), wells)
        self.assertIn(("B01", [2,1]), wells)
        self.assertIn(("B02", [2,2]), wells)
        # Try something longer
        wells = Combinations.generate_well_range("A10", "P12")
        self.assertEqual(16*3, len(wells))
        self.assertIn(("A10", [1,10]), wells)
        self.assertIn(("P12", [16,12]), wells)
        self.assertIn(("D11", [4,11]), wells)
        self.assertIn(("K12", [11,12]), wells)
        # Try putting them in backwards
        wells = Combinations.generate_well_range("P12", "A10")
        self.assertEqual(16*3, len(wells))
        self.assertIn(("A10", [1,10]), wells)
        self.assertIn(("P12", [16,12]), wells)
        self.assertIn(("D11", [4,11]), wells)
        self.assertIn(("K12", [11,12]), wells)
        # Try a single well
        wells = Combinations.generate_well_range("P12", "P12")
        self.assertEqual(1, len(wells))
        self.assertIn(("P12", [16,12]), wells)
        return



class Platemap_TestingMethods(unittest.TestCase):
    
    def setUp(self):
        self.mapfile = "Test_Files\\Platemap.csv"
        self.combine_file = "Test_Files\\Combination Template.csv"
        self.wrkdir = "Test_Files\\Echo Combination Builder"
        self.mosaicfile = "Test_Files\\PlateSummary.txt"
        self.mosaicmulti = "Test_Files\\PlateSummary-Multi.txt"
        self.echofile = "Test_Files\\ECHO CSV.csv"
        warnings.simplefilter('ignore', category=UserWarning)
        return

    def tearDown(self):
        # Clear the Platemap object
        Combinations.Platemap.wells = dict()
        Combinations.Platemap.backfill = dict()
        Combinations.Platemap.controls = dict()
        # Clear the SourcePlates object
        Combinations.SourcePlates.plates = dict()
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
    
    def test_01_Platemap_Initializes(self):
        test = Combinations.Platemap()
        # Check wells
        self.assertIsNotNone(test.wells)
        self.assertEqual(0, len(test.wells))
        # Check backfill
        self.assertIsNotNone(test.backfill)
        self.assertEqual(0, len(test.backfill))
        # Check controls
        self.assertIsNotNone(test.controls)
        self.assertEqual(0, len(test.controls))
        return
    
    def test_03_Platemap_set_backfill_wells(self):
        test = Combinations.Platemap()
        self.assertIsNotNone(test.wells)
        # Try a short list
        test.set_backfill_wells(["A01", "A02", "A03"])
        self.assertIn("A01", test.backfill)
        self.assertEqual([1,1], test.backfill["A01"]["location"])
        self.assertEqual(0, test.backfill["A01"]["usage"])
        self.assertIn("A02", test.backfill)
        self.assertEqual([1,2], test.backfill["A02"]["location"])
        self.assertEqual(0, test.backfill["A02"]["usage"])
        self.assertIn("A03", test.backfill)
        self.assertEqual([1,3], test.backfill["A03"]["location"])
        self.assertEqual(0, test.backfill["A03"]["usage"])
        return
    
    def test_04_Platemap_set_controls(self):
        test = Combinations.Platemap()
        self.assertIsNotNone(test.wells)
        test.wells["SJ000312343-2"] = {'location':[1,1], 'usage':0}
        test.wells["SJ000285285-13"] = {'location':[2,1], 'usage':0}
        test.wells["SJ000285696-8"] = {'location':[16,1], 'usage':0}
        test.wells["SJ000312317-9"] = {'location':[15,1], 'usage':0}
        self.assertEqual(4, len(test.wells))
        # Try adding a couple of compounds to controls
        controls = ["SJ000285696-8", "SJ000312317-9"]
        test.set_controls(controls, [50, 82.5])
        self.assertEqual(2, len(test.controls))
        self.assertEqual(2, len(test.wells))
        # Check the first control
        self.assertIn("SJ000285696-8", test.controls)
        self.assertIn("location", test.controls["SJ000285696-8"])
        self.assertEqual([16,1], test.controls["SJ000285696-8"]["location"])
        self.assertIn("times_used", test.controls["SJ000285696-8"])
        self.assertEqual(16, test.controls["SJ000285696-8"]["times_used"])
        self.assertIn("volume", test.controls["SJ000285696-8"])
        self.assertEqual(50, test.controls["SJ000285696-8"]["volume"])
        # Check the second control
        self.assertIn("SJ000312317-9", test.controls)
        self.assertIn("location", test.controls["SJ000312317-9"])
        self.assertEqual([15,1], test.controls["SJ000312317-9"]["location"])
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


class SourcePlates_TestingMethods(unittest.TestCase):

    def setUp(self):
        self.mapfile = "Test_Files\\Platemap.csv"
        self.combine_file = "Test_Files\\Combination Template.csv"
        self.wrkdir = "Test_Files\\Echo Combination Builder"
        self.mosaicfile = "Test_Files\\PlateSummary.txt"
        self.mosaicmulti = "Test_Files\\PlateSummary-Multi.txt"
        self.echofile = "Test_Files\\ECHO CSV.csv"
        warnings.simplefilter('ignore', category=UserWarning)
        return

    def tearDown(self):
        # Clear the Platemap object
        Combinations.Platemap.wells = dict()
        Combinations.Platemap.backfill = dict()
        Combinations.Platemap.controls = dict()
        # Clear the SourcePlates object
        Combinations.SourcePlates.plates = dict()
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
    
    def test_01_SourcePlates_Initializes_with_basic_file(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertEqual(1, len(test.plates))
        self.assertIn("source1", test.plates)
        self.assertEqual(3, len(test.plates["source1"].wells))
        self.assertIn("Dasatinib", test.plates["source1"].wells)
        self.assertIn("Bortezomib", test.plates["source1"].wells)
        self.assertIn("Topotecan", test.plates["source1"].wells)
        # Check Dasatinib
        self.assertEqual(2, len(test.plates["source1"].wells["Dasatinib"]))
        self.assertIn("location", test.plates["source1"].wells["Dasatinib"])
        self.assertEqual(2, len(test.plates["source1"].wells["Dasatinib"]["location"]))
        self.assertIn("usage", test.plates["source1"].wells["Dasatinib"])
        self.assertEqual(0, test.plates["source1"].wells["Dasatinib"]["usage"])
        # Check Bortezomib
        self.assertEqual(2, len(test.plates["source1"].wells["Bortezomib"]))
        self.assertIn("location", test.plates["source1"].wells["Bortezomib"])
        self.assertEqual(2, len(test.plates["source1"].wells["Bortezomib"]["location"]))
        self.assertIn("usage", test.plates["source1"].wells["Bortezomib"])
        self.assertEqual(0, test.plates["source1"].wells["Bortezomib"]["usage"])
        # Check Topotecan
        self.assertEqual(2, len(test.plates["source1"].wells["Topotecan"]))
        self.assertIn("location", test.plates["source1"].wells["Topotecan"])
        self.assertEqual(2, len(test.plates["source1"].wells["Topotecan"]["location"]))
        self.assertIn("usage", test.plates["source1"].wells["Topotecan"])
        self.assertEqual(0, test.plates["source1"].wells["Topotecan"]["usage"])
        return
    
    def test_02_SourcePlates_Initializes_with_mosaic_file(self):
        test = Combinations.SourcePlates(self.mosaicfile)
        self.assertIsNotNone(test.plates)
        self.assertEqual(1, len(test.plates))
        self.assertIn("E3P00000776", test.plates)
        self.assertEqual(16, len(test.plates["E3P00000776"].wells))
        self.assertIn("SJ000312343-2", test.plates["E3P00000776"].wells)
        self.assertIn("SJ000312327-8", test.plates["E3P00000776"].wells)
        self.assertIn("SJ000982892-2", test.plates["E3P00000776"].wells)
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000312343-2"]))
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000312327-8"]))
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000982892-2"]))
        return
    
    def test_03_SourcePlates_Initializes_with_mosaic_file_multiple_sources(self):
        test = Combinations.SourcePlates(self.mosaicmulti)
        print(test.plates["E3P00000776"].wells)
        print(test.plates["E3P00000777"].wells)
        self.assertIsNotNone(test.plates)
        self.assertEqual(2, len(test.plates))
        self.assertIn("E3P00000776", test.plates)
        self.assertIn("E3P00000777", test.plates)
        # Check the loading of the first plate
        self.assertEqual(16, len(test.plates["E3P00000776"].wells))
        self.assertIn("SJ000312343-2", test.plates["E3P00000776"].wells)
        self.assertIn("SJ000312327-8", test.plates["E3P00000776"].wells)
        self.assertIn("SJ000982892-2", test.plates["E3P00000776"].wells)
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000312343-2"]))
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000312327-8"]))
        self.assertEqual(2, len(test.plates["E3P00000776"].wells["SJ000982892-2"]))
        # Check the loading of the second plate
        self.assertEqual(3, len(test.plates["E3P00000777"].wells))
        self.assertIn("SJ000312343-3", test.plates["E3P00000777"].wells)
        self.assertIn("SJ000285285-14", test.plates["E3P00000777"].wells)
        self.assertIn("SJ000312344-6", test.plates["E3P00000777"].wells)
        self.assertEqual(2, len(test.plates["E3P00000777"].wells["SJ000312343-3"]))
        self.assertEqual(2, len(test.plates["E3P00000777"].wells["SJ000285285-14"]))
        self.assertEqual(2, len(test.plates["E3P00000777"].wells["SJ000312344-6"]))
        return
    
    def test_04_SourcePlates_Initializes_raises_warning(self):
        self.assertWarns(UserWarning, Combinations.SourcePlates, self.mosaicfile)
        return
    
    def test_05_SourcePlates_Initializes_raises_exception(self):
        self.assertRaises(Exception, Combinations.SourcePlates, self.echofile)
        return
    
    def test_06_SourcePlates_get_all_compounds(self):
        test = Combinations.SourcePlates(self.mosaicmulti)
        self.assertIsNotNone(test.plates)
        self.assertEqual(2, len(test.plates))
        # Test method
        actual = test.get_all_compounds()
        self.assertEqual(19, len(actual))
        self.assertIn("SJ000312343-2", actual)
        self.assertIn("SJ000285285-13", actual)
        self.assertIn("SJ000312345-16", actual)
        self.assertIn("SJ000312317-9", actual)
        self.assertIn("SJ000312344-5", actual)
        # Add a compound to plate 2 and check that both locations are returned
        test.plates["E3P00000777"].wells["SJ000312343-2"] = {"location": [15, 2], "usage": 0}
        test.plates["E3P00000777"].wells["SJ000312344-5"] = {"location": [16, 2], "usage": 0}
        actual = test.get_all_compounds()
        self.assertEqual(21, len(actual))
        self.assertEqual(2, len([i for i, x in enumerate(actual) if x == "SJ000312343-2"]))
        self.assertEqual(2, len([i for i, x in enumerate(actual) if x == "SJ000312344-5"]))
        return
    
    def test_07_SourcePlates_find(self):
        test = Combinations.SourcePlates(self.mosaicmulti)
        self.assertIsNotNone(test.plates)
        test.plates["E3P00000777"].wells["SJ000312343-2"] = {'location':[2,2], 'usage':0}
        self.assertEqual(2, len(test.plates))
        # Test method
        t1 = test.find("SJ000986010-1")
        self.assertEqual([("E3P00000776", "SJ000986010-1", {'location':[4,1], 'usage':0})], t1)
        t2 = test.find("SJ000312363-15")
        self.assertEqual([("E3P00000776", "SJ000312363-15", {'location':[10,1], 'usage':0})], t2)
        t3 = test.find("SJ000312343-2")
        self.assertEqual([("E3P00000776", "SJ000312343-2", {'location':[1,1], 'usage':0}),
                          ("E3P00000777", "SJ000312343-2", {'location':[2,2], 'usage':0})], t3)

    def test_08_SourcePlates_mark_use(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertEqual(1, len(test.plates))
        self.assertIn("source1", test.plates)
        self.assertEqual(3, len(test.plates["source1"].wells))
        # Test Method
        test.mark_use("source1", "Topotecan")
        self.assertEqual(1, test.plates["source1"].wells["Topotecan"]["usage"])
        test.mark_use("source1", "Topotecan")
        self.assertEqual(2, test.plates["source1"].wells["Topotecan"]["usage"])
        test.mark_use("source1", "Topotecan")
        self.assertEqual(3, test.plates["source1"].wells["Topotecan"]["usage"])
        test.mark_use("source1", "Topotecan")
        self.assertEqual(4, test.plates["source1"].wells["Topotecan"]["usage"])
        self.assertEqual(0, test.plates["source1"].wells["Bortezomib"]["usage"])
        self.assertEqual(0, test.plates["source1"].wells["Dasatinib"]["usage"])
        return

    def test_09_SourcePlates_has_backfills(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertEqual(1, len(test.plates))
        self.assertIn("source1", test.plates)
        test.plates["source1"].set_backfill_wells(["A24", "B24", "C24"])
        # Test Method
        self.assertTrue(test.has_backfills)
        return 

    def test_10_SourcePlates_get_backfill_wells(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertEqual(1, len(test.plates))
        self.assertIn("source1", test.plates)
        test.plates["source1"].set_backfill_wells(["A24", "B24", "C24"])
        # Test Method
        actual = test.get_backfill_wells()
        self.assertEqual(3, len(actual))
        self.assertEqual(3, len(actual[0]))
        # Check the first element
        self.assertEqual("source1", actual[0][0])
        self.assertEqual("A24", actual[0][1])
        self.assertEqual([1,24], actual[0][2]["location"])
        # Check the last element
        self.assertEqual("source1", actual[2][0])
        self.assertEqual("C24", actual[2][1])
        self.assertEqual([3,24], actual[2][2]["location"])
        # Test with multiple plates
        test.plates["source2"] = Combinations.Platemap()
        test.plates["source2"].set_backfill_wells(["D24", "E24", "F24"])
        actual = test.get_backfill_wells()
        self.assertEqual(6, len(actual))
        self.assertEqual(3, len(actual[4]))
        # Check the first element
        self.assertEqual("source1", actual[0][0])
        self.assertEqual("A24", actual[0][1])
        self.assertEqual([1,24], actual[0][2]["location"])
        # Check the last element
        self.assertEqual("source2", actual[5][0])
        self.assertEqual("F24", actual[5][1])
        self.assertEqual([6,24], actual[5][2]["location"])
        return
    
    def test_11_SourcePlates_has_controls(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertFalse(test.has_controls())
        test.plates["source1"].set_controls(["Dasatinib"], [125], 16)
        self.assertTrue(test.has_controls())
        return
    
    def test_12_SourcePlates_get_control_wells(self):
        test = Combinations.SourcePlates(self.mapfile)
        self.assertIsNotNone(test.plates)
        self.assertFalse(test.has_controls())
        test.plates["source1"].set_controls(["Dasatinib"], [125], 16)
        test.plates["source1"].set_controls(["Bortezomib"], [100], 16)
        actual = test.get_control_wells()
        self.assertEqual(2, len(actual))
        self.assertEqual(("source1", "Dasatinib", {"location": [1,1], "times_used": 16, "volume": 125, "usage": 0}), actual[0])
        self.assertEqual(("source1", "Bortezomib", {"location": [1,2], "times_used": 16, "volume": 100, "usage": 0}), actual[1])
        return


class Combinations_TestingMethods(unittest.TestCase):
   
    def setUp(self):
        self.mapfile = "Test_Files\\Platemap.csv"
        self.combine_file = "Test_Files\\Combination Template.csv"
        self.wrkdir = "Test_Outputs"
        self.mosaicfile = "Test_Files\\PlateSummary.txt"
        self.mosaicmulti = "Test_Files\\PlateSummary-Multi.txt"
        self.echofile = "Test_Files\\ECHO CSV.csv"
        self.unsorted = "Test_Files\\Test_Output-Unsorted.csv"
        self.sourcesorted = "Test_Files\\Test_Output-SourceSorted.csv"
        self.destsorted = "Test_Files\\Test_Output-DestSorted.csv"
        self.srcsortedlong = "Test_Files\\Test_Output_SrcLong.csv"
        self.destsortedlong = "Test_Files\\Test_Output_DestLong.csv"
        warnings.simplefilter('ignore', category=UserWarning)
        return

    def tearDown(self):
        # Clear the Platemap object
        Combinations.Platemap.wells = dict()
        Combinations.Platemap.backfill = dict()
        Combinations.Platemap.controls = dict()
        # Clear the SourcePlates object
        Combinations.SourcePlates.plates = dict()
        # Clear the other Combinations attributes
        Combinations.Combinations.clist = list()
        Combinations.Combinations.platemap = None
        Combinations.Combinations.transfers = {"all": list()}
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
        self.assertIn("all", test.transfers)
        self.assertEqual(1, len(test.transfers["all"]))
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
        self.assertEqual(3, len(test.platemap.get_all_compounds()))
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
        self.assertEqual(3, len(test.platemap.get_all_compounds()))
        test.platemap.plates["source1"].set_backfill_wells(["P20", "P21", "P22", "P23", "P24"])
        self.assertEqual(5, len(test.platemap.plates["source1"].backfill))
        well = test.get_next_backfill()        
        self.assertEqual("source1", well[0])
        self.assertTrue("P20" in well[1])
        self.assertEqual([16,20], well[2]['location'])
        self.assertEqual(1, well[2]['usage'])
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual("source1", well[0])
        self.assertTrue("P21" in well[1])
        self.assertEqual([16,21], well[2]['location'])
        self.assertEqual(1, well[2]['usage'])
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual("source1", well[0])
        self.assertTrue("P22" in well[1])
        self.assertEqual([16,22], well[2]['location'])
        self.assertEqual(1, well[2]['usage'])
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual("source1", well[0])
        self.assertTrue("P23" in well[1])
        self.assertEqual([16,23], well[2]['location'])
        self.assertEqual(1, well[2]['usage'])
        # Test that the next well is returned
        well = test.get_next_backfill()
        self.assertEqual("source1", well[0])
        self.assertTrue("P24" in well[1])
        self.assertEqual([16,24], well[2]['location'])
        self.assertEqual(1, well[2]['usage'])
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
        expected_str = "Source1,1,1,Destination1,1,1,100,\n"
        self.assertEqual(expected_str, test_str)
        # Test 2
        test_str = test.format_transfer("Source1", "2", "1", "Destination1", "2", "1", "100")
        expected_str = "Source1,1,2,Destination1,1,2,100,\n"
        self.assertEqual(expected_str, test_str)
        # Test 3
        test_str = test.format_transfer("Source1", "1", "3", "Destination1", "3", "1", "150")
        expected_str = "Source1,3,1,Destination1,1,3,150,\n"
        self.assertEqual(expected_str, test_str)
        return
    
    def test_14_1_Combinations_sort_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mapfile)
        self.assertIsNotNone(test.platemap)
        self.assertTrue(len(test.platemap.get_all_compounds()) > 0)
        self.assertFalse(test.platemap.has_backfills())
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(7, len(test.clist))
        # Create the transfer list
        self.assertEqual(1, len(test.transfers["all"]))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers["all"]))
        # Add a second group that goes to a second destination
        d2 = [x.replace("destination1", "destination2") for x in test.transfers["all"] if test.trns_header not in x]
        test.transfers["all"].extend(d2)
        # Check that they are not sorted
        with open(self.unsorted, 'r') as unsorted:
            for i,line in enumerate(unsorted):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
        # Sort by source -> default
        test.sort_transfers()
        with open(self.sourcesorted, 'r') as sourcesorted:
            for i,line in enumerate(sourcesorted):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
        # Sort by destination
        test.sort_transfers("destination")
        with open(self.destsorted, 'r') as destsorted:
            for i,line in enumerate(destsorted):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
        # Sort by source explicitly
        test.sort_transfers("source")
        with open(self.sourcesorted, 'r') as sourcesorted:
            for i,line in enumerate(sourcesorted):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
        return
    
    def test_14_2_Combinations_sort_transfers(self):
        test = Combinations.Combinations()
        # Load platemap
        self.assertIsNone(test.platemap)
        test.load_platemap(self.mosaicfile)
        self.assertIsNotNone(test.platemap)
        self.assertTrue(len(test.platemap.get_all_compounds()) > 0)
        # Set some backfill wells
        wells = [x[0] for x in Combinations.generate_well_range("A21", "P24")]
        test.platemap.plates["E3P00000776"].set_backfill_wells(wells)
        self.assertTrue(test.platemap.has_backfills())
        # Set up combinations
        self.assertEqual(0, len(test.clist))
        test.generate_combinations()
        self.assertEqual(696, len(test.clist))
        # Set a volume
        test.set_volume(100)
        # Create the transfer list
        self.assertEqual(1, len(test.transfers["all"]))
        test.create_transfers()
        self.assertEqual(2073, len(test.transfers["all"]))
        # Test default sorting
        test.sort_transfers()
        with open(self.srcsortedlong, 'r') as srcsortedlong:
            for i,line in enumerate(srcsortedlong):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
        # Test destination sorting
        test.sort_transfers("destination")
        with open(self.destsortedlong, 'r') as destsortedlong:
            for i,line in enumerate(destsortedlong):
                self.assertEqual("\n", test.transfers["all"][i][-1])
                self.assertEqual(line.strip(), test.transfers["all"][i].strip())
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
        self.assertEqual(1, len(test.transfers["all"]))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers["all"]))
        self.assertEqual(377, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        # Add some backfill wells and repeat with backfills
        test.transfers["all"] = [test.trns_header]
        test.destinations = dict()
        backfill_wells = Combinations.generate_well_range("A21", "P24")
        test.platemap.plates["source1"].set_backfill_wells([x[0] for x in backfill_wells])
        self.assertEqual(64, len(test.platemap.get_backfill_wells()))
        test.create_transfers()
        self.assertEqual(19, len(test.transfers["all"]))
        # Count wells that are not used ()
        self.assertEqual(377, len([w for p in test.destinations for w in test.destinations[p] if "transfers" not in test.destinations[p][w]]))
        # Add some controls and test again
        test.transfers["all"] = [test.trns_header]
        test.destinations = dict()
        test.reserve_control_wells(['A21', 'A22', 'A23', 'A24', 'B21', 'B22', 'B23', 'B24'])
        test.platemap.plates["source1"].wells["Control1"] = {"location": [1,24], "usage": 0}
        test.platemap.plates["source1"].wells["Control2"] = {"location": [2,24], "usage": 0}
        test.platemap.plates["source1"].set_controls(["Control1", "Control2"], [125], 4)
        test.set_volume(100)
        test.create_transfers()
        self.assertEqual(35, len(test.transfers["all"]))
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
        self.assertEqual(1, len(test.transfers["all"]))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers["all"]))
        # Capture the Output
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        # Run the method
        test.print_transfers()
        # Reset the stdout
        sys.stdout = sys.__stdout__
        self.assertIn("all: source1,1,1,destination1,1,1,0.0", capturedOutput.getvalue())
        self.assertIn("all: source1,2,1,destination1,2,1,0.0", capturedOutput.getvalue())
        self.assertIn("all: source1,3,1,destination1,7,1,0.0", capturedOutput.getvalue())
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
        self.assertEqual(1, len(test.transfers["all"]))
        test.create_transfers()
        self.assertEqual(13, len(test.transfers["all"]))
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
        # TODO: Add test for split output mode
        return



