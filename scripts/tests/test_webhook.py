from scripts.app import webhook, gatherUpdatedFiles, formAWSString
from unittest import TestCase
from os.path import dirname, join

class TestWebhooks(TestCase):

    def test_gather_updated_files(self):
        "Converts GitHub's JSON to a list of files to update in S3."
        
        files_list = ['scripts/static/css/lens.css', 'scripts/static/js/index.js', 'scripts/static/js/map.js']

        files_list_output = gatherUpdatedFiles(payload_master)

        self.assertEqual(files_list_output, files_list)

    def test_form_aws_string(self):
        "Should return awscli command if file is in static folder, or return None if file is of some other type."
        
        f1 = 'scripts/static/css/lens.css'
        f2 = 'scripts/static/js/index.js'

        f1_output = formAWSString(f1)
        f2_output = formAWSString(f2)

        self.assertEqual(f1_output, 'aws s3 cp /Users/Tom/projects/land-records/repo/scripts/static/css/lens.css s3://lensnola/land-records/css/lens.css --acl public-read')
        self.assertEqual(f2_output, 'aws s3 cp /Users/Tom/projects/land-records/repo/scripts/static/js/index.js s3://lensnola/land-records/js/index.js --acl public-read')

payload_master = {
  "ref": "refs/heads/master",
  "before": "9ae4c6315c0d105b78e7877e81e482a9b4cac87b",
  "after": "bd842e5ea6d37675d6074528152a963f54514162",
  "created": False,
  "deleted": False,
  "forced": False,
  "base_ref": None,
  "compare": "https://github.com/TheLens/land-records/compare/9ae4c6315c0d...bd842e5ea6d3",
  "commits": [
    {
      "id": "bd842e5ea6d37675d6074528152a963f54514162",
      "distinct": True,
      "message": ".",
      "timestamp": "2015-03-09T14:53:53-05:00",
      "url": "https://github.com/TheLens/land-records/commit/bd842e5ea6d37675d6074528152a963f54514162",
      "author": {
        "name": "ThomasThoren",
        "email": "tthoren@thelensnola.org"
      },
      "committer": {
        "name": "ThomasThoren",
        "email": "tthoren@thelensnola.org"
      },
      "added": [
          "scripts/static/css/lens.css",
          "scripts/templates/search.html"
      ],
      "removed": [
        'scripts/app.py'
      ],
      "modified": [
        "scripts/static/js/index.js",
        "scripts/templates/search.html",
        "scripts/static/js/map.js"
      ]
    }
  ],
  "head_commit": {
    "id": "bd842e5ea6d37675d6074528152a963f54514162",
    "distinct": True,
    "message": ".",
    "timestamp": "2015-03-09T14:53:53-05:00",
    "url": "https://github.com/TheLens/land-records/commit/bd842e5ea6d37675d6074528152a963f54514162",
    "author": {
      "name": "ThomasThoren",
      "email": "tthoren@thelensnola.org"
    },
    "committer": {
      "name": "ThomasThoren",
      "email": "tthoren@thelensnola.org"
    },
    "added": [

    ],
    "removed": [

    ],
    "modified": [
      "scripts/static/js/index.js",
      "scripts/static/js/map.js"
    ]
  },
  "repository": {
    "id": 28202015,
    "name": "land-records",
    "full_name": "TheLens/land-records",
    "owner": {
      "name": "TheLens",
      "email": ""
    },
    "private": False,
    "html_url": "https://github.com/TheLens/land-records",
    "description": "",
    "fork": False,
    "url": "https://github.com/TheLens/land-records",
    "forks_url": "https://api.github.com/repos/TheLens/land-records/forks",
    "keys_url": "https://api.github.com/repos/TheLens/land-records/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/TheLens/land-records/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/TheLens/land-records/teams",
    "hooks_url": "https://api.github.com/repos/TheLens/land-records/hooks",
    "issue_events_url": "https://api.github.com/repos/TheLens/land-records/issues/events{/number}",
    "events_url": "https://api.github.com/repos/TheLens/land-records/events",
    "assignees_url": "https://api.github.com/repos/TheLens/land-records/assignees{/user}",
    "branches_url": "https://api.github.com/repos/TheLens/land-records/branches{/branch}",
    "tags_url": "https://api.github.com/repos/TheLens/land-records/tags",
    "blobs_url": "https://api.github.com/repos/TheLens/land-records/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/TheLens/land-records/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/TheLens/land-records/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/TheLens/land-records/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/TheLens/land-records/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/TheLens/land-records/languages",
    "stargazers_url": "https://api.github.com/repos/TheLens/land-records/stargazers",
    "contributors_url": "https://api.github.com/repos/TheLens/land-records/contributors",
    "subscribers_url": "https://api.github.com/repos/TheLens/land-records/subscribers",
    "subscription_url": "https://api.github.com/repos/TheLens/land-records/subscription",
    "commits_url": "https://api.github.com/repos/TheLens/land-records/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/TheLens/land-records/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/TheLens/land-records/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/TheLens/land-records/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/TheLens/land-records/contents/{+path}",
    "compare_url": "https://api.github.com/repos/TheLens/land-records/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/TheLens/land-records/merges",
    "archive_url": "https://api.github.com/repos/TheLens/land-records/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/TheLens/land-records/downloads",
    "issues_url": "https://api.github.com/repos/TheLens/land-records/issues{/number}",
    "pulls_url": "https://api.github.com/repos/TheLens/land-records/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/TheLens/land-records/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/TheLens/land-records/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/TheLens/land-records/labels{/name}",
    "releases_url": "https://api.github.com/repos/TheLens/land-records/releases{/id}",
    "created_at": 1418937480,
    "updated_at": "2014-12-19T19:13:51Z",
    "pushed_at": 1425930838,
    "git_url": "git://github.com/TheLens/land-records.git",
    "ssh_url": "git@github.com:TheLens/land-records.git",
    "clone_url": "https://github.com/TheLens/land-records.git",
    "svn_url": "https://github.com/TheLens/land-records",
    "homepage": None,
    "size": 380,
    "stargazers_count": 0,
    "watchers_count": 0,
    "language": "Python",
    "has_issues": True,
    "has_downloads": True,
    "has_wiki": True,
    "has_pages": False,
    "forks_count": 0,
    "mirror_url": None,
    "open_issues_count": 27,
    "forks": 0,
    "open_issues": 27,
    "watchers": 0,
    "default_branch": "master",
    "stargazers": 0,
    "master_branch": "master",
    "organization": "TheLens"
  },
  "pusher": {
    "name": "ThomasThoren",
    "email": "thomasjthoren@gmail.com"
  },
  "organization": {
    "login": "TheLens",
    "id": 10246645,
    "url": "https://api.github.com/orgs/TheLens",
    "repos_url": "https://api.github.com/orgs/TheLens/repos",
    "events_url": "https://api.github.com/orgs/TheLens/events",
    "members_url": "https://api.github.com/orgs/TheLens/members{/member}",
    "public_members_url": "https://api.github.com/orgs/TheLens/public_members{/member}",
    "avatar_url": "https://avatars.githubusercontent.com/u/10246645?v=3",
    "description": ""
  },
  "sender": {
    "login": "ThomasThoren",
    "id": 5692185,
    "avatar_url": "https://avatars.githubusercontent.com/u/5692185?v=3",
    "gravatar_id": "",
    "url": "https://api.github.com/users/ThomasThoren",
    "html_url": "https://github.com/ThomasThoren",
    "followers_url": "https://api.github.com/users/ThomasThoren/followers",
    "following_url": "https://api.github.com/users/ThomasThoren/following{/other_user}",
    "gists_url": "https://api.github.com/users/ThomasThoren/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/ThomasThoren/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/ThomasThoren/subscriptions",
    "organizations_url": "https://api.github.com/users/ThomasThoren/orgs",
    "repos_url": "https://api.github.com/users/ThomasThoren/repos",
    "events_url": "https://api.github.com/users/ThomasThoren/events{/privacy}",
    "received_events_url": "https://api.github.com/users/ThomasThoren/received_events",
    "type": "User",
    "site_admin": False
  }
}

if __name__ == '__main__':
    unittest.main()