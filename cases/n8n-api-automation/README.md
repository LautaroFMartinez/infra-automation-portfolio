# n8n and API automation

## Problem
Operational information is spread across forms, email, spreadsheets and APIs, creating repetitive manual work.

## First-stage workflow

- Define one concrete input and output.
- Validate incoming data.
- Call the required API with protected credentials.
- Deduplicate and record the result.
- Route uncertain cases to human review.
- Log failures and document how to replay safely.

## Success criteria

The workflow removes a measurable manual step without creating silent failures or irreversible actions.

## Runnable proof

The sanitized fixture can be validated locally without credentials or an external API:

```bash
python validate_payload.py mock_payload.json
```

The validator checks the required intake fields and makes the human-review route explicit. A real workflow should apply equivalent validation before deduplication or any side effect.

## Safety

Examples must use mock payloads and placeholder credentials. Never commit client data, API tokens or real webhook URLs.
