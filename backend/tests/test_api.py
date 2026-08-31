import pytest
from httpx import AsyncClient
from pathlib import Path


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data


@pytest.mark.asyncio
async def test_create_and_list_repositories(async_client: AsyncClient):
    payload = {
        "url": "https://github.com/fastapi/fastapi",
        "name": "fastapi",
        "owner": "fastapi",
        "default_branch": "master"
    }
    create_res = await async_client.post("/api/repositories", json=payload)
    assert create_res.status_code == 201
    repo_data = create_res.json()
    assert repo_data["name"] == "fastapi"
    assert repo_data["owner"] == "fastapi"

    list_res = await async_client.get("/api/repositories")
    assert list_res.status_code == 200
    repos = list_res.json()
    assert len(repos) >= 1
    assert any(r["url"] == payload["url"] for r in repos)


@pytest.mark.asyncio
async def test_create_analysis_run_and_add_findings(
    async_client: AsyncClient,
    sample_local_git_repo: Path
):
    # 1. Trigger analysis with local test repo
    payload = {
        "repo_url": str(sample_local_git_repo),
        "branch": "master",
        "shallow_depth": 50
    }
    res = await async_client.post("/api/analyses", json=payload)
    assert res.status_code == 201
    analysis = res.json()
    assert analysis["id"] is not None
    assert analysis["status"] in ["RUNNING", "COMPLETED"]
    assert analysis["commit_hash"] is not None

    analysis_id = analysis["id"]

    # 2. Add finding to analysis
    finding_payload = {
        "finding": "Missing Error Handling in Gateway",
        "category": "CODE",
        "severity": "CRITICAL",
        "confidence": 0.98,
        "verification_status": "VERIFIED",
        "verification_notes": "Reproduction test failed with UnhandledException.",
        "evidence": [
            {
                "type": "code",
                "file": "src/main.py",
                "line_start": 1,
                "line_end": 5,
                "description": "Function does not catch connection errors."
            }
        ]
    }
    f_res = await async_client.post(f"/api/analyses/{analysis_id}/findings", json=finding_payload)
    assert f_res.status_code == 201
    finding_data = f_res.json()
    assert finding_data["finding"] == finding_payload["finding"]
    assert len(finding_data["evidence"]) == 1
    assert finding_data["evidence"][0]["file"] == "src/main.py"

    # 3. Retrieve analysis run and check populated findings
    get_res = await async_client.get(f"/api/analyses/{analysis_id}")
    assert get_res.status_code == 200
    fetched_analysis = get_res.json()
    assert len(fetched_analysis["findings"]) >= 1
    assert any(f["severity"] == "CRITICAL" for f in fetched_analysis["findings"])

    # 4. List sandbox files
    files_res = await async_client.get(f"/api/sandboxes/{analysis_id}/files")
    assert files_res.status_code == 200
    files_data = files_res.json()
    assert files_data["count"] == 3
    assert "README.md" in files_data["files"]

    # 5. Read sandbox file content
    content_res = await async_client.get(
        f"/api/sandboxes/{analysis_id}/file-content",
        params={"file_path": "README.md"}
    )
    assert content_res.status_code == 200
    assert "Test Repo" in content_res.json()["content"]

    # 6. Cleanup sandbox
    del_res = await async_client.delete(f"/api/sandboxes/{analysis_id}")
    assert del_res.status_code == 200
    assert del_res.json()["cleaned"] is True
