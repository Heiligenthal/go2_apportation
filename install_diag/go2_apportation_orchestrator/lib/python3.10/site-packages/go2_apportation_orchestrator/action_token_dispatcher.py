from __future__ import annotations

from .skills.skill_bundle import SkillBundle


NO_ACTION_TOKENS = {"", "--"}


def _extract_parenthesized_payload(token: str) -> str | None:
    start = token.find("(")
    end = token.rfind(")")
    if start < 0 or end <= start:
        return None

    payload = token[start + 1 : end].strip()
    if not payload:
        return None
    return payload


def parse_action_token(token: str) -> dict[str, object]:
    raw = token.strip()
    lowered = raw.lower()

    if raw in NO_ACTION_TOKENS:
        return {
            "token": token,
            "handled": False,
            "kind": "noop",
            "status": "ignored",
            "unhandled_reason": "no_action",
        }

    if lowered.startswith("nav_goal"):
        payload_expr = _extract_parenthesized_payload(raw)
        if payload_expr is None:
            return {
                "token": token,
                "handled": False,
                "kind": "nav_goal",
                "status": "unhandled",
                "unhandled_reason": "missing_payload",
            }
        return {
            "token": token,
            "handled": True,
            "kind": "nav_goal",
            "status": "dispatched",
            "goal_type": payload_expr,
            "goal_payload": {"expr": payload_expr},
        }

    if "nav_cancel" in lowered or "cancel_nav" in lowered:
        return {
            "token": token,
            "handled": True,
            "kind": "nav_cancel",
            "status": "dispatched",
            "reason": "token_request",
        }

    if "pick_cancel" in lowered or "cancel_pick" in lowered:
        return {
            "token": token,
            "handled": True,
            "kind": "pick_cancel",
            "status": "dispatched",
            "reason": "token_request",
        }

    if lowered.startswith("start_pick") or lowered.startswith("pick(") or lowered == "do_pick":
        payload_expr = _extract_parenthesized_payload(raw)
        if payload_expr is None:
            return {
                "token": token,
                "handled": False,
                "kind": "pick",
                "status": "unhandled",
                "unhandled_reason": "missing_payload",
            }
        return {
            "token": token,
            "handled": True,
            "kind": "pick",
            "status": "dispatched",
            "target": {"expr": payload_expr},
        }

    if lowered.startswith("release(") or lowered in ("do_release", "release_service"):
        mode_expr = _extract_parenthesized_payload(raw)
        mode = mode_expr if mode_expr is not None else "OPEN_GRIPPER"
        return {
            "token": token,
            "handled": True,
            "kind": "release",
            "status": "dispatched",
            "mode": mode,
            "verify_open": True,
        }

    return {
        "token": token,
        "handled": False,
        "kind": "unknown",
        "status": "unhandled",
        "unhandled_reason": "unsupported_token",
    }


def dispatch_action_tokens(
    action_tokens: tuple[str, ...],
    skills: SkillBundle,
    *,
    nav_goal_demo_pose: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    dispatched: list[dict[str, object]] = []

    for token in action_tokens:
        parsed = parse_action_token(token)
        kind = str(parsed.get("kind", ""))
        status = str(parsed.get("status", ""))

        if status != "dispatched":
            dispatched.append(parsed)
            continue

        if kind == "nav_goal":
            try:
                goal_payload = dict(parsed.get("goal_payload", {}))
                if nav_goal_demo_pose is not None and not _goal_payload_has_pose(goal_payload):
                    goal_payload.update(nav_goal_demo_pose)
                    parsed["goal_payload"] = goal_payload
                    parsed["pose_source"] = "demo_pose_param"
                    parsed["pose_provided"] = True
                else:
                    parsed["pose_provided"] = _goal_payload_has_pose(goal_payload)

                skills.nav2.request_navigate(
                    goal_type=str(parsed.get("goal_type", "")),
                    goal_payload=goal_payload,
                )
                dispatched.append(parsed)
            except NotImplementedError as exc:
                fallback = dict(parsed)
                fallback.update(
                    {
                        "handled": False,
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )
                dispatched.append(fallback)
            continue

        if kind == "nav_cancel":
            try:
                skills.nav2.request_cancel(reason=str(parsed.get("reason", "token_request")))
                dispatched.append(parsed)
            except NotImplementedError as exc:
                fallback = dict(parsed)
                fallback.update(
                    {
                        "handled": False,
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )
                dispatched.append(fallback)
            continue

        if kind == "pick":
            try:
                skills.manip.request_pick(target=dict(parsed.get("target", {})))
                dispatched.append(parsed)
            except NotImplementedError as exc:
                fallback = dict(parsed)
                fallback.update(
                    {
                        "handled": False,
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )
                dispatched.append(fallback)
            continue

        if kind == "pick_cancel":
            try:
                skills.manip.request_pick_cancel(reason=str(parsed.get("reason", "token_request")))
                dispatched.append(parsed)
            except NotImplementedError as exc:
                fallback = dict(parsed)
                fallback.update(
                    {
                        "handled": False,
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )
                dispatched.append(fallback)
            continue

        if kind == "release":
            try:
                skills.manip.request_release(
                    mode=parsed.get("mode", "OPEN_GRIPPER"),
                    verify_open=bool(parsed.get("verify_open", True)),
                )
                dispatched.append(parsed)
            except NotImplementedError as exc:
                fallback = dict(parsed)
                fallback.update(
                    {
                        "handled": False,
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )
                dispatched.append(fallback)
            continue

        fallback = dict(parsed)
        fallback.update(
            {
                "handled": False,
                "status": "unhandled",
                "unhandled_reason": "dispatcher_missing_handler",
            }
        )
        dispatched.append(fallback)

    return dispatched


def _goal_payload_has_pose(goal_payload: dict[str, object]) -> bool:
    if not isinstance(goal_payload, dict):
        return False
    if isinstance(goal_payload.get("pose_stamped"), dict):
        return True
    required = {"x", "y", "yaw", "frame_id"}
    return required.issubset(set(goal_payload.keys()))
