# Payment provider readiness and onboarding

This is a **sanitized implementation checklist**, not legal, tax or financial advice. Provider availability, required documents, currencies, fees and payout methods vary by country, entity type, product and risk review. Confirm them in the merchant's regional dashboard before promising an integration.

## First classify the client

| Client situation | Client must do | Integrator can do |
|---|---|---|
| No account | Check country/product eligibility, register, complete KYC/KYB, verify email/identity and connect an eligible payout method | Provide a readiness checklist, explain the sequence and identify blockers |
| Account exists, no API | Finish merchant activation and enable the required payment capabilities | Guide sandbox/developer setup, app creation, keys, scopes and webhook configuration |
| API already exists | Deliver test/live credentials through a secure channel and confirm permissions | Implement checkout/orders/captures/refunds, signature verification, idempotency and reconciliation |
| Marketplace/platform | Approve connected/seller-account model, seller onboarding and payout responsibilities | Build OAuth/onboarding, tenant isolation, webhooks and account-requirement handling |

The integrator does not open an account in the client's name, invent KYC data, retain passwords/2FA codes or guarantee provider approval.

## Information to collect during discovery

- Country of residence and country of legal incorporation.
- Individual, monotributista, company or other legal form.
- Product/service category and restricted activities.
- Expected countries, currencies and payment methods.
- Payout country, currency and bank account.
- Existing merchant account, verification state and restrictions.
- Sandbox/live access and who can create API credentials.
- Required flows: authorize, capture, refund, dispute, subscription or marketplace payout.
- HTTPS domain and webhook endpoint ownership.
- Who approves irreversible actions and refunds.

## Stripe

1. Confirm that Stripe Payments supports the merchant's country/entity setup. Do not assume an Argentine business can open a local Stripe Payments account merely because Stripe APIs are available.
2. The merchant creates or confirms the Stripe account, users/roles and business profile.
3. The merchant completes identity/business verification and adds payout details where required.
4. Start in test mode and create products/prices or the required PaymentIntent/Checkout flow.
5. Generate test API keys and a webhook endpoint secret in the Dashboard; test and live webhook secrets are separate.
6. Verify payment state server-side through webhooks, not only a browser redirect.
7. Test successful, failed, cancelled, refunded and disputed payments before live activation.
8. For Connect, decide whether the platform uses Standard, Express or Custom connected accounts and who owns KYC, support, payouts and negative-balance risk.

Stripe-hosted or embedded Connect onboarding can collect changing requirements, documents and verification information. Connected-account requirements depend on country, business type and requested capabilities.

Official sources:

- [Global availability](https://stripe.com/global)
- [Connect onboarding](https://docs.stripe.com/connect/onboarding)
- [Required verification information](https://docs.stripe.com/connect/required-verification-information)
- [API keys](https://docs.stripe.com/keys)
- [Webhooks](https://docs.stripe.com/webhooks)
- [PaymentIntents](https://docs.stripe.com/payments/payment-intents)
- [Stripe Atlas](https://docs.stripe.com/atlas) — separate company-formation product, not a workaround for false residency or business information

## PayPal

1. Create the appropriate PayPal Business account on the regional PayPal site.
2. Confirm email, identity and business information requested by PayPal.
3. Add and verify an eligible withdrawal/bank method; Argentina has regional PayPal withdrawal documentation, but exact limits, currencies and methods must be confirmed in the client's account.
4. Create a Developer account and sandbox buyer/seller accounts.
5. Create a REST app in the Developer Dashboard and keep Client ID/Secret server-side.
6. Implement Orders: create → buyer approval → server-side capture.
7. Configure HTTPS webhooks and verify their signatures; deduplicate by event ID.
8. Test completed, denied/failed, refund, dispute and reversal flows.
9. Create/configure live credentials only after the Business account and merchant capabilities are active.
10. For multiparty, separately scope seller consent/onboarding, partner attribution, fees and payouts.

Do not mark an order paid because it was merely created or approved. Confirm capture and the provider event/state.

Official sources:

- [Account selection for Argentina](https://www.paypal.com/ar/webapps/mpp/account-selection)
- [Withdrawal to an Argentine bank account](https://www.paypal.com/ar/cshelp/article/how-do-i-withdraw-money-from-paypal-to-my-bank-account-help394)
- [Sandbox](https://developer.paypal.com/docs/api-basics/sandbox/)
- [Multiparty get started](https://developer.paypal.com/docs/multiparty/get-started/)
- [Seller onboarding](https://developer.paypal.com/docs/multiparty/seller-onboarding/)
- [Webhook API](https://developer.paypal.com/docs/api/webhooks/v1/)

## Revolut Merchant

1. Check the current country/residency and legal-entity eligibility for Revolut Business before quoting the integration. Do not assume Revolut Business or Merchant is available in Argentina just because the Merchant API is public.
2. The eligible client opens Revolut Business and completes business/representative verification.
3. The client applies for and waits for approval of a Merchant account.
4. After approval, the client generates production API keys from Revolut Business → Merchant overview → Merchant API.
5. Keep the Secret key server-side; use the Public key only where the documented payment flow requires it.
6. Send the required `Revolut-Api-Version` header for versioned endpoints.
7. Configure an HTTPS webhook URL and implement the documented signing verification.
8. Implement order/payment lifecycle, refunds and idempotency. Use `Idempotency-Key` for sensitive operations such as refunds where supported.
9. Test all relevant order, payment, payout and dispute events before production.

Official sources:

- [Merchant get started](https://developer.revolut.com/docs/guides/merchant/get-started)
- [Merchant API](https://developer.revolut.com/docs/merchant/merchant-api)
- [Merchant webhooks](https://developer.revolut.com/docs/merchant/webhooks)
- [Refund an order](https://developer.revolut.com/docs/merchant/refund-order)
- [Webhook events](https://developer.revolut.com/docs/merchant/retrieve-webhook-list)
- [Business eligibility](https://help.revolut.com/business/help/setting-up-an-account/is-my-business-eligible/what-country-of-residence-is-eligible-to-open-a-revolut-business-account/)

## Handoff checklist before implementation

The client should provide, through a secure channel and never in a public repository:

- provider and country/entity decision;
- confirmed merchant account and verification status;
- sandbox access or test credentials;
- required scopes/capabilities;
- test/live separation;
- webhook URL and signing-secret procedure;
- products, currencies and payment states;
- refund/dispute ownership;
- payout expectations;
- a test plan and acceptance criteria.

The integrator delivers:

- provider adapter and normalized payment state model;
- signature verification and event deduplication;
- idempotent payment/capture/refund boundaries;
- retries, dead letters and replay runbook;
- logs/metrics without secrets or unnecessary PII;
- reconciliation and failure alerts;
- deployment, secrets and rollback documentation.

## Scope boundary

Account approval, tax/legal advice, bank settlement, chargeback decisions and provider risk reviews remain the merchant's responsibility. The integration can expose their state and make it operationally visible; it cannot bypass provider controls.
