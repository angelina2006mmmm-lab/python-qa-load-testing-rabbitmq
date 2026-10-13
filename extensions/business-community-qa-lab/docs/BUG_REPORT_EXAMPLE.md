# QA-DEMO-001 — illustrative bug report (not observed in SberBusiness)
Summary: two rapid Publish presses on slow network show duplicate content.
Environment: HYPOTHETICAL Android Chrome, throttled network.
Precondition: logged-in test user, valid draft.
Steps: enter draft; throttle to Slow 3G; double tap Publish before response; refresh feed.
Expected: one post or idempotency behaviour according to agreed requirement.
Actual (SIMULATED): duplicate records.
Severity: medium hypothetical; priority to agree with product.
Evidence needed for real incident: screencast, HAR and request IDs.
This is a testing risk scenario, NOT a bug found in any bank app.