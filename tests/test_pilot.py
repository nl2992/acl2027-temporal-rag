import sys, os, unittest, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "pilot"))
from dateparse import resolve, find_dates, TODAY
from router import route2
D = dt.date
class T(unittest.TestCase):
    def test_formats(self):
        for q, d in [("on March 3, 2019", D(2019,3,3)), ("on 3 March 2019", D(2019,3,3)), ("on 2019-03-03", D(2019,3,3)), ("on 3/3/2019", D(2019,3,3)), ("by Sept. 9, 2016", D(2016,9,9))]:
            self.assertEqual(find_dates(q)[0][1], d, q)
    def test_resolve(self):
        self.assertEqual(resolve("rule in effect on May 5, 2017", "valid_at"), (D(2017,5,5), TODAY))
        self.assertEqual(resolve("latest rule as of June 1, 2018", "known_at"), (D(2018,6,1), D(2018,6,1)))
        self.assertEqual(resolve("what applies now", "current"), (TODAY, TODAY))
        self.assertIsNone(resolve("what applied back then", "valid_at"))
        self.assertEqual(resolve("On July 7, 2019, rule in force on June 20, 2019?", "valid_known"), (D(2019,6,20), D(2019,7,7)))
    def test_router(self):
        self.assertEqual(route2("Which rule applies right now?"), "current")
        self.assertEqual(route2("What rule was in force on May 5, 2017?"), "valid_at")
        self.assertEqual(route2("Latest rule published by May 5, 2017?"), "known_at")
        self.assertEqual(route2("Using only what had been published by May 5, 2017, which rule was in force on June 1, 2017?"), "valid_known")
    def test_invalid_date_is_skipped(self):
        self.assertEqual(find_dates("on February 30, 2019"), [])
if __name__ == "__main__":
    unittest.main()
