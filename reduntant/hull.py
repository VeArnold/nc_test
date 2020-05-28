import concurrent
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import ThreadPoolExecutor
import random
import requests


def get_response(url):

    # @parameter exit_status sets the exit code for the slave. Defaulted to 0.
    exit_status = 0

    try:
        response = requests.get(url)
        status = response.status_code

        # If connection is established, but the status code is not equal to 200, exit_status is set to 1.
        if status != 200:
            exit_status = 1
        exit(exit_status)

    # If connection could not be established, exit_status will be set to 2.
    except requests.ConnectionError as err:
        exit_status = 2
        exit(exit_status)
    finally:
        return exit_status


def generate_urls(number_of_urls):

    urls = []

    for i in range(number_of_urls):
        urls.append("https://postman-echo.com/delay/" + str(random.randint(1, 5)))

    urls.append("http://google.com/5q25q32")

    return urls


def result_message(retries, urls):

    if retries == -1 and len(urls) > 0:
        print("Unsuccessful connections to %s, not retrying..." % str(urls))
    elif len(urls) > 0:
        print("Unsuccessful connections to %s, retrying connection..." % str(urls))
    else:
        print("All URLs responded with status code 200.")


def main():

    # Parameter to manage number of urls generated.
    # @parameter number_of_urls is defaulted to 5.
    number_of_urls = 5

    urls = generate_urls(number_of_urls)

    # Parameter to manage how many times the program tries to establish connection
    # to websites, if the first try fails
    # @parameter connection_retry is defaulted to 1
    connection_retry = 1

    with ThreadPoolExecutor(max_workers=5) as slaves:


        futures = {slaves.submit(get_response, url): url for url in urls}

        # wait for all of the responses
        concurrent.futures.wait(futures, return_when=ALL_COMPLETED)

        # check results, if failed, resubmit failed workers
        for future in futures:
            if future.result() != 0:
                slaves.submit(get_response, futures[future])
            else:
                urls.remove(futures[future])

        connection_retry = connection_retry - 1

        # printing results
        result_message(connection_retry, urls)


main()




