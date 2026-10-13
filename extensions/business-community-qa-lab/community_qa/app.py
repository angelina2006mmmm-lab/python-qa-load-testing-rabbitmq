"""Educational test API for a fictional entrepreneur community (not SberBusiness)."""
from pathlib import Path
import sqlite3
from fastapi import FastAPI,Header,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
BASE=Path(__file__).resolve().parents[1]
class Post(BaseModel):
 model_config=ConfigDict(extra="forbid")
 title:str=Field(min_length=3,max_length=80)
 body:str=Field(min_length=1,max_length=500)
class Comment(BaseModel):
 model_config=ConfigDict(extra="forbid")
 text:str=Field(min_length=1,max_length=300)
def create_app():
 db=sqlite3.connect(":memory:",check_same_thread=False)
 db.row_factory=sqlite3.Row
 db.execute("PRAGMA foreign_keys=ON")
 db.executescript((BASE/"sql/schema.sql").read_text(encoding="utf-8"))
 db.executescript((BASE/"sql/seed.sql").read_text(encoding="utf-8"))
 db.commit()
 app=FastAPI(title="Educational Business Community QA Mock")
 def user(n):
  if n is None or db.execute("SELECT id FROM users WHERE id=?",(n,)).fetchone() is None:raise HTTPException(401,"Test user required")
  return n
 @app.get("/health")
 def health():return {"status":"ok"}
 @app.get("/v1/posts")
 def feed(page:int=Query(1,ge=1),size:int=Query(5,ge=1,le=20)):
  count=db.execute("SELECT count(*) FROM posts").fetchone()[0]
  rows=db.execute("SELECT id,owner_id,title,body FROM posts ORDER BY id DESC LIMIT ? OFFSET ?",(size,(page-1)*size)).fetchall()
  return {"items":[dict(x) for x in rows],"total":count,"page":page,"size":size}
 @app.get("/v1/posts/{post_id}")
 def get(post_id:int):
  r=db.execute("SELECT id,owner_id,title,body FROM posts WHERE id=?",(post_id,)).fetchone()
  if r is None:raise HTTPException(404,"Missing post")
  return dict(r)
 @app.post("/v1/posts",status_code=201)
 def create(d:Post,x_user_id:int|None=Header(None,alias="X-User-Id")):
  n=user(x_user_id)
  with db:c=db.execute("INSERT INTO posts(owner_id,title,body) VALUES(?,?,?)",(n,d.title,d.body))
  return {"id":c.lastrowid,"owner_id":n,"title":d.title,"body":d.body}
 @app.delete("/v1/posts/{post_id}",status_code=204)
 def delete(post_id:int,x_user_id:int|None=Header(None,alias="X-User-Id")):
  n=user(x_user_id)
  r=db.execute("SELECT owner_id FROM posts WHERE id=?",(post_id,)).fetchone()
  if r is None:raise HTTPException(404,"Missing post")
  if r["owner_id"]!=n:raise HTTPException(403,"Wrong author")
  with db:db.execute("DELETE FROM posts WHERE id=?",(post_id,))
 @app.post("/v1/posts/{post_id}/comments",status_code=201)
 def comment(post_id:int,d:Comment,x_user_id:int|None=Header(None,alias="X-User-Id")):
  n=user(x_user_id)
  if db.execute("SELECT id FROM posts WHERE id=?",(post_id,)).fetchone() is None:raise HTTPException(404,"Missing post")
  with db:c=db.execute("INSERT INTO comments(post_id,author_id,text) VALUES(?,?,?)",(post_id,n,d.text))
  return {"id":c.lastrowid,"post_id":post_id,"author_id":n,"text":d.text}
 @app.get("/v1/posts/{post_id}/comments")
 def comments(post_id:int):
  if db.execute("SELECT id FROM posts WHERE id=?",(post_id,)).fetchone() is None:raise HTTPException(404,"Missing post")
  return {"items":[dict(x) for x in db.execute("SELECT id,post_id,author_id,text FROM comments WHERE post_id=? ORDER BY id",(post_id,))]}
 return app
app=create_app()
