"""Computing loss of McDonald's in the USA due to broken ice-cream machines"""
import os
import shutil
import json
import argparse
from datetime import datetime
from git import Repo


# these constants are main assumptions in this project

# number of people visiting McDonald's in the USA per day
# information in free access
NUM_VISITORS_PER_DAY = 45e6

# percentage of people, who order desert
# there is no information on this in free access, so this is fully my assumption
DESERT_PERCENTAGE = 0.5

# percentage of ice cream among ordered desserts
# https://as.nyu.edu/content/dam/nyu-as/psychology/documents/case-studies/MCD%20Business%20Case.pdf
ICE_CREAM_PERCENTAGE = 0.6

# net income from one ice cream
# mcflurry average cost is 2.1$ and it making cost is around 0.4-0.5$
# there are a lot of different sources on making cost matter, but most of them are out of date
ICE_CREAM_NET_INCOME = 2.1 - 0.45

# computing net ice cream income per day
NET_ICE_CREAM_INCOME_PER_DAY = NUM_VISITORS_PER_DAY * DESERT_PERCENTAGE * ICE_CREAM_PERCENTAGE * ICE_CREAM_NET_INCOME  # pylint: disable=locally-disabled, line-too-long

# url to GitHub archive of McBroken site
GIT_ARCHIVE_URL = "https://github.com/rashiq/mcbroken-archive"


def initialize_parser():
    """Initializing argument parser"""
    parser = argparse.ArgumentParser(
        description="Compute revenue loss of McDonald's in the USA due to broken "
                    "ice-cream machines at the specific date")
    parser.add_argument("-t", "--target_date",
                        help="set date for lost net calculation in DD/MM/YY format",
                        required=True)
    parser.add_argument("-r", "--reinit", action="store_true",
                        help="flag for reinitialization of git repo "
                             "(in case you need most recent results)")
    return parser


def initialize_repo(git_url, reinit=False):
    """Downloading and initializing GitHub repo with archive"""
    git_path = "./data/mcbroken-archive/"
    if os.path.isdir(git_path):
        if reinit:
            shutil.rmtree(git_path)
        else:
            return Repo(git_path)
    print("Cloning archive repository... It can take a few minutes due to big commit history.")
    return Repo.clone_from(git_url, git_path)


def retrieve_data_from_commits(commit_hashes):
    """Retrieving data from commits of certain date"""
    if not os.path.isdir("./data/mcbroken-archive/retrieved/"):
        os.mkdir("./data/mcbroken-archive/retrieved/")
    os.chdir("./data/mcbroken-archive/")
    data = []
    for commit_hash in commit_hashes:
        # subprocess is not working here(not seeing .git)
        os.system(f'git cat-file -p {commit_hash}:./mcbroken.json > ./retrieved/{commit_hash}.mcbroken.json')  # pylint: disable=locally-disabled, line-too-long
        with open(f'./retrieved/{commit_hash}.mcbroken.json', encoding='utf-8') as json_file:
            data.append(json.load(json_file))
    os.chdir("./")
    return data


def format_commits_data(data):
    """Compute hours with broken ice-cream machine per every restaurant"""
    broken_time = {}
    for commit_data in data:
        for point in commit_data:
            key = tuple(point['geometry']['coordinates'])
            if key not in broken_time:
                broken_time[key] = 0
            if point['properties']['country'] == 'USA' and point['properties']["is_active"]:
                broken_time[key] += point['properties']['is_broken']
    return broken_time


def compute_net_loss():
    """Compute net loss on certain date"""
    arg_parser = initialize_parser()
    args = arg_parser.parse_args()
    target_date = datetime.strptime(args.target_date, "%d/%m/%y")

    repo = initialize_repo(GIT_ARCHIVE_URL, args.reinit)
    # check that the repository loaded correctly
    if not repo.bare:
        print(f'Repo at {GIT_ARCHIVE_URL} successfully loaded.')
        commits = list(repo.iter_commits('main'))
        target_date_commits = list(reversed([commit for commit in commits
                                             if commit.committed_datetime.date() == target_date.date()]))  # pylint: disable=locally-disabled, line-too-long
        commits_data = retrieve_data_from_commits(target_date_commits)
        broken_time_data = format_commits_data(commits_data)
        broken_days = sum(broken_time_data.values()) / 24.0
        print(f"Lost revenue: {broken_days * (NET_ICE_CREAM_INCOME_PER_DAY / len(broken_time_data)):.0f}$")  # pylint: disable=locally-disabled, line-too-long
    else:
        print(f'Could not load repository at {GIT_ARCHIVE_URL} :(')


if __name__ == "__main__":
    compute_net_loss()
