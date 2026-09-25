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

class PositionUpdate(BaseModel):
    quantite: float
    px_moyen: float

@app.put("/positions/{nom}")
def update_position(nom: str, update: PositionUpdate, user=Depends(get_user)):
    supabase.table("positions").update(update.dict()).eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} modifié"}

# ─── Routes CTO ───
class CTO(BaseModel):
    nom: str
    ticker: str
    quantite: float
    px_moyen: float

@app.get("/cto")
def get_cto(user=Depends(get_user)):
    response = supabase.table("cto").select("*").eq("user_id", user.id).execute()
    return response.data

@app.post("/cto")
def add_cto(cto: CTO, user=Depends(get_user)):
    data = cto.dict()
    data["user_id"] = user.id
    response = supabase.table("cto").insert(data).execute()
    return {"message": "Position CTO ajoutée", "data": response.data}

@app.put("/cto/{nom}")
def update_cto(nom: str, update: PositionUpdate, user=Depends(get_user)):
    supabase.table("cto").update(update.dict()).eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} modifié"}

@app.delete("/cto/{nom}")
def delete_cto(nom: str, user=Depends(get_user)):
    supabase.table("cto").delete().eq("nom", nom).eq("user_id", user.id).execute()
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

class LivretUpdate(BaseModel):
    valeur: float

@app.put("/livrets/{nom}")
def update_livret(nom: str, update: LivretUpdate, user=Depends(get_user)):
    supabase.table("livrets").update(update.dict()).eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} modifié"}

# ─── Routes crypto ───
class Crypto(BaseModel):
    nom: str
    ticker: str
    quantite: float

@app.get("/crypto")
def get_crypto(user=Depends(get_user)):
    response = supabase.table("crypto").select("*").eq("user_id", user.id).execute()
    return response.data

@app.post("/crypto")
def add_crypto(crypto: Crypto, user=Depends(get_user)):
    data = crypto.dict()
    data["user_id"] = user.id
    response = supabase.table("crypto").insert(data).execute()
    return {"message": "Crypto ajoutée", "data": response.data}

@app.delete("/crypto/{nom}")
def delete_crypto(nom: str, user=Depends(get_user)):
    supabase.table("crypto").delete().eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} supprimé"}

class CryptoUpdate(BaseModel):
    quantite: float

@app.put("/crypto/{nom}")
def update_crypto(nom: str, update: CryptoUpdate, user=Depends(get_user)):
    supabase.table("crypto").update(update.dict()).eq("nom", nom).eq("user_id", user.id).execute()
    return {"message": f"{nom} modifié"}
# ─── Route historique ───
@app.get("/historique")
def get_historique(user=Depends(get_user)):
    response = supabase.table("historique").select("*").eq("user_id", user.id).order("date").execute()
    return response.data
