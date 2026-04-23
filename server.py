"""
Trustnet node server – receives and returns Shamir shares over mutual TLS.

Runs one instance per node. All nodes in the network run the same code.
Authentication is enforced at the TLS layer: every client must present a
certificate signed by the shared CA (CERT_REQUIRED). The application layer
additionally checks that the caller's declared participant_name is registered
in participants.ini.

Required keys in default_config.ini [local_settings]:
    participant_name   – this node's name
    ca_file            – path to shared CA certificate (for verifying clients)
    certificate        – path to this node's certificate (signed by CA)
    private_key        – path to this node's private key
    participant_file   – path to participants.ini
    server_port        – TCP port to listen on (default: 8443)
    share_store_file   – where to persist received shares (default: share_store.json)

Run standalone:
    python server.py
Or call server.run(settings, participant_dict) from main.py.
"""

import configparser
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Trustnet Node")

# Module-level state, populated by run() before uvicorn starts.
_settings: dict = {}
_participant_dict: dict = {}
_share_store: dict = {}
_share_store_path: str = "share_store.json"


# ── storage ───────────────────────────────────────────────────────────────────

def _load_store(path: str) -> dict:
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else {}


def _save_store() -> None:
    Path(_share_store_path).write_text(json.dumps(_share_store, indent=2))


# ── request model ─────────────────────────────────────────────────────────────

class ReceiveShareRequest(BaseModel):
    owner_name: str   # self-declared identity of the sender
    share: dict       # full participant dict from ShamirSecret.iterate_participants()


# ── auth helper ───────────────────────────────────────────────────────────────

def _require_participant(name: str) -> None:
    """Reject callers not listed in participants.ini."""
    if name not in _participant_dict:
        raise HTTPException(status_code=403, detail=f"Unknown participant: {name}")


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {"node": _settings.get("participant_name", "unknown"), "status": "ok"}


@app.post("/shares", status_code=201)
async def receive_share(body: ReceiveShareRequest) -> dict:
    """
    Store a Shamir share sent by another node during secret distribution.

    The share dict is the exact value yielded by ShamirSecret.iterate_participants().
    Server-side metadata (_received_at, _sent_by) is stored with a leading
    underscore so it is stripped before the share is returned to callers.
    """
    _require_participant(body.owner_name)
    secret_uuid = body.share.get("uuid")
    if not secret_uuid:
        raise HTTPException(status_code=400, detail="Share data is missing 'uuid'")
    body.share["_received_at"] = datetime.now(timezone.utc).isoformat()
    body.share["_sent_by"] = body.owner_name
    _share_store[secret_uuid] = body.share
    _save_store()
    return {"status": "stored", "uuid": secret_uuid}


@app.get("/shares/{secret_uuid}")
async def get_share(secret_uuid: str, requester: str) -> dict:
    """
    Return the stored share for secret_uuid.

    Only the original sender (the secret owner) may retrieve the share.
    Pass ?requester=<participant_name> in the query string.
    """
    _require_participant(requester)
    entry = _share_store.get(secret_uuid)
    if not entry:
        raise HTTPException(status_code=404, detail="Share not found")
    if entry.get("_sent_by") != requester and entry.get("owner") != requester:
        raise HTTPException(status_code=403, detail="Not authorised for this share")
    # Strip internal metadata before returning
    return {k: v for k, v in entry.items() if not k.startswith("_")}


# ── entry points ──────────────────────────────────────────────────────────────

def run(settings: dict, participant_dict: dict) -> None:
    """
    Start the node server. Blocks until the process is terminated.

    settings       – dict of [local_settings] from default_config.ini
    participant_dict – loaded from participants.ini (Participants.participant_dict)
    """
    global _settings, _participant_dict, _share_store, _share_store_path
    _settings = settings
    _participant_dict = participant_dict
    _share_store_path = settings.get("share_store_file", "share_store.json")
    _share_store = _load_store(_share_store_path)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(settings.get("server_port", 8443)),
        ssl_keyfile=settings["private_key"],
        ssl_certfile=settings["certificate"],
        ssl_ca_certs=settings["ca_file"],
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        log_level="info",
    )


if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read("default_config.ini")
    s = dict(cfg["local_settings"])

    from participant import Participants
    p = Participants()
    p.load_all(s["participant_file"])

    run(s, p.participant_dict)
