# Role Prep: Senior Product Manager, External Developer Experience — Sokin

_Target Role: Senior Product Manager — External Developer Experience_  
_Reports to: Group Product Manager (Get Set Up & Build)_  
_Location: London (Hybrid — clarify exact days)_  
_Candidate Profile: Loaded (`profile.md` — API Platform, Governance & Financial Infrastructure Specialist)_  
_Date: Tuesday, 24 November 2026_

---

## 1. Company Intelligence & Strategic Context

### Business Model & Scale
* **What Sokin Does:** London-headquartered (Africa House, Kingsway, WC2B) next-generation B2B payments, FX, treasury management, and embedded financial infrastructure provider founded in 2019 by CEO **Vroon Modgill**. Operates across **170+ countries** and **70+ currencies**, backed by **regulatory licenses spanning 36 countries**.
* **Valuation & Capitalization:** Reached a **$300M valuation** in December 2025 following a **$50M Series B** led by Prysm Capital (with Morgan Stanley Expansion Capital, Watershed Ventures, Aurum Partners, and ex-PayPal executives Gary Marino and Mark Britto). Further bolstered by a **$15M BlackRock debt facility** (early 2025) and a **$100M (€83M / £70M) growth debt facility from Oxford Finance** (January 2026) explicitly earmarked for North America/APAC/MENA/LATAM expansion, regulatory licensing, and embedded finance.
* **Revenue & Profitability:** Profitable while growing >100% YoY. Closed FY2025 at **$45M audited net revenue** ($60M Dec 2025 run-rate; $9B+ TPV), reached **$90M run-rate net revenue in H1 2026**, and is tracking toward **$120M run-rate net revenue by December 2026**.

### Competitive Dynamics & Moat
| Competitor | Core Positioning | How Sokin Competes / Differentiates |
|---|---|---|
| **Airwallex** | All-in-one global financial OS for tech/growth companies; strong APIs & accounting syncs | Sokin competes on predictable/fixed-fee pricing structures, rapid licensing footprint (36 countries), and hybrid fiat + stablecoin settlement rails. |
| **Wise Business / Wise Platform** | SMB transparency (mid-market rate + fee); Wise Platform for bank/enterprise embedding | Sokin focuses on mid-market/enterprise B2B trade, treasury, and vertical partnerships (sports/entertainment, logistics, travel) plus white-label embedded accounts. |
| **Ebury** | High-touch corporate FX, hedging, and trade finance with human dealers | Sokin is building a modern, API-first, self-serve and AI-ready infrastructure layer rather than phone/dealer-led workflows. |
| **Currencycloud (Visa)** | Pure-play B2B embedded FX & multi-currency API infrastructure | Closest peer for Sokin's embedded/white-label channel. Sokin differentiates via unified direct + embedded stack, native stablecoin rails (post-Genpaid), and early mover advantage on MCP/agentic treasury. |

### Product Velocity & Leadership Vision (2025–2026)
* **Vroon Modgill's Thesis ("The Layer Underneath" & "Agentic Finance"):** Modgill's public narrative in 2026 is that AI agents and front-end UX are easily commoditised; the true defensible moat is **regulated global infrastructure** (licenses, direct banking rails, compliance frameworks) that autonomous agents and software platforms must plug into to actually move money.
* **2026 Strategic Acquisitions:**
  * **Settle Group AS (Early 2026):** Norwegian fintech acquisition expanding Sokin's European EMI licensing and technical footprint.
  * **Genpaid (March 2026):** Acquired blockchain-native non-custodial stablecoin stack and AI/crypto payment protocols (founder Ross Kolodyazhnyi joined to lead hybrid-finance).
* **2026 Major Product Launches:**
  * **Hybrid Finance / Native Stablecoin Rails (March 2026):** Unified fiat and stablecoin wallets/settlement within a single licensed platform, abstracting away keys and gas fees.
  * **Model Context Protocol (MCP) Connector for AI Treasury (September 2026):** Connects Sokin's regulated rails directly to ChatGPT, Claude, Gemini, and Perplexity so finance teams can query cash positions, fetch live FX quotes, add beneficiaries, and stage cross-border payments under human-in-the-loop approval rules.
* **Embedded Finance API Suite:** Includes Onboarding/KYB API, Corporate Currency Accounts (CCAs / virtual IBANs), Payments & Payouts API, FX & Treasury workflows (with custom partner markups), and Acceptance/Checkout (via Adyen). Embedded finance is a primary driver of Sokin's North American revenue growth.

### AI Signal Detection
* **Signal Strength: VERY HIGH (Core Strategic Pillar).**
* Sokin shipped an **MCP Connector in September 2026**, and the JD explicitly assigns this PM to: *"Define how MCP and agent access is granted and controlled, as an entitlement an administrator grants with scope and limits recorded."* The JD also evaluates candidates on using AI tools pragmatically in their own PM workflow while retaining full accountability.

### User Sentiment & Culture
* **Trustpilot (~4.0–4.1 / 5):**
  * *Delighters:* Competitive FX rates, multi-currency coverage, approachable human onboarding support.
  * *Friction Points:* Compliance/KYB checks, periodic transaction verification delays, and slower resolution on complex/automated support tickets. *(Directly explains why the JD emphasises actionable API error design, Support collaboration, and partner onboarding SLAs!)*
* **Culture & Ways of Working:** Fast-paced, high-energy scale-up with hubs in London and Belgrade. Operates a hybrid model in London (confirm exact days/week early, given candidate preference).

---

## 2. Matches, Gaps & Keyword Mapping

### Matches & Gaps Analysis

| JD Requirement | Status | Evidence / Bridge Strategy |
|---|---|---|
| 6+ years PM owning an API, developer platform, or developer-facing product in payments / B2B fintech | ✅ Strong Match | 6+ years at SWIFT (API Lifecycle, Community APIs, Cash Reporting & Trade Finance APIs) + 2.5 years at Metro Bank (built API function, Apigee, Open Banking/PSD2 APIs from scratch). |
| API-as-a-product: design principles, consistency, versioning, deprecation, auth, webhooks, sandbox | ✅ Strong Match | Owned API design governance across SWIFT's entire external API estate (including 3rd-party partner approval); implemented OAuth 2.0 / OIDC Hybrid Flow + eIDAS at Metro Bank; designed PSD2 sandbox & Developer Portal from OpenAPI specs. |
| Technical documentation around developer jobs (get set up, send, collect, track) | ✅ Strong Match | Translated dense ISO 20022 and Open Banking specifications into developer-consumable OpenAPI designs and portal guides; ran developer webinars (SmartBear, ION) and Sibos panels. |
| Comfortable with white label & embedded finance models (commercial & regulatory) | ⚠️ Gap (Flagged) | **Bridge Strategy:** Use the dedicated primer in Section 3 below. Anchor on your **SWIFT multi-party GTM** (pricing, legal docs, ordering/provisioning, 3rd-party partner API approval) and **Metro Bank PSD2/FCA regulatory accountability** — those are the exact building blocks of embedded finance. |
| Curious about AI agents as API consumers (MCP, permissions, limits, audit) | 〰️ Emerging / Bridgeable | Frame MCP agent access as **delegated authorization & least-privilege API governance** — an evolution of OAuth 2.0 scopes, token limits, eIDAS-style identity assurance, and audit trails you already built at Metro Bank and SWIFT. |
| Cross-functional work with Client Implementation, Solutions, Support, Compliance, Security, Commercial | ✅ Strong Match | Extensive experience running customer working groups (10 banks, 10 corporates, 4 TMS vendors at SWIFT), ICC industry bodies, and FCA compliance delivery at Metro Bank. |
| Location: London (Hybrid) | ⚠️ Check Policy | Profile prefers remote-first or max 2 days/week London hybrid. Clarify Sokin's exact in-office expectation during recruiter screen. |

### ATS / CV Keyword Mapping

| Keyword (JD Signal) | Profile Potential | Actionable Reframing Suggestion |
|---|---|---|
| API-as-a-Product / Versioning & Governance | ✅ Usable | Highlight owning SWIFT's external API design governance, third-party partner API approval, and Metro Bank's API Delivery Operating Model. |
| Sandbox Parity & Developer Portal | ✅ Usable | Highlight designing Metro Bank's PSD2 sandbox and OpenAPI-generated Developer Portal, plus SWIFT pilot test execution. |
| Payments / FX / Treasury APIs | ✅ Usable | Highlight SWIFT corporate cash reporting APIs (multi-bank cash management, <5 min data freshness) and Open Banking payment initiation. |
| White Label / Embedded Finance | 〰️ Reframe | Frame SWIFT's multi-bank Community API channel (enabling TMS vendors and corporates to embed multi-bank cash/trade APIs) and GTM packaging (pricing, legal, provisioning) as multi-party platform productisation. |
| MCP / Agentic Entitlements | 〰️ Reframe | Connect OAuth 2.0 / OIDC scopes, eIDAS identity verification, and API gateway traffic/policy controls (Apigee) to agentic scope, rate/value limits, and auditability. |
| Jobs to Be Done (JTBD) | ✅ Usable | Frame your translation of ISO 20022 business processes into developer journeys ("get set up, send, collect, track") as JTBD-driven DX. |

---

## 3. Deep-Dive Primer: White Label & Embedded Finance Models

> *Tailored specifically to close your flagged uncertainty on: "You are comfortable with white label and embedded finance models, and the commercial and regulatory questions they raise."*

### A. The Three Integration Archetypes (Know the Spectrum)

| Model | Who Owns the Brand & UI? | Who Holds the License & Compliance Liability? | Sokin Example |
|---|---|---|---|
| **1. Direct API Integration** | Direct corporate client (integrates Sokin into their ERP/TMS like NetSuite, SAP, Xero) | Sokin (direct relationship with corporate) | A logistics firm automates supplier payouts via Sokin's Payments API. |
| **2. Embedded Finance (Co-branded / Invisible Rails)** | A software platform (e.g., an AP/AR SaaS, payroll platform, or travel marketplace) embeds Sokin inside its workflow | Sokin holds the EMI/PI licenses; legal footer discloses *"Payments powered by Sokin"* | A B2B invoice platform lets its SME users pay overseas invoices in-app without leaving the SaaS UI. |
| **3. White Label / Reseller** | A partner (e.g., a regional fintech, neo-bank, or vertical B2B platform) resells Sokin's full multi-currency account/FX suite under **its own brand**, often using Sokin's hosted/white-labelled UI + APIs | Usually Sokin (under an introducer/distributor or EMD Agent model), OR a hybrid where a regulated partner handles Front-End KYC and Sokin provides regulated rails/settlement | A sports management or regional B2B platform launches "PartnerPay Global Accounts" powered end-to-end by Sokin. |

---

### B. The Commercial Questions (How You Productise, Price & Support It)

When the JD says *"Productise the white label offer: packaging, pricing and the support model for reseller and embedded partners"*, here are the exact commercial mechanics at play:

1. **Revenue Model & Split (How both Sokin and the Partner make money):**
   * **Platform / Minimum Monthly Fee (MMF):** Covers Sokin's fixed onboarding, dedicated sandbox/implementation, and ongoing compliance overhead. Prevents "zombie partners" who integrate and never drive volume.
   * **Usage / Account Fees:** Per-KYB check fee, per-active Corporate Currency Account (vIBAN) fee, or per-payment rail fee (e.g., SWIFT wire vs. local rail).
   * **FX Spread & Revenue Share (The Big Lever):** Sokin gives the partner a **wholesale FX rate** (e.g., interbank + 20 bps). The partner sets their own **retail markup** via API (e.g., +40 bps) and keeps the delta — OR Sokin splits net FX revenue (e.g., 70/30 or 60/40) based on volume tiers.
   * **Float / Interest Share:** For large embedded platforms holding significant balances in multi-currency accounts, partners often negotiate a share of net interest income (subject to EMI safeguarding rules).
2. **Packaging (Stopping Bespoke One-Off Deals):**
   * Unproductised white-label businesses die by "custom contract sprawl" (every sales deal promises custom webhooks, custom fees, bespoke SLAs).
   * Productising means defining **3 standard tiers** (e.g., *API-Only Embedded*, *White-Label Hosted Components*, *Enterprise Reseller*) with clear feature gates, standard rate cards, and self-serve vs. assisted implementation paths.
3. **The Support Model (Crucial JD Clue!):**
   * Look closely at the JD: *"...so that a partner's customers receive the same onboarding service levels as Sokin's direct clients."*
   * In white-label models, **Tier 1 Support** (basic UI questions, password resets, "how do I add a beneficiary?") MUST sit with the **Partner** (who owns the brand relationship), while **Tier 2/3 Support** (stuck SWIFT payment, compliance/RFI hold, API error, safeguarding issue) escalates to **Sokin**.
   * **The classic failure mode:** A partner's end-customer gets stuck in Sokin's KYB or AML queue, the partner has *zero visibility* into why, and the end-customer blames the partner.
   * **The PM solution:** Expose **onboarding & compliance status webhooks + structured RFI (Request for Information) APIs** and a **Partner Operations Console** so the partner can see queue status, collect missing documents from their customer in-brand, and hit the exact same onboarding SLA as Sokin's direct clients.

---

### C. The Regulatory Questions (Where Compliance Pushback Comes From)

Because Sokin holds **licenses in 36 countries** (UK FCA EMI/PI, European EMI via Settle Group, etc.), Compliance will push back on white-label ideas around five core questions:

1. **Who is the Legal Customer? (Tripartite Relationship):**
   * Even if the end-user thinks they are using "PartnerPay", legally **Sokin is providing the regulated payment service**. That requires a **tripartite legal structure** (or direct click-through acceptance of Sokin's End-User T&Cs) so Sokin has the legal right to freeze funds, run sanctions checks, or offboard a bad actor.
2. **KYB / KYC & Financial Crime Liability (Cannot Be Outsourced Away):**
   * Regulators (like the FCA) hold the **license holder (Sokin)** strictly liable for AML, sanctions screening, and KYB—even if the partner collects the documents.
   * *Product trade-off:* **Hosted/Embedded KYB SDK** (Sokin controls the UX/validation, faster compliance approval, slightly less customisable) vs. **Headless KYB API** (partner builds the form and passes JSON + documents to Sokin; prettier UX, but prone to validation mismatches and higher rejection rates).
3. **Regulatory Status of the Partner (Licensing Perimeter):**
   * If a partner is unregulated, they cannot legally *provide* payment services or hold client funds. They must operate either as a **Technical Service Provider / Introducer** (passing instructions to Sokin) or be registered as an **EMD Agent / Authorised Representative** under Sokin's license (which requires Sokin to audit and oversee the partner!).
4. **Branding & Financial Promotions (FCA FinProm / Disclosure Rules):**
   * "White label" is never 100% invisible legally. Regulators require clear, unambiguous disclosure to the end-customer about who holds and safeguards their money (e.g., *"Multi-currency accounts and payment services are provided by Sokin Ltd, authorised and regulated by the FCA..."*).
5. **Safeguarding & Account Segregation:**
   * End-customer funds must be safeguarded (ring-fenced from both Sokin's AND the partner's corporate insolvency). Virtual IBANs / segregated Corporate Currency Accounts (CCAs) help maintain clean ledger attribution and reconciliation per end-customer.

---

### D. How to Bridge YOUR Experience in the Interview

You actually understand more of this than you think—just under different names:
* **SWIFT Community APIs & 3rd-Party Partner Approval** = Multi-party platform governance where an intermediary (TMS vendor / bank) distributes standardised financial APIs to end-corporates, complete with **pricing, legal documentation, and provisioning** (which you owned end-to-end).
* **Metro Bank PSD2 / Open Banking** = Regulated third-party access (TPPs acting on behalf of end-customers), **FCA regulatory perimeter accountability** (even designing the FCA-compliant fallback), and identity/certificate verification (eIDAS/OAuth2).

**Strong, honest interview framing if asked directly:**
> *"My direct hands-on background is in regulated multi-party financial APIs—running SWIFT's Community API channel with banks, corporates, and TMS vendors (including pricing, legal, and provisioning) and delivering Metro Bank's FCA-regulated Open Banking platform. Where I'm keen to go deeper at Sokin is the commercial packaging and regulatory perimeter design of white-label reseller tiers—specifically how Sokin structures tripartite T&Cs, KYB handoff SLAs, and Tier 1/Tier 2 support boundaries across its 36 licensed jurisdictions so partners scale without creating bespoke compliance debt."*

---

## 4. Role Reality Check

### What You'll Spend 70–80% of Your Time On
* **Fixing Foundational DX Debt (API-as-a-Product):** Sokin has scaled from consumer remittance → B2B portal → $90M run-rate global payments + two 2026 acquisitions (Settle Group, Genpaid). Rapid growth + M&A almost always leaves **inconsistent API schemas, legacy endpoint-centric docs, sandbox/prod drift, and opaque error codes**. A huge chunk of your first 6 months will be auditing the current API estate, enforcing design/versioning standards, and driving sandbox parity with Engineering.
* **Partnering with Support, Implementation & Solutions:** Mining support tickets and stalled integration logs to find where developers get stuck (usually auth, webhook verification, KYB states, and unclear payment rejection errors) and turning those into roadmap fixes.
* **Specifying Enterprise Governance for MCP / AI Agents:** Sokin launched its MCP connector in Sept 2026. Moving it from an exciting launch into something a risk-averse CFO/CISO will enable requires defining **admin-granted entitlements, granular scopes, transaction/velocity limits, approval workflows, and immutable audit logs**.
* **Untangling Ad-Hoc White-Label Deals:** Working with Commercial, Legal, Compliance, and Onboarding Experience to turn bespoke partner deals into repeatable packages, clear pricing/rev-share hooks, and automated onboarding/KYB status tracking.

### What Success Looks Like in 3–6 Months
* **Baseline & North Star Metrics Live:** Instrumented dashboards for Time to First Payment (TTFP) in sandbox, integration success rate, top API error drivers, and developer CSAT.
* **API Standards & Versioning Policy Published:** An enforced API design/error-handling standard and public versioning/deprecation policy adopted by internal squads.
* **Sandbox Parity Milestone:** Developers can register, authenticate, create a beneficiary, get an FX quote, and execute a simulated payment end-to-end in <1 day using production-identical payloads.
* **JTBD Documentation Overhaul Initiated:** Docs reorganised around developer workflows (*Get Set Up, Send, Collect, Track*) rather than raw Swagger endpoint dumps.
* **MCP Entitlements Spec Approved:** Security, Compliance, and Engineering signed off on the admin entitlement model (scopes, limits, audit) for AI agent access.

### Where This Role Could Go
* Reporting to the **Group PM (Get Set Up & Build)** in a $300M, profitable, $90M→$120M run-rate scale-up gives high visibility and scope.
* Natural trajectory: **Principal PM / Group PM for Developer Platform & Embedded Ecosystem** as Sokin scales its embedded/white-label channel and agentic treasury rails toward IPO or Series C.

### Flags Worth Noting
1. **London Hybrid Policy:** Your `profile.md` prefers remote-first (or max 2 days/week London hybrid). Sokin operates a hybrid London HQ—confirm exact in-office expectations upfront.
2. **Broad Scope for One Senior PM:** API governance + Docs + Sandbox + SDKs + MCP/Agent entitlements + White-Label commercial productisation is a *huge* surface area. Ask in the interview how the squad is staffed (dedicated DX engineers? Tech writer? Solutions/Implementation support?) and what the **#1 priority for the first 90 days** is.
3. **Post-M&A Platform Complexity:** Integrating Settle Group (EU EMI) and Genpaid (stablecoin stack) while maintaining a clean, unified external API is a classic platform challenge—probe whether you're unifying multiple underlying APIs behind one gateway/façade.
4. **Domain Alignment:** While `profile.md` notes a preference to move away from *traditional retail banking*, Sokin is a high-velocity, profitable B2B fintech infrastructure scale-up—much closer to Stripe/Airwallex/Currencycloud than a legacy bank.

---

## 5. Three 6-Month Proposals

### Proposal 1: "Zero-Drift" Sandbox Parity & Jobs-Based Developer Portal
* **The opportunity:** Sokin's rapid growth and 2026 acquisitions (Settle Group, Genpaid) create natural API surface fragmentation, while Trustpilot and JD signals point to support ticket volume from opaque errors and stalled integrations. If developers cannot reach a first successful payment within a day, Sokin loses embedded deals to Airwallex and Currencycloud.
* **What you'd do:**
  1. Audit the top 20 integration-blocking tickets with Support and Client Implementation to build a **standardised, actionable API Error Taxonomy** (machine-readable codes, human-readable remediation links, correlation IDs).
  2. Establish a **contract-first OpenAPI governance pipeline** (linting, breaking-change detection, published versioning & deprecation policy) so Sandbox and Production share identical schemas and validation logic.
  3. Rebuild the Developer Portal around Sokin's **Jobs to Be Done** (*Get Set Up → Send → Collect → Track*) with runnable quickstarts, webhook simulators (including simulated KYB/compliance holds), and copy-pasteable SDK snippets.
  4. Instrument **Time to First Sandbox Payment (TTFP)** and **Sandbox-to-Production Conversion Rate** as core squad KPIs.
* **Why you're well-placed to lead this:** You owned API design governance across SWIFT's entire external estate and built Metro Bank's Open Banking sandbox and OpenAPI-generated Developer Portal from scratch.
* **How you'd measure success:**
  * Median Time to First Sandbox Payment reduced to **< 1 business day** (target: < 4 hours for self-serve).
  * **30%+ reduction** in integration-related Tier-2 API support tickets within 6 months.
  * 100% of net-new external API endpoints passing automated contract-linting and sandbox parity checks before release.
* **Dependencies and risks:** Requires Engineering buy-in to enforce contract-first CI gates and avoid "mock-only" sandboxes that drift from core payment rail behavior.

---

### Proposal 2: Enterprise "Agentic Entitlements" & Scoped MCP Governance
* **The opportunity:** Sokin's September 2026 MCP Connector puts it ahead of incumbents on Vroon Modgill's "agentic finance" thesis. However, enterprise CFOs and CISOs will block AI agents from touching live treasury rails unless agent access is governed like a first-class, least-privilege corporate entitlement—not a shared API key.
* **What you'd do:**
  1. Define the **Agent Entitlement Data Model**: distinct machine/agent identity linked to a sponsoring human administrator, scoped strictly to specific capabilities (e.g., `read:balances`, `create:fx_quote`, `stage:payment` vs. `execute:payment`).
  2. Build **Deterministic Policy Guardrails** enforced at the API/Gateway layer (not inside the LLM prompt): per-transaction caps, daily velocity limits, whitelisted beneficiary/currency corridors, and mandatory human-in-the-loop (HITL) step-up approval thresholds.
  3. Ship an **Immutable Agent Audit Log & Kill-Switch** in the admin portal (and via API/webhooks) showing *which* agent, under *which* admin grant, staged or executed every action, with instant one-click revocation.
  4. Publish an **Agentic Integration Reference Guide** for enterprise customers and embedded partners building treasury copilots on Sokin's MCP server.
* **Why you're well-placed to lead this:** Deep expertise in OAuth 2.0 / OIDC Hybrid Flow, eIDAS identity assurance (Metro Bank), API gateway policy enforcement (Apigee), and regulated financial controls (SWIFT).
* **How you'd measure success:**
  * Launch GA of Admin-Controlled MCP Entitlements with **100% of agentic actions logged** with actor/scope/policy attribution.
  * **Zero unauthorized or out-of-policy executions** across pilot cohorts.
  * **15+ enterprise or embedded partners** actively using scoped MCP/agent workflows in production within 6 months.
* **Dependencies and risks:** Requires tight alignment across Security, Compliance/Risk, Platform Services (identity/RBAC), and the AI/MCP engineering team.

---

### Proposal 3: Productised White-Label & Embedded Partner Kit (KYB-to-Live SLA)
* **The opportunity:** Embedded finance is a major growth driver for Sokin (especially post-$100M Oxford Finance facility for global expansion), yet Trustpilot reviews highlight compliance/onboarding friction and the JD flags a need to productise white-label packaging, pricing, and support so partners' customers match direct onboarding SLAs.
* **What you'd do:**
  1. Define **standardised White-Label / Embedded Tiers** (e.g., *Embedded API*, *Co-Branded Hosted*, *White-Label Reseller*) with clear commercial building blocks (platform fee, per-KYB/vIBAN fee, configurable FX markup API) to eliminate bespoke sales contracts.
  2. Co-design a **Partner Onboarding & KYB Handoff Flow** with Onboarding Experience & Compliance: expose real-time KYB status webhooks and structured Request-for-Information (RFI) endpoints so partners can resolve missing compliance docs inside their own UI without email back-and-forth.
  3. Establish a **Tier 1 / Tier 2 Support Operating Model & SLA Contract**, backed by a lightweight Partner Ops view (or API) giving partner support teams visibility into stuck payments and verification queues.
* **Why you're well-placed to lead this:** Owned end-to-end commercial GTM (pricing, legal docs, ordering/provisioning) and third-party partner onboarding for SWIFT's multi-bank Community APIs, plus FCA compliance delivery at Metro Bank.
* **How you'd measure success:**
  * Partner end-customer onboarding SLA matches **≥95% parity** with Sokin direct client onboarding times.
  * **40% reduction** in Partner-to-Sokin implementation cycle time (contract signed → first live partner customer).
  * Standardised commercial & technical packaging adopted for **100% of new embedded/white-label deals**.
* **Dependencies and risks:** Heavy cross-functional dependency on Commercial/Sales (stopping bespoke overrides), Legal (tripartite T&Cs across 36 jurisdictions), and Compliance (KYB automation appetite).

---

## 6. Product Sense Deep Dive (The 5 Thinking Shifts — AI Overlay)

**High-Probability Prompt:** *"Sokin just launched its MCP connector for AI treasury. How would you design and scale AI agent access to Sokin's APIs so enterprise customers and embedded partners trust it with real money movement?"*

### Shift 1: Strategic Context (2–3 min opening)
"Sokin's thesis—as Vroon has articulated—is that AI agents will become a primary interface for corporate treasury, but the agent itself is a commodity; Sokin's real moat is its **36-country regulatory license footprint and hybrid fiat/stablecoin settlement rails**. Right now, we're scaling from $90M toward $120M run-rate net revenue, with embedded finance and enterprise treasury driving growth. If we nail agentic access *safely*, we turn Sokin into the default regulated execution rail for AI-native finance—making us far stickier than FX-only competitors like Ebury or Wise. If we get it wrong—even one hallucinated or unauthorized transfer—we destroy institutional trust and invite regulatory scrutiny."

### Shift 2: Relationship Segmentation
Rather than segmenting by company size (SMB vs. Enterprise), segment users by their **Trust & Autonomy Relationship with AI Execution**:
1. **Read-Only Analysts (High Curiosity, Zero Execution Trust):** Finance teams using ChatGPT/Claude to query multi-currency balances, reconcile receivables, and pull live FX quotes. *Need:* Instant OAuth/MCP setup, rich structured data, zero risk of mutation.
2. **Staged-Execution Operators (Delegated Prep, Human Sign-Off):** Treasury managers letting an agent add beneficiaries, calculate optimal fiat vs. stablecoin routing, and *stage* batch payouts—while a human CFO approves via existing corporate rules. *Need:* Clear diff previews, approval queue webhooks, deterministic error messages.
3. **Bounded Autonomous Agents (Programmatic Policy Trust):** Embedded fintechs or sophisticated treasuries running recurring, rules-bound sweeps (e.g., auto-converting EUR→USD when balances exceed €50k within a 20 bps band). *Need:* Machine-enforced spend caps, corridor whitelists, instant kill-switches, and regulatory-grade audit logs.

### Shift 3: Architectural Distinction (Core Platform vs. Application Layer)
* **Core / Platform Layer (High Rigor, Gateway-Enforced, Longer Cycle):**
  * **Agent Identity & Scoped Entitlements:** Extend Sokin's RBAC/OAuth2 layer so every MCP/agent token is a distinct sub-principal bound to a corporate admin grant, carrying non-bypassable scopes, velocity/amount limits, and beneficiary whitelists enforced at the **API Gateway / Ledger boundary** (never trusting the LLM to police itself).
  * **Idempotency & Immutable Audit Ledger:** Mandatory idempotency keys (preventing retry double-spends by looping agents) and cryptographically linked audit trails recording *sponsoring admin + agent ID + tool call + policy decision*.
* **Application / DX Layer (Fast Iteration, Product-Owned):**
  * **MCP Tool Schema & Error Optimization:** Rewrite tool descriptions and error responses specifically for *both* human developers and LLM reasoning (e.g., returning structured `remediation_action` and `missing_fields` so an agent recovers cleanly instead of retrying blindly).
  * **Sandbox Agent Simulator:** Allow developers to test agent workflows against simulated FX volatility, compliance holds, and limit breaches in Sandbox with zero financial risk.

### Shift 4: Trust-by-Design (Baked Into Every Solution)
* **Policy-before-Execution:** Every mutating MCP tool call runs through a deterministic policy engine (`amount <= limit`, `beneficiary in whitelist`, `currency in allowed_corridors`). Out-of-policy calls automatically downgrade from `execute` to `pending_human_approval`.
* **Blast-Radius Containment:** Default new agent entitlements to `read-only` + `stage-only` with short-lived tokens and a one-click **Emergency Revoke** in the Admin Portal and API.
* **Explainable Rejections:** When Compliance or a policy limit blocks an agent action, return an explicit, safe reason code so the finance team knows *why* it paused without leaking AML tipping-off details.

### Shift 5: Growth Flywheels (The "Math")
* **Activation Flywheel (Read → Stage → Execute):** Frictionless `read-only` MCP onboarding gets finance teams connected in <15 minutes → once they trust the cash/FX visibility, they upgrade the entitlement to `stage-only` (cutting manual payment prep time) → eventually enabling bounded auto-sweeps. Each step increases **TPV per account** and **FX conversion volume**.
* **Embedded Distribution Flywheel:** When embedded partners (ERP/AP/AR platforms) inherit Sokin's pre-built, compliance-approved Agent Entitlements framework, they can ship "AI Treasury" features to *their* customers in weeks instead of months—accelerating **Partner Acquisition** and **Net Revenue Retention (NRR)** across Sokin's white-label channel.

---

## 7. Candidate Strategic Bridge (5 High-Signal Proof Points)

1. **API-as-a-Product Governance at Global Financial Scale (Shift 3 Core Rigor):** At SWIFT, you owned API design governance across the entire external API estate—including approving third-party partner APIs—giving you battle-tested muscle for enforcing consistency, versioning, and deprecation across Sokin's rapidly expanding (and post-M&A) API surface.
2. **Translating Complex Financial Standards into Developer Experience (Shift 3 App/DX Layer):** You bridged dense ISO 20022 and Open Banking specifications into clean OpenAPI contracts and developer portals—directly transferable to rebuilding Sokin's docs around developer *Jobs to Be Done* (get set up, send, collect, track) and clear, actionable error taxonomies.
3. **Regulated Sandbox & Security-First Access Control (Shift 4 Trust-by-Design):** At Metro Bank, you built the PSD2/Open Banking API function, sandbox, Developer Portal, and OAuth 2.0 / OIDC Hybrid Flow + eIDAS security model under hard FCA deadlines—the exact architectural foundation required to govern **MCP and AI agent entitlements** with scopes, limits, and auditability.
4. **Multi-Party Commercial GTM & Provisioning (White-Label Bridge):** At SWIFT, you didn't just write specs—you led end-to-end delivery of multi-bank corporate cash reporting APIs across 10 banks, 10 corporates, and 4 TMS vendors, owning **pricing, legal documentation, ordering/provisioning, and commercial promotion**. That directly maps to productising Sokin's white-label/embedded partner offer.
5. **Hands-On Technical Credibility & Pragmatic Delivery:** From managing a 6-person API engineering team with BDD automated testing and Apigee gateways to designing an FCA-compliant fallback solution when strategy pivoted, you can review a developer's experience firsthand, challenge engineering trade-offs, and keep roadmap momentum without waiting to be managed.

---

## 8. Interview Question Sets

### A. Hiring Manager (Group PM — Get Set Up & Build)
1. **"Walk me through how you would define 'excellent' for Sokin's developer experience and what your first 90 days would focus on."**
   > _What they're really testing: Whether you jump straight to building features vs. baselining developer pain (Support tickets, Implementation stalls, TTFP) and ruthlessly prioritising across a very broad remit._
2. **"Tell me about a time you treated an API as a product—specifically how you handled breaking changes, versioning, or deprecation with external customers."**
   > _What they're really testing: Real-world scars managing external developer trust and balancing engineering velocity against backward compatibility._
3. **"Our docs today are endpoint-centric. How would you restructure them around Jobs to Be Done, and how would you prove it worked?"**
   > _What they're really testing: Whether you connect documentation directly to measurable funnel outcomes (time to first payment, ticket deflection) rather than treating docs as an afterthought._
4. **"How would you approach productising our white-label offer so partners' end-customers get the same onboarding SLA as Sokin's direct clients?"**
   > _What they're really testing: Commercial + operational maturity—do you spot that KYB visibility, RFI APIs, and Tier 1/Tier 2 support boundaries are the real bottlenecks?_
5. **"How do you personally use AI tools in your PM workflow today, and where do you draw the line on trusting their output?"**
   > _What they're really testing: Authentic hands-on fluency (explicitly called out in the JD) paired with critical judgement and accountability._

### B. Engineering Lead / Platform Architect
1. **"How do you actually achieve sandbox-to-production parity in a multi-rail payments platform—especially for asynchronous webhooks, FX quotes, and compliance holds?"**
   > _What they're really testing: Technical depth—do you understand that static mocks fail, and that sandboxes need deterministic state triggers (e.g., magic amounts/IBANs to simulate AML holds or failed wires) sharing production validation logic?_
2. **"Design the authorization and control model for an AI agent connecting to Sokin via MCP. Where should limits and permissions be enforced?"**
   > _What they're really testing: Security architecture instinct—confirming you enforce scopes, spend caps, and idempotency at the API/gateway layer, never relying on LLM prompt instructions._
3. **"Give me an example of an API error design you're proud of—or one that caused pain and how you fixed it."**
   > _What they're really testing: Attention to developer craft (RFC 7807 Problem Details, stable machine error codes, field-level validation pointers, correlation IDs, safe compliance messaging)._
4. **"How do you enforce API design consistency across multiple squads (including recently acquired teams) without becoming a bureaucratic bottleneck?"**
   > _What they're really testing: Practical API governance—automated OpenAPI linting (e.g., Spectral) in CI/CD + lightweight design reviews vs. heavy approval committees._

### C. Product Leadership / Commercial & Compliance Stakeholders
1. **"Embedded partners constantly ask for bespoke pricing, custom KYB flows, and dedicated engineering tweaks to close big deals. How do you push back without killing commercial momentum?"**
   > _What they're really testing: Commercial backbone and ability to translate recurring bespoke requests into scalable product tiers and configurable primitives (like API-driven FX markups)._
2. **"What regulatory and liability risks keep you up at night when scaling a white-label payments product across 36 jurisdictions?"**
   > _What they're really testing: Whether you understand Sokin's non-delegable EMI/AML liability, tripartite T&Cs, financial promotion disclosures, and safeguarding segregation._
3. **"How do you prioritise developer experience investments (better errors, sandbox parity, docs) when Sales is screaming for a new payment rail or stablecoin feature?"**
   > _What they're really testing: Ability to quantify DX in commercial terms—linking faster TTFP and lower implementation friction directly to faster time-to-revenue (TPV activation) and lower Support/Implementation headcount cost._
4. **"Why Sokin, and why now—especially given your background at SWIFT and Metro Bank?"**
   > _What they're really testing: Genuine curiosity about Sokin's 2026 inflection point (hybrid fiat/stablecoin rails, MCP/agentic treasury, scaling $90M→$120M) and whether you thrive in a fast-moving scale-up._

### Smart Questions for YOU to Ask Sokin
1. *(To Hiring Manager)* "This remit spans API governance, docs, sandbox, SDKs, MCP entitlements, and white-label productisation. How is the squad currently structured, and which two areas are the sharpest bottleneck to hitting the $120M run-rate target?"
2. *(To Hiring Manager / Commercial)* "On white-label today, are partners mostly integrating headless APIs or expecting hosted/white-labelled UI components—and where does onboarding currently stall most between Sokin's KYB team and the partner?"
3. *(To Engineering)* "Following the Settle Group and Genpaid acquisitions, how unified is the external API surface today—are developers hitting one consistent gateway/schema across fiat and stablecoin rails, or is unification part of this role?"
4. *(To Recruiter / HM)* "What is the practical hybrid expectation for the London Kingsway office for Product and Engineering?"

---

## 9. Research Audit Log (`search-governance.md` Compliance)

*Total web searches executed: 6 / 8 limit (single parallel batch).*

| # | Query | Rationale | Key Findings |
|---|---|---|---|
| 1 | `Sokin B2B payments company funding revenue growth valuation 2024 2025 2026` | Business model, funding, revenue, scale | $300M valuation, $50M Series B (Prysm), $100M Oxford Finance debt, profitable, $45M FY25 → $90M H1 2026 run-rate → $120M target, 36 country licenses. |
| 2 | `Sokin API developer documentation sandbox white label embedded finance` | Existing API modules & embedded capabilities | Onboarding/KYB, Corporate Currency Accounts (vIBANs), Payments/Payouts, FX/Treasury custom markups, Adyen Acceptance, RESTful sandbox. |
| 3 | `Sokin CEO Vroon Modgill product strategy vision 2025 2026` | Leadership voice & strategic pillars | "Layer underneath" thesis; agentic finance moat = regulated licenses & rails; pragmatic fiat+stablecoin rails; embedded finance driving NA growth. |
| 4 | `Sokin competitors Airwallex Wise Ebury Currencycloud B2B FX payments` | Competitive positioning & differentiation | Positioned vs. Airwallex, Wise Platform, Ebury, Currencycloud on predictable pricing, global licensing, embedded + direct hybrid rails. |
| 5 | `Sokin Trustpilot G2 Glassdoor reviews culture London hybrid office policy` | User sentiment, delighters/friction, culture | Trustpilot ~4.0–4.1; delighters (FX, onboarding staff) vs. friction (compliance checks, verification delays, slow automated tickets); London Kingsway HQ + Belgrade hub, hybrid. |
| 6 | `Sokin acquisitions product launches 2025 2026 AI treasury` | Product velocity, M&A, AI signals | Acquired Settle Group AS (EU EMI) & Genpaid (stablecoin stack); launched Hybrid Finance (Mar 2026) and MCP Connector for AI Treasury (Sep 2026). |
