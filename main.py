from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerifyRequest(BaseModel):
    phone: str
    code: str

@app.post("/verify-code")
async def verify_code(payload: VerifyRequest):
    async with httpx.AsyncClient() as client:
        url = f"{SUPABASE_URL}/rest/v1/users"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        params = {
            "phone": f"eq.{payload.phone}",
            "code": f"eq.{payload.code}",
            "select": "*"
        }

        response = await client.get(url, headers=headers, params=params)
        data = response.json()

        if not data:
            return {"success": False, "message": "Invalid verification code"}

        user = data[0]

        return {
            "success": True,
            "user": {
                "id": user.get("id"),
                "firstName": (user.get("full_name") or "").split(" ")[0],
                "vehicle_reg": user.get("vehicle_reg"),
                "policy_start": user.get("policy_start"),
                "policy_end": user.get("policy_end"),
                "policy_time": user.get("policy_time"),
                "policy_number": user.get("policy_number"),
                "vehicle_details": user.get("vehicle_details"),
            }
        }
