from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client
from typing import Optional

app = FastAPI()

# ─── Connexion Supabase ───
SUPABASE_URL = "https://tuwzhitjtjiwjapjsasq.supabase.co"
SUPABASE_KEY = "sb_publishable_k2PYlNHBLQqiDOlPxSukAA_gfWW-Xw3"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Modèles ───
class UserRegister(BaseModel):
    email: str
    password: str

class Position(BaseModel):
    nom: str
    ticker: str
    quantite: float
    px_moyen: float
    type: str

# ─── Fonction pour vérifier le token ───
def get_user(token: str):
    try:
        response = supabase.auth.get_user(token)
        return response.user
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

# ─── Routes auth ───
@app.post("/register")
def register(user: UserRegister):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        return {"message": "Compte créé !", "user": response.user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: UserRegister):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return {
            "message": "Connecté !",
            "user": response.user.email,
            "token": response.session.access_token
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─── Routes positions ───
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

def get_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        response = supabase.auth.get_user(credentials.credentials)
        return response.user
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.get("/positions")
def get_positions(user=Depends(get_user)):
    response = supabase.table("positions").select("*").eq("user_id", user.id).execute()
    return response.data

@app.post("/positions")
def add_position(position: Position, user=Depends(get_user)):
    data = position.dict()
    data["user_id"] = user.id
    response = supabase.table("positions").insert(data).execute()
    return {"message": "Position ajoutée", "data": response.data}

@app.delete("/positions/{nom}")
def delete_position(nom: str, user=Depends(get_user)):
    supabase.table("positions").delete().eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} supprimé"}

# ─── Routes livrets ───
class Livret(BaseModel):
    nom: str
    valeur: float

@app.get("/livrets")
def get_livrets(user=Depends(get_user)):
    response = supabase.table("livrets").select("*").eq("user_id", user.id).execute()
    return response.data

@app.post("/livrets")
def add_livret(livret: Livret, user=Depends(get_user)):
    data = livret.dict()
    data["user_id"] = user.id
    response = supabase.table("livrets").insert(data).execute()
    return {"message": "Livret ajouté", "data": response.data}

@app.delete("/livrets/{nom}")
def delete_livret(nom: str, user=Depends(get_user)):
    supabase.table("livrets").delete().eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} supprimé"}
