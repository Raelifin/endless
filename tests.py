import itertools

import main

input_set = ['0', '1', '2', '3', '4', '5', 'shta']

class EndOfTest(Exception):
    pass

class TestInputSource(object):
    def __init__(self, feed):
        self.feed = feed
        self.index = 0

    def __call__(self):
        if self.index == len(self.feed):
            raise EndOfTest()
        result = self.feed[self.index]
        print("> " + result)
        self.index += 1
        return result

for x in itertools.combinations_with_replacement(input_set, 10):
    get_input = TestInputSource(x)
    try:
        main.main(get_input)
    except EndOfTest:
        print("Test completed successfully!")
