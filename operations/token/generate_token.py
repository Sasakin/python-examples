# generate_jwt.py
import jwt
import datetime
import uuid
from typing import List, Optional

class AuthorizationContainer:
    def __init__(self, roles: List[str]):
        self.roles = roles

class IamContext:
    def __init__(self, tid: uuid.UUID, rid: uuid.UUID, uid: uuid.UUID, aid: uuid.UUID,
                 sid: Optional[uuid.UUID] = None, ak: Optional[uuid.UUID] = None,
                 ln: Optional[str] = None, scope: Optional[str] = None,
                 exp: Optional[int] = None, iat: Optional[int] = None,
                 email: Optional[str] = None, azcs: Optional[List[AuthorizationContainer]] = None):
        self.tid = tid
        self.rid = rid
        self.uid = uid
        self.sid = sid
        self.aid = aid
        self.ak = ak
        self.ln = ln
        self.scope = scope
        self.exp = exp
        self.iat = iat
        self.email = email
        self.azcs = azcs

    def to_dict(self):
        return {
            "tid": str(self.tid),
            "rid": str(self.rid),
            "uid": str(self.uid),
            "sid": str(self.sid) if self.sid else None,
            "aid": str(self.aid),
            "ak": str(self.ak) if self.ak else None,
            "ln": self.ln,
            "scope": self.scope,
            "exp": self.exp,
            "iat": self.iat,
            "email": self.email,
            "azcs": [{"roles": azc.roles} for azc in self.azcs] if self.azcs else None
        }

# Generate UUIDs
tid = uuid.uuid4()
rid = uuid.uuid4()
uid = uuid.uuid4()
sid = uuid.uuid4()
aid = uuid.uuid4()
ak = uuid.uuid4()

# Generate timestamps
exp = int((datetime.datetime.utcnow() + datetime.timedelta(hours=8760)).timestamp())  # Token valid for 1 hour
iat = int(datetime.datetime.utcnow().timestamp())

# Create AuthorizationContainer instances
azcs = [AuthorizationContainer(roles=["role1", "role2"]), AuthorizationContainer(roles=["role3"])]

# Create IamContext instance
iam_context = IamContext(
    tid=tid,
    rid=rid,
    uid=uid,
    sid=sid,
    aid=aid,
    ak=ak,
    ln="en",
    scope="read write",
    exp=exp,
    iat=iat,
    email="user@example.com",
    azcs=azcs
)

# Convert IamContext to dictionary
payload = iam_context.to_dict()

# Symmetric key for signing the token
secret_key = ""

# Encode the payload to create a new token with signing
new_token = jwt.encode(payload, secret_key, algorithm='HS256')

print(new_token)