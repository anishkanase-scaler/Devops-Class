# 01 — Introduction to DevOps & Microservices

> **Source resources**
> - `resources/Introduction to DevOps & Microservices - Class  Scaler Academy.txt` — live class transcript (auto-generated, ASR-noisy)
> - `resources/devops1.pdf` — 14-page GoodNotes board export (13 handwritten boards) from the same class
>
> **Course:** DevOps & Cloud [SWE], Scaler Academy
> **Class date:** 11 August 2026, 09:35 IST · 120 min
> **Instructor emphasis:** monolith vs. microservices tradeoffs, the 13-item DevOps toolchain, the 8-stage lifecycle, job-role landscape, and "shift left" as the one-word definition of DevSecOps
>
> **Topics covered:** monolithic architecture · microservices architecture · when each wins · what DevOps is and why it exists · the DevOps lifecycle · the toolchain (Git, Docker, Python/Go, Linux, networking, CI/CD, cloud, Kubernetes, Terraform, Ansible, monitoring, GitOps, DevSecOps) · SAST/DAST/SCA/OWASP · DevOps job roles
>
> **Web-verified as of:** 11 August 2026

---

## TL;DR — the mental model to hold in your head

1. **Architecture decides your deployment unit.** A monolith is *one* deployable artifact; microservices are *N* independently deployable artifacts. Everything else — scaling, blast radius, team autonomy, ops cost — falls out of that one choice.
2. **Microservices don't make software better, they make it independently changeable.** You trade a simple system with coupled *change* for a complex system with decoupled *change*. That trade is only worth it when change velocity or scale is your actual bottleneck.
3. **DevOps is the practice that makes the microservices trade survivable.** N deployables means N build pipelines, N sets of logs, N things to scale. Doing that by hand does not work — so you automate: containers, CI/CD, IaC, orchestration, observability.
4. **The lifecycle is a loop, not a line:** Plan → Code → Build → Test → Release → Deploy → Operate → Monitor → (feeds back into Plan).
5. **DevSecOps = shift left.** Security stops being a gate at the end and becomes a check at every stage — in the IDE, in the PR, in the image build, in the running cluster.

---

## Part 1 — The running example: a college placement portal

The instructor anchored the whole class to one problem statement, and every note file in this course will reuse it. Keep it in mind; it makes the abstract concrete.

**The problem:** LinkedIn job applications are a black hole. You apply, you get an "Unfortunately…" mail three weeks later or nothing at all. So: **build a college placement portal** — `placement-portal` — where students apply to companies, upload resumes, track application state, and move through interview rounds.

From the class quiz, the portal has these features:

| # | Feature | What it owns |
|---|---------|--------------|
| 1 | Auth / user profile | student login, profile, branch, CGPA |
| 2 | Company & job listings | recruiter data, JD, eligibility criteria |
| 3 | Resume upload & storage | PDF blobs, parsing, versions |
| 4 | Application tracking | "applied → shortlisted → OA → rejected" state machine |
| 5 | Interview rounds | OA, DSA round, technical rounds, scheduling |
| 6 | HR round & offers | HR policies, offer letters, CTC breakup |
| 7 | Admin / placement cell | eligibility rules, onboarding recruiters, reports |

> **Note:** The instructor deliberately picked *placement portal* rather than a toy app because it has a property that drives the architecture decision: **the user base only grows.** Every year a new batch joins, and the previous batch becomes alumni whose data you keep. There is no steady state.

---

## Part 2 — Monolithic architecture

### What it is

> **Board (#1):** *"Monolithic Architecture"*

A **monolith** is an application where all functionality lives in **one codebase**, builds into **one artifact**, and deploys as **one unit**. Frontend, backend, business logic, and data access are compiled/packaged together and run in a single process (or N identical copies of that same process).

The class definition — *"everything that we need in one single repository"* — is the right intuition but slightly off on the key word.

> **Transcript correction:** Monolith is about the **deployment unit**, not the **repository**. You can have a monolith split across 5 repos (bad idea, but possible), and you can have 50 microservices in **one monorepo** — Google, Meta, and Uber all do exactly that. The test is: *"If I change one line, what is the smallest thing I can ship?"* If the answer is "the whole application," it's a monolith.

### Concrete: what a placement-portal monolith looks like

```text
placement-portal/                    # ONE repo, ONE deployable
├── src/
│   ├── main/java/com/college/placement/
│   │   ├── PlacementPortalApplication.java   # single entry point
│   │   ├── auth/         AuthController.java      AuthService.java
│   │   ├── company/      CompanyController.java   CompanyService.java
│   │   ├── resume/       ResumeController.java    ResumeService.java
│   │   ├── application/  ApplicationController.java
│   │   ├── interview/    InterviewController.java
│   │   ├── hr/           OfferController.java
│   │   └── admin/        AdminController.java
│   └── main/resources/
│       ├── application.yml                   # ONE datasource for all 7 features
│       ├── static/                           # the React build is baked in here
│       └── db/migration/V1__init.sql         # ONE schema: users, companies, applications…
├── pom.xml                                   # ONE dependency tree
└── Dockerfile                                # ONE image
```

One `mvn package` → one `placement-portal-1.0.0.jar` → one container image → one deployment. Every feature team commits into the same tree and ships on the same release train.

### Why the monolith was — and still is — the default

- **One thing to run.** `mvn spring-boot:run` or `npm start` and the whole product is up. No service discovery, no local Kubernetes, no 12 terminal tabs.
- **Refactoring is free.** Renaming a method across all 7 features is one IDE operation, and the compiler proves you didn't break anything. Across service boundaries, the compiler can't help you — you get a runtime 500 in staging instead.
- **No network between components.** An in-process function call is nanoseconds and cannot fail. An HTTP call is milliseconds and *can and will* fail. Every boundary you introduce is a new failure mode.
- **Transactions are trivial.** "Create application row + decrement company slot count" is one `BEGIN … COMMIT`. ACID does the work for you.
- **One place to look.** One log stream, one stack trace, one debugger, one profiler.

> **Production reality:** Monoliths are not legacy. Shopify, GitHub, Basecamp, and Stack Overflow run enormous, profitable monoliths in production today. "Monolith = old-fashioned" is a résumé cliché, not an engineering fact.

### Dry run: the cost of a one-line change

The instructor's example: *"I just want to change the Placement Report button from blue to another colour."* Trace it through a monolith.

```text
09:00  dev edits src/main/resources/static/css/theme.css   →  --btn-primary: #2563eb  →  #16a34a
09:02  git commit -m "chore(ui): placement report button to green" && git push
09:03  CI triggers: full pipeline for the WHOLE application
       ├─ mvn -B clean verify            6m 40s   (compiles all 7 feature packages)
       ├─ 1,847 unit tests               4m 10s   (all of them; you changed CSS)
       ├─ 214 integration tests          7m 55s   (spins Postgres via Testcontainers)
       ├─ npm run build (React)          2m 30s
       └─ docker build + push (410 MB)   3m 05s
09:28  artifact: registry.college.edu/placement-portal:1.4.7
09:30  deploy to staging → smoke tests   5m
09:40  ⛔ BLOCKED: release train is frozen — the interview-scheduling team merged a
       half-finished migration on Tuesday. Nothing ships until they revert or finish.
       ↓
Thu    revert lands, pipeline re-runs, release approved
Thu    prod deploy, rolling restart of 6 identical instances   4m
────────────────────────────────────────────────────────────────
Wall-clock for a 6-character CSS change: 2 days.
Actual work: 30 seconds.
```

That gap — 30 seconds of work, 2 days of process — is the pain that produced both microservices *and* DevOps. Note carefully: **the blocker wasn't the build, it was the shared release train.** Someone else's unfinished work froze your change. That is coupling of *people*, and it is the real reason large organisations split monoliths.

### Failure modes of a monolith

| Failure mode | What actually happens |
|---|---|
| **Single point of failure** | An unbounded `SELECT *` in the admin reports page OOMs the JVM. The JVM also served login, resume upload, and interview scheduling. **Whole portal down.** |
| **Coarse-grained scaling** | Resume PDF parsing is CPU-bound and needs 8 cores. Login is I/O-bound and needs almost nothing. You can only scale *the whole jar*, so you buy 8-core boxes to serve login pages. You pay for your most expensive component × every replica. |
| **Deploy queue / release train** | See the dry run above. Team velocity becomes `min(velocity of all teams)`. |
| **Tight coupling → accidental coupling** | Nothing stops the interview module from importing `AuthRepository` and querying the `users` table directly. Six months later `users` cannot be changed without breaking four modules. |
| **Blast radius of dependency upgrades** | Bumping Jackson for a CVE means retesting all 7 features. So nobody bumps it. So you ship a known CVE. (This is the seed of [DevSecOps](#13-devsecops--shift-left).) |
| **Long feedback loop** | 25-minute CI means developers batch changes, which makes each change bigger, which makes CI slower and failures harder to bisect. Vicious cycle. |

### The option the class skipped: the modular monolith

Between "one mud ball" and "17 services" sits the **modular monolith** — one deployable, but with *enforced* internal module boundaries. Modules talk only through published interfaces; each module owns its own tables and no other module may query them.

```text
placement-portal/
├── modules/
│   ├── auth/           ← exposes AuthApi only; owns tables auth_*
│   ├── company/        ← exposes CompanyApi only; owns tables company_*
│   ├── application/    ← depends on AuthApi, CompanyApi (interfaces, not internals)
│   └── interview/
└── app/                ← the only module that wires everything and builds the jar
```

Enforce it mechanically — Java `module-info.java` / ArchUnit tests, .NET internal visibility, Go internal packages, ESLint `no-restricted-imports`. If a module tries to reach into another's internals, **the build fails.**

> **Interview tip:** "Modular monolith first, extract services when a boundary proves it needs independent deployment or independent scaling" is the answer a senior engineer gives. It gets you the clean boundaries of microservices with the operational simplicity of a monolith, and it makes later extraction cheap because the seams already exist. If you say "always microservices," a good interviewer will ask you to cost out the ops overhead and watch you struggle.

---

## Part 3 — Microservices architecture

### What it is

> **Board (#1):** *"Microservice Architecture"*

A **microservice architecture** splits the application into a set of small services, each of which:

- owns **one business capability**,
- owns **its own data** (nobody else touches its tables),
- is **independently deployable** — shipping it does not require shipping anything else,
- communicates over the **network** via well-defined contracts (REST/gRPC/events),
- can be built by a **small team** in whatever language and datastore fits.

Independent deployability is the load-bearing property. If service A cannot ship without service B shipping at the same time, you have a **distributed monolith** — all the ops cost of microservices and none of the benefit. That is the most common way microservice migrations fail.

### The class analogies (both good, keep them)

**The university analogy.** When you join a college you don't go to the *library* to pay your fees, and you don't go to the *finance office* to complain about a faculty member. There's an admissions department, a finance department, an HOD per branch, a library. Each has its own staff, its own records, its own counter. You interact through a defined interface — a form, a queue, a portal. That's bounded contexts and APIs.

**The Zepto analogy.** Adding milk to your cart is one team's code. Paying for it is a *completely different* team's code. Cart has nothing to do with payment reconciliation; payment has nothing to do with the user's login session. Separate codebases, separate deploys, separate on-call rotations.

### Concrete: placement-portal as services

```text
placement-portal/                          # a monorepo is fine — deploys are still independent
├── services/
│   ├── auth-svc/          Node + Express   → Postgres  auth_db      :8081
│   ├── company-svc/       Java Spring Boot → Postgres  company_db   :8082
│   ├── resume-svc/        Python FastAPI   → S3 + Postgres resume_db:8083
│   ├── application-svc/   Java Spring Boot → Postgres  app_db       :8084
│   ├── interview-svc/     Go              → Postgres  interview_db :8085
│   ├── offer-svc/         Java Spring Boot → Postgres  offer_db     :8086
│   └── notification-svc/  Python          → Redis + SES            :8087
├── web/                   React SPA (its own deploy, served from CDN)
└── platform/
    ├── k8s/               one Deployment + Service per svc
    └── terraform/         VPC, EKS, RDS instances, S3 buckets
```

```mermaid
graph TD
    U[Student browser] --> CDN[CloudFront + S3<br/>React SPA]
    U --> GW[API Gateway / Ingress<br/>ALB]

    GW --> A[auth-svc<br/>:8081]
    GW --> C[company-svc<br/>:8082]
    GW --> R[resume-svc<br/>:8083]
    GW --> AP[application-svc<br/>:8084]
    GW --> I[interview-svc<br/>:8085]
    GW --> O[offer-svc<br/>:8086]

    A --> ADB[(auth_db)]
    C --> CDB[(company_db)]
    R --> RDB[(resume_db)]
    R --> S3[(S3 resumes bucket)]
    AP --> APDB[(app_db)]
    I --> IDB[(interview_db)]
    O --> ODB[(offer_db)]

    AP -.->|publishes ApplicationSubmitted| K{{Kafka / SNS}}
    K -.-> N[notification-svc]
    K -.-> I
    N --> SES[(Amazon SES)]

    style K fill:#1f2937,stroke:#60a5fa,color:#fff
    style GW fill:#1f2937,stroke:#fbbf24,color:#fff
```

Note the two communication styles, because interviewers dig here:

- **Synchronous (solid arrows).** `application-svc` asks `company-svc` "is this student eligible for job 4471?" over HTTP/gRPC and waits. Simple, but it makes `application-svc`'s availability a *product* of every service it calls. Three dependencies at 99.9% each ≈ 99.7% for you.
- **Asynchronous (dotted arrows).** `application-svc` writes its row, commits, and publishes `ApplicationSubmitted`. `notification-svc` and `interview-svc` react whenever they can. `notification-svc` being down no longer breaks applying — mails just go out late. **This is how you buy back availability**, and it's why event-driven design and microservices show up together.

### The failure story from class, told properly

The instructor's point: *"if the frontend doesn't come up, in a monolith the whole website fails; in microservices one component down doesn't kill the others. You see 404, 502, 503."* That's right, and it's worth knowing what those codes actually mean, because this is a standard interview follow-up.

| Code | Name | Who emits it | What it means in the placement portal |
|---|---|---|---|
| `404` | Not Found | any service | Route/resource doesn't exist. Often a bad client path, sometimes a mis-configured Ingress rule. |
| `500` | Internal Server Error | the app itself | Your code threw. The app is **up** — it answered — it just failed. |
| `502` | Bad Gateway | proxy/LB | The proxy reached the upstream pod and got garbage or a dropped connection. Usually **the pod crashed or is still booting.** |
| `503` | Service Unavailable | proxy/LB | The proxy has **no healthy upstream at all** — every pod failed its readiness probe, or the Service has zero endpoints. |
| `504` | Gateway Timeout | proxy/LB | Upstream is alive but didn't answer within the proxy timeout. Slow query, deadlock, thread-pool exhaustion. |

> **Gotcha:** 502 vs 503 is the single most useful diagnostic split in production. **503 = "nothing is there"** → check `kubectl get endpoints`, readiness probes, label selectors. **502 = "something is there but broken"** → check the pod's own logs and whether it's crash-looping. Being able to say this in an interview immediately reads as "has actually operated a system."

And the frontend-side symptom the instructor described — *"sometimes the frontend doesn't load, you see a JSON like `payment not found`"* — is the graceful-degradation payoff. The SPA still loads from the CDN, renders the shell, and shows an error only in the one panel whose service is down. In a monolith the same fault serves a blank 502 page for the entire product.

### The real costs of microservices

The class listed "more operational complexity" — correct, but it's worth unpacking, because *this* is what separates a candidate who has read a blog post from one who has run a system.

> **Board (#2):** microservices = *"more operational complexity"* · *"easily deployable"* · *"micro-components for each feature"* · *"loosely coupled"*

1. **The network is now part of your business logic.** Every call can be slow, can fail, can succeed-but-you-never-hear-back. You need timeouts (always), retries (with jitter and caps), circuit breakers, and idempotency keys. Retry without idempotency = duplicate job applications.
2. **No distributed transactions.** "Create application AND decrement the company's remaining slots" now spans two databases. Two-phase commit is a trap at scale; you use a **saga** — a sequence of local transactions with compensating actions — and you accept **eventual consistency**. Students consistently underestimate this. It is the hardest part of microservices, not the YAML.
3. **Debugging requires infrastructure you must build first.** One request touches 6 services. You cannot grep 6 log files by hand. You need **correlation IDs** propagated everywhere, centralised logs, and **distributed tracing** (OpenTelemetry → Jaeger/Tempo). Without it, "the portal is slow" is unanswerable.
4. **Ops multiplies.** 7 services × (pipeline + image + secrets + dashboards + alerts + on-call runbook + dependency upgrades). This is *the* fixed cost, and it's why a 3-person team should not do microservices.
5. **Latency adds up.** Five in-process calls become five network hops. Each is ~1–5 ms inside a cluster; a chatty design turns a 20 ms page into 300 ms.
6. **Cloud bill goes up before it goes down.** A student in class raised exactly this and was right: 7 RDS instances, 7 sets of replicas, a load balancer, Kafka, and a service mesh cost far more than one EC2 box. Microservices save money only at a scale where you can *right-size each component independently*.
7. **Local development gets hard.** "Run the whole product on my laptop" stops being possible. You need docker-compose profiles, Tilt/Skaffold, or shared dev namespaces.

### When *not* to use microservices

- Team of fewer than ~10 engineers, or fewer engineers than proposed services.
- Domain boundaries not yet understood. **Splitting on the wrong seams is far more expensive than not splitting** — you get chatty services and cross-service transactions everywhere.
- Greenfield product still hunting for product-market fit; requirements change weekly and boundaries move.
- No CI/CD, no containers, no observability yet. Microservices without automation is just a monolith you have to SSH into 7 times.

> **Production reality:** Martin Fowler's [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html) is still the mainstream senior position in 2026, now usually phrased as "modular monolith first." Start with one deployable and hard internal boundaries; extract a service when a specific boundary earns it (needs separate scaling, separate release cadence, separate language, or separate compliance boundary).

---

## Part 4 — Monolith vs. microservices: the decision

### The board comparison, expanded

> **Board (#2)** — reproduced faithfully, then extended.

| Dimension | Monolith | Microservices |
|---|---|---|
| **Getting started** | ✅ Simple to start (board #1) | ❌ More operational complexity (board #1) |
| **Deployment** | ❌ Complex, delayed deploys (board #2) | ✅ Easily deployable, independently (board #2) |
| **Codebase** | One common codebase (board #3) | Micro-components per feature (board #3) |
| **Coupling** | Tightly coupled, more often (board #4) | Loosely coupled (board #4) |
| **Scaling** | Whole app only; pay for the worst component × N | Per-service; scale `resume-svc` to 20, `offer-svc` stays at 2 |
| **Fault isolation** | None — one OOM kills everything | Strong — `notification-svc` down ⇒ mails delayed only |
| **Data** | One schema, ACID transactions, easy joins | DB per service, sagas, eventual consistency, no cross-service joins |
| **Tech choice** | One stack for everything | Per-service: Go for `interview-svc`, Python for `resume-svc` |
| **Team model** | Shared ownership, shared release train | One team owns a service end-to-end, ships on its own cadence |
| **Debugging** | Single stack trace | Distributed tracing required |
| **Refactoring across boundaries** | ✅ Compiler-checked | ❌ Contract versioning, backward compatibility, deprecation cycles |
| **Infra cost at small scale** | ✅ Low | ❌ Substantially higher |
| **Infra cost at large scale** | ❌ Wasteful (over-provision everything) | ✅ Efficient (right-size each) |
| **Onboarding a junior** | Big codebase, but one mental model | Small codebase, but must learn the whole distributed system |

### The quiz, answered properly

> **Board (#13):** *"To build a 'College Placement Application', which type of architecture will you use? ① Monolith ② Microservice"* — the instructor boxed **Microservice**.

The instructor's reasoning was sound and worth reconstructing:

1. The portal has **6–7 genuinely distinct capabilities** (see Part 1) with different owners and different change rates.
2. **Load is spiky and correlated.** On placement day, 10,000 students hit one job posting in the same 5 minutes. If the monolith saturates at 8,000 concurrent users, the portal dies exactly when it matters most. Resume upload and application submission need to scale hard and independently; the admin reports page does not.
3. **The dataset only grows.** New batch every year, alumni data retained forever. There is no point at which you can stop scaling.
4. **A single failure takes down everything.** Losing the portal during the placement window is not "an outage," it's a career event for hundreds of students.

The nuance the class arrived at through Q&A — and this is the part to actually remember:

> **Interview tip:** The strongest answer is **conditional, and you state the condition first.** "For a single college, 500 students, one placement season a year, run a **modular monolith** — the complexity isn't earned. For a multi-college SaaS placement platform with 10k+ concurrent applicants on placement day, **microservices**, and I'd extract in this order: `resume-svc` first (CPU-heavy, spiky, S3-bound), then `notification-svc` (async, failure-tolerant), then `application-svc`. I'd keep auth and admin in the core until they prove they need to move." Naming an **extraction order** is what makes it sound like experience rather than recitation.

### The two industry cases the class referenced — corrected

> **Transcript correction — the Amazon story.** The instructor said Amazon's monolith "crashed during some streaming" and that's why they moved to microservices. The actual, well-documented history: by 2001 Amazon.com ran a monolith called **Obidos** on top of shared databases. The bottleneck wasn't a single crash — it was that *every* schema change needed a DBA, so teams couldn't ship independently. The migration to service-oriented architecture took roughly **three years**, pulling functional units out and wrapping each in a web-service interface, with **no shared databases**. It was reinforced by Bezos's 2002 API mandate (all teams expose data only through service interfaces, no back-door DB access). Sources: [Werner Vogels, ACM Queue 2006](https://queue.acm.org/detail.cfm?id=1142065), [The New Stack](https://thenewstack.io/led-amazon-microservices-architecture/), [Amazon's 1998 Distributed Computing Manifesto](https://www.allthingsdistributed.com/2022/11/amazon-1998-distributed-computing-manifesto.html).

> **Transcript correction — "Microsoft keeps monoliths because their old code is in C."** This was a second-hand anecdote in class. Treat it as an anecdote, not a fact. The *defensible* general principle underneath it is real and worth knowing: **large legacy monoliths often stay monoliths because the migration cost exceeds the benefit.** No customer pays for "we rewrote it in microservices." The instructor's own framing was the right one: *"what is working, don't touch it."*

> **The counter-case the class didn't mention — and you should.** In March 2023 **Amazon Prime Video's Video Quality Analysis team went the other way**: they collapsed a distributed, AWS Step Functions + S3-based microservice pipeline into a **single monolithic process** on EC2/ECS. Result: they broke past a hard scaling ceiling they'd hit at 5% of target load, and cut cost **over 90%** — mostly by eliminating S3 round-trips and orchestration overhead between components that were passing video frames back and forth. ([Prime Video engineering write-up coverage](https://devclass.com/2023/05/05/reduce-costs-by-90-by-moving-from-microservices-to-monolith/))
>
> The lesson is not "microservices bad." It's that **service boundaries should follow business capabilities, not processing steps.** Splitting a tight, high-throughput data pipeline into services means paying network + serialisation cost on every frame. Bringing this up unprompted in an interview is a strong signal.

---

## Part 5 — What DevOps actually is

> **Board (#3):** *"DevOps = Dev + Ops"*

### The literal decomposition (the class answer)

- **Dev** — developers: write the code, own the features.
- **Ops** — operations: deploy it, run it, keep it up, get paged at 3 AM.

### The historical problem it solves — "the wall of confusion"

Before ~2009, Dev and Ops were separate departments with **opposed incentives**:

- Dev was measured on **features shipped**. More change = good.
- Ops was measured on **uptime**. Change is the #1 cause of outages, so change = bad.

The result was ceremonial: Dev "threw the build over the wall" with a Word document of deployment steps. Ops ran the steps, something differed from the dev machine, it broke, and each side blamed the other. Releases were quarterly, took a weekend, and needed a war room and a rollback plan nobody had tested.

**DevOps is the response:** make the people who build the thing also responsible for running it, and remove the manual toil that made shipping scary in the first place. "You build it, you run it" (Werner Vogels' phrase, from that same Amazon transition).

```mermaid
graph LR
    subgraph BEFORE["Before — the wall of confusion"]
        D1[Dev<br/>measured on features] -->|"tarball + a Word doc<br/>quarterly"| W[/"🧱 WALL"/]
        W --> O1[Ops<br/>measured on uptime]
        O1 -.->|"it works on my machine"| D1
    end
    subgraph AFTER["After — DevOps"]
        T[One team owns build AND run] --> P[Automated pipeline:<br/>build · test · scan · deploy]
        P --> R[Runs in prod]
        R -->|"metrics, logs, traces,<br/>the same team's pager"| T
    end
    BEFORE ~~~ AFTER
```

### Definition worth memorising

> **DevOps** is a set of cultural practices and automation that shortens the time from *"a developer commits a change"* to *"that change is safely running in production and observed"* — while **increasing** stability rather than trading it away.

The counter-intuitive, empirically-established part is the last clause. Two decades of DORA research show speed and stability are **positively** correlated: teams that deploy more often have *lower* change-failure rates, because small changes are easier to reason about, review, test, and roll back.

### CALMS — the five pillars

| Pillar | Meaning | Concretely, in the placement portal |
|---|---|---|
| **C**ulture | Blameless postmortems; shared ownership of prod | The dev who wrote `resume-svc` is on its pager |
| **A**utomation | No manual step in the path to prod | `git push` → tests → scan → image → deploy, zero humans |
| **L**ean | Small batches, limit WIP, remove queues | Ship one PR at a time, not a quarterly release train |
| **M**easurement | Instrument everything; decide with data | p95 latency and error rate per service, DORA metrics per team |
| **S**haring | Runbooks, dashboards, blameless writeups in the open | Postmortem for "placement-day 503s" readable by all teams |

### How DevOps is measured: DORA metrics

Interviewers love this because it separates buzzword people from practitioners. [DORA](https://dora.dev/guides/dora-metrics-four-keys/) originally defined **four keys**; the current framing has **five**, split into throughput and instability:

**Throughput**
1. **Deployment Frequency** — how often you deploy to production.
2. **Change Lead Time** — commit → running in production.
3. **Failed Deployment Recovery Time** — how fast you recover from a deploy that needs immediate intervention. *(Previously phrased as MTTR.)*

**Instability**
4. **Change Fail Rate** — % of deploys needing immediate intervention (rollback / hotfix).
5. **Deployment Rework Rate** — % of deploys that were unplanned, triggered by a production incident.

> **Note:** DORA's own current guidance warns against turning these into org-wide mandates — "deploy 10× a day or else" gets you gamed metrics, not better software. Use them as a **conversation starter about bottlenecks**, per team, with context. The [2025 State of DevOps Report](https://dora.dev/research/)'s headline finding is that **AI amplifies whatever your underlying sociotechnical system already is** — good systems get much faster, bad systems get faster at producing bad outcomes.

### Three things DevOps is *not*

1. **Not a tool.** You cannot buy DevOps. "We use Jenkins, so we do DevOps" is like "we own a treadmill, so we're fit."
2. **Not a job title, strictly speaking** — though the industry has thoroughly ignored this and "DevOps Engineer" is a real, well-paid role. Be aware of the purist objection; don't die on the hill.
3. **Not a separate team you throw work at.** The classic anti-pattern: create a "DevOps team," and you've rebuilt the wall of confusion with a new sign on it. The healthy version is a **platform team** that builds self-service capability for product teams (see [Part 8 — Job roles](#part-8--job-roles)).

---

## Part 6 — The DevOps lifecycle

> **Board (#9):** `Plan → Code → Build → Test → Release → Deploy → Operate → Monitor` (and the arrow loops back)

```mermaid
graph LR
    P[Plan] --> C[Code] --> B[Build] --> T[Test] --> R[Release] --> D[Deploy] --> O[Operate] --> M[Monitor]
    M -->|feedback: incidents, metrics,<br/>user behaviour| P

    P -.- p1["Jira, Linear<br/>ADRs, threat model"]
    C -.- c1["Git, GitHub, PRs<br/>SonarQube in IDE"]
    B -.- b1["Maven/npm, Docker build<br/>GitHub Actions, Jenkins"]
    T -.- t1["unit, integration, e2e<br/>SAST, SCA, image scan"]
    R -.- r1["version, tag, changelog<br/>approval gate = CDelivery"]
    D -.- d1["Helm, Argo CD<br/>blue-green, canary"]
    O -.- o1["Kubernetes, HPA<br/>runbooks, on-call"]
    M -.- m1["Prometheus, Grafana<br/>Loki, OTel, alerts"]
```

Walk each stage on the placement portal. The class covered the names; here's what actually happens.

| Stage | What happens | Who/what does it | Failure that shows up here |
|---|---|---|---|
| **Plan** | Decide *what* to build and *why*. Requirements, acceptance criteria, capacity estimate ("10k concurrent on placement day"), and — if you're mature — a **threat model** and an **ADR** for the architecture decision. | PM + tech lead + security | Building the wrong thing. No amount of DevOps saves you. |
| **Code** | Write it, review it. Feature branch → PR → review → merge to `main`. Linting and IDE-level static analysis catch problems before they're even committed. | Developers, Git/GitHub | Untested code, no reviewers, direct pushes to `main` |
| **Build** | Turn source into a deployable artifact. `mvn package`, `npm run build`, `docker build`. **Build once, promote the same artifact** through every environment. | CI runner | "Works in staging, breaks in prod" — because you rebuilt instead of promoting |
| **Test** | Prove it works and is safe. Unit → integration → contract → e2e; plus **SAST**, **SCA**, **container image scan**, **IaC scan**. | CI runner | Flaky tests train the team to ignore red builds. Fatal culturally. |
| **Release** | Decide the artifact is *eligible* for production. Tag `v1.4.7`, write the changelog, satisfy the approval gate. **This stage is where CDelivery and CDeployment differ.** | Release manager, or nobody (automated) | Untested rollback plan |
| **Deploy** | Put it in production. Rolling / blue-green / canary. Feature flags to decouple *deploy* from *release to users*. | Helm, Argo CD, Kubernetes | Big-bang deploy with no rollback; no health gate |
| **Operate** | Keep it running. Scale up for placement day, scale down after. Rotate secrets, patch nodes, respond to pages. | SRE / on-call, HPA, Kubernetes | No runbook; only one person knows how it works |
| **Monitor** | Know what's happening: metrics, logs, traces, SLOs, alerts. | Prometheus, Grafana, Loki, OpenTelemetry | Alerting on CPU instead of on user-visible symptoms |

> **Gotcha:** The class glossed **Release** as "cross-verifying everything before it goes live," which is fine but undersells it. In modern practice, **Deploy ≠ Release.** You *deploy* code to production behind a feature flag turned off, then *release* it to 1% of users, then 50%, then 100% — with no further deploys. Decoupling these two is how large orgs ship continuously without betting the company on each push. This distinction is a common senior interview question.

The instructor's Flipkart/Google-doodle example (icons that change for Diwali, IPL, a football tournament) is exactly this: the asset is deployed well in advance and *released* by flipping a date-gated flag. Nobody ships code at midnight on Diwali.

---

## Part 7 — The toolchain, in the order taught

The board listed 13 numbered items. Each gets: **why it exists → what it replaced → what you'll actually run → current state in 2026.**

### 1. Git & GitHub

> **Board (#4):** *"1. Git & GitHub"*

**Why it exists:** Before distributed version control, "the code" lived on a central server (SVN, CVS, Perforce). Branching was expensive, so nobody branched; you edited trunk and prayed. Losing the server lost your history.

**Git** gives every developer a **full copy of the entire history**, makes branching nearly free (a branch is a 40-byte pointer to a commit), and makes merging a solved problem. **GitHub** adds the collaboration layer on top: pull requests, code review, issues, Actions.

**Why it's #1 in DevOps:** Git is the **source of truth** that everything else keys off. CI triggers on push. IaC lives in Git. GitOps makes Git the *desired state of production* (item 12). No Git, no DevOps.

```bash
# The 90% you'll use daily
git switch -c feat/resume-parser          # new branch (modern alternative to checkout -b)
git add -p                                # stage hunk by hunk — review your own diff
git commit -m "feat(resume): parse CGPA from PDF text layer"
git push -u origin feat/resume-parser
# ...open PR, get review, merge...

git switch main && git pull --ff-only     # never create surprise merge commits on main
git log --oneline --graph --decorate -15  # what actually happened
git blame -L 40,60 src/parser.py          # who changed these lines and why
git bisect start HEAD v1.4.0              # binary-search for the commit that broke it
```

> **Interview tip:** Two questions come up constantly. **(a) `merge` vs `rebase`:** merge preserves true history and is safe on shared branches; rebase rewrites commits onto a new base for a linear history and must never be done on a branch others have pulled ("never rebase public history"). **(b) `reset` vs `revert`:** `reset` moves your branch pointer (rewrites history — local only); `revert` creates a *new* commit that undoes an old one (safe on `main`, and the only correct answer for "undo a bad commit that's already pushed").

Covered in depth in a later note: `notes/02-git-and-github.md`.

### 2. Docker

> **Board (#4):** *"2. Docker"*

**Why it exists:** "Works on my machine." Your laptop has Node 22 and OpenSSL 3; the server has Node 18 and OpenSSL 1.1. The app dies. Before containers you solved this with a 40-page runbook, or with a full VM per app — which meant booting a whole guest OS (GBs of RAM, ~60 s startup) to run a 30 MB Python service.

**Docker** packages the app **with its entire userland** — libraries, runtime, config — into an **image**, and runs it as a **container**: an ordinary Linux process isolated by kernel features (namespaces for what it can *see*, cgroups for what it can *use*, union filesystems for layered images). No guest kernel. Milliseconds to start, megabytes of overhead.

| | Virtual machine | Container |
|---|---|---|
| Isolation boundary | Hypervisor; separate guest kernel | Kernel namespaces + cgroups; **shared host kernel** |
| Size | GBs (full OS) | MBs (just your app + deps) |
| Boot time | 30–90 s | 50–500 ms |
| Density per host | tens | hundreds to thousands |
| Security boundary | Strong (hardware-assisted) | Weaker — a kernel escape is a host compromise |
| Runs a different OS kernel? | Yes (Windows guest on Linux host) | No — Linux containers need a Linux kernel |

> **Note (Windows 11 / your setup):** Docker Desktop on Windows runs a Linux VM under **WSL2** and your containers run inside *that* kernel. So "containers are lighter than VMs" is true, but on Windows you're paying for one VM up front and then getting cheap containers inside it. Enable WSL2 integration for your distro (`Docker Desktop → Settings → Resources → WSL Integration`) so `docker` works from both PowerShell and your WSL shell.

**Why the instructor called it "the base":** every later tool consumes container images. Kubernetes schedules them. CI produces them. Trivy scans them. Learn Docker properly or nothing downstream makes sense.

Here is the Dockerfile shape the instructor walked through verbally — base image → workdir → deps → copy → expose → entrypoint — written the way you'd actually ship it:

```dockerfile
# services/resume-svc/Dockerfile — multi-stage, non-root, pinned
# ---- build stage: has compilers, never ships ----
FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements.txt .
# --no-cache-dir keeps the layer small; wheels are built here, not at runtime
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime stage: only what's needed to run ----
FROM python:3.13-slim
# Run as a non-root user. A container escape as root == host root.
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser src/ ./src/
USER 10001
EXPOSE 8083                                  # documentation only; does NOT publish the port
# Give the orchestrator something to probe
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8083/healthz')"
# exec form (no shell) so PID 1 receives SIGTERM and can shut down gracefully
ENTRYPOINT ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8083"]
```

```bash
docker build -t placement/resume-svc:1.4.7 services/resume-svc
docker run -d --name resume -p 8083:8083 --env-file .env placement/resume-svc:1.4.7
docker logs -f resume
docker exec -it resume sh                    # get a shell inside a running container
docker image ls --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

> **Gotcha:** `EXPOSE 8083` does **not** publish anything. It's metadata. Only `-p 8083:8083` (or a Kubernetes Service) actually makes the port reachable. Candidates get this wrong constantly.

> **Gotcha:** `ENTRYPOINT ["python", ...]` (exec form) vs `ENTRYPOINT python ...` (shell form). Shell form runs your process as a *child* of `/bin/sh`, so `SIGTERM` from `docker stop` / Kubernetes goes to the shell and your app never gets it — you get a hard 10-second SIGKILL, dropped connections, and no graceful shutdown. **Always use exec form.**

**Current state (verified 11 Aug 2026):** Docker Engine **29.7.2** (released 5 Aug 2026) — [endoflife.date/docker-engine](https://endoflife.date/docker-engine).

### 3. Python (and why Go is the second language)

> **Board (#4):** *"3. Python → Go"*

**Why Python:** it's the glue. AWS SDK (`boto3`), Kubernetes client, Ansible (itself written in Python), log parsing, report generation, cost scripts, Lambda handlers, CI helper scripts. Fast to write, ubiquitous, huge library ecosystem. **Focus here first** — the instructor was explicit about that.

```python
#!/usr/bin/env python3
"""Find EC2 instances in ap-south-1 with no 'Owner' tag — the classic cost leak."""
import boto3

ec2 = boto3.client("ec2", region_name="ap-south-1")
paginator = ec2.get_paginator("describe_instances")

untagged = []
for page in paginator.paginate(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
):
    for reservation in page["Reservations"]:
        for inst in reservation["Instances"]:
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            if "Owner" not in tags:
                untagged.append((inst["InstanceId"], inst["InstanceType"],
                                 tags.get("Name", "<unnamed>")))

for iid, itype, name in sorted(untagged):
    print(f"{iid:22} {itype:12} {name}")
print(f"\n{len(untagged)} running instances with no Owner tag → chase these down")
```

**Why Go is second:** the instructor asked the class this and it's a genuinely good question. **Docker, Kubernetes, Terraform, Prometheus, Helm, etcd, containerd, Trivy, and Argo CD are all written in Go.** Reasons Go won this niche:

- **Static single binary.** `GOOS=linux go build` gives one file with no runtime, no interpreter, no `LD_LIBRARY_PATH`. You can `FROM scratch` a 12 MB image. Perfect for tools that must run anywhere.
- **Goroutines** make "watch 5,000 pods concurrently" natural — Kubernetes is an enormous concurrent reconciliation engine.
- **Fast compiles + strong stdlib** (especially `net/http`) for network services.

So: Python for *automation you write*; Go for *reading and contributing to the tools you use*, and for writing Kubernetes controllers/operators.

> **Transcript correction:** The transcript's tool list included "IAM, SQL" as Go-written tools — that's ASR noise. The accurate list is Docker, Kubernetes, Terraform, Prometheus, Helm, etcd, containerd, Trivy, Argo CD.

### 4. Linux — "the heart of DevOps"

> **Board (#4):** *"4. Linux — heart of devops"*

**Why:** essentially all servers, all containers, all Kubernetes nodes, and most CI runners are Linux. Every abstraction above it (containers = namespaces + cgroups; volumes = mounts; networking = iptables/nftables/eBPF) is a Linux kernel feature with a friendlier name. When Kubernetes misbehaves, you debug it *as Linux*.

The instructor opened with `chmod`, so:

```bash
# Permissions — the model interviewers probe
ls -l id_rsa
# -rw-------  1 ubuntu ubuntu 1679 Aug 11 09:40 id_rsa
#  ↑↑↑ ↑↑↑ ↑↑↑
#  usr grp oth        r=4  w=2  x=1

chmod 400 ~/.ssh/placement-portal.pem   # SSH keys MUST be 400/600 or ssh refuses them
chmod 755 deploy.sh                     # rwx for owner, r-x for group+others
chmod -R g+w /srv/app/uploads           # recursive, symbolic form
chown -R appuser:appuser /srv/app       # ownership, not permissions — different thing
```

> **Gotcha:** the #1 real-world `chmod` error. `Permissions 0644 for 'key.pem' are too open. This private key will be ignored.` → `chmod 400 key.pem`. On **Windows**, `chmod` doesn't exist for NTFS files; use `icacls key.pem /inheritance:r /grant:r "$env:USERNAME:(R)"`, or keep the key inside WSL2 where POSIX permissions are real.

The survival set, grouped by what you're actually trying to find out:

```bash
# Where am I / what is this box?
uname -a; cat /etc/os-release; uptime

# What's eating the machine?
top          # or htop — live CPU/mem by process
free -h      # memory, and crucially how much is cache vs used
df -h        # disk FULL is the single most common cause of "everything is broken"
du -sh /var/log/* | sort -h | tail   # what filled it
iostat -x 2  # disk saturation

# What is running / listening?
ps aux --sort=-%mem | head
systemctl status placement-portal
journalctl -u placement-portal -f --since "10 min ago"
ss -tulpn                            # sockets: which process owns which port

# Text surgery
grep -rn "NullPointerException" /var/log/app/ | tail -50
tail -f /var/log/nginx/error.log
awk '{print $9}' access.log | sort | uniq -c | sort -rn   # status-code histogram
sed -i 's/localhost/db.internal/g' application.yml
find /var/log -name "*.gz" -mtime +30 -delete
```

Covered in depth later: `notes/03-linux-fundamentals.md`.

### 5. Networking

> **Board (#5):** *"5. Networking — TCP/UDP, OSI layer"*

**Why DevOps cares:** every production incident that isn't "the app threw an exception" is a networking problem. Wrong security group, DNS not propagated, service has no endpoints, TLS cert expired, MTU mismatch, connection pool exhausted. And Kubernetes is, above all, a networking system.

**The layers you actually use** (the class asked the OSI question; here's the pragmatic version):

| Layer | Name | Placement-portal example | Debug with |
|---|---|---|---|
| 7 | Application | HTTP request to `/api/applications` | `curl -v`, browser devtools |
| 6/5 | Presentation/Session | TLS handshake, cookies | `openssl s_client` |
| 4 | Transport | TCP port 8084, UDP 53 for DNS | `ss`, `nc`, `telnet` |
| 3 | Network | IP routing, VPC route tables | `ping`, `traceroute`, `ip route` |
| 2 | Data link | ENI, MAC, VLAN | `ip link`, `arp` |
| 1 | Physical | fibre, NIC | (someone else's problem) |

> **Interview tip:** In practice engineers reason in the **TCP/IP 4-layer model** (Link → Internet → Transport → Application) and treat OSI as vocabulary. Know both; know that "layer 4 load balancer" (AWS NLB — routes by IP:port) vs "layer 7 load balancer" (AWS ALB — routes by Host header and URL path) is the distinction that actually matters in cloud work.

**TCP vs UDP** — asked constantly:

| | TCP | UDP |
|---|---|---|
| Connection | 3-way handshake (SYN, SYN-ACK, ACK) | Connectionless, fire-and-forget |
| Guarantees | Ordered, reliable, retransmits, flow + congestion control | None. Datagrams may be lost, duplicated, reordered |
| Overhead | 20-byte header + state per connection | 8-byte header, no state |
| Used by | HTTP/1.1, HTTP/2, SSH, TLS, Postgres, Redis | DNS, NTP, syslog, VXLAN, QUIC (→ **HTTP/3**), video/voice |

> **Note:** HTTP/3 runs over **QUIC**, which runs over **UDP** — so "HTTP is always TCP" is now wrong. Good detail to know.

**The debugging ladder the instructor walked through** (his sequence was right; here it is with the modern tool for each rung):

```bash
# 1. Does the name resolve?                      Layer 7/3
dig +short api.placement.college.edu
# 43.204.18.7

# 2. Is the host reachable at the IP layer?      Layer 3
ping -c 4 43.204.18.7
# 64 bytes from 43.204.18.7: icmp_seq=1 ttl=51 time=18.4 ms
#   ↑ ICMP replies prove routing works — they prove NOTHING about your app

# 3. Where does the path break / where's the latency?   Layer 3
traceroute 43.204.18.7            # Linux/macOS
tracert  43.204.18.7              # Windows (PowerShell)
mtr 43.204.18.7                   # traceroute + ping, continuous — the pro choice

# 4. Is the PORT open? (the instructor's question)      Layer 4
nc -zv 43.204.18.7 8084           # preferred: netcat, scriptable, exit code
# Connection to 43.204.18.7 8084 port [tcp/*] succeeded!
telnet 43.204.18.7 8084           # the classic; works, but often not installed
# Trying 43.204.18.7... Connected.   ← port open
# Trying 43.204.18.7... telnet: connect to address: Connection refused
#     ↑ refused  = something answered "no" → nothing listening on that port
# Trying 43.204.18.7... telnet: connect ... Connection timed out
#     ↑ timeout  = packets dropped silently → FIREWALL / security group

# 5. What's listening locally, and who owns it?         Layer 4
ss -tulpn | grep 8084
# tcp LISTEN 0 4096 *:8084 *:*  users:(("java",pid=2841,fd=42))
netstat -tulpn                    # legacy equivalent

# 6. Does the app actually answer correctly?            Layer 7
curl -sv -o /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} code=%{http_code}\n' \
  https://api.placement.college.edu/healthz

# 7. TLS specifics
openssl s_client -connect api.placement.college.edu:443 -servername api.placement.college.edu </dev/null 2>/dev/null | openssl x509 -noout -dates
# notBefore=Jun 12 00:00:00 2026 GMT
# notAfter =Sep 10 23:59:59 2026 GMT     ← expiring cert = the classic 3 AM page
```

> **Transcript correction:** the transcript says *"curl is a Windows command that we are not using."* Backwards. **`curl` is the single most important network debugging tool in DevOps** and ships on Linux, macOS, and Windows. What the instructor was likely reaching for is that **`tracert`** is the Windows spelling of `traceroute`. Also: **`netstat` is deprecated on modern Linux** in favour of `ss` (from `iproute2`) — `ss` is faster and is what you'll see in current runbooks, though `netstat` still works and still gets asked about in interviews.

**PowerShell equivalents** (you're on Windows 11):

| Purpose | Linux | PowerShell |
|---|---|---|
| Reachability | `ping -c 4 host` | `Test-Connection host -Count 4` |
| Port check | `nc -zv host 8084` | `Test-NetConnection host -Port 8084` |
| Route trace | `traceroute host` | `Test-NetConnection host -TraceRoute` / `tracert host` |
| Listening sockets | `ss -tulpn` | `Get-NetTCPConnection -State Listen \| Sort-Object LocalPort` |
| DNS lookup | `dig +short host` | `Resolve-DnsName host` |
| HTTP probe | `curl -sv URL` | `Invoke-WebRequest URL -Method Head` (or `curl.exe`, which ships with Win11) |

Covered in depth later: `notes/05-networking-for-devops.md`.

### 6. CI/CD

> **Board (#5):** *"6. CICD — Continuous Integration; CD = Continuous **deployment**; CD = Continuous **Delivery** — manual approval"*

The instructor's distinction here was **exactly right** and is one of the most-asked interview questions. Nail the vocabulary:

| Term | What it means | Where it ends | Human in the loop? |
|---|---|---|---|
| **Continuous Integration (CI)** | Every commit is automatically merged into `main` and verified: build + test + scan. Goal: `main` is always green and releasable. | A tested artifact exists | No |
| **Continuous Delivery (CD)** | Every green artifact is automatically pushed all the way to a **production-ready** state; deploying is a **one-click, always-available** business decision. | Waiting at the prod gate | **Yes — one approval click** |
| **Continuous Deployment (CD)** | Every green artifact goes to production **automatically**. No gate. | Live in production | **No** |

```mermaid
graph LR
    G[git push] --> CI["CI: build · unit · integration<br/>SAST · SCA · image scan"]
    CI -->|green| ART[artifact v1.4.7<br/>immutable image]
    ART --> STG[deploy → staging<br/>+ smoke tests]
    STG --> GATE{prod gate}
    GATE -->|"human clicks Approve"| PRD1[production]
    GATE -.->|"no gate at all"| PRD2[production]

    subgraph CDelivery["Continuous DELIVERY"]
        GATE
        PRD1
    end
    subgraph CDeployment["Continuous DEPLOYMENT"]
        PRD2
    end
    style GATE fill:#78350f,stroke:#fbbf24,color:#fff
```

> **Interview tip:** The follow-up is always *"which should we use?"* The honest answer: **Continuous Delivery for anything with regulatory, financial, or reputational consequence to a bad release** (payments, offer letters, medical) — you want a named human accountable. **Continuous Deployment where your automated verification is genuinely trustworthy and rollback is cheap and fast** (a stateless frontend behind feature flags with canary + auto-rollback on error-rate). Then add the kicker: *"and the prerequisite for Continuous Deployment isn't a tool, it's a test suite you'd bet production on plus automated rollback. Most teams that claim it actually have Continuous Delivery with a rubber-stamp approver."*

A complete, runnable pipeline for the placement portal:

```yaml
# .github/workflows/resume-svc.yml
name: resume-svc CI/CD

on:
  push:
    branches: [main]
    paths: ['services/resume-svc/**', '.github/workflows/resume-svc.yml']
  pull_request:
    paths: ['services/resume-svc/**']

# Least privilege by default; jobs opt in to what they need.
permissions:
  contents: read

env:
  IMAGE: ghcr.io/${{ github.repository }}/resume-svc
  AWS_REGION: ap-south-1
  EKS_CLUSTER: placement-portal-prod

jobs:
  # ---------- CI ----------
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: resume_test }
        options: >-
          --health-cmd pg_isready --health-interval 5s
          --health-timeout 5s --health-retries 10
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: '3.13'
          cache: pip
      - run: pip install -r services/resume-svc/requirements.txt -r services/resume-svc/requirements-dev.txt
      - name: Unit + integration tests
        working-directory: services/resume-svc
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/resume_test
        run: pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80

  sast:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write        # so Sonar can comment on the PR
    steps:
      - uses: actions/checkout@v5
        with: { fetch-depth: 0 }  # Sonar needs full history for new-code detection
      - name: SonarQube scan (SAST + quality gate)
        uses: SonarSource/sonarqube-scan-action@v6
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      - name: Fail the build if the quality gate fails
        uses: SonarSource/sonarqube-quality-gate-action@v1
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  build-and-scan:
    needs: [test, sast]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write             # push to GHCR
      id-token: write             # OIDC — no long-lived AWS keys
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v5
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v6
        with:
          context: services/resume-svc
          push: true
          tags: |
            ${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Trivy image scan — fail on HIGH/CRITICAL
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: ${{ env.IMAGE }}:${{ github.sha }}
          severity: HIGH,CRITICAL
          ignore-unfixed: true     # don't block on CVEs with no available patch
          exit-code: '1'
      - name: Generate SBOM (supply-chain evidence)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: ${{ env.IMAGE }}:${{ github.sha }}
          format: cyclonedx
          output: sbom.cdx.json
      - uses: actions/upload-artifact@v4
        with: { name: sbom, path: sbom.cdx.json }

  # ---------- CD: staging is automatic ----------
  deploy-staging:
    needs: build-and-scan
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-staging
          aws-region: ${{ env.AWS_REGION }}
      - run: aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }}-staging
      - run: |
          kubectl -n staging set image deployment/resume-svc \
            resume-svc=${{ env.IMAGE }}:${{ github.sha }}
          kubectl -n staging rollout status deployment/resume-svc --timeout=180s

  # ---------- CD: production requires approval  → CONTINUOUS DELIVERY ----------
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production        # ← configure required reviewers here. THIS is the gate.
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-prod
          aws-region: ${{ env.AWS_REGION }}
      - run: aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }}
      - run: |
          kubectl -n prod set image deployment/resume-svc \
            resume-svc=${{ env.IMAGE }}:${{ github.sha }}
          # rollout status is the health gate — non-zero exit means the new pods
          # never went Ready, and we roll back immediately.
          kubectl -n prod rollout status deployment/resume-svc --timeout=300s \
            || { kubectl -n prod rollout undo deployment/resume-svc; exit 1; }
```

Delete the `environment: production` line and that same file becomes **Continuous Deployment**. That one line is the entire difference.

> **Gotcha — the security point most tutorials skip:** notice `id-token: write` and `role-to-assume`. That's **OIDC federation** — GitHub gets a short-lived AWS credential per run. The alternative you'll see in bad tutorials is storing `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` as repo secrets: long-lived static keys that leak in logs, survive employee departures, and top the breach post-mortem charts. **Use OIDC.**

**Tool landscape in 2026:** **GitHub Actions** dominates for anything already on GitHub (free minutes on public repos, huge marketplace). **GitLab CI** for GitLab shops. **Jenkins** is still everywhere in enterprises — it's the incumbent, plugin-rich and self-hosted, and you *will* meet a `Jenkinsfile`. **Argo Workflows / Tekton** for Kubernetes-native pipelines. **CircleCI** and **Travis CI** have lost substantial share to Actions.

Covered later: `notes/07-ci-cd-with-github-actions-and-jenkins.md`.

### 7. Cloud

> **Board (#6):** *"7. Cloud — AWS, Azure, Oracle, GCP"*

**Why:** you no longer buy a server, wait 6 weeks for procurement, rack it, and over-provision for peak. You call an API and get capacity in 60 seconds, priced by the second, and you give it back when placement day ends. That elasticity is the economic precondition for everything else in DevOps.

The service map you need for the placement portal:

| Need | AWS | Azure | GCP |
|---|---|---|---|
| Virtual machine | **EC2** | Virtual Machines | Compute Engine |
| Object storage (resume PDFs) | **S3** | Blob Storage | Cloud Storage |
| Managed relational DB | **RDS** (Postgres/MySQL) | Azure Database for PostgreSQL | Cloud SQL |
| Managed Kubernetes | **EKS** | **AKS** | **GKE** |
| Container registry | ECR | ACR | Artifact Registry |
| Serverless functions | Lambda | Functions | Cloud Run functions |
| Network isolation | **VPC** | VNet | VPC |
| Layer-7 load balancer | ALB | Application Gateway | Cloud Load Balancing |
| Identity / permissions | **IAM** | Entra ID + RBAC | IAM |
| Secrets | Secrets Manager / SSM Parameter Store | Key Vault | Secret Manager |
| DNS | Route 53 | Azure DNS | Cloud DNS |
| CDN | CloudFront | Front Door | Cloud CDN |
| Managed events/queue | SNS + SQS / MSK | Event Grid / Service Bus | Pub/Sub |
| Metrics & logs | CloudWatch | Monitor | Cloud Monitoring |
| Managed LLM APIs | **Bedrock** | **Azure AI Foundry** | Vertex AI |

The instructor's EKS/AKS/GKE mapping was correct: **E**lastic **K**ubernetes **S**ervice, **A**zure **K**ubernetes **S**ervice, **G**oogle **K**ubernetes **E**ngine.

> **Production reality — the bill will be your problem.** The four ways students burn their free tier: (1) an idle NAT Gateway (~$32/month in `ap-south-1` just for existing, plus data processing), (2) unattached EBS volumes and old snapshots after you terminate instances, (3) an ALB left running (~$16–20/month idle), (4) **egress** — data *out* of AWS is billed, data in is free. Set an **AWS Budgets** alert at ₹500 on day one, tag everything with an `Owner`, and run `terraform destroy` when you finish a lab.

> **Security note the class skipped entirely:** never use your AWS **root** account for daily work. Create an IAM user or, better, use IAM Identity Center SSO; enable MFA on root and lock the credentials away. Never put access keys in code — use IAM **roles** (for EC2/EKS: instance profiles and IRSA; for CI: OIDC). A leaked key in a public GitHub repo gets found by scanners in **minutes** and the resulting crypto-mining bill can be five figures.

Covered later: `notes/08-aws-fundamentals.md`.

### 8. Kubernetes (K8s)

> **Board (#6):** *"8. Kubernetes — K8s — Pod, replicaset, stateful, volume"*

**The name:** Greek κυβερνήτης, "helmsman/pilot" (same root as *governor*). **K8s** = `K` + the **8** letters `ubernete` + `s`. The instructor's quiz answer was right.

**Who built it:** **Google**, released open-source in 2014, drawing on their internal **Borg** system. Donated to the **CNCF** in 2015 — so today it's CNCF-governed, not a Google product. That nuance matters in interviews.

**Why it exists:** Docker gives you *one container on one machine*. Production needs: hundreds of containers across dozens of machines, restarted when they die, rescheduled when a machine dies, load-balanced, rolling-updated with zero downtime, and scaled on demand. Doing that with shell scripts and `docker run` is how you get a 3 AM outage.

Kubernetes is a **declarative control loop**. You submit desired state ("I want 5 replicas of `resume-svc:1.4.7`"); controllers continuously compare actual to desired and act to close the gap. **This reconciliation loop is the single most important idea in Kubernetes** — everything else is a detail.

```mermaid
graph TB
    subgraph CP["Control plane"]
        API[kube-apiserver<br/>the only door in]
        ETCD[(etcd<br/>all cluster state)]
        SCHED[kube-scheduler<br/>assigns Pods → Nodes]
        CM[controller-manager<br/>runs the reconcile loops]
    end
    subgraph N1["Worker node 1"]
        K1[kubelet] --> C1[containerd]
        C1 --> P1[Pod: resume-svc]
        KP1[kube-proxy]
    end
    subgraph N2["Worker node 2"]
        K2[kubelet] --> C2[containerd]
        C2 --> P2[Pod: resume-svc]
        C2 --> P3[Pod: application-svc]
        KP2[kube-proxy]
    end
    U[kubectl / Argo CD] --> API
    API <--> ETCD
    SCHED --> API
    CM --> API
    K1 --> API
    K2 --> API
    style API fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style ETCD fill:#374151,stroke:#9ca3af,color:#fff
```

**The objects — the class named four; here are the ones you actually need:**

| Object | What it is | Placement-portal use |
|---|---|---|
| **Pod** | Smallest deployable unit: **one or more** containers sharing a network namespace (same IP, same `localhost`) and optionally volumes | One `resume-svc` container + optionally a log-shipper sidecar |
| **ReplicaSet** | Keeps exactly N identical Pods running | 5 replicas of `resume-svc` |
| **Deployment** | Manages ReplicaSets to give you **rolling updates and rollback** | What you actually write. Almost never create a bare Pod or ReplicaSet. |
| **Service** | Stable virtual IP + DNS name that load-balances to a changing set of Pods | `resume-svc.prod.svc.cluster.local:8083` |
| **Ingress / Gateway API** | HTTP(S) routing from outside the cluster into Services | `api.placement.college.edu/resumes/*` → `resume-svc` |
| **ConfigMap** | Non-secret config, injected as env vars or files | feature flags, log level, S3 bucket name |
| **Secret** | Same, for sensitive values (base64, **not encrypted by default**) | DB password, JWT signing key |
| **StatefulSet** | Pods with **stable identity** (`db-0`, `db-1`) and stable per-Pod storage, started/stopped in order | self-managed Postgres/MySQL, Kafka, etcd |
| **PersistentVolumeClaim** | A request for durable storage that survives Pod restarts | Postgres data directory on an EBS volume |
| **Job / CronJob** | Run-to-completion / scheduled work | nightly "email unplaced students" batch |
| **HorizontalPodAutoscaler** | Scales replica count on CPU/memory/custom metrics | 3 → 40 replicas on placement day, back down after |
| **Namespace** | Logical partition for isolation and quotas | `dev`, `staging`, `prod` |

> **Transcript correction — "Pod is nothing but a Docker container."** Close enough to start, wrong enough to fail an interview. Three corrections: **(1)** A Pod is a *wrapper* around one or more containers that share a network namespace and IP — this is what makes sidecars (service-mesh proxies, log shippers) possible. **(2)** The container inside is an **OCI** container, and since **Kubernetes v1.24 removed dockershim**, the runtime is normally **containerd** or **CRI-O**, *not* Docker. Images built with `docker build` still run perfectly — the OCI image format is standard ([dockershim FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/)). **(3)** Pods are **ephemeral and disposable**; they get new IPs on restart. That's exactly why Services exist.

> **Transcript correction — "we just do one Helm command to scale up/down."** **Helm is a package manager and templating tool** for Kubernetes — it renders and installs charts, tracks releases, and does `helm rollback`. It is *not* the scaling mechanism. Scaling is `kubectl scale deployment/resume-svc --replicas=20`, or declaratively via a **HorizontalPodAutoscaler** (which is what you actually want, so it's automatic).

Here's the manifest set the instructor described, written properly:

```yaml
# platform/k8s/resume-svc.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-svc
  namespace: prod
  labels: { app: resume-svc, tier: backend }
spec:
  replicas: 3
  revisionHistoryLimit: 5
  selector:
    matchLabels: { app: resume-svc }      # MUST match template labels below
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                          # at most 1 extra pod during rollout
      maxUnavailable: 0                    # never drop below 3 ready → zero-downtime
  template:
    metadata:
      labels: { app: resume-svc, tier: backend }
    spec:
      serviceAccountName: resume-svc       # bound to an IAM role via IRSA — no static keys
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: resume-svc
          image: ghcr.io/college/placement-portal/resume-svc:1.4.7   # pin a tag, never :latest
          ports:
            - containerPort: 8083
          env:
            - name: LOG_LEVEL
              valueFrom: { configMapKeyRef: { name: resume-config, key: log_level } }
            - name: DATABASE_URL
              valueFrom: { secretKeyRef: { name: resume-secrets, key: database_url } }
          # ---- Resources. Getting these wrong is the #1 cause of K8s pain. ----
          resources:
            requests: { cpu: "250m", memory: "512Mi" }   # scheduler uses this to place the pod
            limits:   { cpu: "1000m", memory: "1Gi" }    # exceed memory limit → OOMKilled
          # ---- Probes: how K8s knows what "healthy" means ----
          startupProbe:                    # slow starters: don't let liveness kill them mid-boot
            httpGet: { path: /healthz, port: 8083 }
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:                  # FAIL → removed from Service endpoints (no traffic)
            httpGet: { path: /readyz, port: 8083 }
            periodSeconds: 5
          livenessProbe:                   # FAIL → container RESTARTED
            httpGet: { path: /healthz, port: 8083 }
            periodSeconds: 10
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
          volumeMounts:
            - { name: tmp, mountPath: /tmp }   # needed because rootfs is read-only
      volumes:
        - name: tmp
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: resume-svc
  namespace: prod
spec:
  type: ClusterIP            # internal only; the Ingress/Gateway fronts it
  selector: { app: resume-svc }   # ← THIS is how the Service finds Pods. Typo here = 503.
  ports:
    - name: http
      port: 8083              # the Service's port
      targetPort: 8083        # the container's port
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resume-svc
  namespace: prod
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: resume-svc }
  minReplicas: 3
  maxReplicas: 40             # placement day
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # don't thrash: wait 5 min of calm before shrinking
---
apiVersion: policy/v1
kind: PodDisruptionBudget      # protects you during node drains / cluster upgrades
metadata:
  name: resume-svc
  namespace: prod
spec:
  minAvailable: 2
  selector:
    matchLabels: { app: resume-svc }
```

```bash
kubectl apply -f platform/k8s/resume-svc.yaml
kubectl -n prod rollout status deployment/resume-svc
kubectl -n prod get pods -l app=resume-svc -o wide
kubectl -n prod describe pod resume-svc-7d4f9c8b6-xk2p9   # ← Events section = your first stop
kubectl -n prod logs -f deploy/resume-svc --tail=100
kubectl -n prod logs resume-svc-7d4f9c8b6-xk2p9 --previous  # logs of the CRASHED container
kubectl -n prod get endpoints resume-svc                    # empty = your 503
kubectl -n prod rollout undo deployment/resume-svc          # instant rollback
kubectl -n prod exec -it deploy/resume-svc -- sh
kubectl -n prod port-forward svc/resume-svc 8083:8083       # test without exposing publicly
kubectl top pods -n prod                                    # actual CPU/mem vs your requests
```

**The self-healing story from class, made precise.** The instructor described a server going down mid-traffic and Kubernetes restarting a pod. What actually happens, layer by layer:

```text
T+0s    Node ip-10-0-3-77 loses network (spot reclaim / AZ blip)
T+10s   kubelet stops sending heartbeats to the API server
T+40s   node-lifecycle-controller marks Node NotReady
T+40s   kube-proxy on every other node removes that node's pod IPs from
        the Service's iptables/IPVS rules  →  traffic stops being sent there
        ★ This is why the user sees nothing. No 503, no error. ★
T+5m    Pods on the dead node are marked for eviction (default toleration 300s)
T+5m    The ReplicaSet controller notices: desired=3, actual=2  →  creates 1 Pod
T+5m1s  kube-scheduler places it on ip-10-0-1-22 (fits requests, satisfies anti-affinity)
T+5m3s  kubelet pulls the image (cached) and starts the container
T+5m9s  startupProbe passes → readinessProbe passes
T+5m9s  Endpoint added; the new Pod starts receiving traffic. Desired state restored.
        Total user-visible impact: whatever was in flight on the dead node.
```

> **Interview tip:** the killer follow-up is *"and what if the whole node group is gone?"* Answer: **Cluster Autoscaler** or **Karpenter** provisions new nodes; **PodDisruptionBudgets** stop voluntary drains from taking you below quorum; **topologySpreadConstraints** / pod anti-affinity spread replicas across **Availability Zones** so a single-AZ failure can't take all 3. Saying "multi-AZ spread + PDB + autoscaler" is the complete answer.

**Ingress → Gateway API: the big 2026 change.** This is fresh and worth knowing cold, because it will be new to most interviewers too:

> **⚠️ Version-sensitive (verified 11 Aug 2026):** The **Ingress-NGINX controller was retired on 31 March 2026** — no more releases, bug fixes, or security patches. The Kubernetes **Ingress API itself is *not* deprecated**, but the most widely deployed controller implementing it is now unmaintained. The community direction is **Gateway API**, which is more expressive (typed routes, traffic splitting, cross-namespace delegation, role separation between platform and app teams) and is GA. Gateway API **v1.6.0** shipped 30 June 2026, graduating `TCPRoute` and `UDPRoute` to Standard. Alternatives if you must stay on Ingress: F5's NGINX Ingress Controller, Traefik, HAProxy, Envoy Gateway, or a cloud-native controller (AWS Load Balancer Controller, which reached GA with Gateway API support in March 2026).
> Sources: [Kubernetes Steering/Security statement](https://www.kubernetes.io/blog/2026/01/29/ingress-nginx-statement/), [Google Open Source blog](https://opensource.googleblog.com/2026/02/the-end-of-an-era-transitioning-away-from-ingress-nginx.html), [Gateway API v1.6 release](https://kubernetes.io/blog/2026/08/03/gateway-api-v1-6-release/)

**Docker Swarm — the thing Kubernetes beat.** The instructor mentioned Swarm had "some problems." Accurately: Swarm is simpler and easier to learn (it's `docker` commands you already know), but it lacks the ecosystem — no equivalent of CRDs/operators, far weaker autoscaling, thin RBAC/network policy, no comparable third-party tooling. Kubernetes won on extensibility and ecosystem gravity, not simplicity. Swarm is **not dead**: Mirantis (which bought Docker Enterprise in 2019) has [committed to supporting Swarm through 2030](https://www.mirantis.com/blog/mirantis-guarantees-long-term-support-for-swarm/). It's a reasonable choice for small deployments and edge. For placements: learn Kubernetes; know Swarm exists and why it lost.

**Version-sensitive (verified 11 Aug 2026):** Kubernetes stable is **v1.36.2** (released 9 June 2026); **v1.37 is scheduled for 26 August 2026** — [kubernetes.io/releases](https://kubernetes.io/releases/). Managed offerings lag upstream by ~1–2 minors, so check EKS/AKS/GKE supported-version pages before pinning.

Covered later: `notes/09-kubernetes-fundamentals.md`.

### 9. Terraform — Infrastructure as Code

> **Board (#6):** *"9. Terraform — Infra provisioner"*

**Why it exists:** the instructor's description was spot-on. To stand up the portal you need a VPC, subnets, an EKS cluster, an RDS instance, an S3 bucket, security groups, and IAM roles. Clicking through the AWS console: 40 minutes, undocumented, unrepeatable, and impossible to review. Need the same thing in `ap-southeast-1` for a second college? Another 40 minutes, and it'll be subtly different — that difference is where your next outage lives. Need 10 servers? Ten times the clicking.

**Terraform** makes infrastructure **declarative code**: you describe the desired end state, Terraform computes a **dependency graph**, diffs it against recorded **state**, and shows you a **plan** before changing anything. Code review for infrastructure. `git log` for your VPC.

```hcl
# platform/terraform/main.tf
terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
  # Remote state: shared, locked, versioned. NEVER commit local state to Git —
  # it contains resource IDs and sometimes secrets, and two people running
  # apply against a local file will corrupt each other's world.
  backend "s3" {
    bucket       = "college-tfstate-ap-south-1"
    key          = "placement-portal/prod/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true      # S3-native state locking (no DynamoDB table needed)
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "placement-portal"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = "platform-team"        # so the cost report has a name on it
    }
  }
}

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "environment" {
  type    = string
  default = "prod"
}

# ---- Networking ----
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "placement-portal-${var.environment}"
  cidr = "10.0.0.0/16"

  # Three AZs so a single-AZ failure can't take the portal down on placement day
  azs              = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  private_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]

  # Without this the module does NOT emit database_subnet_group_name,
  # and the aws_db_instance below fails with a confusing null-value error.
  create_database_subnet_group = true

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "prod"   # 1 NAT in dev (cheap), 3 in prod (HA)

  # EKS needs these tags to auto-discover subnets for load balancers
  public_subnet_tags  = { "kubernetes.io/role/elb"          = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
}

# ---- Resume storage ----
resource "aws_s3_bucket" "resumes" {
  bucket = "college-placement-resumes-${var.environment}"
}

resource "aws_s3_bucket_public_access_block" "resumes" {
  bucket                  = aws_s3_bucket.resumes.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true    # resumes contain PII. This is not optional.
}

resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_versioning" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  versioning_configuration { status = "Enabled" }   # accidental delete ≠ data loss
}

# ---- Database ----
# The DB is reachable ONLY from inside the VPC. No public IP, no 0.0.0.0/0.
resource "aws_security_group" "rds" {
  name        = "placement-rds-${var.environment}"
  description = "Postgres access from within the VPC only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Postgres from the private subnets (app pods live here)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "app" {
  identifier     = "placement-app-${var.environment}"
  engine         = "postgres"
  engine_version = "17"
  instance_class = var.environment == "prod" ? "db.t4g.medium" : "db.t4g.micro"

  allocated_storage     = 50
  storage_encrypted     = true
  multi_az              = var.environment == "prod"
  backup_retention_period = 7
  deletion_protection   = var.environment == "prod"
  skip_final_snapshot   = var.environment != "prod"

  db_name  = "placement"
  username = "placement_admin"
  # Let AWS generate and store the password in Secrets Manager — never a
  # literal password in HCL, because plan/state would expose it.
  manage_master_user_password = true

  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]
}

output "resumes_bucket" { value = aws_s3_bucket.resumes.id }
output "db_endpoint"    { value = aws_db_instance.app.endpoint }
```

```bash
terraform init          # download providers, configure the backend
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan   # ← READ THIS. Every time. It is the whole point.
terraform apply tfplan
terraform destroy       # lab hygiene: your wallet will thank you
```

Dry run of a real plan — learn to read the symbols, because they are the difference between a deploy and an outage:

```text
$ terraform plan
Terraform will perform the following actions:

  # aws_db_instance.app will be updated in-place
  ~ resource "aws_db_instance" "app" {
      ~ instance_class = "db.t4g.micro" -> "db.t4g.medium"
        id             = "placement-app-prod"
    }

  # aws_s3_bucket.resumes must be replaced
-/+ resource "aws_s3_bucket" "resumes" {
      ~ bucket = "college-placement-resumes-prod" -> "college-resumes-prod" # forces replacement
    }

Plan: 1 to add, 1 to change, 1 to destroy.
```

> **Gotcha:** `-/+ must be replaced` and `# forces replacement` mean **DESTROY THEN CREATE**. On an S3 bucket that is *every resume your students uploaded, gone*. On an RDS instance it's your database. Renaming an immutable attribute is the most common way juniors delete production. Read every plan; treat `forces replacement` as a stop sign; use `prevent_destroy` lifecycle blocks and `deletion_protection` on stateful resources.

**Terraform vs Ansible** — the class covered both back-to-back and the distinction is a guaranteed interview question:

| | **Terraform** | **Ansible** |
|---|---|---|
| Category | Infrastructure **provisioning** (IaC) | **Configuration management** |
| Question it answers | "What resources should *exist*?" | "What should be *true inside* a machine?" |
| Model | **Declarative**, with **state** and a plan/diff | Procedurally-written playbooks executing **idempotent** tasks; **no state file** |
| Knows what it created? | Yes — `terraform.tfstate` | No — it inspects the target each run |
| Deletes things? | Yes — `terraform destroy`, and removing a block from code deletes the resource | No — removing a task does nothing |
| Agent on target? | None (talks to cloud APIs) | None (**agentless**, over SSH / WinRM) |
| Typical use | VPC, EKS, RDS, S3, IAM | install Docker on 500 hosts, push nginx.conf, patch packages, rotate certs |
| Language | HCL | YAML |

> **Interview tip:** *"Terraform builds the house; Ansible furnishes it."* Then add the modern nuance that gets you the offer: *"though in a container world Ansible's role has shrunk — server config is baked into the image at build time and servers are immutable. Ansible is still essential for on-prem, network gear, VM fleets, and bootstrapping, but I wouldn't reach for it to configure a Kubernetes node pool."*

> **⚠️ Version-sensitive & licensing (verified 11 Aug 2026):** Terraform is **1.15.8** (8 July 2026) — [endoflife.date/terraform](https://endoflife.date/terraform). Since **v1.6 (Aug 2023)** Terraform is licensed **BUSL 1.1**, *not* open source — free for internal use, but you may not build a competing product with it. That triggered **[OpenTofu](https://opentofu.org/)**, a Linux Foundation, MPL-2.0 fork that is a drop-in replacement (`tofu` instead of `terraform`); OpenTofu is at **1.12.5** (21 July 2026) — [endoflife.date/opentofu](https://endoflife.date/opentofu). **IBM completed its $6.4 B acquisition of HashiCorp on 27 February 2025** ([IBM newsroom](https://newsroom.ibm.com/2024-04-24-IBM-to-Acquire-HashiCorp-Inc-Creating-a-Comprehensive-End-to-End-Hybrid-Cloud-Platform)). Learn Terraform (it's what job ads say); know the OpenTofu story — it's a great "do you follow the industry?" signal.

Covered later: `notes/11-terraform-and-iac.md`.

### 10. Ansible

> **Board (#6):** *"10. Ansible"*

**Why:** the instructor's framing was perfect. "Install Docker on 10,000 servers." SSH into each, run 4 commands, verify, repeat 10,000 times. That's not a job, that's a punishment. And it's not *repeatable* — server 4,712 will have a different Docker version because you fat-fingered it at 2 AM.

Ansible: one **inventory** (which hosts), one **playbook** (what should be true), one command. **Agentless** — plain SSH, no software to install on targets. **Idempotent** — run it 50 times, converge to the same state; tasks that are already satisfied report `ok` and change nothing.

```yaml
# platform/ansible/inventory.yml
all:
  children:
    placement_app:
      hosts:
        app-01: { ansible_host: 10.0.1.11 }
        app-02: { ansible_host: 10.0.2.11 }
        app-03: { ansible_host: 10.0.3.11 }
      vars:
        ansible_user: ubuntu
        ansible_ssh_private_key_file: ~/.ssh/placement-portal.pem
```

```yaml
# platform/ansible/install-docker.yml
- name: Install and harden Docker Engine on the placement app fleet
  hosts: placement_app
  become: true                # sudo
  serial: "25%"               # rolling: 25% of the fleet at a time, not all at once
  vars:
    docker_users: [ubuntu, deploy]

  tasks:
    - name: Install prerequisites
      ansible.builtin.apt:
        name: [ca-certificates, curl, gnupg]
        state: present
        update_cache: true
        cache_valid_time: 3600

    - name: Create keyring directory
      ansible.builtin.file:
        path: /etc/apt/keyrings
        state: directory
        mode: "0755"

    - name: Add Docker's official GPG key
      ansible.builtin.get_url:
        url: https://download.docker.com/linux/ubuntu/gpg
        dest: /etc/apt/keyrings/docker.asc
        mode: "0644"

    - name: Add the Docker apt repository
      ansible.builtin.apt_repository:
        repo: >-
          deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc]
          https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable
        filename: docker
        state: present

    - name: Install Docker Engine and plugins
      ansible.builtin.apt:
        name:
          - docker-ce
          - docker-ce-cli
          - containerd.io
          - docker-buildx-plugin
          - docker-compose-plugin
        state: present
        update_cache: true
      notify: Restart docker

    - name: Configure the daemon (log rotation — otherwise /var/lib/docker eats the disk)
      ansible.builtin.copy:
        dest: /etc/docker/daemon.json
        mode: "0644"
        content: |
          {
            "log-driver": "json-file",
            "log-opts": { "max-size": "50m", "max-file": "3" },
            "live-restore": true
          }
      notify: Restart docker

    - name: Allow listed users to run docker without sudo
      ansible.builtin.user:
        name: "{{ item }}"
        groups: docker
        append: true
      loop: "{{ docker_users }}"

    - name: Ensure Docker is running and enabled at boot
      ansible.builtin.systemd:
        name: docker
        state: started
        enabled: true

    - name: Verify Docker actually works
      ansible.builtin.command: docker run --rm hello-world
      register: hello
      changed_when: false          # a check, not a change — keeps the report honest
      failed_when: "'Hello from Docker' not in hello.stdout"

  handlers:
    - name: Restart docker
      ansible.builtin.systemd:
        name: docker
        state: restarted
```

```bash
ansible -i inventory.yml placement_app -m ping        # can I reach and auth to every host?
ansible-playbook -i inventory.yml install-docker.yml --check --diff   # DRY RUN. Always first.
ansible-playbook -i inventory.yml install-docker.yml
ansible-playbook -i inventory.yml install-docker.yml --limit app-02   # blast radius of one
ansible-vault encrypt group_vars/prod/secrets.yml     # encrypt secrets at rest in Git
```

Dry run — note the idempotency proof:

```text
$ ansible-playbook -i inventory.yml install-docker.yml

PLAY [Install and harden Docker Engine on the placement app fleet] **************
TASK [Install prerequisites]         ok: [app-01]  ok: [app-02]  ok: [app-03]
TASK [Add Docker's official GPG key] changed: [app-01]  changed: [app-02]  changed: [app-03]
TASK [Install Docker Engine ...]     changed: [app-01]  changed: [app-02]  changed: [app-03]
TASK [Verify Docker actually works]  ok: [app-01]  ok: [app-02]  ok: [app-03]
RUNNING HANDLER [Restart docker]     changed: [app-01]  changed: [app-02]  changed: [app-03]

PLAY RECAP *********************************************************************
app-01 : ok=9  changed=4  unreachable=0  failed=0
app-02 : ok=9  changed=4  unreachable=0  failed=0
app-03 : ok=9  changed=4  unreachable=0  failed=0

$ ansible-playbook -i inventory.yml install-docker.yml     # run it AGAIN
PLAY RECAP *********************************************************************
app-01 : ok=9  changed=0  unreachable=0  failed=0     ← changed=0. THAT is idempotency.
```

> **Gotcha:** `changed=0` on the second run is the property you're checking for. If a task reports `changed` every single run, it isn't idempotent — usually a raw `command`/`shell` task with no `creates:`, `removes:`, or `changed_when:`. Non-idempotent playbooks make `--check` mode useless and restart services needlessly (handlers fire → rolling restart → unnecessary blip).

**Version-sensitive (verified 11 Aug 2026):** Ansible community package **14.2.0** (14 July 2026), bundling **ansible-core 2.21** — [endoflife.date/ansible](https://endoflife.date/ansible).

Covered later: `notes/12-ansible-and-configuration-management.md`.

### 11. Monitoring & observability

> **Board (#6):** *"11. Monitoring — Grafana = Dashboard, Prometheus"*

The instructor's split was correct: **Prometheus stores and queries; Grafana visualises.** Neither replaces the other.

**Why it exists:** the class question was *"your website is up — what's next?"* Answer: you have no idea whether it's *working*. Uptime is not health. The portal can be "up" while every resume upload silently fails, or while p99 latency is 14 seconds. Without instrumentation, you find out from an angry student on Twitter.

**The three pillars of observability:**

| Pillar | Answers | Tool | Cost/cardinality profile |
|---|---|---|---|
| **Metrics** | "*Is* something wrong? How much, how often, trending which way?" | Prometheus, CloudWatch | Cheap, aggregated, low cardinality. Alert on these. |
| **Logs** | "*What exactly* happened in this one request?" | Loki, ELK/OpenSearch, CloudWatch Logs | Expensive at volume. Structure them as JSON. |
| **Traces** | "*Where* in the 6-service call chain did the time go?" | OpenTelemetry → Jaeger / Tempo / X-Ray | Sample them (1–10%); indispensable for microservices |

**Prometheus: pull, not push** — a favourite interview question.

| | **Pull (Prometheus)** | **Push (StatsD, Graphite)** |
|---|---|---|
| Who initiates | Prometheus scrapes `GET /metrics` every 15 s | The app sends metrics to a collector |
| Service discovery | Prometheus discovers targets (K8s API, EC2 tags, Consul) | App must know the collector's address |
| Health signal | **Free** — a failed scrape *is* "target down" (`up == 0`) | Silence is ambiguous: dead app, or dead network, or idle? |
| Firewall/NAT | Needs inbound reachability to targets | Works from anywhere outbound |
| Short-lived jobs | Awkward — a CronJob may finish between scrapes | Natural fit |
| Escape hatch | **Pushgateway** for exactly those batch jobs | — |

> **Interview tip:** the crisp answer is *"pull gives you liveness detection and centralised control of scrape config for free, which is why it fits dynamic Kubernetes environments where targets appear and disappear constantly. Push fits short-lived batch jobs and networks where you can't reach in — and Prometheus handles that case with the Pushgateway, which you should use sparingly because it breaks the liveness signal."*

```yaml
# platform/monitoring/prometheus-rules.yaml — alert on SYMPTOMS, not causes
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: placement-portal-slos
  namespace: monitoring
spec:
  groups:
    - name: placement-portal.slo
      rules:
        # Alert when >1% of requests are failing over 5 minutes.
        - alert: ResumeSvcHighErrorRate
          expr: |
            sum(rate(http_requests_total{job="resume-svc",status=~"5.."}[5m]))
              /
            sum(rate(http_requests_total{job="resume-svc"}[5m]))
            > 0.01
          for: 5m                  # must persist 5 min → no paging on a single blip
          labels: { severity: critical, team: platform }
          annotations:
            summary: "resume-svc error rate {{ $value | humanizePercentage }} (>1%)"
            runbook: https://wiki.college.edu/runbooks/resume-svc-5xx

        # Latency SLO: p95 under 800 ms
        - alert: ResumeSvcSlow
          expr: |
            histogram_quantile(0.95,
              sum by (le) (rate(http_request_duration_seconds_bucket{job="resume-svc"}[5m]))
            ) > 0.8
          for: 10m
          labels: { severity: warning, team: platform }

        # Capacity: pods being OOMKilled means your memory limit is wrong
        - alert: ResumeSvcOOMKilled
          expr: increase(kube_pod_container_status_restarts_total{container="resume-svc"}[15m]) > 2
          for: 0m
          labels: { severity: critical }
          annotations:
            summary: "resume-svc restarting repeatedly — check limits and heap"
```

> **Gotcha — the #1 monitoring mistake:** alerting on **causes** (CPU > 80%, disk 70% full, pod restarted once) instead of **symptoms** (users are getting errors, requests are slow). High CPU with happy users is not an incident; it's a well-utilised machine. Cause-based alerts produce pager fatigue, and pager fatigue produces missed real outages. Alert on **SLO burn rate**; put causes on dashboards for diagnosis.

**Version-sensitive (verified 11 Aug 2026):** Prometheus **3.13.2** (30 July 2026), with **3.13 as the current LTS** — [endoflife.date/prometheus](https://endoflife.date/prometheus). Grafana **13.1.3** (7 Aug 2026) — [endoflife.date/grafana](https://endoflife.date/grafana).

> **Transcript correction:** the transcript's monitoring tool answer "Sanity" is ASR noise for **Sentry** (error/exception tracking — complementary to Prometheus, not a substitute). And the instructor's aside that Prometheus/Grafana are "old" isn't right: Prometheus is a **graduated CNCF project** and the de facto standard for metrics in Kubernetes in 2026. What *has* changed around it: **OpenTelemetry** is now the standard instrumentation layer (vendor-neutral SDKs + collector), **Loki** for logs, **Tempo/Jaeger** for traces, and **Grafana Mimir / VictoriaMetrics / Thanos** for long-term, horizontally-scalable metric storage.

Covered later: `notes/13-monitoring-prometheus-grafana.md`.

### 12. GitOps

> **Board (#7):** *"12. GitOps"*

The transcript's definition — *"tracking everything from version control till production"* — points in the right direction but misses the mechanism.

> **Transcript correction:** GitOps is not primarily an audit-trail or log-tracking tool. **GitOps is a deployment model in which a Git repository is the single source of truth for the *desired state* of your infrastructure, and an agent running inside the cluster continuously pulls from Git and reconciles reality to match it.** The audit trail is a *consequence* (Git history = change history), not the definition.

The four [OpenGitOps principles v1.0](https://opengitops.dev/):

1. **Declarative** — the system's desired state is expressed declaratively.
2. **Versioned and Immutable** — desired state is stored immutably, versioned, with complete history.
3. **Pulled Automatically** — software agents automatically pull the desired state from the source.
4. **Continuously Reconciled** — agents continuously observe actual state and act to apply desired state.

**Why it beats push-based CD:**

```text
PUSH model (the CI/CD pipeline in item 6):
  CI runner holds prod cluster credentials  →  kubectl apply  →  cluster
  ✗ CI has god-mode credentials to production (huge blast radius if CI is compromised)
  ✗ Drift is invisible: someone runs `kubectl edit` at 3 AM and Git no longer matches reality
  ✗ "What is running in prod right now?" is answered by querying the cluster, not by reading a repo

PULL model (GitOps):
  CI builds image + opens a PR bumping the tag in the config repo
  Argo CD (INSIDE the cluster) watches that repo  →  reconciles every ~3 min
  ✓ No external system holds cluster credentials
  ✓ Manual `kubectl edit` is detected as DRIFT and (optionally) auto-reverted
  ✓ Rollback = `git revert`. The audit trail is `git log`.
  ✓ Disaster recovery = point a fresh cluster at the repo and wait
```

```mermaid
graph LR
    D[Developer] -->|PR| AR[app repo]
    AR --> CI[CI: build + test + scan]
    CI -->|push image| REG[(registry)]
    CI -->|PR: bump image tag| CR[config repo<br/>k8s manifests / Helm values]
    CR -->|"merge to main"| GIT[(Git = desired state)]
    ARGO[Argo CD agent<br/>inside the cluster] -->|pull every 3 min| GIT
    ARGO -->|"reconcile: apply diff"| K8S[Kubernetes cluster]
    K8S -.->|"observed state"| ARGO
    ARGO -.->|"drift detected → revert or alert"| K8S
    style GIT fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style ARGO fill:#064e3b,stroke:#34d399,color:#fff
```

**Tools:** **Argo CD** (CNCF graduated; has a UI that makes drift and sync status visually obvious — the common choice) and **Flux CD** (CNCF graduated; CLI/CRD-first, lighter, composes well with Kustomize). Both implement the same four principles.

> **Interview tip:** The killer follow-up is *"where do secrets live if everything is in Git?"* You do **not** commit plaintext Secrets. Answers, best first: **External Secrets Operator** (Kubernetes pulls from AWS Secrets Manager / Vault at runtime — nothing sensitive in Git at all), **Sealed Secrets** (asymmetric encryption; only the in-cluster controller can decrypt, so ciphertext in Git is safe), or **SOPS + age/KMS** (encrypt values in the YAML file itself). Knowing this distinguishes people who've *done* GitOps from people who've *read about* it.

Covered later: `notes/14-gitops-with-argocd.md`.

### 13. DevSecOps — shift left

> **Board (#7):** *"13. SecOps — DevSecOps → SonarQube → SAST; SAST, DAST, OWASP; Trivy, Snyk"*
> **Board (#8):** *"★ Trivy → Scan the Docker Image"*

The instructor made the class *search for the one word*, and the answer he wanted was **shift left**. That's the whole idea, so understand it properly.

**The problem.** Classically, security was a **gate at the end**: you finished building, then a security team ran a scan and handed back a 200-page PDF a week before launch. Two bad outcomes — either you ship the vulnerabilities because there's no time, or you delay the launch. And a design flaw found at that point (say, resumes stored in a public S3 bucket) costs 100× what it would have cost to fix at design time.

**Shift left** = move each security activity as early ("left") in the lifecycle as it can possibly go:

```text
     Plan ──── Code ──── Build ──── Test ──── Release ──── Deploy ──── Operate
      │         │          │          │          │            │           │
   threat    IDE linter  SAST +     DAST      signed      admission    runtime
   model     secret      SCA +      against    images +    control      detection,
   + design  scanning    IaC scan   staging    SBOM        (policy)     WAF, audit
   review    on save     on PR                             gates
      └──────────── cheap to fix ────────────┼─────── expensive to fix ────────┘
```

**The four scan types — this is where the transcript needs the most correction:**

| Type | Full name | What it looks at | App running? | Finds | Tools (2026) |
|---|---|---|---|---|---|
| **SAST** | Static Application Security Testing | **Your source code** | No | SQL injection, XSS sinks, hardcoded secrets, unsafe deserialization, bad crypto | **SonarQube**, Semgrep, CodeQL, Snyk Code, Checkmarx |
| **SCA** | Software Composition Analysis | **Your dependencies** (`package.json`, `requirements.txt`, `pom.xml`, container base image layers) | No | Known **CVEs** in third-party libraries, license violations | **Trivy**, **Snyk Open Source**, Dependabot, OWASP Dependency-Check, Grype |
| **DAST** | Dynamic Application Security Testing | **A running application**, from the outside, black-box | **Yes** | Auth bypass, session flaws, misconfigured headers, injection reachable in practice, SSRF | **OWASP ZAP**, Burp Suite, Nuclei |
| **IaC / config scan** | — | Terraform, K8s YAML, Dockerfiles | No | Public S3 bucket, `0.0.0.0/0` security group, privileged container | **Trivy** (config mode), Checkov, tfsec, KICS |

> **Transcript correction — the important one.** The class said: *"For DAST there are a lot of tools — Trivy, Snyk."* **This is wrong, and it's the kind of error an interviewer will catch.**
> - **Trivy** is an **SCA + misconfiguration + secrets + license scanner**. It analyses container images, filesystems, Git repos, Kubernetes clusters, and IaC files **statically**. It never sends a request to a running app. ([Aqua Security](https://www.aquasec.com/products/trivy/))
> - **Snyk** is **SAST (Snyk Code) + SCA (Snyk Open Source) + container + IaC scanning** — also static.
> - **Real DAST tools are OWASP ZAP and Burp Suite.** They *attack a live URL*.
>
> The defining test: **does the tool need a running application to point at?** If yes, it's DAST. If it reads files, it's static (SAST/SCA/IaC).
>
> Also: the instructor described DAST as being about *"a package you use getting deprecated after your code is already live."* That scenario is real and important, but it is **continuous SCA / SBOM monitoring** (re-scan your already-shipped artifacts as new CVEs are published), not DAST.

> **Transcript correction — SonarQube's scope.** SonarQube is primarily **code quality + SAST**: bugs, code smells, cognitive complexity, test coverage, security hotspots, and a configurable **quality gate** that fails your build. The transcript claimed you *"connect SonarQube to your application URL and it fetches your app"* — no; SonarQube analyses **source code** in CI, it doesn't crawl a live site. And its dependency-CVE coverage is limited — that's what **SCA** tools are for. Use SonarQube **and** Trivy/Snyk; they cover different things.
>
> **Naming note (verified 11 Aug 2026):** Sonar renamed its products in late 2024. **SonarQube Server** = self-hosted (formerly just "SonarQube"), **SonarQube Cloud** = SaaS (formerly SonarCloud), **SonarQube for IDE** = the IDE plugins (formerly SonarLint). Using the current names signals you're up to date. ([Sonar press release](https://www.sonarsource.com/company/press-releases/sonar-streamlines-product-naming-to-reflect-core-mission-of-code-quality-and-security/))

**OWASP — what it actually is.**

> **Transcript correction:** the class said *"OWASP is like 10 tools out there for each simple thing."* **OWASP (Open Worldwide Application Security Project) is a non-profit foundation**, not a tool and not a list of tools. It publishes free standards, guides, and open-source projects. What you're expected to know by name:
> - **OWASP Top 10** — the flagship awareness document: the ten most critical web application security risks. This is what interviewers mean when they say "OWASP."
> - **OWASP ASVS** (Application Security Verification Standard) — the actual requirements checklist for building secure apps.
> - **OWASP ZAP** — their open-source DAST scanner.
> - **OWASP Dependency-Check** — their SCA tool.
> - **OWASP Top 10 for LLM Applications** — increasingly asked about in 2026 (prompt injection, insecure output handling, training-data poisoning).

**⚠️ The current OWASP Top 10 is the 2025 edition** (announced November 2025 at Global AppSec DC; final release January 2026). Most course material and most interviewers still quote the 2021 list — knowing the 2025 one is a genuine differentiator. Verified against [owasp.org/Top10/2025](https://owasp.org/Top10/2025/):

| ID | Category | Note |
|---|---|---|
| **A01:2025** | Broken Access Control | Still #1. **SSRF was absorbed into this category.** |
| **A02:2025** | Security Misconfiguration | Moved up sharply |
| **A03:2025** | **Software Supply Chain Failures** | **NEW** — broader than 2021's "Vulnerable and Outdated Components". Covers the whole dependency/build/distribution chain |
| **A04:2025** | Cryptographic Failures | |
| **A05:2025** | Injection | Dropped from #3 (2021) — better framework defaults |
| **A06:2025** | Insecure Design | |
| **A07:2025** | Authentication Failures | Renamed from "Identification and Authentication Failures" |
| **A08:2025** | Software or Data Integrity Failures | |
| **A09:2025** | Security Logging and **Alerting** Failures | Renamed — "Monitoring" → "Alerting" |
| **A10:2025** | **Mishandling of Exceptional Conditions** | **NEW** — error handling, fail-open logic, information leakage via errors |

Built from analysis of 175,000+ CVEs mapped across 248 CWEs.

**Trivy in practice** — the instructor's starred point. Trivy scans the image you just built for CVEs in OS packages *and* application dependencies, layer by layer:

```bash
# Scan a built image, fail CI on HIGH/CRITICAL that actually have a fix available
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 \
  ghcr.io/college/placement-portal/resume-svc:1.4.7

# Scan the source tree: dependencies + secrets + licenses
trivy fs --scanners vuln,secret,license .

# Scan your Terraform and Kubernetes YAML for misconfigurations
trivy config platform/terraform/
trivy config platform/k8s/

# Scan a live cluster
trivy k8s --report summary cluster

# Produce an SBOM for supply-chain compliance (A03:2025)
trivy image --format cyclonedx -o sbom.cdx.json ghcr.io/.../resume-svc:1.4.7
```

Real output, and how to read it:

```text
$ trivy image --severity HIGH,CRITICAL python:3.11-slim

python:3.11-slim (debian 12.5)
══════════════════════════════
Total: 3 (HIGH: 2, CRITICAL: 1)

┌──────────────┬────────────────┬──────────┬───────────────────┬───────────────┐
│   Library    │ Vulnerability  │ Severity │ Installed Version │ Fixed Version │
├──────────────┼────────────────┼──────────┼───────────────────┼───────────────┤
│ libexpat1    │ CVE-2024-45491 │ CRITICAL │ 2.5.0-1           │ 2.5.0-1+deb12u1│
│ libssl3      │ CVE-2024-5535  │ HIGH     │ 3.0.11-1~deb12u2  │ 3.0.13-1~deb12u1│
│ zlib1g       │ CVE-2023-45853 │ HIGH     │ 1:1.2.13.dfsg-1   │ (no fix)       │
└──────────────┴────────────────┴──────────┴───────────────────┴───────────────┘
```

**The fix, in order of effectiveness:**
1. `FROM python:3.13-slim` — a newer base image usually carries the patched packages. **Rebuilding on a fresh base fixes most of these for free**, which is why you rebuild images on a schedule, not only when your code changes.
2. Add `RUN apt-get update && apt-get upgrade -y` in the build (rebuilds pick up patches).
3. Switch to a **distroless** or **Alpine/Chainguard** base — fewer packages means a smaller attack surface and far fewer findings.
4. `--ignore-unfixed` for the `zlib1g` case (no upstream fix exists yet; blocking your build achieves nothing). Track it, don't block on it.

> **Production reality:** Every image you build has CVEs. The goal is **not zero findings** — it's *no unfixed HIGH/CRITICAL that is actually reachable in your application, and a rebuild cadence fast enough that you're never more than a week behind a published patch.* A team that blocks all builds on all findings quickly learns to add `--exit-code 0`, and then the scan is theatre.

**Two more things the class didn't mention but every real pipeline has:**

- **Secret scanning.** Hardcoded AWS keys and DB passwords are the single most-exploited class of leak. Enable GitHub secret scanning + push protection, and run **gitleaks** or **TruffleHog** in CI. A key committed to a public repo is scraped by bots in **minutes**.
- **Signing and provenance** (A03:2025 territory). Sign images with **Sigstore/cosign**, generate an **SBOM** per build, and enforce at admission (Kyverno / OPA Gatekeeper) that the cluster only runs signed images from your registry. This is what stops "someone pushed a malicious image tagged `1.4.7`."

**Version-sensitive (verified 11 Aug 2026):** Trivy **v0.71.0** (1 June 2026).

Covered later: `notes/15-devsecops-sast-dast-sca.md`.

---

## Part 8 — Job roles

> **Board (#10):** *"1. DevOps Engineer 2. DevSecOps Engineer 3. Platform Engineer 4. SRE — Site Reliability Engineer"*
> **Board (#11):** *"5. Cloud Engineer 6. Solution Architect — 5 YOE 7. AIOps Engineer 8. MLOps Engineer 9. AI Cloud Engineer"*

| Role | What they actually do day to day | Distinguishing skill | Realistic entry point |
|---|---|---|---|
| **DevOps Engineer** | Build and run CI/CD, containers, IaC, Kubernetes, monitoring for product teams | Breadth across the toolchain | ✅ Yes — the standard entry role |
| **DevSecOps Engineer** | Everything above **plus** owning the security controls in the pipeline: SAST/SCA/DAST gates, secrets management, image signing, admission policy, compliance evidence | Security depth (OWASP, threat modelling, CVE triage) | ✅ Yes, and it's the differentiator the instructor stressed |
| **Site Reliability Engineer (SRE)** | Reliability as an engineering problem: define **SLIs/SLOs/error budgets**, run incident response and postmortems, do capacity planning, and *automate away toil* | Deep production debugging + the discipline of error budgets. Google's framing: "SRE is what happens when you ask a software engineer to design an operations team." | ⚠️ Usually needs 2+ years — you can't reason about reliability you've never been paged for |
| **Platform Engineer** | Build the **internal developer platform**: golden paths, self-service templates, a paved road so product teams don't each reinvent CI and K8s | Product thinking — your users are other engineers | ⚠️ Mid-level |
| **Cloud Engineer** | Design/operate cloud infra: networking, IAM, cost, migrations, landing zones | One cloud, deeply (usually AWS or Azure) | ✅ Yes |
| **Solution Architect** | Design end-to-end systems, choose the architecture, own non-functional requirements, translate business needs into technical design. Does **not** write the pipeline. | System design + business context + communication | ❌ Genuinely senior — the instructor's "~5 YOE" is fair, often more |
| **MLOps Engineer** | Pipelines for ML: feature stores, training orchestration, model registry, versioning, deployment, drift detection, retraining | DevOps + ML lifecycle | ⚠️ Needs DevOps first |
| **AIOps Engineer** | Two distinct meanings in job ads: (a) using AI/ML *for* operations — anomaly detection, alert correlation, automated remediation; (b) operating AI systems. Read the JD carefully. | Observability data + ML | ⚠️ Mid-level |
| **AI / LLM Platform Engineer** (the "AI Cloud Engineer" on the board) | Deploy and operate LLM applications: inference endpoints, RAG pipelines, GPU capacity, token cost control, guardrails, eval harnesses, agent orchestration | DevOps + cloud AI services (**Amazon Bedrock**, **Azure AI Foundry**, Vertex AI) | ⚠️ Growing fast; DevOps is the prerequisite |
| **Developer Advocate** | Technical content, talks, docs, community; the bridge between users and the product team | Communication + genuine technical depth | ⚠️ Needs credibility first |

**The AI/ML/DL nesting the instructor drew:**

> **Board (#12):** three concentric circles — AI ⊃ ML ⊃ DL

```text
┌─────────────────────────────────────────────────────┐
│ AI — any system that performs tasks needing         │
│      "intelligence" (incl. rule-based expert        │
│      systems, search, planning)                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ ML — systems that learn patterns from data    │  │
│  │      instead of being explicitly programmed   │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ DL — ML using deep neural networks.     │  │  │
│  │  │      Transformers → LLMs live here.     │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

> **Note:** the instructor's split of "MLOps engineers build/enhance the algorithms and LLMs, AI engineers use them" is a reasonable sketch of team boundaries but conflates roles. More accurately: **ML/research engineers** design and train models; **MLOps engineers** build the infrastructure that trains, versions, serves, and monitors them (they generally don't invent algorithms); **AI/LLM application engineers** build products on top of model APIs. The instructor's underlying career point stands and is good advice: **DevOps → MLOps/AIOps is a short hop, because the hard parts (pipelines, containers, cloud, observability, cost) are the same.**

**On the SRE-vs-DevOps question a student asked** (the answer in class got tangled up with product-management duties): the clean distinction is *"DevOps is a set of practices for shipping software fast and safely; SRE is a specific, opinionated implementation of those practices with reliability as the explicit engineering objective — quantified through SLOs and error budgets."* The error budget is the crisp mechanism: if you've burned your budget for the quarter, feature launches stop and reliability work takes priority. That's a *policy*, agreed in advance, that removes the speed-vs-stability argument from the room. Neither role is a product owner or a client-facing translator — that's a PM/TPM function.

> **Transcript note:** the instructor's mention of **Kiro** as *"Cursor's old version from AWS"* is inaccurate. **[Kiro](https://kiro.dev/) is AWS's own agentic AI development platform** (IDE + CLI + web), generally available, built around **spec-driven development** — you write requirements, design, and task breakdown first, and the agent implements against that spec rather than free-form "vibe coding." It's not a Cursor fork or an old version of anything. **Azure AI Foundry** (the instructor's "AI Factory") and **Amazon Bedrock** were correctly named.

---

## Part 9 — Command reference

### Docker

| Command | Meaning | When you use it |
|---|---|---|
| `docker build -t name:tag .` | Build image from Dockerfile in `.` | Every code change |
| `docker run -d -p 8083:8083 --env-file .env img` | Run detached, publish port, load env | Local testing |
| `docker ps -a` | List containers, including stopped ones | "Why did it exit?" |
| `docker logs -f --tail 100 <c>` | Follow last 100 log lines | First debugging step |
| `docker exec -it <c> sh` | Shell inside a running container | Poke at the filesystem, run `env` |
| `docker inspect <c>` | Full JSON: mounts, networks, env, exit code | Deep debugging |
| `docker stats` | Live CPU/mem/net per container | "What's eating the host?" |
| `docker compose up -d --build` | Bring up the whole local stack | Local dev of multi-service apps |
| `docker system prune -af --volumes` | Reclaim disk (**deletes unused volumes**) | Disk full — read the flags first |
| `docker image history <img>` | Per-layer size breakdown | Shrinking a fat image |

### Kubernetes

| Command | Meaning |
|---|---|
| `kubectl get pods -n prod -o wide` | Pods with node and IP |
| `kubectl describe pod <p>` | **Events** — always your first stop for scheduling/probe failures |
| `kubectl logs -f deploy/<d>` | Follow logs of a Deployment's pods |
| `kubectl logs <p> --previous` | Logs of the **crashed** previous container |
| `kubectl get events -A --sort-by=.lastTimestamp` | Cluster-wide timeline of what just happened |
| `kubectl get endpoints <svc>` | Pods backing a Service — **empty means 503** |
| `kubectl rollout status deploy/<d>` | Block until rollout completes (health gate in CI) |
| `kubectl rollout undo deploy/<d>` | Instant rollback to previous ReplicaSet |
| `kubectl scale deploy/<d> --replicas=20` | Manual scale (prefer an HPA) |
| `kubectl top pods` | Actual CPU/mem usage vs your requests |
| `kubectl exec -it deploy/<d> -- sh` | Shell into a pod |
| `kubectl port-forward svc/<s> 8083:8083` | Reach a ClusterIP Service from your laptop |
| `kubectl apply -f dir/ --dry-run=server` | Validate manifests against the live API without applying |
| `kubectl config get-contexts` | **Which cluster am I about to change?** Check before every `apply`. |

### Git

| Command | Meaning |
|---|---|
| `git switch -c <branch>` | Create and switch (modern `checkout -b`) |
| `git add -p` | Stage interactively, hunk by hunk |
| `git log --oneline --graph --decorate` | Readable history |
| `git diff --staged` | What you're about to commit |
| `git revert <sha>` | New commit undoing an old one — **safe on shared branches** |
| `git reset --soft HEAD~1` | Undo last commit, keep changes staged — **local only** |
| `git bisect start` | Binary-search history for the breaking commit |
| `git stash push -m "wip"` | Park uncommitted work |
| `git blame -L 40,60 <file>` | Who last touched these lines |

### Networking

| Command | Layer | Answers |
|---|---|---|
| `dig +short <host>` | 7/3 | Does DNS resolve, and to what? |
| `ping -c 4 <host>` | 3 | Is the host routable? (says nothing about your app) |
| `traceroute` / `tracert` / `mtr` | 3 | Where does the path break or slow down? |
| `nc -zv <host> <port>` | 4 | **Is the port open?** (`refused` = nothing listening; `timeout` = firewall) |
| `telnet <host> <port>` | 4 | Same, classic form |
| `ss -tulpn` | 4 | What's listening locally and which PID owns it |
| `curl -sv -w '%{time_total}'` | 7 | Does the app respond correctly, and how fast? |
| `openssl s_client -connect h:443` | 6 | TLS chain, cert expiry |
| `tcpdump -i any port 8084 -nn` | 2–4 | Last resort: what's actually on the wire |

### Terraform / Ansible

| Command | Meaning |
|---|---|
| `terraform init` | Download providers, configure backend |
| `terraform plan -out=tfplan` | Compute the diff — **read it every time** |
| `terraform apply tfplan` | Apply exactly the reviewed plan |
| `terraform state list` / `state show <r>` | Inspect tracked resources |
| `terraform import <addr> <id>` | Adopt an existing manual resource into state |
| `terraform destroy` | Tear down (lab hygiene) |
| `ansible -m ping all` | Connectivity + auth check across the fleet |
| `ansible-playbook p.yml --check --diff` | **Dry run** with a diff of intended changes |
| `ansible-playbook p.yml --limit host` | Restrict blast radius to one host |
| `ansible-vault encrypt f.yml` | Encrypt secrets at rest in Git |

---

## Part 10 — Common errors & debugging

### `Permissions 0644 for 'key.pem' are too open. This private key will be ignored.`
**Cause:** SSH refuses world- or group-readable private keys.
**Fix:** `chmod 400 key.pem`. On Windows/NTFS: `icacls key.pem /inheritance:r /grant:r "$env:USERNAME:(R)"`, or keep keys inside WSL2.

### `docker: Error response from daemon: driver failed programming external connectivity: Bind for 0.0.0.0:8083 failed: port is already allocated`
**Cause:** something already owns 8083 on the host.
**Fix:** `docker ps --filter publish=8083` then `docker rm -f <c>`; or find the non-Docker owner with `ss -tulpn | grep 8083` (PowerShell: `Get-NetTCPConnection -LocalPort 8083`). Or just publish a different host port: `-p 8090:8083`.

### `CrashLoopBackOff`
**Cause:** the container starts, exits, and Kubernetes restarts it with exponential backoff. Usually a config error, a missing env var, or an unreachable dependency at boot.
**Debug:**

```bash
kubectl -n prod logs <pod> --previous     # ← the crashed container's output. THE key step.
kubectl -n prod describe pod <pod>        # Events: image pull? OOMKilled? probe failing?
kubectl -n prod get pod <pod> -o jsonpath='{.status.containerStatuses[0].lastState.terminated}'
```
Exit code 1 = app-level error (read the logs). Exit **137** = SIGKILL, almost always **OOMKilled** → raise `resources.limits.memory` or fix the leak. Exit **143** = SIGTERM, a clean shutdown that something asked for.

### `ImagePullBackOff` / `ErrImagePull`
**Causes, in order of likelihood:** typo in the image name or tag; the tag doesn't exist in the registry; the registry is private and there's no `imagePullSecret`; the node has no network route to the registry.
**Debug:** `kubectl describe pod <pod>` shows the exact registry error. Verify with `docker pull <same image>` from a machine you control.

### `503 Service Unavailable` from your Ingress, but the pods look Running
**Cause (99% of the time):** the Service's `selector` doesn't match the Pods' `labels`, so the Service has no endpoints. Second most likely: readiness probe is failing, so healthy-looking pods were pulled from rotation.
**Debug:**

```bash
kubectl -n prod get endpoints resume-svc     # empty = confirmed
kubectl -n prod get pods --show-labels
kubectl -n prod get svc resume-svc -o jsonpath='{.spec.selector}'   # compare them character by character
kubectl -n prod describe pod <pod> | grep -A5 Readiness
```

### `0/6 nodes are available: 3 Insufficient cpu, 3 node(s) had untolerated taint`
**Cause:** the scheduler can't place the Pod. Your `resources.requests` exceed what any node has free, or nodes carry taints your Pod doesn't tolerate.
**Fix:** lower `requests` (and check they're realistic — `kubectl top pods` shows actual usage), add nodes / let the autoscaler do it, or add the matching `tolerations`.

### `Error: Error acquiring the state lock ... Lock Info: ID: 9f3c..., Operation: OperationTypeApply`
**Cause:** a previous `terraform apply` died (Ctrl-C, CI runner killed) and left the lock held.
**Fix:** **First confirm no one is actually applying** — ask in the team channel. Then `terraform force-unlock <LOCK_ID>`. Force-unlocking during a live apply corrupts state.

### `Error: Instance cannot be destroyed ... has lifecycle.prevent_destroy set`
**Cause:** you (correctly) protected a stateful resource, and your change requires replacing it.
**Fix:** don't remove the guard reflexively — that guard just prevented a data-loss incident. Work out *why* replacement is needed (usually an immutable attribute change) and find a non-destructive path, or plan a real migration with a snapshot first.

### `fatal: [app-02]: UNREACHABLE! => Failed to connect to the host via ssh: Permission denied (publickey)`
**Causes:** wrong `ansible_user`; wrong key path; key not in the target's `authorized_keys`; key permissions too open locally.
**Debug:** `ansible -i inventory.yml app-02 -m ping -vvvv` prints the exact SSH command it ran — run that by hand and the real error appears.

### Prometheus target shows `DOWN` with `context deadline exceeded`
**Causes:** the app doesn't expose `/metrics`; wrong port in the ServiceMonitor/scrape config; a NetworkPolicy blocks Prometheus; the endpoint is genuinely slower than the scrape timeout.
**Debug:** `kubectl port-forward pod/<p> 8083:8083` then `curl localhost:8083/metrics`. If that works, it's discovery or network policy, not the app.

### CI passes locally, fails in the pipeline
The classic four causes: **(1)** you have a dependency installed locally that isn't in `requirements.txt`/`package.json`; **(2)** tests depend on execution order or on data left behind by a previous local run; **(3)** timezone/locale differences (`Asia/Kolkata` locally, `UTC` in CI); **(4)** an environment variable that exists in your shell and nowhere else. Fix by running CI's exact container locally: `docker run --rm -it -v ${PWD}:/w -w /w python:3.13-slim bash`.

---

## Part 11 — Interview questions with model answers

**Q1. What's the difference between monolithic and microservices architecture, and which would you choose for a college placement portal?**

> A monolith packages all functionality into a single deployable artifact; microservices split it into independently deployable services, each owning its own data and communicating over the network. The load-bearing difference is the *deployment unit* — not the number of repositories, since you can run microservices from a monorepo.
>
> The monolith is simpler to start, gives you ACID transactions and compiler-checked refactoring across the whole domain, and one place to look when debugging. The costs are coarse-grained scaling — you scale the whole app, so you provision for your most expensive component — a shared release train that couples all teams' velocity to the slowest, and no fault isolation: one memory leak takes down everything.
>
> Microservices give you independent deployment, per-service scaling, fault isolation, and per-service technology choice. You pay with distributed-systems complexity: the network becomes part of your business logic, so you need timeouts, retries with backoff, circuit breakers, and idempotency; you lose distributed transactions and have to write sagas with eventual consistency; and you can't debug without correlation IDs and distributed tracing.
>
> For the placement portal I'd make it conditional. Single college, 500 students, one placement season: a **modular monolith** — one deployable, but hard internal module boundaries enforced by the build, so extraction is cheap later. The microservices complexity isn't earned at that scale, and the cloud bill would be several times higher.
>
> Multi-college SaaS with 10,000 concurrent applicants on placement day: microservices, extracted in this order — `resume-svc` first because PDF parsing is CPU-heavy and spiky and shouldn't compete with request-serving; then `notification-svc`, because it's naturally asynchronous and failure-tolerant, so making it a separate service actively *increases* availability; then `application-svc`. I'd keep auth and admin in the core until they demonstrated a reason to move.

**Q2. CI vs CD — and CD means two different things. Explain.**

> CI, Continuous Integration, is about the *shared branch*: every commit is automatically merged to `main` and verified with build, tests, and security scans, so `main` is always green and releasable. It ends when a tested artifact exists.
>
> CD is overloaded. **Continuous Delivery** means every green artifact is automatically taken all the way to a production-ready state, so deploying is a one-click business decision that's always available — there's a deliberate human approval gate. **Continuous Deployment** removes that gate: every green artifact goes to production automatically.
>
> In a GitHub Actions workflow, the difference is literally one line — an `environment: production` with required reviewers.
>
> Which to use is a risk decision, not a maturity ladder. Continuous Delivery for anything with financial, regulatory, or reputational consequence — the offer-letter service, payments. Continuous Deployment where automated verification is genuinely trustworthy and rollback is cheap: a stateless frontend behind feature flags with canary deploys and auto-rollback on error-rate. And I'd add that the prerequisite for Continuous Deployment isn't a tool — it's a test suite you'd bet production on, plus automated rollback. Most teams that claim Continuous Deployment actually have Continuous Delivery with a rubber-stamp approver.

**Q3. SAST vs DAST vs SCA. Give a tool for each and say where it runs in the pipeline.**

> **SAST** — Static Application Security Testing — analyses *your source code* without running it, looking for injection sinks, XSS, unsafe deserialization, hardcoded secrets, weak crypto. **SonarQube** is the common one; also Semgrep and CodeQL. Runs on every pull request. Cheap and early, but it can't see runtime configuration and it produces false positives because it doesn't know what's actually reachable.
>
> **SCA** — Software Composition Analysis — scans *your dependencies* for known CVEs and license problems: `requirements.txt`, `package.json`, and the OS packages inside your container base image. **Trivy** and **Snyk Open Source** are standard. Runs at build time on the image, and importantly also on a *schedule* against already-shipped artifacts, because new CVEs get published against code you already deployed.
>
> **DAST** — Dynamic Application Security Testing — attacks a *running* application from the outside, black-box. **OWASP ZAP** or Burp Suite. Runs against staging after deploy, because it needs a live target. It finds things static analysis can't — broken auth, session handling, missing security headers, injection that's actually reachable — but it's slow and it only covers the paths it manages to crawl.
>
> The defining test is: does the tool need a running application to point at? If yes it's DAST; if it reads files, it's static.
>
> I'd add a fourth that's just as important in practice: **IaC and configuration scanning** — Trivy in config mode, or Checkov — catching a public S3 bucket or a `0.0.0.0/0` security group in the Terraform *before* it's applied. And secret scanning with gitleaks, because leaked credentials are the most-exploited class of finding.
>
> All of it together is "shift left": move each check as early as it can possibly run, because a design flaw caught at PR time costs orders of magnitude less than the same flaw found in production.

**Q4. A pod is in `CrashLoopBackOff`. Walk me through your debugging.**

> First, `kubectl logs <pod> --previous` — the `--previous` flag is essential because the current container may have just started and have no output yet; I need the *crashed* container's stdout. That usually names the problem outright: a missing environment variable, a database connection refused, a config parse error.
>
> Second, `kubectl describe pod <pod>` and read the **Events** section from the bottom up. That tells me whether it's actually an application crash or something else wearing the same costume: `ImagePullBackOff`, a failing liveness probe restarting a healthy-but-slow app, or `OOMKilled`.
>
> Third, the exit code — `kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[0].lastState.terminated}'`. Exit 1 is an application error, read the logs. Exit **137** is SIGKILL, which in Kubernetes almost always means OOMKilled: the container exceeded its memory limit, so I either raise the limit or find the leak. Exit 143 is SIGTERM — a clean shutdown that something requested, which points at a probe or an eviction rather than a bug.
>
> A specific trap worth calling out: if the app is slow to boot and the **liveness** probe's `initialDelaySeconds` is too short, Kubernetes kills it mid-startup, forever. It looks exactly like a crash but the app is fine. The fix is a **startupProbe** — it holds off liveness until the app is genuinely up, so you can keep liveness aggressive afterwards.
>
> If the logs are empty and events are clean, I'd temporarily override the command to `sleep 3600` so the container stays up, then `kubectl exec` in and run the real start command by hand to see the failure interactively.

**Q5. Terraform vs Ansible — do I need both?**

> They solve different problems. Terraform does **provisioning**: it answers "what resources should exist?" — VPC, EKS cluster, RDS instance, S3 bucket, IAM roles. It's declarative, it keeps a **state file** recording what it created, and it shows you a **plan** diff before changing anything. Because it tracks state, it can also *delete* — removing a block from your code destroys the resource.
>
> Ansible does **configuration management**: "what should be true *inside* this machine?" Install these packages, render this config file, ensure this service is running. It's agentless over SSH, and it's idempotent — it inspects the target each run rather than keeping state, so removing a task from a playbook does nothing to the host.
>
> The one-liner: Terraform builds the house, Ansible furnishes it.
>
> Do you need both? Increasingly, no. In a container world you bake configuration into the **image** at build time and treat servers as immutable — if a node is wrong you replace it rather than reconfigure it, so Ansible's core use case shrinks. It's still essential for on-prem fleets, network devices, long-lived VMs, Windows estates, and bootstrapping. But I wouldn't reach for Ansible to configure a Kubernetes node pool; I'd use a managed node group with a custom AMI built by Packer.
>
> Worth knowing: since v1.6 Terraform is BUSL-licensed rather than open source, which produced **OpenTofu**, a Linux Foundation MPL-2.0 fork that's a drop-in replacement. HashiCorp is now part of IBM. Job ads still say Terraform, so learn Terraform — but the licensing story matters if you're choosing for a product.

**Q6. Why is Prometheus pull-based instead of push-based?**

> Three reasons, and one honest caveat.
>
> First, **liveness comes free**. If a scrape fails, Prometheus records `up == 0` for that target, so "the service is gone" is a first-class, alertable signal. In a push model, silence is ambiguous — is the app dead, is the network broken, or is it just idle?
>
> Second, **service discovery centralises configuration**. Prometheus queries the Kubernetes API, EC2 tags, or Consul to find targets. In a dynamic cluster where pods appear and vanish every few minutes, nothing needs to be told where to send metrics — new pods are discovered automatically. With push, every app needs the collector's address baked into its config.
>
> Third, **the scrape config is one place you control**: intervals, timeouts, relabelling, and which targets exist are all managed centrally rather than negotiated with every application team.
>
> The caveat is short-lived jobs. A CronJob that runs for 8 seconds may never be scraped at all. Prometheus's answer is the **Pushgateway** — the job pushes before exiting, and Prometheus scrapes the gateway. You should use it sparingly and only for that case, because it breaks the liveness signal: the Pushgateway keeps serving the last value forever, so a job that stops running entirely looks perfectly healthy.

**Q7. What's GitOps, and how is it different from just running `kubectl apply` in my CI pipeline?**

> GitOps means a Git repository holds the **desired state** of the system declaratively, and an agent running *inside* the cluster continuously pulls from that repo and reconciles reality to match it. The four OpenGitOps principles are: declarative, versioned and immutable, pulled automatically, and continuously reconciled.
>
> The difference from `kubectl apply` in CI is push versus pull, and it has three concrete consequences.
>
> **Credentials.** In the push model your CI runner holds admin credentials to production. Compromise CI and you own the cluster. In GitOps the agent runs inside the cluster and pulls — no external system holds cluster credentials at all.
>
> **Drift.** With push, someone runs `kubectl edit` at 3 AM during an incident and Git silently stops matching reality. Nobody notices until the next deploy overwrites the fix, or doesn't. A GitOps agent *detects* that as drift and either reverts it automatically or flags it as out-of-sync.
>
> **Rollback and recovery.** Rollback is `git revert` — the same mechanism as any other change, with the same review trail. Disaster recovery is pointing a fresh cluster at the repo and waiting for it to converge.
>
> Tools are **Argo CD** and **Flux**, both CNCF graduated. Argo CD's UI makes sync status and drift very legible, which is usually why teams pick it.
>
> The question that always follows is **secrets** — you obviously don't commit plaintext Kubernetes Secrets. Best option is the **External Secrets Operator**, where the cluster pulls values from AWS Secrets Manager or Vault at runtime and nothing sensitive is ever in Git. Alternatives are **Sealed Secrets**, where only an in-cluster controller holds the private key so ciphertext in Git is safe, or **SOPS** with age/KMS to encrypt values in place.

**Q8. Your placement portal is fine all year and falls over on placement day. What do you do?**

> First, **measure before I change anything** — otherwise I'm guessing. I need to know *what* saturated: is it CPU on the app pods, connection exhaustion on Postgres, p99 latency climbing while CPU is flat (which points at lock contention or a slow downstream), or the load balancer rejecting connections? `kubectl top pods` versus my resource requests, the RDS connection-count metric, and a latency histogram broken out per endpoint answer that.
>
> Assuming it's the application tier: an **HorizontalPodAutoscaler** on the hot services with `minReplicas` raised ahead of the event, plus **Cluster Autoscaler or Karpenter** so nodes exist for those pods to land on. HPA is reactive, though — it takes tens of seconds to react and more to schedule and warm up, and placement-day load arrives in a step function the moment applications open. So I'd **pre-scale** on a schedule; you know the date in advance.
>
> Then I'd look for the things scaling won't fix. **The database is usually the real ceiling**, because you can't horizontally scale writes by adding replicas. So: connection **pooling** with PgBouncer, read replicas for the listings and dashboard queries which are overwhelmingly read-heavy, and an index review — one missing index on `applications(student_id, job_id)` will beat any amount of pod scaling.
>
> Architecturally, I'd make the write path **asynchronous**. Submitting an application shouldn't synchronously generate a PDF, email the recruiter, and update the dashboard. Write the row, publish an event, return 202. Now the spike lands in a queue instead of on your database, and `notification-svc` drains it at whatever rate it can sustain.
>
> I'd also add **load shedding and rate limiting** at the gateway, so that under genuine overload the portal degrades — some users get a "try again in a moment" — rather than everyone getting timeouts. A partially available portal is far better than a dead one.
>
> And I'd **load test it beforehand** with k6 or Locust at 2× expected peak, because every one of these hypotheses is worthless until measured. Placement day is not the time to discover which of them was right.

**Q9. What does "shift left" mean, and what does it look like concretely?**

> Shift left means moving each activity — especially security and testing — as early in the lifecycle as it can possibly happen, because the cost of fixing a defect rises steeply with how late you find it. A design flaw caught in a threat model costs a conversation. The same flaw found in production costs an incident, a disclosure, and possibly a breach.
>
> Concretely, across the lifecycle: at **Plan**, threat modelling and a design review, so "resumes go in a public bucket" never gets built. At **Code**, IDE-level static analysis and secret scanning on save, plus pre-commit hooks — findings before a commit even exists. At **Build/PR**, SAST, SCA on dependencies, IaC scanning on the Terraform, and image scanning on the container, all as required checks that block the merge. At **Test**, DAST against staging. At **Release**, image signing and SBOM generation. At **Deploy**, admission control that refuses to run unsigned images or privileged containers. At **Operate**, runtime detection and continuous re-scanning of shipped artifacts, because new CVEs are published against code you deployed months ago.
>
> The important caveat: shift left is not "run every scanner and block on everything." Do that and developers route around you — you'll find `--exit-code 0` in the pipeline within a month. The engineering work is **tuning**: block on high-confidence, high-severity, *fixable* findings; report the rest; suppress known-unreachable ones with a documented reason and an expiry. A gate developers trust is worth ten gates they've learned to bypass.

**Q10. Difference between a Deployment, a StatefulSet, and a DaemonSet?**

> All three manage pods; they differ in what identity and lifecycle guarantees they give.
>
> A **Deployment** manages ReplicaSets to run N *interchangeable* pods. Names are random, pods can be created and destroyed in any order, and any pod can serve any request. This is what you want for stateless services — `resume-svc`, `application-svc`, anything behind a load balancer. It gives you rolling updates and rollback.
>
> A **StatefulSet** gives pods **stable identity and stable storage**. Pods get ordinal names — `postgres-0`, `postgres-1` — that survive rescheduling; each gets its *own* PersistentVolumeClaim that follows that identity; and they're created and terminated in order, scaling down highest-ordinal-first. Plus a headless Service giving each pod its own stable DNS name. That matters for anything where pods aren't interchangeable: a database with one primary and replicas, Kafka brokers, etcd — systems that do leader election or shard data and therefore need to know *which* member they are.
>
> A **DaemonSet** runs exactly one pod **per node**, and automatically places one on any node that joins. That's for node-level agents: log collectors like Fluent Bit, the Prometheus node-exporter, CNI plugins, security agents. You don't specify replicas — the node count is the replica count.
>
> The practical advice on StatefulSets: in 2026, if you're on a cloud provider, **strongly prefer managed RDS or Aurora over running Postgres in a StatefulSet yourself.** The StatefulSet gets you scheduling and storage identity; it does not get you backups, point-in-time recovery, automated failover, or minor-version patching. Those are the hard parts of running a database, and they're exactly what the managed service is selling. Self-managed StatefulSet databases make sense on-prem, or when you have a specific reason and a DBA.

---

## Part 12 — Hands-on exercise

Build the two-architecture comparison yourself. Everything below runs on Docker Desktop with WSL2 on your Windows 11 machine; the Kubernetes part uses `kind` locally, so **zero cloud cost**.

### Stage 1 — Build the monolith (~1 hour)

Create a small Flask/Express app with three routes in one file: `/login`, `/jobs`, `/apply`. One Dockerfile, one container, one SQLite or Postgres DB.

```bash
docker build -t placement-monolith:1.0 .
docker run -d -p 8080:8080 --name mono placement-monolith:1.0
curl localhost:8080/jobs
```

**Now break it deliberately.** Add an endpoint that allocates memory in a loop:

```python
@app.get("/boom")
def boom():
    leak = []
    while True:            # deliberately unbounded
        leak.append("x" * 10_000_000)
```

```bash
docker run -d -p 8080:8080 -m 256m --name mono placement-monolith:1.0
curl localhost:8080/boom &
sleep 5 && curl -sf localhost:8080/jobs || echo "❌ /jobs is ALSO dead"
docker inspect mono --format '{{.State.ExitCode}} {{.State.OOMKilled}}'
# 137 true      ← exit 137 = SIGKILL = OOMKilled
```

**Observe:** one bad endpoint killed *every* feature. Write that down — it's the single point of failure, felt rather than read.

### Stage 2 — Split into three services (~2 hours)

Split into `auth-svc`, `jobs-svc`, `apply-svc`, each with its own Dockerfile and its own port.

```yaml
# docker-compose.yml
services:
  auth-svc:
    build: ./services/auth-svc
    ports: ["8081:8081"]
    mem_limit: 256m
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/healthz"]
      interval: 10s
      retries: 3
  jobs-svc:
    build: ./services/jobs-svc
    ports: ["8082:8082"]
    mem_limit: 256m
    depends_on:
      db: { condition: service_healthy }
  apply-svc:
    build: ./services/apply-svc
    ports: ["8083:8083"]
    mem_limit: 256m
    environment:
      AUTH_URL: http://auth-svc:8081       # service name = DNS inside the compose network
      JOBS_URL: http://jobs-svc:8082
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: devonly
      POSTGRES_DB: placement
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes: { pgdata: {} }
```

```bash
docker compose up -d --build
docker compose ps

# Kill ONE service and watch the others survive
docker compose stop jobs-svc
curl -sf localhost:8081/healthz && echo "✅ auth-svc still alive"
curl -s  localhost:8083/apply  | jq .        # should degrade gracefully, not 500
docker compose start jobs-svc
```

**Then feel the cost side too.** Add a 3-second `sleep` inside `auth-svc`'s handler and call `/apply` — watch `apply-svc` hang because it has no timeout. Then add a 500 ms timeout with a fallback and watch it degrade instead of hanging. **That is the microservices tax, in ten lines of code.** Every network boundary needs this.

### Stage 3 — Put it on Kubernetes (~2 hours)

```bash
# kind = Kubernetes in Docker. Free, local, disposable.
winget install Kubernetes.kind      # PowerShell on Windows 11
kind create cluster --name placement
kubectl cluster-info --context kind-placement

# Load your locally-built images so the cluster doesn't try to pull from a registry
kind load docker-image placement/auth-svc:1.0 --name placement

kubectl apply -f platform/k8s/
kubectl get pods -w

# Prove self-healing: delete a pod and watch the ReplicaSet replace it
kubectl delete pod -l app=auth-svc
kubectl get pods -w        # a new one appears within seconds

# Prove the 503 diagnosis from Part 10: break the selector on purpose
kubectl patch svc auth-svc -p '{"spec":{"selector":{"app":"typo-svc"}}}'
kubectl get endpoints auth-svc          # <none>   ← this is your 503, and now you've seen it
kubectl patch svc auth-svc -p '{"spec":{"selector":{"app":"auth-svc"}}}'
```

### Stage 4 — Wire up the pipeline and scan it (~2 hours)

1. Push to GitHub. Add the workflow from [item 6](#6-cicd) (trim it to `test` + `build-and-scan` first).
2. Add a Trivy step. **Deliberately use an old base image** (`FROM python:3.9-slim`) and watch CI go red with real CVEs.
3. Fix it by bumping to `python:3.13-slim`. Watch it go green. That loop — scan, understand, fix, verify — *is* DevSecOps.
4. Add a `deploy` job gated on `environment: production` with yourself as required reviewer. You have now built Continuous Delivery. Delete the line and you have Continuous Deployment. Feel the difference.

### Stage 5 — Write it up

Write a short `DECISION.md` in the repo answering: *for a single college with 500 students, which architecture would you actually ship, and why?* Argue against your own Stage 2 work. **The ability to argue both sides is exactly what the interview is testing** — and a candidate who says "I built microservices, then concluded a modular monolith was right at this scale, here's the reasoning" is far more convincing than one who only ever says "microservices are better."

---

## Part 13 — Transcript corrections, collected

Every place the live class was wrong, imprecise, or garbled by ASR. Trust this list over the recording.

| # | Class said | Reality |
|---|---|---|
| 1 | Monolith = "everything in one repository" | Monolith = one **deployment unit**. Microservices can live in a monorepo (Google, Uber). Repos ≠ architecture. |
| 2 | "Trivy and Snyk are DAST tools" | **Both are static.** Trivy = SCA + misconfig + secrets + license. Snyk = SAST + SCA. Real DAST = **OWASP ZAP**, **Burp Suite**. Test: does it need a *running* app? |
| 3 | "SonarQube fetches your application URL" | SonarQube analyses **source code** in CI. It doesn't crawl a live site. Also its dependency-CVE coverage is limited — pair it with an SCA tool. |
| 4 | "OWASP is 10 tools" | OWASP is a **non-profit foundation**. The **OWASP Top 10** is an awareness document — currently the **2025 edition** (final release Jan 2026). |
| 5 | "Pod is nothing but a Docker container" | A Pod wraps **one or more** containers sharing a network namespace. Runtime is normally **containerd/CRI-O** — **dockershim was removed in Kubernetes v1.24**. Docker-built images still work fine (OCI standard). |
| 6 | "We scale up/down with one Helm command" | **Helm is a package manager/templating tool.** Scaling is `kubectl scale`, or declaratively an **HorizontalPodAutoscaler**. |
| 7 | "curl is a Windows command we don't use" | **`curl` is essential** on every platform. `tracert` is the Windows spelling of `traceroute`. |
| 8 | `netstat` presented as current | **Deprecated on modern Linux** in favour of **`ss`**. Still worth knowing for interviews. |
| 9 | "Amazon's app crashed during streaming, so they moved to microservices" | ~2001: the **Obidos** monolith with shared databases; the bottleneck was that every schema change needed a DBA, blocking independent shipping. **~3-year** migration to SOA, no shared DBs, reinforced by the 2002 Bezos API mandate. |
| 10 | Microservices framed as strictly better | **Prime Video's VQA team went microservices → monolith in March 2023** and cut cost **>90%** while breaking a scaling ceiling. Boundaries should follow business capabilities, not processing steps. |
| 11 | GitOps = "tracking everything from version control to production" | GitOps = **Git as the declarative desired state**, with an in-cluster agent **pulling** and **continuously reconciling**. Audit trail is a consequence, not the definition. See the [4 OpenGitOps principles](https://opengitops.dev/). |
| 12 | Go tools list included "IAM, SQL" | ASR noise. Accurate list: Docker, Kubernetes, Terraform, Prometheus, Helm, etcd, containerd, Trivy, Argo CD. |
| 13 | Monitoring tool "Sanity" | **Sentry** (error tracking). Complements Prometheus; doesn't replace it. |
| 14 | Prometheus/Grafana called "old" | Prometheus is a **graduated CNCF project** and the 2026 standard for Kubernetes metrics. What's new *around* it: OpenTelemetry, Loki, Tempo, Mimir/Thanos. |
| 15 | "Kiro is Cursor's old version from AWS" | **[Kiro](https://kiro.dev/)** is AWS's own agentic dev platform (IDE + CLI + web), GA, built around **spec-driven development**. Not a Cursor fork. |
| 16 | EC2 "t series, micro, nano series" | **Family** = `t`/`m`/`c`/`r`/`g`; **size** = `.nano`/`.micro`/`.large`. So `t4g.micro` is family `t4g`, size `micro`. |
| 17 | "MLOps engineers build the LLM models" | **ML/research engineers** train models; **MLOps engineers** build the infra to train/version/serve/monitor them; **AI application engineers** build products on model APIs. |
| 18 | SRE described as translating client requirements | That's a **PM/TPM** function. SRE = reliability as engineering, quantified by **SLIs/SLOs/error budgets** and incident response. |
| 19 | "Microsoft keeps monoliths because the code is in C" | Second-hand anecdote — treat as such. The defensible principle: **migration cost often exceeds benefit for large legacy systems.** |
| 20 | Ingress/NGINX assumed as the default way in | **Ingress-NGINX retired 31 March 2026.** The Ingress *API* is fine; that controller is unmaintained. Direction of travel is **Gateway API** (v1.6.0, June 2026). |

---

## Part 14 — Version reference (verified 11 August 2026)

> **⚠️ Re-check this table before relying on it.** Every row moves.

| Tool | Version | Released | Source |
|---|---|---|---|
| Kubernetes | **1.36.2** (1.37 due 26 Aug 2026) | 9 Jun 2026 | [kubernetes.io/releases](https://kubernetes.io/releases/) |
| Docker Engine | **29.7.2** | 5 Aug 2026 | [endoflife.date](https://endoflife.date/docker-engine) |
| Terraform | **1.15.8** (BUSL 1.1) | 8 Jul 2026 | [endoflife.date](https://endoflife.date/terraform) |
| OpenTofu | **1.12.5** (MPL-2.0) | 21 Jul 2026 | [endoflife.date](https://endoflife.date/opentofu) |
| Ansible (community pkg) | **14.2.0** (`ansible-core` 2.21) | 14 Jul 2026 | [endoflife.date](https://endoflife.date/ansible) |
| Prometheus | **3.13.2** (3.13 = LTS) | 30 Jul 2026 | [endoflife.date](https://endoflife.date/prometheus) |
| Grafana | **13.1.3** | 7 Aug 2026 | [endoflife.date](https://endoflife.date/grafana) |
| Trivy | **v0.71.0** | 1 Jun 2026 | [Aqua Security](https://www.aquasec.com/products/trivy/) |
| Gateway API | **v1.6.0** (v1.6.1 latest) | 30 Jun 2026 | [k8s blog](https://kubernetes.io/blog/2026/08/03/gateway-api-v1-6-release/) |
| OWASP Top 10 | **2025 edition** | Final Jan 2026 | [owasp.org/Top10/2025](https://owasp.org/Top10/2025/) |
| Ingress-NGINX | **RETIRED** | 31 Mar 2026 | [k8s statement](https://www.kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) |

---

## Further reading

**Architecture**
- [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html) and [MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html) — still the canonical treatment
- [Werner Vogels — A Conversation with Werner Vogels, ACM Queue 2006](https://queue.acm.org/detail.cfm?id=1142065) — the Amazon Obidos → SOA transition, first-hand
- [Amazon's 1998 Distributed Computing Manifesto](https://www.allthingsdistributed.com/2022/11/amazon-1998-distributed-computing-manifesto.html) — the internal doc that started it
- Sam Newman, *Building Microservices* (2nd ed.) — the practical book, strong on *when not to*
- [microservices.io — pattern catalogue](https://microservices.io/patterns/) — saga, API gateway, CQRS, circuit breaker

**DevOps practice**
- [DORA — DevOps Research & Assessment](https://dora.dev/) — the [five metrics](https://dora.dev/guides/dora-metrics-four-keys/) and the annual State of DevOps report
- Forsgren, Humble, Kim — *Accelerate* — the research behind DORA
- Kim, Debois, Willis, Humble — *The DevOps Handbook*
- Gene Kim — *The Phoenix Project* — the novel; a fast, genuinely useful read on why the wall of confusion exists

**Tools (official docs — always prefer these over blog posts)**
- [Kubernetes docs](https://kubernetes.io/docs/home/) · [Gateway API](https://gateway-api.sigs.k8s.io/) · [dockershim FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/)
- [Docker docs](https://docs.docker.com/) · [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- [Terraform docs](https://developer.hashicorp.com/terraform/docs) · [OpenTofu](https://opentofu.org/docs/)
- [Ansible docs](https://docs.ansible.com/) · [Prometheus docs](https://prometheus.io/docs/) · [Grafana docs](https://grafana.com/docs/)
- [GitHub Actions docs](https://docs.github.com/actions) · [Argo CD](https://argo-cd.readthedocs.io/) · [Flux](https://fluxcd.io/docs/)

**Security**
- [OWASP Top 10:2025](https://owasp.org/Top10/2025/) · [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) · [OWASP ZAP](https://www.zaproxy.org/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — increasingly asked about
- [Trivy docs](https://trivy.dev/) · [SonarQube docs](https://docs.sonarsource.com/) · [Sigstore / cosign](https://docs.sigstore.dev/)
- [OpenGitOps principles](https://opengitops.dev/)

**SRE**
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — free online; read chapters 1–6 at minimum
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/) — the practical companion, especially SLO chapters

**Landscape**
- [CNCF Landscape](https://landscape.cncf.io/) — every tool in the ecosystem, by category. Overwhelming by design; useful for orientation.
- [endoflife.date](https://endoflife.date/) — bookmark this. Fastest way to check any tool's current version and support window.

---

## Where this goes next

The course arc from here (each becomes its own note file):

`02` Git & GitHub → `03` Linux fundamentals → `04` Shell scripting → `05` Networking for DevOps → `06` Python for DevOps → `07` Docker deep dive → `08` CI/CD → `09` AWS fundamentals → `10` Kubernetes → `11` Terraform & IaC → `12` Ansible → `13` Monitoring → `14` GitOps → `15` DevSecOps

Every one of them will keep using `placement-portal` as the running example, so the artifacts you build in the exercise above carry forward.
