import json

from pytest import CaptureFixture

from gromodex.agent import agent_manifest
from gromodex.cli import main


def test_agent_manifest_lists_cli_tools() -> None:
    manifest = agent_manifest()

    assert manifest["transport"] == "cli"
    assert manifest["output"]["format"] == "json"
    assert {tool["name"] for tool in manifest["tools"]} == {
        "preview",
        "generate",
        "collect",
        "run",
    }


def test_cli_tools_outputs_agent_manifest(capsys: CaptureFixture[str]) -> None:
    main(["tools"])

    output = capsys.readouterr().out
    manifest = json.loads(output)

    assert manifest["name"] == "gromodex"
    assert manifest["discovery_command"] == ["uv", "run", "gromodex", "tools"]
