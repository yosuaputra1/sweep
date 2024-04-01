import html
import multiprocessing

import typer
from fastapi.testclient import TestClient
from github import Github

from sweepai.api import app
from sweepai.utils.github_utils import get_github_client, get_installation_id, get_installation


def fetch_pr_review_request(issue_url: str, __version__: str = "0"):
    (
        protocol_name,
        _,
        _base_url,
        org_name,
        repo_name,
        _issues,
        pr_number,
    ) = issue_url.split("/")
    print("Fetching installation ID...")
    installation_id = get_installation_id(org_name)
    installation = get_installation(org_name)
    print("Fetching access token...")
    _token, g = get_github_client(installation_id)
    g: Github = g
    print("Fetching repo...")
    org = g.get_organization(org_name)
    repo = g.get_repo(f"{org_name}/{repo_name}")
    pr = repo.get_pull(int(pr_number))
    comments = pr.get_review_comments()
    comment_requests = []

    for comment in comments:
        comment_created_request = {
            "action": "created",
            "comment": comment.raw_data,
            "pull_request": pr.raw_data,
            "repository": repo.raw_data,
            "organization": org.raw_data,
            "sender": comment.raw_data['user'],
            "installation": installation
        }
        comment_requests.append(comment_created_request)
    return comment_requests


def send_request(issue_request):
    with TestClient(app) as client:
        response = client.post(
            "/", json=issue_request.dict(), headers={"X-GitHub-Event": "issues"}
        )
        print(response)  # or return response, depending on your needs


def update_pr_review_comments(
    pr_url: str,
    better_stack_prefix: str = "https://logs.betterstack.com/team/199101/tail?rf=now-30m&q=metadata.issue_url%3A",
    debug: bool = True,
):
    pr_url: str = pr_url or typer.prompt("PR URL")
    print(f"Fetching issue metadata...")
    comment_requests = fetch_pr_review_request(pr_url)
    print(f"Sending request...")

    client = TestClient(app)
    for request in comment_requests:
        response = client.post(
            "/", json=request, headers={"X-GitHub-Event": "pull_request_review_comment"}
        )
        print(response)


    better_stack_link = f"{better_stack_prefix}{html.escape(pr_url)}"
    print(f"Track the logs at the following link:\n\n{better_stack_link}")


if __name__ == "__main__":
    typer.run(update_pr_review_comments)
