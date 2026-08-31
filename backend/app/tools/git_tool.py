import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from git import Repo, NULL_TREE


@dataclass
class FileChurnStat:
    file_path: str
    commit_count: int
    insertions: int
    deletions: int
    bugfix_count: int
    authors: Dict[str, int] = field(default_factory=dict)


@dataclass
class GitAnalysisResult:
    total_commits: int
    total_authors: int
    top_churn_files: List[FileChurnStat]
    bugfix_commits: int
    reverted_commits: int
    recent_commits: List[Dict[str, str]]
    bus_factor_risks: List[Dict[str, any]]


class GitTool:
    """Safely extracts deterministic git history metrics, churn, bugfix concentration, and bus factor."""

    BUGFIX_PATTERN = re.compile(r'\b(fix|bug|hotfix|patch|resolve|issue|defect)\b', re.IGNORECASE)
    REVERT_PATTERN = re.compile(r'\b(revert|rollback)\b', re.IGNORECASE)

    @classmethod
    def analyze_repository(
        cls,
        repo_path: Path,
        max_commits: int = 200,
        top_n_files: int = 15,
    ) -> GitAnalysisResult:
        """
        Analyzes commit history to compute churn metrics, bug-fix density, and author ownership.
        """
        repo_path = Path(repo_path)
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitAnalysisResult(
                total_commits=0,
                total_authors=0,
                top_churn_files=[],
                bugfix_commits=0,
                reverted_commits=0,
                recent_commits=[],
                bus_factor_risks=[],
            )

        repo = None
        try:
            repo = Repo(str(repo_path))
            commits = list(repo.iter_commits(max_count=max_commits))
            total_commits = len(commits)

            file_churn: Dict[str, FileChurnStat] = {}
            authors_set = set()
            bugfix_commits = 0
            reverted_commits = 0
            recent_commits = []

            for commit in commits:
                author_name = commit.author.name or "Unknown"
                authors_set.add(author_name)
                msg = commit.message.strip()

                is_bugfix = bool(cls.BUGFIX_PATTERN.search(msg))
                is_revert = bool(cls.REVERT_PATTERN.search(msg))

                if is_bugfix:
                    bugfix_commits += 1
                if is_revert:
                    reverted_commits += 1

                if len(recent_commits) < 10:
                    recent_commits.append({
                        "hexsha": commit.hexsha[:8],
                        "author": author_name,
                        "date": commit.committed_datetime.isoformat(),
                        "message": msg.split("\n")[0][:100],
                        "is_bugfix": is_bugfix,
                    })

                # Check diff stats for stats per file
                diffs = commit.diff(commit.parents[0]) if commit.parents else commit.diff(NULL_TREE)
                for diff in diffs:
                        file_path = diff.a_path or diff.b_path
                        if not file_path:
                            continue

                        # Normalize path
                        file_path = Path(file_path).as_posix()
                        if file_path.startswith(".git/"):
                            continue

                        if file_path not in file_churn:
                            file_churn[file_path] = FileChurnStat(
                                file_path=file_path,
                                commit_count=0,
                                insertions=0,
                                deletions=0,
                                bugfix_count=0,
                                authors=defaultdict(int),
                            )

                        stat = file_churn[file_path]
                        stat.commit_count += 1
                        stat.authors[author_name] += 1
                        if is_bugfix:
                            stat.bugfix_count += 1

            # Identify top churn files
            sorted_churn = sorted(
                file_churn.values(),
                key=lambda x: (x.commit_count, x.bugfix_count),
                reverse=True
            )[:top_n_files]

            # Detect bus factor risks (files with > 80% commits by single author when total commits >= 5)
            bus_factor_risks = []
            for stat in sorted_churn:
                if stat.commit_count >= 5:
                    top_author, author_commits = max(stat.authors.items(), key=lambda a: a[1])
                    ratio = author_commits / stat.commit_count
                    if ratio >= 0.8:
                        bus_factor_risks.append({
                            "file": stat.file_path,
                            "dominant_author": top_author,
                            "author_commit_ratio": round(ratio, 2),
                            "total_commits": stat.commit_count,
                            "risk": "High ownership concentration (Single point of failure)",
                        })

            return GitAnalysisResult(
                total_commits=total_commits,
                total_authors=len(authors_set),
                top_churn_files=sorted_churn,
                bugfix_commits=bugfix_commits,
                reverted_commits=reverted_commits,
                recent_commits=recent_commits,
                bus_factor_risks=bus_factor_risks,
            )
        finally:
            if repo:
                repo.close()
