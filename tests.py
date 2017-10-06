from typing import Tuple, Generator, Callable, Union, List, Optional
import itertools
import sys

import main
import basic_io as io

class EndOfTest(Exception):
    def __repr__(self) -> str:
        return "[END OF TEST]"

class TestInputSource(object):
    def __init__(self, feed: Tuple[str], output: io.Output) -> None:
        self.feed = feed
        self.output = output
        self.index = 0

    def __call__(self) -> str:
        if self.index == len(self.feed):
            raise EndOfTest()
        result = self.feed[self.index]
        self.output("> " + result)
        self.index += 1
        return result

class TestOutputBuffer(object):
    def __init__(self) -> None:
        self.buffer: List[str] = []

    def __call__(self, text: Optional[str]) -> None:
        if text is None:
            text = ""
        self.buffer += text.split('\n')

def try_sequence(game: io.MainFunction, sequence: Tuple[str]) -> Tuple[Exception, List[str]]:
    output_buffer = TestOutputBuffer()
    get_input = TestInputSource(sequence, output_buffer)
    try:
        game(get_input, output_buffer)
        raise EndOfTest()
    except Exception as e:
        return e, output_buffer.buffer

def _simple_test(game: io.MainFunction, sequence: Tuple[str], not_implemented_errors_are_okay: bool=False) -> None:
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

def _compare_test(original: io.MainFunction, refactor: io.MainFunction, sequence: Tuple[str]) -> None:
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

# The type signature for this test generator is an absolute monster. Ignore it.
def test_input_combinations():  # type: ignore
    input_set = ['0', 'shta', 'shak', 'chai', 'reho', '2']
    sequence_length = 10
    comparison_testing = False
    if comparison_testing:
        import main2
        for x in itertools.combinations_with_replacement(input_set, sequence_length):
            yield _compare_test, main.main, main2.main, x  # type: ignore
    else:
        not_implemented_errors_are_okay = False
        for x in itertools.combinations_with_replacement(input_set, sequence_length):
            yield _simple_test, main.main, x, not_implemented_errors_are_okay  # type: ignore

if __name__ == "__main__":
    print("Use nosetests on this file.")
