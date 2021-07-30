#! python
import sys
import argparse
def r20_parser(string);
    pass
def main(args):
    print(__file__,args.__dict__)
def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument('meaningful_name',
                        nargs='+',
                        help='basic argument')
    return parser.parse_args(args_)
if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
