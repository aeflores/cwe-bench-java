"""
Usage: python fetch_one.py <project_slug>

The script fetches one project from Github, checking out the buggy commit,
and then patches it with the essential information for it to be buildable.
The project is specified with the Project Slug that contains project name,
CVE ID, and version tag.

Example:

``` bash
$ python3 fetch_one.py apache__camel_CVE-2018-8041_2.20.3
```
"""

import os
import argparse
import csv
import subprocess

CWE_BENCH_JAVA_ROOT_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("project_slug", type=str)
  parser.add_argument("--fixed", action="store_true")
  args = parser.parse_args()
  get_fixed = args.fixed

  project_slug = args.project_slug
  reader = csv.DictReader(open(f"{CWE_BENCH_JAVA_ROOT_DIR}/data/project_info_fixed.csv"))
  for line in reader:
    if line["project_slug"] == project_slug:
      row = line

  repo_url = row["github_url"]
  if get_fixed:
    project_sources = "project-sources-fixed"
    commit_id = row["last_fix_commit_id"]
  else:
    commit_id = row["buggy_commit_id"]
    project_sources = "project-sources"
  target_dir = f"{CWE_BENCH_JAVA_ROOT_DIR}/{project_sources}/{project_slug}"

  if os.path.exists(f"{CWE_BENCH_JAVA_ROOT_DIR}/{project_sources}/{project_slug}"):
    print(f">> [CWE-Bench-Java/fetch_one] skipping")
    exit(0)

  if get_fixed:
    depth_args = []
  else:
    depth_args =  ["--depth", "1"]

  print(f">> [CWE-Bench-Java/fetch_one] Cloning repository from `{repo_url}`...")
  git_clone_cmd = ["git", "clone"] + depth_args + [repo_url, target_dir]
  subprocess.run(git_clone_cmd)

  print(f">> [CWE-Bench-Java/fetch_one] Fetching and checking out commit `{commit_id}`...")
  git_fetch_commit = ["git", "fetch"] + depth_args + [ "origin", commit_id]
  subprocess.run(git_fetch_commit, cwd=target_dir)
  git_checkout_commit = ["git", "checkout", commit_id]
  subprocess.run(git_checkout_commit, cwd=target_dir)

  patch_dir = f"{CWE_BENCH_JAVA_ROOT_DIR}/patches/{project_slug}.patch"
  if not get_fixed and os.path.exists(patch_dir):
    print(f">> [CWE-Bench-Java/fetch_one] Applying patch `{patch_dir}`...")
    git_patch = ["git", "apply", patch_dir]
    subprocess.run(git_patch, cwd=target_dir)
  else:
    print(f">> [CWE-Bench-Java/fetch_one] There is no patch; skipping patching the repository")
