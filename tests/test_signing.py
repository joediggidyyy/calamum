import json
from pathlib import Path

from calamum.signing import sign_json_artifact, sign_payload, verify_json_artifact, verify_signature


def test_hmac_sign_and_verify_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("CALAMUM_POLICY_SIGNING_KEY", "dev-secret")

    payload = {"hello": "world", "value": 7}
    signature_hex, algorithm = sign_payload(payload)

    assert algorithm == "HMAC-SHA256"
    assert verify_signature(payload, "{0}:{1}".format(algorithm, signature_hex))

    artifact_path = tmp_path / "payload.json"
    artifact_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    signed = sign_json_artifact(artifact_path)

    assert Path(signed["signature_path"]).exists()
    assert Path(signed["checksum_path"]).exists()
    assert verify_json_artifact(artifact_path)
