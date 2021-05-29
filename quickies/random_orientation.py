import random

def random_angle():
    return (-90 + int(181*random.random()))

def random_orientation():
    print(f"\nx:{random_angle()}, y:{random_angle()}, z:{random_angle()}\n")
    
if __name__ == "__main__":
	random_orientation()