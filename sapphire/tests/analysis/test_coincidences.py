from mock import sentinel, patch
import unittest

from sapphire.analysis import coincidences


class CoincidencesTests(unittest.TestCase):

    def setUp(self):
        self.c = coincidences.Coincidences(sentinel.data, None,
                                           sentinel.station_groups,
                                           progress=False)

    @patch.object(coincidences.Coincidences, 'search_coincidences')
    @patch.object(coincidences.Coincidences, 'process_events')
    @patch.object(coincidences.Coincidences, 'store_coincidences')
    def test_search_and_store_coincidences(self, mock_store, mock_process,
                                           mock_search):
        self.c.search_and_store_coincidences()
        mock_search.assert_called_with(window=2000)
        mock_process.assert_called_with()
        mock_store.assert_called_with(None)
        self.c.search_and_store_coincidences(sentinel.window, sentinel.cluster)
        mock_search.assert_called_with(window=sentinel.window)
        mock_process.assert_called_with()
        mock_store.assert_called_with(sentinel.cluster)

    def test__do_search_coincidences(self):
        # [(timestamp, station_idx, event_idx), ..]
        timestamps = [(0, 0, 0), (0, 1, 0), (10, 1, 1), (15, 2, 0),
                      (100, 1, 2), (200, 2, 1), (250, 0, 1), (251, 0, 2)]

        c = self.c._do_search_coincidences(timestamps, window=6)
        expected_coincidences = [[0, 1], [2, 3], [6, 7]]
        self.assertEqual(c, expected_coincidences)

        c = self.c._do_search_coincidences(timestamps, window=150)
        expected_coincidences = [[0, 1, 2, 3, 4], [4, 5], [5, 6, 7]]
        self.assertEqual(c, expected_coincidences)

        c = self.c._do_search_coincidences(timestamps, window=300)
        expected_coincidences = [[0, 1, 2, 3, 4, 5, 6, 7]]
        self.assertEqual(c, expected_coincidences)


class CoincidencesESDTests(CoincidencesTests):

    def setUp(self):
        self.c = coincidences.CoincidencesESD(sentinel.data, None,
                                              sentinel.station_groups,
                                              progress=False)

    @patch.object(coincidences.CoincidencesESD, 'search_coincidences')
    @patch.object(coincidences.CoincidencesESD, 'store_coincidences')
    def test_search_and_store_coincidences(self, mock_store, mock_search):
        self.c.search_and_store_coincidences()
        mock_search.assert_called_with(window=2000)
        mock_store.assert_called_with(cluster=None)
        self.c.search_and_store_coincidences(sentinel.window,
                                             sentinel.cluster)
        mock_search.assert_called_with(window=sentinel.window)
        mock_store.assert_called_with(cluster=sentinel.cluster)

    @patch.object(coincidences.CoincidencesESD, '_search_coincidences')
    def test_search_coincidences(self, mock__search):
        mock__search.return_value = (sentinel.c_index, sentinel.timestamps)
        self.c.search_coincidences()
        mock__search.assert_called_with(2000, None, None)
        self.assertEqual(self.c._src_timestamps, sentinel.timestamps)
        self.assertEqual(self.c._src_c_index, sentinel.c_index)

        self.c.search_coincidences(sentinel.window, sentinel.shifts,
                                   sentinel.limit)
        mock__search.assert_called_with(sentinel.window, sentinel.shifts,
                                        sentinel.limit)


if __name__ == '__main__':
    unittest.main()
