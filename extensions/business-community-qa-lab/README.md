# Business Community QA Lab (educational)

An independent API mock for a fictional entrepreneur social feed. Not SberBusiness.
Tested features: posts/comments, pagination, input validation, user ownership checks, DDL/DML with SQLite.
20 automated HTTP tests cover success and 401/403/404/422. CI runs pytest.
Manual artefacts: 16 proposed web/mobile checks (NOT executed), 5 written test cases, a hypothetical bug-report example.
Local: python -m pip install -r requirements.txt ; python -m pytest -q tests/
Run mock: uvicorn community_qa.app:app --reload; OpenAPI: http://127.0.0.1:8000/docs
X-User-Id is a fake test-only identity and NOT secure authentication. There is no real UI or bank integration.
