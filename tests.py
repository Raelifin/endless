import itertools
import sys

import main
import main2

class EndOfTest(Exception):
    def __str__(self):
        return "[END OF TEST]"

class TestInputSource(object):
    def __init__(self, feed, output):
        self.feed = feed
        self.output = output
        self.index = 0

    def __call__(self):
        if self.index == len(self.feed):
            raise EndOfTest()
        result = self.feed[self.index]
        self.output("> " + result)
        self.index += 1
        return result

class TestOutputBuffer(object):
    def __init__(self):
        self.buffer = []

    def __call__(self, text):
        self.buffer.append(text)

def try_sequence(game, sequence):
    output_buffer = TestOutputBuffer()
    get_input = TestInputSource(sequence, output_buffer)
    try:
        game(get_input, output_buffer)
        raise EndOfTest()
    except Exception as e:
        return e, output_buffer.buffer

def simple_test(game, sequence):
    result, log = try_sequence(game, x)
    if isinstance(result, EndOfTest):
        sys.stdout.write('.')
    elif isinstance(result, NotImplementedError):
        sys.stdout.write('-')
    else:
        sys.stdout.write('E')
    sys.stdout.flush()

def compare_test(original, refactor, sequence):
    result1, log1 = try_sequence(original, x)
    result2, log2 = try_sequence(refactor, x)
    log1.append(str(result1))
    log2.append(str(result2))
    if log1 == log2:
        sys.stdout.write('.')
        sys.stdout.flush()
    else:
        print()
        print("###### LOG ######")
        for i in range(max(len(log1), len(log2))):
            if log1[i] == log2[i]:
                print(log1[i])
            else:
                print("###### DIVERGENCE! ######")
                print("ORIGINAL:")
                print("\t%s" % log1[i])
                print("REFACTOR:")
                print("\t%s" % log2[i])
                print()
                raise Exception("Test divergence!")

input_set = ['0', 'shta', '2']
for x in itertools.combinations_with_replacement(input_set, 10):
    compare_test(main.main, main2.main, x)
print()
