# Reproducible test cases
TC01 Create: POST /v1/posts with X-User-Id:1 and valid JSON -> 201, GET by id -> 200 and identical text.
TC02 Permission: DELETE /v1/posts/2 as X-User-Id:1 -> 403, then GET -> 200.
TC03 Empty comment: POST /v1/posts/1/comments with empty text -> 422, no record.
TC04 Pagination: GET /v1/posts?page=1&size=1 and page=2 -> distinct rows, page=0 -> 422.
TC05 Unknown actor: POST /v1/posts as X-User-Id:999 -> 401.
