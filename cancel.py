import os
import argparse

def cancel_jobs(start, end)
for i in range(start, end+1):
    os.system(f'scancel {i}')

def main(args):
    cancel_jobs(args.start, args.end)

if __name__ = '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    args = parser.parse_args()