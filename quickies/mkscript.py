#! python
import sys
import argparse
import pathlib
"""for each script try and make a templated version"""
template = """#! python
import sys
import argparse
def main(args):
    print(__file__,args.__dict__)
def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument('meaningful_name',
                        nargs='+',
                        help='basic argument')
    return parser.parse_args(args_)
if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))"""

def make_script(script):
    file_name = script
    if len(script.split('.')) == 1:
        file_name = file_name + '.py'
    script_path = pathlib.Path(file_name)

    if script_path.exists():
        print(f"oops {str(script_path)} already exists")
        quit(1)
        
    with open(script_path, 'w') as script_file:
        script_file.write(template)
        script_path.chmod(0o755)
        
def main(args):
    print(__file__,args.__dict__)
    for script in args.scripts:
        make_script(script)
        
def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument('scripts',
                        nargs='+',
                        help='path to scripts to be made')
    return parser.parse_args(args_)

if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
