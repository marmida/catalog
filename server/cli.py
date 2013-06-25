'''
Command-line interface
'''

import argparse

import app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--couch-bin', help='Path to couchdb binary', default='couchdb')
    args = parser.parse_args()
    app.run(args.couch_bin)

if __name__ == '__main__':
    main()