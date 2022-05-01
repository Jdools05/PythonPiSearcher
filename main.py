# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math
import time
from multiprocessing import Pool

import requests
import threading

has_found_pattern = False


class ThreadedProcessor(threading.Thread):
    def __init__(self, lower_bound, digit_range, search_pattern):
        threading.Thread.__init__(self)
        self.lower_bound = lower_bound
        self.digit_range = digit_range
        self.search_pattern = search_pattern

    def run(self):
        # the base of the data from the api
        radix = 16
        # get the data from the api
        response = requests.get(
            f'https://api.pi.delivery/v1/pi?start={self.lower_bound}&numberOfDigits={self.digit_range}&radix={radix}')
        decimal = response.json().get('content')
        # convert each digit to binary
        binary = [bin(int(x, radix))[2:].zfill(4) for x in decimal]
        # join the data into a single string
        binary = "".join(binary)
        # search for the pattern
        index = binary.find(self.search_pattern)
        if index != -1:
            print(f'Found at digit: {index+self.lower_bound}')
            print(f'Digit range: {self.lower_bound} - {self.lower_bound+self.digit_range}')
            print(f'Base {radix}: {decimal}')
            print(f'Base 2: {binary}')
            global has_found_pattern
            has_found_pattern = True


def main():
    # this is the pattern to search for
    # this pattern is an among us character
    search_pattern = "1000001100001010"
    # used to determine if the search is complete
    start_time = time.time()

    # create a list of threads
    threads = []
    batch_size = 5
    batch_index = 0
    start_lower_bound = 0
    # keep searching until the pattern is found
    while not has_found_pattern:
        relative_batch_start_time = time.time()

        # the amount of new digits to search per thread
        digit_range = 200

        # create a thread for each batch of digits
        for i in range(batch_size):
            # the lower bound of the digits to search
            lower_bound = (batch_index * batch_size + i) * digit_range + start_lower_bound
            # the amount of digits from the previous batch to search
            thread_overlap = 16
            # create a thread
            thread = ThreadedProcessor(lower_bound, digit_range + thread_overlap, search_pattern)
            threads.append(thread.start())

            while len(threads) > 0:
                pool = Pool()
                for j in range(len(threads)):
                    if threads:
                        t = threads.pop()
                        pool.apply_async(t, ())
                pool.close()
                pool.join()

        elapsed_time = time.time() - relative_batch_start_time
        print(f'Batch {batch_index + 1} time: {elapsed_time}')
        print(f'Batch range: {batch_index * batch_size * digit_range + start_lower_bound} - {(batch_index + 1) * batch_size * digit_range + start_lower_bound}')
        print(f'Total elapsed time: {time.time() - start_time}')
        batch_index += 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
