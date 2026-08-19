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

## Safety

Examples must use mock payloads and placeholder credentials. Never commit client data, API tokens or real webhook URLs.
