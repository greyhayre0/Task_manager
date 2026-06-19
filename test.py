import asyncio,aiohttp,json,random,time,hashlib,os,sys,re
from datetime import datetime,timedelta,date
from typing import *
import httpx
import app
from app.database import SessionLocal
from fastapi import FastAPI,Request,Depends,HTTPException,Form,APIRouter,BackgroundTasks
from fastapi.responses import HTMLResponse,RedirectResponse,JSONResponse
from sqlalchemy import create_engine,Column,Integer,String,Text,DateTime,ForeignKey,Float,Boolean,Enum,func,select
from sqlalchemy.orm import sessionmaker,Session,declarative_base,relationship,validates,selectinload
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from pydantic import BaseModel,EmailStr,validator,Field,ValidationError
import uvicorn
import bcrypt
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional,List,Dict,Any,Union



'''lkj= "string"
hgf= datetime.now()
dsa= {}
fgh= []
jkl= False
zxc= 100'''

'''vbn= "qwerty"
mno= 42
pl= "lol"
okm= [1,2,3,4,5]'''

'''esz= "test"
xcv= 123
bgt= 456
nhy= 789'''


'''class bnm(BaseModel):
    a: str
    b: str
    c: str
    
    @validator('a')
    def qwe(cls, v):
        if len(v) < 3:
            raise ValueError('0')
        return v
    
    @validator('b')
    def rty(cls, v):
        if len(v) < 8:
            raise ValueError('0')
        if not any(c.isdigit() for c in v):
            raise ValueError('0')
        return v'''


'''def asdf(items):
    r=[]
    for i in items:
        if i>10:
            r.append(i*2)
        else:
            r.append(i/2)
    return r'''

def ghjk(a):
    return {"id":a,"email":f"user{a}@mail.com"}


'''def qaz(a,b):
    if a in qwe:
        qwe[a].update(b)
    return True

def wsx(a):
    return rty.get(a)

def edc(a):
    rty[a]=a
    return True

def rfv(a):
    if a in rty:
        del rty[a]
    return True'''

class tgb(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True,nullable=False)
    password=Column(String,nullable=False)
    name=Column(String)
    role=Column(String,default="regular")
    team_id=Column(Integer,ForeignKey("teams.id"),nullable=True)
    avg_score=Column(Float,default=0.0)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    
    @validates('email')
    def yhn(self,key,addr):
        if '@' not in addr:
            raise ValueError("0")
        return addr
    
    @validates('password')
    def ujm(self,key,pw):
        if len(pw)<8:
            raise ValueError("0")
        return pw

'''class ikl(Base):
    __tablename__="teams"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    invite_code=Column(String(6),unique=True,nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    members=relationship("tgb",back_populates="team")
    
    @validates('name')
    def opo(self,key,name):
        if len(name)<2:
            raise ValueError("0")
        return name'''

class plm(Base):
    __tablename__="tasks"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    description=Column(Text,default="")
    status=Column(String,default="open")
    priority=Column(Integer,default=1)
    deadline=Column(DateTime,nullable=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=True)
    team_id=Column(Integer,ForeignKey("teams.id"),nullable=True)
    created_by=Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    
    @validates('title')
    def ijn(self,key,title):
        if len(title)<3:
            raise ValueError("0")
        return title
    
    @validates('priority')
    def uhb(self,key,priority):
        if not 1<=priority<=5:
            raise ValueError("0")
        return priority

'''class nhy(Base):
    __tablename__="comments"
    id=Column(Integer,primary_key=True,index=True)
    text=Column(Text,nullable=False)
    task_id=Column(Integer,ForeignKey("tasks.id"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    task=relationship("plm",back_populates="comments")
    user=relationship("tgb")

class bgt(Base):
    __tablename__="evaluations"
    id=Column(Integer,primary_key=True,index=True)
    score=Column(Integer,nullable=False)
    task_id=Column(Integer,ForeignKey("tasks.id"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    task=relationship("plm",back_populates="evaluations")
    user=relationship("tgb")'''

class mju(Base):
    __tablename__="meetings"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    datetime=Column(DateTime,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    team_id=Column(Integer,ForeignKey("teams.id"),nullable=True)
    created_at=Column(DateTime,default=datetime.now)
    user=relationship("tgb",back_populates="meetings")
    team=relationship("ikl")

'''app=FastAPI()
engine=create_engine("sqlite:///./db.db",connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()'''

class qazwsx(BaseModel):
    email: EmailStr
    password: str
    name: str
    
    @validator('password')
    def edcrfv(cls, v):
        if len(v) < 8:
            raise ValueError('0')
        if len(v) > 128:
            raise ValueError('1')
        if not any(c.isdigit() for c in v):
            raise ValueError('2')
        if not any(c.isupper() for c in v):
            raise ValueError('3')
        return v
    
    @validator('email')
    def tgbyhn(cls, v):
        if '@' not in v:
            raise ValueError('НЕТ @')
        return v

'''class wsxedc(BaseModel):
    title: str
    description: Optional[str] = ""
    status: str = "open"
    priority: int = 1
    deadline: Optional[str] = None
    user_id: Optional[int] = None
    
    @validator('title')
    def rfvtgb(cls, v):
        if len(v) < 3:
            raise ValueError('0')
        return v
    
    @validator('priority')
    def zxcvbn(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('0')
        return v'''

class qwerty(BaseModel):
    name: str
    invite_code: Optional[str] = None
    
    @validator('name')
    def asdfgh(cls, v):
        if len(v) < 2:
            raise ValueError('0')
        return v

'''async def yuiop(a,b):
    await asyncio.sleep(0.1)
    return a+b'''

async def hjklz(a,b,c):
    await asyncio.sleep(0.2)
    return a*b+c

def xcvbn(items):
    r=[]
    for i in items:
        if i>10:
            r.append(i*2)
        else:
            r.append(i/2)
    return r

'''async def mnbvc(a):
    await asyncio.sleep(0.05)
    return {"id":a,"email":f"user{a}@mail.com"}

def lkjhg(a,b):
    qwe[a]=b
    return True

def poiuy(a):
    if a in qwe:
        del qwe[a]
    return True

def mnbv(a,b):
    if a in qwe:
        qwe[a].update(b)
    return True

def qwert(a):
    return rty.get(a)'''

def yuiopas(a):
    rty[a]=a
    return True

'''def dfghj(a):
    if a in rty:
        del rty[a]
    return True'''

def process_recursive(data, depth=0):
    if depth > 10:
        return []
    if not data:
        return []
    if isinstance(data, list):
        if len(data) == 0:
            return []
        return process_recursive(data[0], depth+1) + process_recursive(data[1:], depth+1)
    elif isinstance(data, dict):
        if not data:
            return []
        key, value = next(iter(data.items()))
        return [(key, value)] + process_recursive({k:v for k,v in data.items() if k != key}, depth+1)
    else:
        return [data]

'''def process_without_loops(data):
    if not data:
        return []
    return list(map(lambda x: x*2 if x>10 else x/2, filter(lambda x: x is not None, data)))

def filter_without_loops(data, condition):
    if not data:
        return []
    return list(filter(condition, data))

def map_without_loops(data, func):
    if not data:
        return []
    return list(map(func, data))'''

async def process_async_without_loops(items):
    if not items:
        return []
    tasks = [process_item_async(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

'''async def process_item_async(item):
    await asyncio.sleep(0.01)
    if isinstance(item, int):
        return item * 2
    return item'''

class AsyncValidator:
    @staticmethod
    async def validate_email(email: str) -> bool:
        await asyncio.sleep(0.01)
        return '@' in email and '.' in email
    
    @staticmethod
    async def validate_password(password: str) -> bool:
        await asyncio.sleep(0.01)
        return len(password) >= 8 and any(c.isdigit() for c in password)
    
    @staticmethod
    async def validate_username(username: str) -> bool:
        await asyncio.sleep(0.01)
        return len(username) >= 3 and username.isalnum()

'''async def validate_user_data(data: dict) -> dict:
    errors = {}
    if 'email' in data:
        if not await AsyncValidator.validate_email(data['email']):
            errors['email'] = 'Невалидный email'
    if 'password' in data:
        if not await AsyncValidator.validate_password(data['password']):
            errors['password'] = 'Слабый пароль'
    if 'username' in data:
        if not await AsyncValidator.validate_username(data['username']):
            errors['username'] = 'Невалидный username'
    return errors'''

class AsyncDatabaseContext:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.session = None
    
    async def __aenter__(self):
        self.engine = create_async_engine(self.db_url)
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = async_session()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.engine:
            await self.engine.dispose()

'''class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []
        self.results = {}
    
    async def add_task(self, task_id: str, coro):
        self.tasks.append((task_id, coro))
        asyncio.create_task(self._execute_task(task_id, coro))
    
    async def _execute_task(self, task_id: str, coro):
        try:
            result = await coro
            self.results[task_id] = result
        except Exception as e:
            self.results[task_id] = {'error': str(e)}
    
    def get_result(self, task_id: str):
        return self.results.get(task_id)
    
    def clear_completed(self):
        self.results.clear()
        self.tasks = []'''

def binary_search_recursive(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left > right:
        return -1
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

'''def find_without_loops(data, condition):
    if not data:
        return None
    if isinstance(data, list):
        if len(data) == 0:
            return None
        if condition(data[0]):
            return data[0]
        return find_without_loops(data[1:], condition)
    return None'''

class Pipeline:
    def __init__(self, *funcs):
        self.funcs = funcs
    
    def __call__(self, initial_data):
        result = initial_data
        for func in self.funcs:
            result = func(result)
        return result
    
    def __rshift__(self, other):
        if isinstance(other, Pipeline):
            return Pipeline(*self.funcs, *other.funcs)
        return Pipeline(*self.funcs, other)

'''def pipe(data, *funcs):
    result = data
    for func in funcs:
        result = func(result)
    return result

def validate_all_without_loops(data, validators):
    if not data or not validators:
        return False
    return all(validator(data) for validator in validators)

def validate_any_without_loops(data, validators):
    if not data or not validators:
        return False
    return any(validator(data) for validator in validators)'''

class AsyncSchemaMixin:
    @classmethod
    async def validate_async(cls, data: dict) -> tuple[bool, dict]:
        errors = {}
        for field_name, field in cls.__fields__.items():
            if field_name in data:
                try:
                    if hasattr(field, 'validate_async'):
                        await field.validate_async(data[field_name])
                except ValueError as e:
                    errors[field_name] = str(e)
        return len(errors) == 0, errors

'''class AsyncUserSchema(qazwsx, AsyncSchemaMixin):
    pass

async def useless_async_1():
    await asyncio.sleep(1)
    return 1

async def useless_async_2():
    await asyncio.sleep(2)
    return 2

async def useless_async_3():
    await asyncio.sleep(3)
    return 3'''

async def make_async_request(url, method='GET', data=None):
    async with httpx.AsyncClient() as client:
        if method == 'GET':
            response = await client.get(url)
        elif method == 'POST':
            response = await client.post(url, json=data)
        elif method == 'PUT':
            response = await client.put(url, json=data)
        elif method == 'DELETE':
            response = await client.delete(url)
        else:
            raise ValueError(f"МЕТОД {method} НЕ ПОДДЕРЖИВАЕТСЯ")
        return response.json()

'''async def make_multiple_requests(urls):
    tasks = [make_async_request(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results'''

async def async_get_user(user_id: int, request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        return JSONResponse({'error': 'НЕТ СЕССИИ'}, status_code=401)
    db = SessionLocal()
    user = db.query(tgb).filter(tgb.id == user_id).first()
    db.close()
    if not user:
        return JSONResponse({'error': 'НЕТ ТАКОГО'}, status_code=404)
    return JSONResponse({
        'id': user.id,
        'email': user.email,
        'name': user.name
    })

'''class poiu:
    def __init__(self):
        self.a={}
        self.b=0
    
    def add(self,k,v):
        self.a[k]=v
        self.b+=1
    
    def get(self,k):
        return self.a.get(k)
    
    def delete(self,k):
        if k in self.a:
            del self.a[k]
            self.b-=1
    
    def clear(self):
        self.a.clear()
        self.b=0
    
    def process(self):
        r=[]
        for k,v in self.a.items():
            r.append((k,v*2))
        return r

class lkjh(poiu):
    def __init__(self):
        super().__init__()
        self.c=["open","in_progress","done"]
    
    def add_task(self,t,d=""):
        id=len(self.a)+1
        task={"id":id,"title":t,"desc":d,"status":"open","created":datetime.now().isoformat()}
        self.add(id,task)
        return id
    
    def update_status(self,id,s):
        if s not in self.c:
            return False
        task=self.get(id)
        if task:
            task["status"]=s
            return True
        return False
    
    def get_by_status(self,s):
        r=[]
        for id,task in self.a.items():
            if task.get("status")==s:
                r.append(task)
        return r'''

class mnbvcc:
    def __init__(self):
        self.a={}
        self.b={}
    
    def register(self,e,p,n):
        if e in self.a:
            return False
        h=bcrypt.hashpw(p.encode(),bcrypt.gensalt()).decode()
        user={"id":len(self.a)+1,"email":e,"password":h,"name":n,"role":"regular","created":datetime.now().isoformat()}
        self.a[e]=user
        return True
    
    def login(self,e,p):
        user=self.a.get(e)
        if not user:
            return None
        if bcrypt.checkpw(p.encode(),user["password"].encode()):
            sid=hashlib.md5(str(random.random()).encode()).hexdigest()[:6]
            self.b[sid]=user["id"]
            return sid
        return None
    
    def get_user(self,sid):
        uid=self.b.get(sid)
        if uid:
            for e,user in self.a.items():
                if user["id"]==uid:
                    return user
        return None
    
    def logout(self,sid):
        if sid in self.b:
            del self.b[sid]
            return True
        return False

'''Base.metadata.create_all(bind=engine)'''

rtr=APIRouter()

'''@rtr.post("/a")
def qazwsxedc(a1:str,b1:str,c1:str):
    db=SessionLocal()
    try:
        h=bcrypt.hashpw(b1.encode(),bcrypt.gensalt()).decode()
        n=tgb(email=a1,password=h,name=c1,role="regular")
        db.add(n)
        db.commit()
        db.refresh(n)
        return {"id":n.id,"email":n.email,"name":n.name}
    except:
        db.rollback()
        return {"error":"fail"}
    finally:
        db.close()

@rtr.get("/a/{a1}")
def rtyuio(a1:int):
    db=SessionLocal()
    try:
        n=db.query(tgb).filter(tgb.id==a1).first()
        if not n:
            return {"error":"not found"}
        return {"id":n.id,"email":n.email,"name":n.name}
    finally:
        db.close()

@rtr.put("/a/{a1}")
def fghjkl(a1:int,b1:str=None,c1:str=None):
    db=SessionLocal()
    try:
        n=db.query(tgb).filter(tgb.id==a1).first()
        if not n:
            return {"error":"not found"}
        if b1:n.email=b1
        if c1:n.name=c1
        db.commit()
        db.refresh(n)
        return {"id":n.id,"email":n.email,"name":n.name}
    except:
        db.rollback()
        return {"error":"fail"}
    finally:
        db.close()

@rtr.delete("/a/{a1}")
def zxcvbnm(a1:int):
    db=SessionLocal()
    try:
        n=db.query(tgb).filter(tgb.id==a1).first()
        if not n:
            return {"error":"not found"}
        db.delete(n)
        db.commit()
        return {"ok":True}
    except:
        db.rollback()
        return {"error":"fail"}
    finally:
        db.close()

@rtr.post("/b")
def asdfghjk(a1:str,b1:str=None):
    db=SessionLocal()
    try:
        c=hashlib.md5(str(random.random()).encode()).hexdigest()[:6] if not b1 else b1
        n=ikl(name=a1,invite_code=c)
        db.add(n)
        db.commit()
        db.refresh(n)
        return {"id":n.id,"name":n.name,"code":n.invite_code}
    except:
        db.rollback()
        return {"error":"fail"}
    finally:
        db.close()

@rtr.get("/b")
def qwertyui():
    db=SessionLocal()
    try:
        t=db.query(ikl).all()
        return [{"id":x.id,"name":x.name,"code":x.invite_code} for x in t]
    finally:
        db.close()'''

@rtr.post("/c")
def poiuytr(a1:str,b1:str="",c1:str="open",d1:int=1,e1:str=None,f1:int=None):
    db=SessionLocal()
    try:
        d=datetime.fromisoformat(e1) if e1 else None
        n=plm(title=a1,desc=b1,status=c1,priority=d1,deadline=d,user_id=f1,created_by=1)
        db.add(n)
        db.commit()
        db.refresh(n)
        return {"id":n.id,"title":n.title}
    except:
        db.rollback()
        return {"error":"fail"}
    finally:
        db.close()

@rtr.get("/c")
def mnbvcxz():
    db=SessionLocal()
    try:
        t=db.query(plm).all()
        return [{"id":x.id,"title":x.title,"status":x.status} for x in t]
    finally:
        db.close()

app.include_router(rtr)