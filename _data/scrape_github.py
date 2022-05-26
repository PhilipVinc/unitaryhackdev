# -*- coding: utf-8 -*-
import github
import json
import os
import datetime
import frontmatter
from urllib import parse

# using an access token
g = github.Github(os.getenv('GITHUB_TOKEN'))

project_path = "../projects"
projects = {}
tags = ["[unitaryHACK]", "[unitaryhack]", "[UnitaryHACK]", "[UnitaryHack]"]
pr_keys = ['number', 'state', 'title', 'user', 
           'created_at', 'merged_at', 'closed_at', 'assignee', 'assignees',
           'body', 'requested_reviewers', 'draft']
issue_keys = ['number', 'state', 'title', 'user', 'labels', 'created_at',
              'updated_at', 'closed_at', 'assignee', 'assignees', 'body',
              'closed_by']
repo_keys = ['name', 'full_name', 'owner', 'html_url', 'description',
             'created_at', 'updated_at', 'size', 'stargazers_count',
             'watchers_count', 'language', 'forks_count', 'open_issues_count',
             'subscribers_count', 'license', 'topics']


def filter_info(keys, data):
    info = {key: data[key] for key in keys}
    return {key: to_json_serializable(i) for key, i in info.items()}


def to_json_serializable(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%d/%m/%Y %H:%M:%S')
    elif isinstance(obj, github.NamedUser.NamedUser):
        return obj.login
    return obj


# Scrape the md project files for the yaml metadata
for filename in os.listdir(project_path):
    if filename.endswith(".md") and not filename.startswith("quantify"):
        print(os.path.join(project_path, filename))
        p = frontmatter.load(os.path.join(project_path, filename))
        projects[p["title"]] = p.metadata
        projects[p["title"]]["full_title"] = (
            parse.urlparse(p["project_url"]).path).strip("/")
        projects[p["title"]]["date"] = (
            projects[p["title"]]["date"]).strftime('%d/%m/%Y %H:%M:%S')

# Results for a project should look like this:
#
# projects["mitiq"] =
# {'title': 'Mitiq',
#  'emoji': '�🌴',
#  'project_url': 'https://github.com/unitaryfund/mitiq',
#  'full_name': 'unitaryfund/mitiq',
#  'metaDescription': 'Making NISQ hardware less noisy with a Python-based error mitigating package.',
#  'date': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
#  'summary': 'Python package for quantum error mitigation techniques',
#  'tags': ['error-mitigation', 'noise', 'run-on-hardware', 'python'],
#  'bounties': [{'name': 'Redundant information in citation file',
#    'issue_num': 1227,
#    'value': 50},
#   {'name': 'Use consistent citation style in docs and function doctrings.',
#    'issue_num': 1250,
#    'value': 75},
#   {'name': 'Include backend in execute_with_shots',
#    'issue_num': 1163,
#    'value': 75},
#   {'name': 'Improve H2 example', 'issue_num': 1094, 'value': 100}],
#  'full_title': 'unitaryfund/mitiq'}

# Call GH api to get all repos that are part of the unitaryHACK event and bounty issues
for project, meta in projects.items():
    # Get the GH data for the repo
    project_data = g.get_repo(meta["full_title"])
    print(f"\n-----\nLoaded {project} repo data")
    # Add the GH data to the projects dict
    meta.update(filter_info(repo_keys, project_data.__dict__["_rawData"]))
    print(f"Added {project} repo data")
    # Get the PRs for the repo
    prs = project_data.get_pulls(sort='created')
    print(f"Loaded {project} PR data")
    # Add the PRs with the hackathon tag to the projects dict
    [print(pr.__dict__["_rawData"]) for pr in prs if any(x in pr.title for x in tags)]
    meta["uh_prs"] = [(filter_info(pr_keys, pr.__dict__["_rawData"]))
                      for pr in prs if any(x in pr.title for x in tags)]
    print(f"Added {project} PR data")
    # Look up the bountied issues and check on status
    if "bounties" in meta:
        for bounty in meta["bounties"]:
            issue_data = project_data.get_issue(bounty["issue_num"])
            bounty.update(filter_info(
                issue_keys, issue_data.__dict__["_rawData"]))
            print(f"updated {project} bounty # { bounty['issue_num'] }")

with open("gh.json", "w") as f:
    json.dump(projects, f)

print("Done! ♥")


# Results for the data on an issue should look like this:
#
# issue_data.__dict__["_rawData"] =
# {'url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094',
#  'repository_url': 'https://api.github.com/repos/unitaryfund/mitiq',
#  'labels_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094/labels{/name}',
#  'comments_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094/comments',
#  'events_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094/events',
#  'html_url': 'https://github.com/unitaryfund/mitiq/issues/1094',
#  'id': 1107045969,
#  'node_id': 'I_kwDODhvcQc5B_C5R',
#  'number': 1094,
#  'title': '[unitaryhack-bounty] Improve H2 example',
#  'user': {'login': 'andreamari',
#   'id': 46054446,
#   'node_id': 'MDQ6VXNlcjQ2MDU0NDQ2',
#   'avatar_url': 'https://avatars.github`user`content.com/u/46054446?v=4',
#   'gravatar_id': '',
#   'url': 'https://api.github.com/users/andreamari',
#   'html_url': 'https://github.com/andreamari',
#   'followers_url': 'https://api.github.com/users/andreamari/followers',
#   'following_url': 'https://api.github.com/users/andreamari/following{/other_user}',
#   'gists_url': 'https://api.github.com/users/andreamari/gists{/gist_id}',
#   'starred_url': 'https://api.github.com/users/andreamari/starred{/owner}{/repo}',
#   'subscriptions_url': 'https://api.github.com/users/andreamari/subscriptions',
#   'organizations_url': 'https://api.github.com/users/andreamari/orgs',
#   'repos_url': 'https://api.github.com/users/andreamari/repos',
#   'events_url': 'https://api.github.com/users/andreamari/events{/privacy}',
#   'received_events_url': 'https://api.github.com/users/andreamari/received_events',
#   'type': 'User',
#   'site_admin': False},
#  'labels': [{'id': 1812908008,
#    'node_id': 'MDU6TGFiZWwxODEyOTA4MDA4',
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq/labels/documentation',
#    'name': 'documentation',
#    'color': '0075ca',
#    'default': True,
#    'description': 'Improvements or additions to documentation'},
#   {'id': 1812908014,
#    'node_id': 'MDU6TGFiZWwxODEyOTA4MDE0',
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq/labels/good%20first%20issue',
#    'name': 'good first issue',
#    'color': '7057ff',
#    'default': True,
#    'description': 'Good for newcomers'},
#   {'id': 3067329697,
#    'node_id': 'MDU6TGFiZWwzMDY3MzI5Njk3',
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq/labels/priority/p2',
#    'name': 'priority/p2',
#    'color': 'D19B10',
#    'default': False,
#    'description': 'A non-urgent issue to fix or idea to discuss.'},
#   {'id': 3951006758,
#    'node_id': 'LA_kwDODhvcQc7rf5Qm',
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq/labels/unitaryhack-bounty',
#    'name': 'unitaryhack-bounty',
#    'color': '0E8A16',
#    'default': False,
#    'description': ''},
#   {'id': 4105475738,
#    'node_id': 'LA_kwDODhvcQc70tJaa',
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq/labels/self-contained-project',
#    'name': 'self-contained-project',
#    'color': 'F3888A',
#    'default': False,
#    'description': ''}],
#  'state': 'open',
#  'locked': False,
#  'assignee': None,
#  'assignees': [],
#  'milestone': None,
#  'comments': 2,
#  'created_at': '2022-01-18T15:30:12Z',
#  'updated_at': '2022-05-19T16:12:24Z',
#  'closed_at': None,
#  'author_association': 'MEMBER',
#  'active_lock_reason': None,
#  'body': "The current H2 example could be improved in two different aspects:\r\n\r\n- [ ] The numerical values of the Hamiltonian coefficients _g_j(R)_ are hard-coded from data extracted from a paper. It would be nice to derive them using some chemistry package e.g.: [PySCF](https://pyscf.org/) or [OpenFermion](https://github.com/quantumlib/OpenFermion). Ideally (but only
# if not too complicated), it would be better to use the same Hamiltonian in order to reproduce the same results of the Mitiq paper. \r\n- [ ] Use a `mitiq.Observable` for the Hamiltonian, and just use `mitiq_cirq.compute_density_matrix` for the executor. See the docs for more details on how to define and use observables.\r\n\r\nIf you only fixed one of the two aspects, please don't close this issue but just mark the corresponding item in the above list.",
#  'closed_by': None,
#  'reactions': {'url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094/reactions',
#   'total_count': 0,
#   '+1': 0,
#   '-1': 0,
#   'laugh': 0,
#   'hooray': 0,
#   'confused': 0,
#   'heart': 0,
#   'rocket': 0,
#   'eyes': 0},
#  'timeline_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/1094/timeline',
#  'performed_via_github_app': None,
#  'state_reason': None}


# Results for a PR data
#
# In [128]: prTest.__dict__["_rawData"]
# Out[128]:
# {'url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384',
#  'id': 496925701,
#  'node_id': 'MDExOlB1bGxSZXF1ZXN0NDk2OTI1NzAx',
#  'html_url': 'https://github.com/unitaryfund/mitiq/pull/384',
#  'diff_url': 'https://github.com/unitaryfund/mitiq/pull/384.diff',
#  'patch_url': 'https://github.com/unitaryfund/mitiq/pull/384.patch',
#  'issue_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/384',
#  'number': 384,
#  'state': 'closed',
#  'locked': False,
#  'title': 'Generate and track pdf of documentation, address #341',
#  'user': {'login': 'nathanshammah',
#   'id': 14573436,
#   'node_id': 'MDQ6VXNlcjE0NTczNDM2',
#   'avatar_url': 'https://avatars.githubusercontent.com/u/14573436?v=4',
#   'gravatar_id': '',
#   'url': 'https://api.github.com/users/nathanshammah',
#   'html_url': 'https://github.com/nathanshammah',
#   'followers_url': 'https://api.github.com/users/nathanshammah/followers',
#   'following_url': 'https://api.github.com/users/nathanshammah/following{/other_user}',
#   'gists_url': 'https://api.github.com/users/nathanshammah/gists{/gist_id}',
#   'starred_url': 'https://api.github.com/users/nathanshammah/starred{/owner}{/repo}',
#   'subscriptions_url': 'https://api.github.com/users/nathanshammah/subscriptions',
#   'organizations_url': 'https://api.github.com/users/nathanshammah/orgs',
#   'repos_url': 'https://api.github.com/users/nathanshammah/repos',
#   'events_url': 'https://api.github.com/users/nathanshammah/events{/privacy}',
#   'received_events_url': 'https://api.github.com/users/nathanshammah/received_events',
#   'type': 'User',
#   'site_admin': False},
#  'body': 'Description\r\n-----------\r\nGenerate and track the pdf file of the documentation, addressing #341, to simplify the release process.  \r\n\r\n\r\nIf you have not finished all tasks in the checklist, you can also open a [Draft Pull Request](https://github.blog/2019-02-14-introducing-draft-pull-requests/) to let the others know this on-going work and keep this checklist in the PR description.\r\n\r\nChecklist\r\n-----------\r\nPlease make sure you have finished the following tasks before requesting a review of the pull request (PR). For more information, please refer to the [Contributor\'s Guide](../blob/master/CONTRIBUTING.md):\r\n\r\n- [ ] Contributions to mitiq should follow the [pep8 style](https://www.python.org/dev/peps/pep-0008/). You can enforce it easily with [`black`](https://black.readthedocs.io/en/stable/index.html) style and with [`flake8`](http://flake8.pycqa.org) conventions.\r\n- [ ] Please add tests to cover your changes, if applicable, and make sure that all new and existing tests pass locally.\r\n- [ ] If the behavior of the code has changed or new feature has been added, please also [update the documentation](../blob/master/docs/CONTRIBUTING_DOCS.md).\r\n- [ ] Functions and classes have useful [Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings and [type hints](https://www.python.org/dev/peps/pep-0484/) in the signature of the objects.\r\n- [ ] (Bug fix) The associated issue is referenced above using [auto-close keywords](https://help.github.com/en/articles/closing-issues-using-keywords). If the PR fixes an issue, use the keyword fix/fixes/fixed followed by the issue id. For example, if the PR fixes issue 1184, type "Fixes #1184" (without quotes).\r\n- [ ] The [changelog](https://github.com/unitaryfund/mitiq/blob/master/CHANGELOG.md) is updated, including author and PR number (@username, gh-xxx).\r\n',
#  'created_at': '2020-10-02T13:58:40Z',
#  'updated_at': '2020-10-15T17:51:31Z',
#  'closed_at': '2020-10-15T17:51:30Z',
#  'merged_at': None,
#  'merge_commit_sha': '93e4d9d4ba733ec53a8c6e3e5e71169b4a2badfc',
#  'assignee': None,
#  'assignees': [],
#  'requested_reviewers': [],
#  'requested_teams': [],
#  'labels': [],
#  'milestone': {'url': 'https://api.github.com/repos/unitaryfund/mitiq/milestones/7',
#   'html_url': 'https://github.com/unitaryfund/mitiq/milestone/7',
#   'labels_url': 'https://api.github.com/repos/unitaryfund/mitiq/milestones/7/labels',
#   'id': 5842655,
#   'node_id': 'MDk6TWlsZXN0b25lNTg0MjY1NQ==',
#   'number': 7,
#   'title': '0.3.0',
#   'description': 'First code for PEC module in mitiq/mitiq. ',
#   'creator': {'login': 'willzeng',
#    'id': 5214594,
#    'node_id': 'MDQ6VXNlcjUyMTQ1OTQ=',
#    'avatar_url': 'https://avatars.githubusercontent.com/u/5214594?v=4',
#    'gravatar_id': '',
#    'url': 'https://api.github.com/users/willzeng',
#    'html_url': 'https://github.com/willzeng',
#    'followers_url': 'https://api.github.com/users/willzeng/followers',
#    'following_url': 'https://api.github.com/users/willzeng/following{/other_user}',
#    'gists_url': 'https://api.github.com/users/willzeng/gists{/gist_id}',
#    'starred_url': 'https://api.github.com/users/willzeng/starred{/owner}{/repo}',
#    'subscriptions_url': 'https://api.github.com/users/willzeng/subscriptions',
#    'organizations_url': 'https://api.github.com/users/willzeng/orgs',
#    'repos_url': 'https://api.github.com/users/willzeng/repos',
#    'events_url': 'https://api.github.com/users/willzeng/events{/privacy}',
#    'received_events_url': 'https://api.github.com/users/willzeng/received_events',
#    'type': 'User',
#    'site_admin': False},
#   'open_issues': 0,
#   'closed_issues': 25,
#   'state': 'closed',
#   'created_at': '2020-09-03T21:43:12Z',
#   'updated_at': '2020-10-30T19:38:58Z',
#   'due_on': '2020-11-01T07:00:00Z',
#   'closed_at': '2020-10-30T18:36:12Z'},
#  'draft': False,
#  'commits_url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384/commits',
#  'review_comments_url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384/comments',
#  'review_comment_url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/comments{/number}',
#  'comments_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/384/comments',
#  'statuses_url': 'https://api.github.com/repos/unitaryfund/mitiq/statuses/d213a012351a09b17fee0a6936e137ee64f5f5db',
#  'head': {'label': 'nathanshammah:pdf',
#   'ref': 'pdf',
#   'sha': 'd213a012351a09b17fee0a6936e137ee64f5f5db',
#   'user': {'login': 'nathanshammah',
#    'id': 14573436,
#    'node_id': 'MDQ6VXNlcjE0NTczNDM2',
#    'avatar_url': 'https://avatars.githubusercontent.com/u/14573436?v=4',
#    'gravatar_id': '',
#    'url': 'https://api.github.com/users/nathanshammah',
#    'html_url': 'https://github.com/nathanshammah',
#    'followers_url': 'https://api.github.com/users/nathanshammah/followers',
#    'following_url': 'https://api.github.com/users/nathanshammah/following{/other_user}',
#    'gists_url': 'https://api.github.com/users/nathanshammah/gists{/gist_id}',
#    'starred_url': 'https://api.github.com/users/nathanshammah/starred{/owner}{/repo}',
#    'subscriptions_url': 'https://api.github.com/users/nathanshammah/subscriptions',
#    'organizations_url': 'https://api.github.com/users/nathanshammah/orgs',
#    'repos_url': 'https://api.github.com/users/nathanshammah/repos',
#    'events_url': 'https://api.github.com/users/nathanshammah/events{/privacy}',
#    'received_events_url': 'https://api.github.com/users/nathanshammah/received_events',
#    'type': 'User',
#    'site_admin': False},
#   'repo': {'id': 296623633,
#    'node_id': 'MDEwOlJlcG9zaXRvcnkyOTY2MjM2MzM=',
#    'name': 'mitiq',
#    'full_name': 'nathanshammah/mitiq',
#    'private': False,
#    'owner': {'login': 'nathanshammah',
#     'id': 14573436,
#     'node_id': 'MDQ6VXNlcjE0NTczNDM2',
#     'avatar_url': 'https://avatars.githubusercontent.com/u/14573436?v=4',
#     'gravatar_id': '',
#     'url': 'https://api.github.com/users/nathanshammah',
#     'html_url': 'https://github.com/nathanshammah',
#     'followers_url': 'https://api.github.com/users/nathanshammah/followers',
#     'following_url': 'https://api.github.com/users/nathanshammah/following{/other_user}',
#     'gists_url': 'https://api.github.com/users/nathanshammah/gists{/gist_id}',
#     'starred_url': 'https://api.github.com/users/nathanshammah/starred{/owner}{/repo}',
#     'subscriptions_url': 'https://api.github.com/users/nathanshammah/subscriptions',
#     'organizations_url': 'https://api.github.com/users/nathanshammah/orgs',
#     'repos_url': 'https://api.github.com/users/nathanshammah/repos',
#     'events_url': 'https://api.github.com/users/nathanshammah/events{/privacy}',
#     'received_events_url': 'https://api.github.com/users/nathanshammah/received_events',
#     'type': 'User',
#     'site_admin': False},
#    'html_url': 'https://github.com/nathanshammah/mitiq',
#    'description': 'Mitiq is an open source toolkit for implementing error mitigation techniques on most current intermediate-scale quantum computers.',
#    'fork': True,
#    'url': 'https://api.github.com/repos/nathanshammah/mitiq',
#    'forks_url': 'https://api.github.com/repos/nathanshammah/mitiq/forks',
#    'keys_url': 'https://api.github.com/repos/nathanshammah/mitiq/keys{/key_id}',
#    'collaborators_url': 'https://api.github.com/repos/nathanshammah/mitiq/collaborators{/collaborator}',
#    'teams_url': 'https://api.github.com/repos/nathanshammah/mitiq/teams',
#    'hooks_url': 'https://api.github.com/repos/nathanshammah/mitiq/hooks',
#    'issue_events_url': 'https://api.github.com/repos/nathanshammah/mitiq/issues/events{/number}',
#    'events_url': 'https://api.github.com/repos/nathanshammah/mitiq/events',
#    'assignees_url': 'https://api.github.com/repos/nathanshammah/mitiq/assignees{/user}',
#    'branches_url': 'https://api.github.com/repos/nathanshammah/mitiq/branches{/branch}',
#    'tags_url': 'https://api.github.com/repos/nathanshammah/mitiq/tags',
#    'blobs_url': 'https://api.github.com/repos/nathanshammah/mitiq/git/blobs{/sha}',
#    'git_tags_url': 'https://api.github.com/repos/nathanshammah/mitiq/git/tags{/sha}',
#    'git_refs_url': 'https://api.github.com/repos/nathanshammah/mitiq/git/refs{/sha}',
#    'trees_url': 'https://api.github.com/repos/nathanshammah/mitiq/git/trees{/sha}',
#    'statuses_url': 'https://api.github.com/repos/nathanshammah/mitiq/statuses/{sha}',
#    'languages_url': 'https://api.github.com/repos/nathanshammah/mitiq/languages',
#    'stargazers_url': 'https://api.github.com/repos/nathanshammah/mitiq/stargazers',
#    'contributors_url': 'https://api.github.com/repos/nathanshammah/mitiq/contributors',
#    'subscribers_url': 'https://api.github.com/repos/nathanshammah/mitiq/subscribers',
#    'subscription_url': 'https://api.github.com/repos/nathanshammah/mitiq/subscription',
#    'commits_url': 'https://api.github.com/repos/nathanshammah/mitiq/commits{/sha}',
#    'git_commits_url': 'https://api.github.com/repos/nathanshammah/mitiq/git/commits{/sha}',
#    'comments_url': 'https://api.github.com/repos/nathanshammah/mitiq/comments{/number}',
#    'issue_comment_url': 'https://api.github.com/repos/nathanshammah/mitiq/issues/comments{/number}',
#    'contents_url': 'https://api.github.com/repos/nathanshammah/mitiq/contents/{+path}',
#    'compare_url': 'https://api.github.com/repos/nathanshammah/mitiq/compare/{base}...{head}',
#    'merges_url': 'https://api.github.com/repos/nathanshammah/mitiq/merges',
#    'archive_url': 'https://api.github.com/repos/nathanshammah/mitiq/{archive_format}{/ref}',
#    'downloads_url': 'https://api.github.com/repos/nathanshammah/mitiq/downloads',
#    'issues_url': 'https://api.github.com/repos/nathanshammah/mitiq/issues{/number}',
#    'pulls_url': 'https://api.github.com/repos/nathanshammah/mitiq/pulls{/number}',
#    'milestones_url': 'https://api.github.com/repos/nathanshammah/mitiq/milestones{/number}',
#    'notifications_url': 'https://api.github.com/repos/nathanshammah/mitiq/notifications{?since,all,participating}',
#    'labels_url': 'https://api.github.com/repos/nathanshammah/mitiq/labels{/name}',
#    'releases_url': 'https://api.github.com/repos/nathanshammah/mitiq/releases{/id}',
#    'deployments_url': 'https://api.github.com/repos/nathanshammah/mitiq/deployments',
#    'created_at': '2020-09-18T13:06:33Z',
#    'updated_at': '2022-01-07T14:49:58Z',
#    'pushed_at': '2022-05-20T11:22:17Z',
#    'git_url': 'git://github.com/nathanshammah/mitiq.git',
#    'ssh_url': 'git@github.com:nathanshammah/mitiq.git',
#    'clone_url': 'https://github.com/nathanshammah/mitiq.git',
#    'svn_url': 'https://github.com/nathanshammah/mitiq',
#    'homepage': '',
#    'size': 12894,
#    'stargazers_count': 0,
#    'watchers_count': 0,
#    'language': 'Python',
#    'has_issues': False,
#    'has_projects': True,
#    'has_downloads': True,
#    'has_wiki': True,
#    'has_pages': False,
#    'forks_count': 0,
#    'mirror_url': None,
#    'archived': False,
#    'disabled': False,
#    'open_issues_count': 9,
#    'license': {'key': 'gpl-3.0',
#     'name': 'GNU General Public License v3.0',
#     'spdx_id': 'GPL-3.0',
#     'url': 'https://api.github.com/licenses/gpl-3.0',
#     'node_id': 'MDc6TGljZW5zZTk='},
#    'allow_forking': True,
#    'is_template': False,
#    'topics': [],
#    'visibility': 'public',
#    'forks': 0,
#    'open_issues': 9,
#    'watchers': 0,
#    'default_branch': 'master'}},
#  'base': {'label': 'unitaryfund:master',
#   'ref': 'master',
#   'sha': '32610a044dd015e12441915fb9c28312c4b920db',
#   'user': {'login': 'unitaryfund',
#    'id': 50056634,
#    'node_id': 'MDEyOk9yZ2FuaXphdGlvbjUwMDU2NjM0',
#    'avatar_url': 'https://avatars.githubusercontent.com/u/50056634?v=4',
#    'gravatar_id': '',
#    'url': 'https://api.github.com/users/unitaryfund',
#    'html_url': 'https://github.com/unitaryfund',
#    'followers_url': 'https://api.github.com/users/unitaryfund/followers',
#    'following_url': 'https://api.github.com/users/unitaryfund/following{/other_user}',
#    'gists_url': 'https://api.github.com/users/unitaryfund/gists{/gist_id}',
#    'starred_url': 'https://api.github.com/users/unitaryfund/starred{/owner}{/repo}',
#    'subscriptions_url': 'https://api.github.com/users/unitaryfund/subscriptions',
#    'organizations_url': 'https://api.github.com/users/unitaryfund/orgs',
#    'repos_url': 'https://api.github.com/users/unitaryfund/repos',
#    'events_url': 'https://api.github.com/users/unitaryfund/events{/privacy}',
#    'received_events_url': 'https://api.github.com/users/unitaryfund/received_events',
#    'type': 'Organization',
#    'site_admin': False},
#   'repo': {'id': 236706881,
#    'node_id': 'MDEwOlJlcG9zaXRvcnkyMzY3MDY4ODE=',
#    'name': 'mitiq',
#    'full_name': 'unitaryfund/mitiq',
#    'private': False,
#    'owner': {'login': 'unitaryfund',
#     'id': 50056634,
#     'node_id': 'MDEyOk9yZ2FuaXphdGlvbjUwMDU2NjM0',
#     'avatar_url': 'https://avatars.githubusercontent.com/u/50056634?v=4',
#     'gravatar_id': '',
#     'url': 'https://api.github.com/users/unitaryfund',
#     'html_url': 'https://github.com/unitaryfund',
#     'followers_url': 'https://api.github.com/users/unitaryfund/followers',
#     'following_url': 'https://api.github.com/users/unitaryfund/following{/other_user}',
#     'gists_url': 'https://api.github.com/users/unitaryfund/gists{/gist_id}',
#     'starred_url': 'https://api.github.com/users/unitaryfund/starred{/owner}{/repo}',
#     'subscriptions_url': 'https://api.github.com/users/unitaryfund/subscriptions',
#     'organizations_url': 'https://api.github.com/users/unitaryfund/orgs',
#     'repos_url': 'https://api.github.com/users/unitaryfund/repos',
#     'events_url': 'https://api.github.com/users/unitaryfund/events{/privacy}',
#     'received_events_url': 'https://api.github.com/users/unitaryfund/received_events',
#     'type': 'Organization',
#     'site_admin': False},
#    'html_url': 'https://github.com/unitaryfund/mitiq',
#    'description': 'Mitiq is an open source toolkit for implementing error mitigation techniques on most current intermediate-scale quantum computers.',
#    'fork': False,
#    'url': 'https://api.github.com/repos/unitaryfund/mitiq',
#    'forks_url': 'https://api.github.com/repos/unitaryfund/mitiq/forks',
#    'keys_url': 'https://api.github.com/repos/unitaryfund/mitiq/keys{/key_id}',
#    'collaborators_url': 'https://api.github.com/repos/unitaryfund/mitiq/collaborators{/collaborator}',
#    'teams_url': 'https://api.github.com/repos/unitaryfund/mitiq/teams',
#    'hooks_url': 'https://api.github.com/repos/unitaryfund/mitiq/hooks',
#    'issue_events_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/events{/number}',
#    'events_url': 'https://api.github.com/repos/unitaryfund/mitiq/events',
#    'assignees_url': 'https://api.github.com/repos/unitaryfund/mitiq/assignees{/user}',
#    'branches_url': 'https://api.github.com/repos/unitaryfund/mitiq/branches{/branch}',
#    'tags_url': 'https://api.github.com/repos/unitaryfund/mitiq/tags',
#    'blobs_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/blobs{/sha}',
#    'git_tags_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/tags{/sha}',
#    'git_refs_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/refs{/sha}',
#    'trees_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/trees{/sha}',
#    'statuses_url': 'https://api.github.com/repos/unitaryfund/mitiq/statuses/{sha}',
#    'languages_url': 'https://api.github.com/repos/unitaryfund/mitiq/languages',
#    'stargazers_url': 'https://api.github.com/repos/unitaryfund/mitiq/stargazers',
#    'contributors_url': 'https://api.github.com/repos/unitaryfund/mitiq/contributors',
#    'subscribers_url': 'https://api.github.com/repos/unitaryfund/mitiq/subscribers',
#    'subscription_url': 'https://api.github.com/repos/unitaryfund/mitiq/subscription',
#    'commits_url': 'https://api.github.com/repos/unitaryfund/mitiq/commits{/sha}',
#    'git_commits_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/commits{/sha}',
#    'comments_url': 'https://api.github.com/repos/unitaryfund/mitiq/comments{/number}',
#    'issue_comment_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/comments{/number}',
#    'contents_url': 'https://api.github.com/repos/unitaryfund/mitiq/contents/{+path}',
#    'compare_url': 'https://api.github.com/repos/unitaryfund/mitiq/compare/{base}...{head}',
#    'merges_url': 'https://api.github.com/repos/unitaryfund/mitiq/merges',
#    'archive_url': 'https://api.github.com/repos/unitaryfund/mitiq/{archive_format}{/ref}',
#    'downloads_url': 'https://api.github.com/repos/unitaryfund/mitiq/downloads',
#    'issues_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues{/number}',
#    'pulls_url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls{/number}',
#    'milestones_url': 'https://api.github.com/repos/unitaryfund/mitiq/milestones{/number}',
#    'notifications_url': 'https://api.github.com/repos/unitaryfund/mitiq/notifications{?since,all,participating}',
#    'labels_url': 'https://api.github.com/repos/unitaryfund/mitiq/labels{/name}',
#    'releases_url': 'https://api.github.com/repos/unitaryfund/mitiq/releases{/id}',
#    'deployments_url': 'https://api.github.com/repos/unitaryfund/mitiq/deployments',
#    'created_at': '2020-01-28T10:14:19Z',
#    'updated_at': '2022-05-20T08:35:33Z',
#    'pushed_at': '2022-05-20T16:42:17Z',
#    'git_url': 'git://github.com/unitaryfund/mitiq.git',
#    'ssh_url': 'git@github.com:unitaryfund/mitiq.git',
#    'clone_url': 'https://github.com/unitaryfund/mitiq.git',
#    'svn_url': 'https://github.com/unitaryfund/mitiq',
#    'homepage': 'https://mitiq.readthedocs.io/en/stable/',
#    'size': 19545,
#    'stargazers_count': 200,
#    'watchers_count': 200,
#    'language': 'Python',
#    'has_issues': True,
#    'has_projects': True,
#    'has_downloads': True,
#    'has_wiki': True,
#    'has_pages': True,
#    'forks_count': 84,
#    'mirror_url': None,
#    'archived': False,
#    'disabled': False,
#    'open_issues_count': 81,
#    'license': {'key': 'gpl-3.0',
#     'name': 'GNU General Public License v3.0',
#     'spdx_id': 'GPL-3.0',
#     'url': 'https://api.github.com/licenses/gpl-3.0',
#     'node_id': 'MDc6TGljZW5zZTk='},
#    'allow_forking': True,
#    'is_template': False,
#    'topics': ['cirq',
#     'error-mitigation',
#     'qiskit',
#     'quantum-computers',
#     'quantum-error-mitigation',
#     'quantum-programming',
#     'unitaryhack'],
#    'visibility': 'public',
#    'forks': 84,
#    'open_issues': 81,
#    'watchers': 200,
#    'default_branch': 'master'}},
#  '_links': {'self': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384'},
#   'html': {'href': 'https://github.com/unitaryfund/mitiq/pull/384'},
#   'issue': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/issues/384'},
#   'comments': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/issues/384/comments'},
#   'review_comments': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384/comments'},
#   'review_comment': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/comments{/number}'},
#   'commits': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/pulls/384/commits'},
#   'statuses': {'href': 'https://api.github.com/repos/unitaryfund/mitiq/statuses/d213a012351a09b17fee0a6936e137ee64f5f5db'}},
#  'author_association': 'MEMBER',
#  'auto_merge': None,
#  'active_lock_reason': None,
#  'merged': False,
#  'mergeable': None,
#  'rebaseable': None,
#  'mergeable_state': 'unknown',
#  'merged_by': None,
#  'comments': 2,
#  'review_comments': 0,
#  'maintainer_can_modify': False,
#  'commits': 4,
#  'additions': 18,
#  'deletions': 1,
#  'changed_files': 3}


# {'id': 236706881,
#  'node_id': 'MDEwOlJlcG9zaXRvcnkyMzY3MDY4ODE=',
#  'name': 'mitiq',
#  'full_name': 'unitaryfund/mitiq',
#  'private': False,
#  'owner': {'login': 'unitaryfund',
#   'id': 50056634,
#   'node_id': 'MDEyOk9yZ2FuaXphdGlvbjUwMDU2NjM0',
#   'avatar_url': 'https://avatars.githubusercontent.com/u/50056634?v=4',
#   'gravatar_id': '',
#   'url': 'https://api.github.com/users/unitaryfund',
#   'html_url': 'https://github.com/unitaryfund',
#   'followers_url': 'https://api.github.com/users/unitaryfund/followers',
#   'following_url': 'https://api.github.com/users/unitaryfund/following{/other_user}',
#   'gists_url': 'https://api.github.com/users/unitaryfund/gists{/gist_id}',
#   'starred_url': 'https://api.github.com/users/unitaryfund/starred{/owner}{/repo}',
#   'subscriptions_url': 'https://api.github.com/users/unitaryfund/subscriptions',
#   'organizations_url': 'https://api.github.com/users/unitaryfund/orgs',
#   'repos_url': 'https://api.github.com/users/unitaryfund/repos',
#   'events_url': 'https://api.github.com/users/unitaryfund/events{/privacy}',
#   'received_events_url': 'https://api.github.com/users/unitaryfund/received_events',
#   'type': 'Organization',
#   'site_admin': False},
#  'html_url': 'https://github.com/unitaryfund/mitiq',
#  'description': 'Mitiq is an open source toolkit for implementing error mitigation techniques on most current intermediate-scale quantum computers.',
#  'fork': False,
#  'url': 'https://api.github.com/repos/unitaryfund/mitiq',
#  'forks_url': 'https://api.github.com/repos/unitaryfund/mitiq/forks',
#  'keys_url': 'https://api.github.com/repos/unitaryfund/mitiq/keys{/key_id}',
#  'collaborators_url': 'https://api.github.com/repos/unitaryfund/mitiq/collaborators{/collaborator}',
#  'teams_url': 'https://api.github.com/repos/unitaryfund/mitiq/teams',
#  'hooks_url': 'https://api.github.com/repos/unitaryfund/mitiq/hooks',
#  'issue_events_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/events{/number}',
#  'events_url': 'https://api.github.com/repos/unitaryfund/mitiq/events',
#  'assignees_url': 'https://api.github.com/repos/unitaryfund/mitiq/assignees{/user}',
#  'branches_url': 'https://api.github.com/repos/unitaryfund/mitiq/branches{/branch}',
#  'tags_url': 'https://api.github.com/repos/unitaryfund/mitiq/tags',
#  'blobs_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/blobs{/sha}',
#  'git_tags_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/tags{/sha}',
#  'git_refs_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/refs{/sha}',
#  'trees_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/trees{/sha}',
#  'statuses_url': 'https://api.github.com/repos/unitaryfund/mitiq/statuses/{sha}',
#  'languages_url': 'https://api.github.com/repos/unitaryfund/mitiq/languages',
#  'stargazers_url': 'https://api.github.com/repos/unitaryfund/mitiq/stargazers',
#  'contributors_url': 'https://api.github.com/repos/unitaryfund/mitiq/contributors',
#  'subscribers_url': 'https://api.github.com/repos/unitaryfund/mitiq/subscribers',
#  'subscription_url': 'https://api.github.com/repos/unitaryfund/mitiq/subscription',
#  'commits_url': 'https://api.github.com/repos/unitaryfund/mitiq/commits{/sha}',
#  'git_commits_url': 'https://api.github.com/repos/unitaryfund/mitiq/git/commits{/sha}',
#  'comments_url': 'https://api.github.com/repos/unitaryfund/mitiq/comments{/number}',
#  'issue_comment_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues/comments{/number}',
#  'contents_url': 'https://api.github.com/repos/unitaryfund/mitiq/contents/{+path}',
#  'compare_url': 'https://api.github.com/repos/unitaryfund/mitiq/compare/{base}...{head}',
#  'merges_url': 'https://api.github.com/repos/unitaryfund/mitiq/merges',
#  'archive_url': 'https://api.github.com/repos/unitaryfund/mitiq/{archive_format}{/ref}',
#  'downloads_url': 'https://api.github.com/repos/unitaryfund/mitiq/downloads',
#  'issues_url': 'https://api.github.com/repos/unitaryfund/mitiq/issues{/number}',
#  'pulls_url': 'https://api.github.com/repos/unitaryfund/mitiq/pulls{/number}',
#  'milestones_url': 'https://api.github.com/repos/unitaryfund/mitiq/milestones{/number}',
#  'notifications_url': 'https://api.github.com/repos/unitaryfund/mitiq/notifications{?since,all,participating}',
#  'labels_url': 'https://api.github.com/repos/unitaryfund/mitiq/labels{/name}',
#  'releases_url': 'https://api.github.com/repos/unitaryfund/mitiq/releases{/id}',
#  'deployments_url': 'https://api.github.com/repos/unitaryfund/mitiq/deployments',
#  'created_at': '2020-01-28T10:14:19Z',
#  'updated_at': '2022-05-20T08:35:33Z',
#  'pushed_at': '2022-05-20T16:42:17Z',
#  'git_url': 'git://github.com/unitaryfund/mitiq.git',
#  'ssh_url': 'git@github.com:unitaryfund/mitiq.git',
#  'clone_url': 'https://github.com/unitaryfund/mitiq.git',
#  'svn_url': 'https://github.com/unitaryfund/mitiq',
#  'homepage': 'https://mitiq.readthedocs.io/en/stable/',
#  'size': 19545,
#  'stargazers_count': 200,
#  'watchers_count': 200,
#  'language': 'Python',
#  'has_issues': True,
#  'has_projects': True,
#  'has_downloads': True,
#  'has_wiki': True,
#  'has_pages': True,
#  'forks_count': 84,
#  'mirror_url': None,
#  'archived': False,
#  'disabled': False,
#  'open_issues_count': 81,
#  'license': {'key': 'gpl-3.0',
#   'name': 'GNU General Public License v3.0',
#   'spdx_id': 'GPL-3.0',
#   'url': 'https://api.github.com/licenses/gpl-3.0',
#   'node_id': 'MDc6TGljZW5zZTk='},
#  'allow_forking': True,
#  'is_template': False,
#  'topics': ['cirq',
#   'error-mitigation',
#   'qiskit',
#   'quantum-computers',
#   'quantum-error-mitigation',
#   'quantum-programming',
#   'unitaryhack'],
#  'visibility': 'public',
#  'forks': 84,
#  'open_issues': 81,
#  'watchers': 200,
#  'default_branch': 'master',
#  'temp_clone_token': None,
#  'organization': {'login': 'unitaryfund',
#   'id': 50056634,
#   'node_id': 'MDEyOk9yZ2FuaXphdGlvbjUwMDU2NjM0',
#   'avatar_url': 'https://avatars.githubusercontent.com/u/50056634?v=4',
#   'gravatar_id': '',
#   'url': 'https://api.github.com/users/unitaryfund',
#   'html_url': 'https://github.com/unitaryfund',
#   'followers_url': 'https://api.github.com/users/unitaryfund/followers',
#   'following_url': 'https://api.github.com/users/unitaryfund/following{/other_user}',
#   'gists_url': 'https://api.github.com/users/unitaryfund/gists{/gist_id}',
#   'starred_url': 'https://api.github.com/users/unitaryfund/starred{/owner}{/repo}',
#   'subscriptions_url': 'https://api.github.com/users/unitaryfund/subscriptions',
#   'organizations_url': 'https://api.github.com/users/unitaryfund/orgs',
#   'repos_url': 'https://api.github.com/users/unitaryfund/repos',
#   'events_url': 'https://api.github.com/users/unitaryfund/events{/privacy}',
#   'received_events_url': 'https://api.github.com/users/unitaryfund/received_events',
#   'type': 'Organization',
#   'site_admin': False},
#  'network_count': 84,
#  'subscribers_count': 11}
