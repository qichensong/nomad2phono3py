import os
import argparse

def cancel_jobs(start, end):
    for i in range(int(start), int(end)+1):
        print(f'scancel {i}')
        os.system(f'scancel {i}')

def main(args):
    cancel_jobs(args.fr, args.to)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fr', required=True)
    parser.add_argument('--to', required=True)
    args = parser.parse_args()
    main(args)