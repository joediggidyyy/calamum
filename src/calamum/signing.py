from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

    CRYPTO_AVAILABLE = True
except Exception:  # pragma: no cover - optional runtime dependency during bootstrap
    CRYPTO_AVAILABLE = False


DEFAULT_PRIVATE_KEY_ENV = "CALAMUM_ED25519_PRIVATE_KEY"
DEFAULT_PUBLIC_KEY_ENV = "CALAMUM_ED25519_PUBLIC_KEY"
DEFAULT_HMAC_ENV = "CALAMUM_POLICY_SIGNING_KEY"


class SigningError(RuntimeError):
    """Raised when a signing or verification step fails."""


def canonical_json_text(payload_obj: Dict[str, Any]) -> str:
    return json.dumps(payload_obj, sort_keys=True, separators=(",", ":"))


def canonical_json_bytes(payload_obj: Dict[str, Any]) -> bytes:
    return canonical_json_text(payload_obj).encode("utf-8")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sign_payload(payload_obj: Dict[str, Any], key_path: Optional[str] = None) -> Tuple[str, str]:
    canonical = canonical_json_bytes(payload_obj)
    resolved_key = str(key_path or os.environ.get(DEFAULT_PRIVATE_KEY_ENV, "")).strip()

    if resolved_key and CRYPTO_AVAILABLE:
        try:
            private_key_bytes = Path(resolved_key).read_bytes()
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
            if isinstance(private_key, Ed25519PrivateKey):
                signature = private_key.sign(canonical)
                return signature.hex(), "ED25519"
        except Exception as exc:
            raise SigningError("Failed to sign payload with Ed25519 key: {0}".format(exc))

    hmac_key = str(os.environ.get(DEFAULT_HMAC_ENV, "") or os.environ.get("POLICY_SIGNING_KEY", "")).strip()
    if hmac_key:
        digest = hmac.new(hmac_key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
        return digest, "HMAC-SHA256"

    return sha256_hex(canonical), "SHA256-RAW"


def verify_signature(
    payload_obj: Dict[str, Any],
    signature_value: str,
    public_key_path: Optional[str] = None,
) -> bool:
    canonical = canonical_json_bytes(payload_obj)
    if ":" in str(signature_value):
        algorithm, raw_signature = str(signature_value).split(":", 1)
    else:
        algorithm, raw_signature = "", str(signature_value)
    normalized_algorithm = algorithm.strip().upper()

    resolved_public_key = str(public_key_path or os.environ.get(DEFAULT_PUBLIC_KEY_ENV, "")).strip()
    if normalized_algorithm in ("", "ED25519") and resolved_public_key and CRYPTO_AVAILABLE:
        try:
            public_key_bytes = Path(resolved_public_key).read_bytes()
            public_key = serialization.load_pem_public_key(public_key_bytes)
            if isinstance(public_key, Ed25519PublicKey):
                public_key.verify(bytes.fromhex(raw_signature), canonical)
                return True
        except Exception:
            return False

    hmac_key = str(os.environ.get(DEFAULT_HMAC_ENV, "") or os.environ.get("POLICY_SIGNING_KEY", "")).strip()
    if normalized_algorithm in ("HMAC-SHA256", "") and hmac_key:
        expected = hmac.new(hmac_key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, raw_signature)

    expected_sha = sha256_hex(canonical)
    return hmac.compare_digest(expected_sha, raw_signature)


def write_checksum_sidecar(path: Path) -> Path:
    digest = sha256_hex(path.read_bytes())
    checksum_path = path.with_suffix(path.suffix + ".sha256")
    checksum_path.write_text(digest + "\n", encoding="utf-8")
    return checksum_path


def sign_json_artifact(
    artifact_path: Path,
    *,
    key_path: Optional[str] = None,
    signature_path: Optional[Path] = None,
    allow_fallback: bool = True,
) -> Dict[str, str]:
    if not artifact_path.exists():
        raise SigningError("Artifact does not exist: {0}".format(artifact_path))
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SigningError("Artifact is not valid JSON: {0}".format(exc))
    if not isinstance(payload, dict):
        raise SigningError("JSON artifacts must contain an object payload.")

    signature_hex, algorithm = sign_payload(payload, key_path=key_path)
    if algorithm != "ED25519" and not allow_fallback:
        raise SigningError("Expected ED25519 signature but produced {0}.".format(algorithm))

    resolved_signature_path = signature_path or artifact_path.with_suffix(artifact_path.suffix + ".sig")
    resolved_signature_path.write_text("{0}:{1}\n".format(algorithm, signature_hex), encoding="utf-8")
    checksum_path = write_checksum_sidecar(artifact_path)
    return {
        "artifact": str(artifact_path),
        "signature_path": str(resolved_signature_path),
        "checksum_path": str(checksum_path),
        "algorithm": algorithm,
    }


def verify_json_artifact(
    artifact_path: Path,
    *,
    signature_path: Optional[Path] = None,
    public_key_path: Optional[str] = None,
) -> bool:
    if not artifact_path.exists():
        return False
    resolved_signature_path = signature_path or artifact_path.with_suffix(artifact_path.suffix + ".sig")
    if not resolved_signature_path.exists():
        return False
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        signature_value = resolved_signature_path.read_text(encoding="utf-8").strip()
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    return verify_signature(payload, signature_value, public_key_path=public_key_path)
