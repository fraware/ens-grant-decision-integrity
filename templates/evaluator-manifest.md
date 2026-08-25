# Automated-evaluator manifest worksheet

Complete only when automated evaluation materially informs a recommendation.

- Round ID: __________________
- Profile ID: __________________
- Material AI influence confirmed (`confirm-material-ai-influence`): [ ]

## Manifest fields

- Manifest version / ID: __________________
- Models / tools / parameters: __________________
- Commitment / salt handling planned: yes | no
- Anchor profile (if any): __________________
- Trust policy ID (production C2 only): __________________
- Pre-deadline commitment planned: yes | no | n/a

## Boundaries

- Automated evaluators are advisory participants only.
- They must never populate `decision.authorityKind`.
- Fixture anchors never establish production C2.
- Replay, if used, is artifact recomputation unless a separate re-execution claim exists.
