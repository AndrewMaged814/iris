# Testing

Run the offline contracts with `python -m unittest discover -s tests` and repository checks
with `python tools/validate_repo.py`. Tests cover structured product reads, watch persistence,
change detection, native delivery reconciliation, profile-scoped storage and the three-tool
plugin. They do not contact connected apps.

For live proof, use Hermes's native `mcp test composio`, verify the actual registered tool
inventory, discover a connected source and read a small range. Repeat in a fresh process after
a gateway restart to check persistent authentication. Then verify in the owner's Telegram chat.
Connecting an account alone does not select a catalog or prove its write operations.

`tools/evaluate_iris.py` runs native Hermes evaluation prompts, optionally in a private profile
copy. It has no custom Shopify transport or synthetic GraphQL injection. Evaluation cases are
behavioral checks, not automatic assertions. Keep output private; it can contain owner data.
Never use an evaluation prompt to execute a write in a real connected account.

## Recommendation checks

Four hypothetical cases exercise the recommendation process using supplied business facts:
`recommendation-hold`, `recommendation-opportunity`, `recommendation-missing-fact`, and
`recommendation-cron-hold`. Run with the installed Hermes Python and a new private directory:

```sh
python tools/evaluate_iris.py --profile-home ~/.hermes/profiles/iris \
  --output ~/iris-evaluations/recommendations --isolate \
  --cases recommendation-hold recommendation-opportunity recommendation-missing-fact recommendation-cron-hold
```

Review answers AND tool traces: correct contribution math, a choice grounded in stock and goal,
a measurable bounded test when warranted, one direct question for a missing stock count, and
no app research/writes for these supplied-fact exercises. Exit zero means execution completed,
not that these behavioral criteria passed. These cases do not verify real connected-data joins,
proactive Telegram delivery, app execution or merchant value. Test the live conversation separately.

`recommendation-connected` exercises native connected catalog reads and current watched-product
evidence; check that own-product verification/citations trigger no storefront browser visit and
that the answer has a verdict, short evidence bullets and next step. It can read the connected
account, so keep all evidence private and review tool calls for writes. Copy watch history into
any candidate profile before using `--isolate`; an empty watch database changes the research task.
`recommendation-conflicting-offer` is a supplied-fact case for conflicting single-price/multi-buy
readings and uncertain eligibility. Neither case automatically asserts a behavioral pass.

## Campaign evidence checks

Run `campaign-promotion`, `campaign-clearance`, and `campaign-conflict-followup` with `--isolate`
using the same evaluator. These supplied-fact cases check ordinary discounts versus explicitly
named clearance, campaign scope, and unresolved price evidence across a resumed native session.
Review each turn and tool trace: no unsupported clearance claim, no certainty from a repeated
conflicting extraction, and no external reads or writes. They do not verify live page selection
or extraction accuracy; exercise those separately in the owner's chat.
