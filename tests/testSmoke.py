import unittest
from main import Lemmy

class TestSmoke (unittest.TestCase):

    def testCountEntries (self):
        self.assertEqual (21567, len (Lemmy (
            sort_col = 'id',
            sort     = 'desc',
        ).table()))

    def testExpectedErrors (self):
        with self.assertRaises (UserWarning):
            Lemmy (
                sort_col = 'wurstsemmel',
                sort     = 'desc',
            ).table()

        with self.assertRaises (UserWarning):
            Lemmy (
                sort_col = 'ids',
                sort     = 'wurstsemmel',
            ).table()

        with self.assertRaises (UserWarning):
            Lemmy().table()
