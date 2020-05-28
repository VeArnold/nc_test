
from concurrent.futures.process import ProcessPoolExecutor
import nevercode
import unittest
from unittest.mock import patch


# Arnold Veltmann
# python 3.8.0

# Running from commandline
# pip install requests
# or manually install packages
# python test_nevercode.py -b (disables print output)


class TestNeverCode(unittest.TestCase):

    @classmethod
    def setUp(cls):
        # all tests by default are run with 5 workers
        cls._slaves = ProcessPoolExecutor(max_workers=5)

    # test should pass with return_value 0 and fail with all other return_values
    @patch("concurrent.futures.Future.result", return_value=0)
    def test_start_slaves_success(self, mock_method):

        # if connection_retry > 1, but all requests return status code 200
        # then result_message should still only be called once.
        urls = ["one", "two", "three"]
        connection_retry = 3

        # result_message should be called once with connection_retry - 1 and empty list as parameters
        with patch("nevercode.result_message", return_value = "") as mock:
            nevercode.start_slaves(self._slaves, urls, connection_retry)
            mock.assert_called_once_with(2, [])

    # test should pass with all return_value's that are not equal to 0
    @patch("concurrent.futures.Future.result", return_value=2)
    def test_start_slaves_failure(self, mock_method):

        # if connection_retry = n, but one or more slave program fails each retry, then the
        # total calls for result_message() should equal n+1.
        urls = ["one", "two", "three"]
        connection_retry = 3

        with patch("nevercode.result_message", return_value = "") as mock:
            nevercode.start_slaves(self._slaves, urls, connection_retry)
            self.assertEqual(4, mock.call_count)

    def test_start_slaves_empty(self):

        # if the url list is empty, no future methods are iterated (thus no calls are made for future.result())

        with patch("concurrent.futures.Future.result") as mock:

            nevercode.start_slaves(self._slaves, [], 3)
            mock.assert_not_called()

    def test_generate_urls(self):

        # checking if the right amount of urls are generated
        self.assertEqual(len(nevercode.generate_urls(5)), 5)
        self.assertEqual(len(nevercode.generate_urls(0)), 0)

        # checking if TypeError is raised
        with self.assertRaises(TypeError):
            nevercode.generate_urls(2.0)
            nevercode.generate_urls("2")
            nevercode.generate_urls(-1)

        # check if generated numbers are 1-5

    def test_get_response(self):

        with patch("requests.get") as mock_request:
            url = "https://postman-echo.com/"

            # checking return value for successful connection
            mock_request.return_value.status_code = 200
            self.assertEqual(nevercode.get_response(url), 0)

            # checking return value in case of status code not being equal to 200
            mock_request.return_value.status_code = 404
            self.assertEqual(nevercode.get_response(url), 1)

        # checking return value in case of a network error (can test with a non-existent page)
        self.assertEqual(nevercode.get_response("https://ihopethispagedoesnotexistitprobablywontbutok.xyz/"), 2)

    def test_result_message_empty(self):

        # Test with zero urls in list (all urls removed due to passing)

        urls = []

        self.assertEqual(nevercode.result_message(0, urls), "All URLs responded with status code 200.")
        self.assertEqual(nevercode.result_message(1, urls), "All URLs responded with status code 200.")
        self.assertEqual(nevercode.result_message(-1, urls), "All URLs responded with status code 200.")

    def test_result_message(self):

        # Test with a url still in the list

        urls = ["https://postman-echo.com/"]

        # with retries remaining
        self.assertEqual(nevercode.result_message(0, urls),
                         "Unsuccessful connections to %s, retrying connection..." % str(urls))

        # with no retries
        self.assertEqual(nevercode.result_message(-1, urls),
                         "Unsuccessful connections to %s, not retrying..." % str(urls))

    # testing that start_slaves and generate_urls are only called once
    @patch("nevercode.start_slaves")
    @patch("nevercode.generate_urls")
    def test_main(self, mock_url_generator, mock_slave_starter):

        nevercode.main()

        mock_url_generator.assert_called_once()
        mock_slave_starter.assert_called_once()


if __name__ == '__main__':
    unittest.main()