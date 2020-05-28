import concurrent
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import ProcessPoolExecutor
import random
import requests

# Arnold Veltmann
# python 3.8.0

# Starting from command line
# pip install urllib3; pip install requests
# or manually install packages
# To run: python nevercode.py
# different parameters can be managed from the main() function
# To run tests: python -m unittest test_nevercode.py -b


def get_response(url):

    # @exit_status sets the exit code for the slave. Defaulted to 0.
    exit_status = 0

    try:
        response = requests.get(url)
        status = response.status_code

        # If connection is established, but the status code is not equal to 200, exit_status is set to 1.
        if status != 200:
            exit_status = 1
        exit(exit_status)

    # If connection could not be established, exit_status will be set to 2.
    except requests.ConnectionError:
        exit_status = 2
        exit(exit_status)
    finally:
        return exit_status


def generate_urls(number_of_urls):

    if str(number_of_urls).isdigit() == False:
        raise TypeError("Number of urls generated should be defined by an positive integer...")

    urls = []

    for i in range(number_of_urls):
        urls.append("https://postman-echo.com/delay/" + str(random.randint(1, 5)))

    return urls


def result_message(retries, urls):

    if retries == -1 and len(urls) > 0:
        return "Unsuccessful connections to %s, not retrying..." % str(urls)
    elif len(urls) > 0:
        return "Unsuccessful connections to %s, retrying connection..." % str(urls)
    else:
        return "All URLs responded with status code 200."


def start_slaves(slaves, urls, connection_retry):

    with slaves:

        while connection_retry != -1 and len(urls) != 0:

            # stored futures
            futures = {slaves.submit(get_response, url): url for url in urls}

            # wait for all of the futures to get a response
            concurrent.futures.wait(futures, return_when=ALL_COMPLETED)

            # check results, remove urls from list that returned status code 200
            for future in futures:
                if future.result() == 0:
                    urls.remove(futures[future])

            connection_retry = connection_retry - 1

            # printing update on results and actions
            result = result_message(connection_retry, urls)
            print(result)


def main():

    # @number_of_urls manages number of urls to be generated. Defaulted to 5.
    number_of_urls = 5

    # @connection_retry manages number of connection retries in case status code does not equal 200. Defaulted to 1.
    connection_retry = 1

    # @number_of_workers manages number of slave programs. Defaulted to 5.
    number_of_workers = 5

    urls = generate_urls(number_of_urls)
    slaves = ProcessPoolExecutor(max_workers=number_of_workers)

    start_slaves(slaves, urls, connection_retry)


if __name__ == '__main__':
    main()

