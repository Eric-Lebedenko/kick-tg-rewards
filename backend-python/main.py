import os
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, Session, SQLModel, create_engine, select
from sqlalchemy import delete

# Ensure .env is loaded relative to this file, even if CWD differs
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

app = FastAPI(title="Python Rewards API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
TWITCH_REDIRECT_URI = os.environ.get("TWITCH_REDIRECT_URI")
ENABLE_TWITCH = True
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8001")
KICK_CLIENT_ID = os.environ.get("KICK_CLIENT_ID")
KICK_CLIENT_SECRET = os.environ.get("KICK_CLIENT_SECRET")
KICK_REDIRECT_URI = os.environ.get("KICK_REDIRECT_URI")
KICK_AUTH_URL = os.environ.get("KICK_AUTH_URL")
KICK_TOKEN_URL = os.environ.get("KICK_TOKEN_URL")
KICK_USER_URL = os.environ.get("KICK_USER_URL")
KICK_SCOPE = os.environ.get("KICK_SCOPE", "user:read")
DB_URL = os.environ.get("DB_URL", "sqlite:///./db.sqlite3")

states: Set[str] = set()
pkce_verifiers: Dict[str, str] = {}
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})


class RewardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    token: str = Field(default="USDC", max_length=10)
    amount: float = Field(..., gt=0)


class Reward(RewardCreate):
    id: UUID


class SteamLinkRequest(BaseModel):
    steamTradeLink: str | None = None


class User(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    kick_id: Optional[str] = SQLField(default=None, index=True)
    twitch_id: Optional[str] = SQLField(default=None, index=True)
    email: Optional[str] = None
    display_name: Optional[str] = None
    steam_trade_link: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthToken(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: Optional[int] = SQLField(default=None, foreign_key="user.id")
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: Optional[str] = None


class FollowedStreamer(BaseModel):
    platform: str
    login: str
    display_name: str
    followers: int | None = None
    avatar: str | None = None


class Follow(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: Optional[int] = SQLField(default=None, foreign_key="user.id")
    provider: str
    login: str
    display_name: str
    followers: Optional[int] = None
    avatar: Optional[str] = None


rewards: List[Reward] = [
    Reward(
        id=uuid4(),
        title="Welcome Airdrop",
        description="First time viewer bonus",
        token="USDC",
        amount=5,
    )
]
steam_link: str | None = None


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)


init_db()


def upsert_token(session: Session, user: User, provider: str, token_data: Dict):
    expires_in = token_data.get("expires_in")
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
    token = session.exec(
        select(AuthToken).where(AuthToken.user_id == user.id, AuthToken.provider == provider)
    ).first()
    if not token:
        token = AuthToken(user_id=user.id, provider=provider)
        session.add(token)
    token.access_token = token_data.get("access_token", "")
    token.refresh_token = token_data.get("refresh_token")
    token.token_type = token_data.get("token_type")
    token.expires_at = expires_at
    session.commit()

def replace_follows(session: Session, user: User, provider: str, entries: List[Dict]):
    session.exec(delete(Follow).where(Follow.user_id == user.id, Follow.provider == provider))
    session.commit()
    for e in entries:
        follow = Follow(
            user_id=user.id,
            provider=provider,
            login=e.get("login", ""),
            display_name=e.get("display_name", ""),
            followers=e.get("followers"),
            avatar=e.get("avatar"),
        )
        session.add(follow)
    session.commit()

def ensure_twitch_config() -> None:
    if not ENABLE_TWITCH:
        raise HTTPException(status_code=410, detail="Twitch OAuth is disabled in this build.")
    if not (TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET and TWITCH_REDIRECT_URI):
        raise HTTPException(
            status_code=500,
            detail="Twitch OAuth is not configured. Set TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_REDIRECT_URI.",
        )


def ensure_kick_config() -> None:
    if not (
        KICK_CLIENT_ID
        and KICK_CLIENT_SECRET
        and KICK_REDIRECT_URI
        and KICK_AUTH_URL
        and KICK_TOKEN_URL
        and KICK_USER_URL
    ):
        raise HTTPException(
            status_code=500,
            detail="Kick OAuth is not configured. Set KICK_CLIENT_ID, KICK_CLIENT_SECRET, KICK_REDIRECT_URI, KICK_AUTH_URL, KICK_TOKEN_URL, KICK_USER_URL.",
        )


async def exchange_code_for_token(code: str) -> Dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": TWITCH_CLIENT_ID,
                "client_secret": TWITCH_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": TWITCH_REDIRECT_URI,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        return resp.json()

def generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


async def fetch_twitch_user(access_token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": TWITCH_CLIENT_ID or "",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.twitch.tv/helix/users", headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user from Twitch")
        payload = resp.json()
        data = payload.get("data") or []
        if not data:
            raise HTTPException(status_code=400, detail="No user info returned from Twitch")
        user = data[0]
        return {
            "id": user.get("id"),
            "login": user.get("login"),
            "display_name": user.get("display_name"),
            "avatar": user.get("profile_image_url"),
        }


async def exchange_code_for_token_kick(code: str, verifier: str | None) -> Dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            KICK_TOKEN_URL or "",
            data={
                "client_id": KICK_CLIENT_ID,
                "client_secret": KICK_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": KICK_REDIRECT_URI,
                "code_verifier": verifier or "",
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token (Kick)")
        return resp.json()


async def fetch_kick_user(access_token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": KICK_CLIENT_ID or "",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(KICK_USER_URL or "", headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user from Kick")
        data = resp.json()
        return data


@app.get("/health")
def health():
    return {"ok": True, "service": "python-api"}


@app.get("/steam/link")
def get_steam_link(user_id: int | None = None, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.id == user_id)).first() if user_id else session.exec(select(User)).first()
    link = db_user.steam_trade_link if db_user else None
    return {"steamTradeLink": link}


@app.post("/steam/link")
def set_steam_link(payload: SteamLinkRequest, user_id: int | None = None, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.id == user_id)).first() if user_id else session.exec(select(User)).first()
    if not db_user:
        db_user = User()
        session.add(db_user)
    db_user.steam_trade_link = payload.steamTradeLink
    session.commit()
    session.refresh(db_user)
    return {"steamTradeLink": db_user.steam_trade_link, "userId": db_user.id}


@app.get("/streamers/following")
def get_following(user_id: int | None = None, session: Session = Depends(get_session)) -> List[FollowedStreamer]:
    db_user = session.exec(select(User).where(User.id == user_id)).first() if user_id else session.exec(select(User)).first()
    if not db_user:
        return []
    follows = session.exec(select(Follow).where(Follow.user_id == db_user.id)).all()
    return [
        FollowedStreamer(
            platform=f.provider,
            login=f.login,
            display_name=f.display_name,
            followers=f.followers,
            avatar=f.avatar,
        )
        for f in follows
    ]


@app.get("/auth/twitch/start")
async def auth_twitch_start():
    ensure_twitch_config()
    state = uuid4().hex
    states.add(state)
    params = urlencode(
        {
            "client_id": TWITCH_CLIENT_ID,
            "redirect_uri": TWITCH_REDIRECT_URI,
            "response_type": "code",
            "scope": "user:read:email",
            "state": state,
        }
    )
    url = f"https://id.twitch.tv/oauth2/authorize?{params}"
    return RedirectResponse(url)


@app.get("/auth/twitch/callback")
async def auth_twitch_callback(code: str | None = None, state: str | None = None, session: Session = Depends(get_session)):
    ensure_twitch_config()
    if not code or not state:
        raise HTTPException(status_code=400, detail="Code or state is missing")
    if state not in states:
        raise HTTPException(status_code=400, detail="Invalid state")
    states.discard(state)

    token_data = await exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token in Twitch response")
    user = await fetch_twitch_user(access_token)
    twitch_id = user.get("id") if isinstance(user, dict) else None
    db_user = None
    if twitch_id:
        db_user = session.exec(select(User).where(User.twitch_id == twitch_id)).first()
    if not db_user:
        db_user = User(twitch_id=twitch_id)
        session.add(db_user)
    db_user.display_name = user.get("display_name")
    db_user.avatar_url = user.get("avatar")
    session.commit()
    session.refresh(db_user)
    upsert_token(session, db_user, "twitch", token_data)
    replace_follows(
        session,
        db_user,
        "twitch",
        [
          {
            "login": user.get("login") or "twitch_user",
            "display_name": user.get("display_name") or "twitch_user",
            "followers": 1200,
            "avatar": user.get("avatar"),
          }
        ],
    )
    redirect_params = {
        "twitch_user": user.get("display_name") or user.get("login") or "",
        "twitch_id": user.get("id") or "",
        "twitch_avatar": user.get("avatar") or "",
        "user_id": db_user.id,
    }
    if FRONTEND_URL:
        url = f"{FRONTEND_URL}?{urlencode(redirect_params)}"
        return RedirectResponse(url)
    return {
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
        "user": user,
        "redirect_to": FRONTEND_URL,
    }


@app.get("/auth/kick/start")
async def auth_kick_start():
    ensure_kick_config()
    state = uuid4().hex
    states.add(state)
    verifier, challenge = generate_pkce()
    pkce_verifiers[state] = verifier
    params = urlencode(
        {
            "client_id": KICK_CLIENT_ID,
            "redirect_uri": KICK_REDIRECT_URI,
            "response_type": "code",
            "scope": KICK_SCOPE,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    url = f"{KICK_AUTH_URL}?{params}"
    return RedirectResponse(url)


@app.get("/auth/kick/callback")
async def auth_kick_callback(code: str | None = None, state: str | None = None, session: Session = Depends(get_session)):
    ensure_kick_config()
    if not code or not state:
        raise HTTPException(status_code=400, detail="Code or state is missing")
    if state not in states:
        raise HTTPException(status_code=400, detail="Invalid state")
    states.discard(state)
    verifier = pkce_verifiers.pop(state, None)

    token_data = await exchange_code_for_token_kick(code, verifier)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token in Kick response")
    user = await fetch_kick_user(access_token)
    kick_id = None
    kick_display = None
    kick_email = None
    avatar = None
    if isinstance(user, dict):
        data = user.get("data")
        if isinstance(data, list) and data:
            first = data[0]
            kick_id = str(first.get("user_id") or "")
            kick_display = first.get("name")
            kick_email = first.get("email")
            avatar = first.get("profile_picture")
    db_user = None
    if kick_id:
        db_user = session.exec(select(User).where(User.kick_id == kick_id)).first()
    if not db_user:
        db_user = User(kick_id=kick_id)
        session.add(db_user)
    db_user.display_name = kick_display or db_user.display_name
    db_user.email = kick_email or db_user.email
    db_user.avatar_url = avatar or db_user.avatar_url
    session.commit()
    session.refresh(db_user)
    upsert_token(session, db_user, "kick", token_data)
    replace_follows(
        session,
        db_user,
        "kick",
        [
          {
            "login": kick_display or "kick_user",
            "display_name": kick_display or "kick_user",
            "followers": 352,
            "avatar": avatar,
          }
        ],
    )
    user_data = None
    if isinstance(user, dict):
        if isinstance(user.get("data"), list) and user["data"]:
            user_data = user["data"][0]
    redirect_params = {
        "kick_user": (user_data or {}).get("name") or "",
        "kick_email": (user_data or {}).get("email") or "",
        "kick_id": (user_data or {}).get("user_id") or "",
        "kick_avatar": (user_data or {}).get("profile_picture") or "",
        "user_id": db_user.id,
    }
    target = FRONTEND_URL
    if target:
        url = f"{target}?{urlencode(redirect_params)}"
        return RedirectResponse(url)
    return {
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
        "user": user,
        "redirect_to": FRONTEND_URL,
    }


@app.get("/rewards", response_model=List[Reward])
def list_rewards():
    return rewards


@app.post("/rewards", response_model=Reward, status_code=201)
def create_reward(payload: RewardCreate):
    reward = Reward(id=uuid4(), **payload.model_dump())
    rewards.append(reward)
    return reward


@app.get("/rewards/{reward_id}", response_model=Reward)
def get_reward(reward_id: UUID):
    for reward in rewards:
        if reward.id == reward_id:
            return reward
    raise HTTPException(status_code=404, detail="Reward not found")


@app.delete("/rewards/{reward_id}", status_code=204)
def delete_reward(reward_id: UUID):
    global rewards
    before = len(rewards)
    rewards = [r for r in rewards if r.id != reward_id]
    if len(rewards) == before:
        raise HTTPException(status_code=404, detail="Reward not found")
