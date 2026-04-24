import pytest

from calamum.catalog import CatalogError, normalize_definition


def test_normalize_definition_supports_richer_schema_fields():
    definition = normalize_definition(
        {
            "id": "rich-smoke",
            "title": "Rich smoke",
            "summary": "Exercise the richer schema contract.",
            "status": "active",
            "category": "regression",
            "selector_policy": "exact-name-only",
            "profiles": ["default", "fast"],
            "tags": ["cli", "project"],
            "policy_flags": ["json-first"],
            "evidence_requirements": ["report_json", "report_md"],
            "default_lanes": ["pytest", "sandbox_test"],
            "metadata": {"owner": "qa"},
            "lanes": {
                "pytest": [
                    {
                        "id": "pytest-step",
                        "title": "Pytest step",
                        "cwd": "{working_dir}",
                        "command": ["{python}", "-c", "print('ok')"],
                        "env": {"CALAMUM_MODE": "smoke"},
                        "expected_artifacts": ["stdout"],
                        "evidence_requirements": ["stdout_capture"],
                        "policy_flags": ["containment"],
                        "notes": "exercise token substitution",
                    }
                ],
                "sandbox_test": [],
                "empirical_test": [],
            },
        }
    )

    assert definition["id"] == "rich-smoke"
    assert definition["profiles"] == ["default", "fast"]
    assert definition["tags"] == ["cli", "project"]
    assert definition["policy_flags"] == ["json-first"]
    assert definition["evidence_requirements"] == ["report_json", "report_md"]
    assert definition["default_lanes"] == ["pytest", "sandbox_test"]
    assert definition["metadata"] == {"owner": "qa"}

    step = definition["lanes"]["pytest"][0]
    assert step["cwd"] == "{working_dir}"
    assert step["env"] == {"CALAMUM_MODE": "smoke"}
    assert step["expected_artifacts"] == ["stdout"]
    assert step["evidence_requirements"] == ["stdout_capture"]
    assert step["policy_flags"] == ["containment"]


def test_normalize_definition_supports_adversarial_contract_values():
    definition = normalize_definition(
        {
            "id": "adversarial-smoke",
            "title": "Adversarial smoke",
            "summary": "Exercise hostile-path validation through the contracted schema.",
            "status": "active",
            "category": "adversarial",
            "selector_policy": "exact-name-only",
            "profiles": ["smoke", "release"],
            "tags": ["adversarial", "sandbox"],
            "policy_flags": ["containment", "release-gate"],
            "evidence_requirements": ["report_json", "checksums_json"],
            "default_lanes": ["sandbox_test", "empirical_test"],
            "lanes": {
                "pytest": [],
                "sandbox_test": [
                    {
                        "id": "sandbox-step",
                        "title": "Sandbox step",
                        "command": ["python", "-c", "print('ok')"],
                        "policy_flags": ["containment"],
                    }
                ],
                "empirical_test": [],
            },
        }
    )

    assert definition["category"] == "adversarial"
    assert definition["tags"] == ["adversarial", "sandbox"]
    assert definition["policy_flags"] == ["containment", "release-gate"]


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("status", "mystery"),
        ("category", "mystery"),
        ("profiles", ["mystery"]),
        ("tags", ["mystery"]),
        ("policy_flags", ["mystery"]),
        ("evidence_requirements", ["mystery"]),
    ],
)
def test_normalize_definition_rejects_unknown_controlled_values(field_name, field_value):
    payload = {
        "id": "invalid-smoke",
        "title": "Invalid smoke",
        "summary": "Reject unsupported contract values.",
        "status": "active",
        "category": "regression",
        "selector_policy": "exact-name-only",
        "profiles": ["default"],
        "tags": ["cli"],
        "policy_flags": ["json-first"],
        "evidence_requirements": ["report_json"],
        "default_lanes": ["pytest"],
        "lanes": {"pytest": [], "sandbox_test": [], "empirical_test": []},
    }
    payload[field_name] = field_value

    with pytest.raises(CatalogError):
        normalize_definition(payload)


def test_normalize_definition_rejects_unknown_step_contract_values():
    with pytest.raises(CatalogError):
        normalize_definition(
            {
                "id": "invalid-step-smoke",
                "title": "Invalid step smoke",
                "summary": "Reject unsupported step contract values.",
                "status": "active",
                "category": "regression",
                "selector_policy": "exact-name-only",
                "profiles": ["default"],
                "tags": ["cli"],
                "policy_flags": ["json-first"],
                "evidence_requirements": ["report_json"],
                "default_lanes": ["pytest"],
                "lanes": {
                    "pytest": [
                        {
                            "id": "pytest-step",
                            "title": "Pytest step",
                            "command": ["python", "-c", "print('ok')"],
                            "policy_flags": ["mystery"],
                        }
                    ],
                    "sandbox_test": [],
                    "empirical_test": [],
                },
            }
        )
