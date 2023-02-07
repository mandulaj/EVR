

from src import ETH_VidRip as EVR


import json, os

import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='AutoDownload videos from ETH Video Portal')
    parser.add_argument('-c', "--credentials", type=str, help='ETH Login Credentials', 
        default = "credentials.json")
    parser.add_argument('-o', "--output_dir", type=str, help='Output Directory', 
        default="output")
    parser.add_argument('-t', "--tasks", type=str, help='Task JSON with targets to acquire', 
        required=True)
    parser.add_argument('-n', "--n_jobs", type=str, help="Number of parallel downloads", 
        default=1) 
    parser.add_argument('-x', "--no_skip", action='store_true', help="Don't skip existing files")

    args = parser.parse_args()
    return args



def main():

    args = parse_args()


    with open(args.tasks, "r") as f:
        tasks = json.load(f)

    with open(args.credentials, "r") as f:
        credentials = json.load(f)


    config = {
        'base': args.output_dir,
        'njobs': args.n_jobs,
        "no_skip": args.no_skip
    }


    scraper = EVR.ETHVideoScraper(tasks, credentials, config)

    scraper.run()




if __name__ == "__main__":
    main()

