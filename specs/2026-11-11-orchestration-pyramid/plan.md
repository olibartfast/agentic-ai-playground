# Orchestration Pyramid — Plan

## Approach

1. Update the cross-harness guide first, replacing the obsolete four-role
   hierarchy and explicitly distinguishing behavioral instructions from
   enforced tool/permission restrictions.
2. Align committed Claude Code subagent files, Codex agent TOMLs, and OpenCode
   agent files with the agreed model assignments and role boundaries. Retain
   `implementer` as the worker filename where useful for compatibility.
3. Add a safe Hermes example under `integrations/hermes/` using profile
   routing, role-specific instruction files, Meta/DeepSeek routes, and explicit
   version/plugin prerequisites. Avoid secrets and unverified availability
   claims.
4. Update the historical 2026 role-agent packet with a supersession pointer so
   it remains historical evidence rather than current configuration guidance.
5. Parse example formats, check role/model consistency and relative links, and
   run `git diff --check`. Record any runtime checks not run.

## Boundaries

- Edit repository documentation/configuration only.
- Leave Kilo model configs unchanged; leave Pi guidance intact except for
  shared role descriptions that need correction.
- Do not install Hermes plugins or call model endpoints.
- Model identifiers and product requirements are documented as selected
  settings; provider availability remains a separate verification question.
