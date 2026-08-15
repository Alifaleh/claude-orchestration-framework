"""PreToolUse deny hook (settings.json matcher: Agent).

Enforces the routing floor in ~/.claude/rules/orchestrator.md: never dispatch a
subagent without an explicit `model` alias — omission resolves to the ROOT session
model, which on Fable sessions is the measured 10x pricing accident (184 unset-model
dispatches in one session, 14-day window). A dispatch passes when it carries a
`model`, OR when its `subagent_type` is an agent def whose frontmatter pins a model.

Fails open (exit 0) on any parse error: a broken hook must never block dispatching.

ponytail: PINNED is a static copy of the agent defs that carry frontmatter `model:`
(~/.claude/agents/* + harness built-ins); re-check it when an agent def is added or
its model line is removed. Explicit `model: fable` dispatches also pass — deliberate
choice, not the omission accident; the session-close audit catches those, upgrade to
a deny here only if that audit ever actually finds one.
"""
import json
import sys

PINNED = {
    "scout",
    "verifier",
    "reviewer",
    "researcher",
    "engineer",
    "foreman",
    "explore",
    "claude-code-guide",
    "statusline-setup",
}


def main() -> None:
    try:
        tool_input = json.load(sys.stdin).get("tool_input")
        if not isinstance(tool_input, dict):
            sys.exit(0)  # malformed payload, never a real dispatch -> fail open
        model = tool_input.get("model")
        subagent_type = tool_input.get("subagent_type") or "general-purpose"
    except Exception:
        sys.exit(0)
    if model or str(subagent_type).lower() in PINNED:
        sys.exit(0)
    sys.stderr.write(
        f"routing-floor gate: dispatching '{subagent_type}' without an explicit "
        "model would inherit the ROOT session model — on Fable sessions a 10x "
        "pricing accident (rules/orchestrator.md, routing floor). Re-dispatch with "
        "model: haiku|sonnet|opus per the routing table. Roster agent types with a "
        "pinned frontmatter model (scout, verifier, reviewer, researcher, engineer, "
        "foreman, Explore) pass without one.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
