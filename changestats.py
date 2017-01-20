#!/usr/bin/python

import github3
import getpass
import os

def Authorize():
  credentials_file = ".github_auth"
  scopes = ['user', 'repo', 'read:org', 'repo:status']
  if not os.path.exists(credentials_file):
    username = raw_input("Github login: ")
    password = getpass.getpass("Password: ")
    auth = github3.authorize(
      username,
      password,
      ['user', 'repo', 'admin:org', 'repo:status'],
      note='changestats script',
      note_url='https://github.com/UCLA-CS130/changestats',
      two_factor_callback=lambda: raw_input("OTP: "))
    with open(credentials_file, 'w') as fd:
      fd.write(auth.token + '\n')
      fd.write(str(auth.id))
  with open(credentials_file, 'r') as fd:
    token = fd.readline().strip()
    id = fd.readline().strip()
    # TODO: Check that auth scopes match. gh.authorization(id)...
    return github3.login(token=token)

def PrettyPrint(name, total_count, stats):
  print "%s: %d commits" % (name, total_count)
  for name in sorted(stats, key=stats.get, reverse=True):
    print "%40s %3d" % (name, stats[name])
  print ""

gh = Authorize()
org = gh.organization('UCLA-CS130')

total_commits = 0
overall_commits_by_author = {}
for repo in org.repositories():
  commit_count = 0
  commits_by_author = {}
  try:
    for commit in repo.commits():
      commit_count += 1
      total_commits += 1
      try:
        author = commit.author.login
      except AttributeError:
        author = commit.commit.author['name']
      if author not in commits_by_author:
        commits_by_author[author] = 0
      if author not in overall_commits_by_author:
        overall_commits_by_author[author] = 0
      commits_by_author[author] += 1
      overall_commits_by_author[author] += 1
  except github3.exceptions.ClientError:
    pass

  PrettyPrint(repo.name, commit_count, commits_by_author)

PrettyPrint("Overall", total_commits, overall_commits_by_author)
