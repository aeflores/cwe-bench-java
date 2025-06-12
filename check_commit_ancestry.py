#!/usr/bin/env python3

import csv
import subprocess
from pathlib import Path
from typing import List

EXCLUDED_PROJECTS = [
    "alibaba__one-java-agent_CVE-2022-25842_0.0.1", # No real fixes for this one (the commits seem irrelevant)
]
MANUALLY_EXCLUDED = [
    "a221a864db28eb736d36041df2fa6eb8839fc5cd", # from perwendel__spark_CVE-2018-9159_2.7.1, same as 030e9d00125cbd1ad759668f85488aba1019c668
    "ce9e11517eca69e58ed4378d1e47a02bd06863cc", # from perwendel__spark_CVE-2018-9159_2.7.1 (cannot be found)
    "4f401c09d22c45c94fa97746dc31905e06b19e3", # apache__camel_CVE-2018-8041_2.20.3 (the same fix as 4580e4d6c65cfd544c1791c824b5819477c583cc but applied to other releases)
    "63c7c080de4d18f9ceb25843508710df2c2c6d4", # apache__camel_CVE-2018-8041_2.20.3 (the same fix as 4580e4d6c65cfd544c1791c824b5819477c583cc but applied to other releases)
    "a0d25d9582c6ee85e9567fa39413df0b4f02ef7", # apache__camel_CVE-2018-8041_2.20.3 (the same fix as 4580e4d6c65cfd544c1791c824b5819477c583cc but applied to other releases)
    "7af52a0883a9dbc475cf3001f04ed11b24c8a4c0", # DSpace__DSpace_CVE-2022-31195_5.10, this commit is the equivalent fix (though not exactly the same) to 56e76049185bbd87c994128a9d77735ad7af0199
    # one for dspace-5.11 and the other for dspace-6.4
    "7569c6374aefeafb996e202cf8d631020eda5f24", # DSpace__DSpace_CVE-2022-31194_5.10, this commit is the same as d1dd7d23329ef055069759df15cfa200c8e3 but for dspace-6_x instead of dspace-5_x
    "10de190e7d3f9189deb76b8d08c72334a1fe2df0", # apache__mina-sshd_CVE-2023-35887_2.9.2 this commit is from 2018, it cannot be a fix to a 2023 CVE
    "a61e93035f06bff8fc622ad94870fb773d48b9f0", # apache__mina-sshd_CVE-2023-35887_2.9.2 this commit is the same as c20739b43aab0f7bf2ccad982a6cb37b9d5a8a0b but for sshd-2.15 instead of sshd-2.9.3
    "00921f22ff9a8792d7663ef8fadd4823402a6324", # apache__activemq_CVE-2014-3576_5.10.2 this commit is the same as f07e6a53216f9388185ac2b39f366f3bfd6a8a55 but for activemq-5.11.0 instead of 5.10.2
    "124b7dd6d9a4ad24d4d49f74701f05a13e56ceee", # hibernate__hibernate-validator_CVE-2019-10219_6.0.17.Final same commit as 20d729548511ac5cff6fd459f93de137195420fe but for a different version
    "32e89366e2daa5670ac7a5c5c19f0bf9329a4c1e", # asf__cxf_CVE-2016-6812_3.0.11 same commit as 1be97cb13aef121b799b1be4d9793c0e8b925a12 but for 3.1.x-fixes instead of 3.0.x-fixes
    "1f824d8039c7a42a4aa46f844e6c800e1143c7e7", # asf__cxf_CVE-2016-6812_3.0.11 equivalent commit as a30397b0 but for 3.1.x-fixes instead of 3.0.x-fixes
    "f7758457b7ec3489d525e39aa753cc70809d9ad9", # DSpace__DSpace_CVE-2022-31192_5.10 this commit seems to be unrelated to a XXS. It looks like a path-traversal prevention
    "98b9f2e", # apache__activemq_CVE-2019-0222_5.15.8 same commit as f78c0962ffb46fae3397eed6b7ec1e6e15045031 but for activemq-5.16.0 instead of activemq-5.15.9
    "88b78d0", # apache__activemq_CVE-2020-11998_5.15.12 same commit as 0d6e5f2 but for a different version
    "aa8900c", # apache__activemq_CVE-2020-11998_5.15.12 same commit as 0d6e5f2 but for a different version
    "c3ada731405c5990c36bf58d50b3e61965300703", # similar to 9d411cf04a695e7a3f41036e8377b0aa544d754d but for a different version
    '21c358acf0b06f38ec46034404c7a3d0bbbc132d', # wildfly__wildfly_CVE-2018-1047_11.0.0.Final this commit only adds an intergration test, the real fix is only 735c77c
    '9ff55ed2da845a6f604b2edd1bc3bd311f1b776c', # wildfly__wildfly_CVE-2018-1047_11.0.0.Final this commit only modifies an intergration test, the real fix is only 735c77c
]

VULNERABLE_COMMIT = {
    "perwendel__spark_CVE-2018-9159_2.7.1" : "99d7ddc4636b47892e0190ca170b6ecec70dec2f" 
    # for some reason I cannot find "ce9e11517eca69e58ed4378d1e47a02bd06863cc" locally but it seems to be a legit part of the fix. The parent is this commit.
}

def is_ancestor(repo_path:Path, ancestor_commit:str, descendant_commit:str)-> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor_commit, descendant_commit],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def find_earliest_fix_commit(repo_path:Path, fix_commits:List[str])-> str:
    earliest = fix_commits[0]
    for fix_commit in fix_commits:
        if fix_commit == earliest:
            continue
        if is_ancestor(repo_path, fix_commit, earliest):
            earliest = fix_commit
        elif not is_ancestor(repo_path, earliest, fix_commit):
            print(f"WARNING: fix commits {fix_commit} and {earliest} are not related")
    return earliest

def find_latest_fix_commit(repo_path:Path, fix_commits:List[str])-> str:
    latest = fix_commits[0]
    for fix_commit in fix_commits:
        if fix_commit == latest:
            continue
        if is_ancestor(repo_path, latest, fix_commit):
            latest = fix_commit
        elif not is_ancestor(repo_path, fix_commit, latest):
            print(f"WARNING: fix commits {fix_commit} and {latest} are not related")
    return latest

def find_immediate_predecessor(repo_path:Path, commit:str)-> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{commit}^"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip()

def get_commit_dates(repo_path:Path, commits:List[str]) -> str:
    dates = {}
    for commit in commits:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%cd", "--date=short", commit],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        dates[commit] = result.stdout.strip()
    return dates

    
def main():
    csv_path = Path("data/project_info.csv")
    csv_path_fixed = Path("data/project_info_fixed.csv")
    projects_base_dir = Path("project-sources")
    # Read the CSV file

    refined_results = []
    with open(csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Process each row
        for row in reader:
            project_slug = row['project_slug']
            repo_path = projects_base_dir / project_slug

            if project_slug in EXCLUDED_PROJECTS:
                continue
            
            print(f"Checking project: {project_slug}")
            # Check if the project directory exists
            if not repo_path.exists():
                print(f"  Warning: Project directory {repo_path} does not exist. Skipping.")
                continue
            # Try unshallow in case it has not been done before
            subprocess.run(["git", "fetch", "--unshallow"], 
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            # fetch tags since some commits are found only there
            subprocess.run(["git", "fetch", "--tags"], 
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            
            buggy_commit = row['buggy_commit_id']
            fix_commits = row['fix_commit_ids'].split(';')
            fix_commits = [c for c in fix_commits if c not in MANUALLY_EXCLUDED]
            if len(fix_commits) > 1:
                print(f"{project_slug} has multiple fix commits")
                commit_to_dates = get_commit_dates(repo_path, fix_commits)
                print(commit_to_dates)
            
            latest_fix_commit = find_latest_fix_commit(repo_path,fix_commits)
            if len(fix_commits) > 1:
                print(f"Latest fix commit {latest_fix_commit} {commit_to_dates[latest_fix_commit]}")
            if project_slug in VULNERABLE_COMMIT:
                new_buggy_commit = VULNERABLE_COMMIT[project_slug]
            else:
                earliest_fix_commit = find_earliest_fix_commit(repo_path, fix_commits)
                if len(fix_commits) > 1:
                    print(f"Earliest fix commit {earliest_fix_commit} {commit_to_dates[earliest_fix_commit]}")
                new_buggy_commit = find_immediate_predecessor(repo_path,earliest_fix_commit)

            if latest_fix_commit != fix_commits[-1]:
                print(f"Latest fix commit does not appear last in {project_slug}")
            refined_results.append((project_slug,row["cwe_id"],row["github_url"],new_buggy_commit,latest_fix_commit))
    with open(csv_path_fixed,"w") as f:
        field_names = ["project_slug","cwe_id","github_url","buggy_commit_id","last_fix_commit_id"]
        writer = csv.DictWriter(f,fieldnames=field_names)
        writer.writeheader()
        for project_slug, cwe_id, github_url, buggy_commit_id, last_fix_commit_id in sorted(refined_results):
            writer.writerow({
                "project_slug":project_slug,
                "cwe_id":cwe_id,
                "github_url":github_url,
                "buggy_commit_id":buggy_commit_id,
                "last_fix_commit_id":last_fix_commit_id})

            

if __name__ == "__main__":
    main()
