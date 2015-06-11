import os
import re
import subprocess
import unittest


# TODO: robustness to other current working directories

class ExpectedOutputsTestCase(unittest.TestCase):

    def test_expected_output(self):
        for filename in filter(lambda fn: fn.endswith(".gltrl"),
                               os.listdir("..")):
            example = filename[:-6]
            source_path = os.path.join("..", filename)
            executable_path = os.path.join("..", example)
            with open(source_path) as source_file:
                source = source_file.read()
            expected_output_header = re.search("# Expected output—\n", source,
                                               re.MULTILINE)
            if expected_output_header:
                expected_output_start = expected_output_header.end()
                expected_output = bytes(
                    source[expected_output_start:].replace('# ', ''), 'utf8')
                actual_output = subprocess.check_output(executable_path)
                with self.subTest(example=example):
                    self.assertEqual(expected_output, actual_output)
