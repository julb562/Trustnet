"""
Trustnet mTLS HTTP client - node-to-node communication.

Every outgoing request presents this node's certificate (signed by the shared
CA), satisfying the server's CERT_REQUIRED policy. The server certificate is 
verified against the same CA, so both directions are authenticated.

Required settings keys:
    certificate    - path to this node's certificate
    private_key    - path to this node's private key
    ca_file        - path to the shared CA certificate
    participant_name - this node's name (sent as the caller identity)
"""

import httpx
import data_pipe


def _make_client(settings: dict) -> httpx.Client:
    """Return an httpx.Client configured for mutual TLS."""
    return httpx.Client(
        cert=(settings["certificate"], settings["private_key"]),
        verify=settings["ca_file"],
        timeout=10.0,
    )


def check_health(settings: dict, address: str, port: int) -> dict:
    """Return the health response from a remote node."""
    with _make_client(settings) as c:
        r = c.get(f"https://{address}:{port}/health")
        r.raise_for_status()
        return r.json()


def send_share(
    settings: dict,
    address: str,
    port: int,
    share_data: dict
) -> None:
    """
    Send one participant share to a remote node for storage.

    share_data is a single value yielded by ShamirSecret.iterate_participants().
    The 'keys' field contains Python tuples which JSON will encode as arrays -
    this is handled automatically by the standard json serialiser.
    """
    with _make_client(settings) as c:
        r = c.post(
            f"https://{address}:{port}/shares",
            json={
                "owner_name": settings["participant_name"],
                "share": share_data,
            },
        )
        r.raise_for_status()


def fetch_share(
    settings: dict,
    address: str,
    port: int,
    secret_uuid: str
) -> dict:
    """
    Retrieve a stored share from a remote node.

    Returns a participant data dict ready to pass directly to
    ShamirSecret.populate_decoder(). The JSON round-trip converts tuple (x, y)
    pairs to lists; this function restores them to tuples before returning.
    """
    with _make_client(settings) as c:
        r = c.get(
            f"https://{address}:{port}/shares/{secret_uuid}",
            params={"requester": settings["participant_name"]},
        )
        r.raise_for_status()
        share_data = r.json()
    # Restore (x, y) tuples from JSON arrays so Shamir's unpacking works
    if "keys" in share_data:
        share_data["keys"] = [tuple(k) for k in share_data["keys"]]
    return share_data

if __name__ == "__main__":
    data = data_pipe.Data()
    data.load_all()
    print(f"I'm {data.config["local_settings"]["participant_name"]}")
