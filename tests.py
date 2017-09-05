import itertools
import sys

import main
# import main2

class EndOfTest(Exception):
    def __repr__(self):
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
        if text is None:
            text = ""
        self.buffer += text.split('\n')

def try_sequence(game, sequence):
    output_buffer = TestOutputBuffer()
    get_input = TestInputSource(sequence, output_buffer)
    try:
        game(get_input, output_buffer)
        raise EndOfTest()
    except Exception as e:
        return e, output_buffer.buffer

def _simple_test(game, sequence, not_implemented_errors_are_okay=False):
    result, log = try_sequence(game, sequence)
    if isinstance(result, EndOfTest):
        pass
    elif isinstance(result, NotImplementedError) and not_implemented_errors_are_okay:
        pass
    else:
        for line in log:
            print(line)
        print(repr(result))
        raise result

def _compare_test(original, refactor, sequence):
    result1, log1 = try_sequence(original, sequence)
    result2, log2 = try_sequence(refactor, sequence)
    log1.append(repr(result1))
    log2.append(repr(result2))
    if log1 == log2:
        pass
    else:
        for i in range(max(len(log1), len(log2))):
            if log1[i] == log2[i]:
                print(log1[i])
            else:
                print("###### DIVERGENCE! ######")
                print("ORIGINAL:")
                print("\t%s" % log1[i])
                print("REFACTOR:")
                print("\t%s" % log2[i])
                raise Exception("Test divergence!")

def test_input_combinations():
    input_set = ['0', 'shta', '2']
    not_implemented_errors_are_okay = False
    for x in itertools.combinations_with_replacement(input_set, 10):
        # yield _compare_test, main.main, main2.main, x
        yield _simple_test, main.main, x, not_implemented_errors_are_okay

if __name__ == "__main__":
    print("Use nosetests on this file.")
