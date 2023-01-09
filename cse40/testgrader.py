"""
Tools for testing graders.
"""

import glob
import os
import sys

import cse40.code

def test_dir(grader_path, solutions_dir):
    grader = cse40.code.import_path(grader_path)
    error_count = 0

    for solution_path in glob.glob(os.path.join(solutions_dir, '*.py')):
        print("Testing solution: " + solution_path)

        solution = cse40.code.import_path(solution_path)

        if ('EXPECTED_POINTS' not in dir(solution)):
            print("    ERROR: 'EXPECTED_POINTS' not defined in solution file.")
            error_count += 1
            continue

        assignment = grader.grade(solution_path)
        score, _ = assignment.get_score()

        if (score != solution.EXPECTED_POINTS):
            print("    ERROR: Expected score (%s) does not match actual score (%s)." % (
                solution.EXPECTED_POINTS, score))
            error_count += 1
            continue

    return error_count

def main(grader_path, solutions_dir):
    error_count = test_dir(grader_path, solutions_dir)
    sys.exit(error_count)

def _load_args(args):
    args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 -m cse40.testgrader <grader path> <solution dir>", file = sys.stderr)
        sys.exit(1)

    grader_path = os.path.abspath(args.pop(0))
    solutions_dir = os.path.abspath(args.pop(0))

    return grader_path, solutions_dir

if (__name__ == '__main__'):
    main(*_load_args(sys.argv))
