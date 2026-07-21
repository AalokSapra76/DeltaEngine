from uuid import uuid4
import json
import requests

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from profile_store import (
    add_profile,
    get_profiles,
    remove_profile,
    update_profile,
)

router = APIRouter(tags=["Profiles"])


class WebhookProfile(BaseModel):
    name: str
    url: str
    method: str
    headers: dict[str, str]
    payload: str


@router.get("/profiles")
def list_profiles():
    return get_profiles()


@router.post("/profiles")
def create_profile(profile: WebhookProfile):

    item = profile.model_dump()

    item["id"] = str(uuid4())

    add_profile(item)

    return item


@router.put("/profiles/{profile_id}")
def edit_profile(profile_id: str, profile: WebhookProfile):

    item = profile.model_dump()

    item["id"] = profile_id

    if update_profile(profile_id, item):
        return item

    raise HTTPException(404, "Profile not found")


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):

    if remove_profile(profile_id):
        return {"status": "deleted"}

    raise HTTPException(404, "Profile not found")


@router.post("/profiles/{profile_id}/test")
def test_profile(profile_id: str):

    for profile in get_profiles():

        if profile["id"] != profile_id:
            continue

        try:
            headers = profile.get("headers") or {}
            payload = profile.get("payload") or "{}"

            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    payload = {"payload": payload}

            method = profile.get("method", "POST").upper()

            if method == "POST":
                response = requests.post(profile["url"], json=payload, headers=headers, timeout=5)
            elif method == "PUT":
                response = requests.put(profile["url"], json=payload, headers=headers, timeout=5)
            elif method == "GET":
                response = requests.get(profile["url"], headers=headers, timeout=5)
            else:
                raise HTTPException(400, f"Unsupported HTTP method: {method}")

            return {
                "ok": 200 <= response.status_code < 300,
                "status": response.status_code,
                "reason": response.reason,
                "response": response.text,
            }

        except requests.RequestException as e:
            raise HTTPException(500, str(e))

    raise HTTPException(404, "Profile not found")