import argparse

import trace_parser

def main():
    parser = argparse.ArgumentParser(description="Compare assembly to jit ops")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')

    args = parser.parse_args()

    traces = trace_parser.parse_files(args.filenames, fragment=True)
    return 0

if __name__ == '__main__':
    main()
