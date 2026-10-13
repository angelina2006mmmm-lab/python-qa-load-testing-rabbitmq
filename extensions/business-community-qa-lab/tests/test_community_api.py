import pytest
from fastapi.testclient import TestClient
from community_qa.app import create_app
@pytest.fixture
def c():
 with TestClient(create_app()) as client:yield client
H={"X-User-Id":"1"}
def test_health(c):assert c.get("/health").json()["status"]=="ok"
def test_feed(c):assert c.get("/v1/posts").json()["total"]==2
def test_page(c):
 assert len(c.get("/v1/posts?page=1&size=1").json()["items"])==1
 assert not c.get("/v1/posts?page=3&size=1").json()["items"]
def test_invalid_page(c):
 assert c.get("/v1/posts?page=0").status_code==422
 assert c.get("/v1/posts?size=100").status_code==422
def test_missing(c):assert c.get("/v1/posts/900").status_code==404
def test_create(c):
 r=c.post("/v1/posts",headers=H,json={"title":"Бизнес","body":"Партнёры"})
 assert r.status_code==201
 assert c.get("/v1/posts/"+str(r.json()["id"])).json()["body"]=="Партнёры"
def test_auth_required(c):
 assert c.post("/v1/posts",json={"title":"Бизнес","body":"Текст"}).status_code==401
def test_unknown_auth(c):
 assert c.post("/v1/posts",headers={"X-User-Id":"999"},json={"title":"Бизнес","body":"Текст"}).status_code==401
def test_invalid_fields(c):
 for x in [{"title":"x","body":"y"},{"title":"good","body":""},{"title":"a"*81,"body":"ok"}]:
  assert c.post("/v1/posts",headers=H,json=x).status_code==422
def test_extra_field(c):
 assert c.post("/v1/posts",headers=H,json={"title":"Бизнес","body":"Текст","admin":1}).status_code==422
def test_delete_own(c):
 assert c.delete("/v1/posts/1",headers=H).status_code==204
 assert c.get("/v1/posts/1").status_code==404
def test_delete_other(c):
 assert c.delete("/v1/posts/2",headers=H).status_code==403
 assert c.get("/v1/posts/2").status_code==200
def test_delete_unknown(c):assert c.delete("/v1/posts/900",headers=H).status_code==404
def test_comment(c):
 r=c.post("/v1/posts/1/comments",headers={"X-User-Id":"2"},json={"text":"Напишите мне"})
 assert r.status_code==201
 assert c.get("/v1/posts/1/comments").json()["items"][0]["author_id"]==2
def test_comment_auth(c):
 assert c.post("/v1/posts/1/comments",json={"text":"Тест"}).status_code==401
def test_comment_empty(c):
 assert c.post("/v1/posts/1/comments",headers=H,json={"text":""}).status_code==422
def test_comment_unknown_post(c):
 assert c.post("/v1/posts/999/comments",headers=H,json={"text":"Тест"}).status_code==404
def test_cascade(c):
 c.post("/v1/posts/1/comments",headers=H,json={"text":"Тест"})
 assert c.delete("/v1/posts/1",headers=H).status_code==204
 assert c.get("/v1/posts/1/comments").status_code==404
def test_order(c):
 ids=[x["id"] for x in c.get("/v1/posts").json()["items"]]
 assert ids==sorted(ids,reverse=True)
def test_json(c):assert "application/json" in c.get("/v1/posts").headers["content-type"]
