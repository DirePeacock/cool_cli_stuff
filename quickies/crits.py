#! python
import sys
import argparse
def main(argv):
    per_atk = float(argv[0]) or 0.5
    atk_per_turn = float(argv[1]) or 2.0
    rolls_per_adv = float(argv[2]) or 2.0
    print(f"per_atk={per_atk} atk_per_turn={atk_per_turn} rolls_per_adv={rolls_per_adv}")
    pa_cc = 1.0-pow((1.0-per_atk), rolls_per_adv)
    pt_cc = 1.0-pow((1.0-pa_cc), atk_per_turn)
    print(f"%{pt_cc} per turn")
    print(f"%{pa_cc} per attack")
    
if __name__ == "__main__":
    main(sys.argv[1:])
