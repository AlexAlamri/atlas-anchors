# A pre-registered abandonment-criteria protocol for a personal informatics tool: a single-case observational study (n = 1)

**Alexander Alamri. Independent researcher.**

*Public mirror, released to the evidence repository as a deliberate release under the two-surface model. Registration document, corrected copy of 28 July 2026. This text matches the OSF Preregistration form fields as submitted, with one correction made after the form was completed but before this copy was produced: the Perski reference, cited in the working draft as 2019, is Perski, Blandford, West and Michie (2017), and two references carry scope qualifiers. The correction is recorded as a corrective event in the study's anchored log. Where the registration form's field structure splits this material, the ordering and cross-references here are the authoritative reading.*

---

## Authors

Alexander Alamri. Independent researcher. Sole author, participant, system builder,
and analyst (see Conflicts of Interest). The study is conducted independently: it has
no institutional sponsor, supervisor, or funder, and is not carried out under the
auspices of the author's clinical employer or any academic institution.

## Study type and framing

Prospectively designed, **mid-window externally registered**, single-case
observational study, framed as personal science (Wolf & de Groot, 2020). This is not a
single-case experimental design: no independent variable is manipulated, and no
experimental-control claims are made. The primary contribution is the **protocol**: a
reusable pattern for pre-registering abandonment criteria on a personal tool, with
tamper-evident timestamping, instantiated once. The study does not claim the tool is
effective, and does not claim superiority over its predecessors.

## Background

The subject system ("Atlas") is a self-built personal life-OS: an event-sourced,
append-only Postgres log as canonical state, a progressive web app heads-up display,
deterministic in-database collectors, an authenticated ingest path allowing external
systems to write events, and a push-notification loop governed by a calm-technology
policy enforced in code (only urgent transitions push; changes coalesce; a daily
ceiling applies; non-urgent changes batch to a scheduled digest).

Two predecessor systems built by the same author were abandoned. These predecessors
are **motivating cases**, characterised using the lapsing and abandonment constructs of
the personal-informatics literature (Epstein et al., 2015; 2016). They are **not
historical controls**: they were not comparably instrumented, and no causal comparison
between systems is claimed. Their role is to justify the choice of primary outcome
(sustained engagement versus abandonment), nothing more.

The research questions:

- RQ1: Does the builder's engagement with the system meet engagement criteria that
  were pre-specified and timestamped before the observation windows opened?
- RQ2: Is the protocol itself feasible and honest at n = 1: can abandonment criteria be
  pre-registered, externally anchored, and honoured (including honouring a failure)?

## Declared intervention components

Two factors that would ordinarily be treated as confounds are declared here as
**components of the intervention**, because for an abandonment study they are the
mechanism of interest:

1. **Self-monitoring reactivity.** The system instruments its own use, and the builder
   knows it. Reactivity is expected to persist while monitoring continues; the study
   asks whether instrumentation-plus-stakes sustains engagement past the point where
   uninstrumented predecessors died.
2. **The publication incentive.** Writing about whether the tool survives changes
   whether it survives. The claim is therefore scoped to: what happened when one person
   ran this protocol under publication stakes. No claim is made that the tool is
   intrinsically engaging absent these components.

## Participant

n = 1: the author, a practising surgeon-researcher who is also the system's builder.
The design context is an interruption-heavy professional life with high
context-switching load across clinical, academic, and venture roles; the system
specifically targets the prospective-memory failure mode, open loops dropped between
contexts, that characterised the predecessors' abandonment. This context is part of the
lived-informatics contribution.

## System evolution during observation (evolving population)

The system remains in active development throughout observation; a frozen system would
misrepresent the phenomenon under study, and the lived-informatics framing requires
genuine, evolving use. Four disciplines govern this honestly.

**Phase discipline.** Every change to a measured surface is recorded as a dated,
append-only phase event before or with the change; analyses annotate phases. This
discipline has been breached twice, and both breaches are disclosed under Deviations
below rather than smoothed over.

**Corona freeze.** The primary graph surface (the "corona") is frozen from 21 Jul to
3 Aug 2026: no visual or interaction changes, and no developer stress-testing sessions,
during its measurement window. Freeze status is asserted in each intervening phase
event and is auditable from the log.

**Tap-surface growth is disclosed, not frozen.** The notification and HUD tap surface
did change during the Gate 2 window and is phase-annotated throughout: push
delivery-outcome instrumentation (24 Jul); digest lane live (25 Jul); urgent-push
population change (25 Jul, see the ruling registered under Gate 2); daily ceiling
narrowed to count urgent-kind rows only, and digest payload persisted (26 Jul);
registry decay items joined the digest (26 Jul); and a new HUD control entered the tap
surface (26 Jul). The last of these enlarges the set of controls a user may tap. It
writes no telemetry row and therefore changes no gate value, but it changes the
surface, and it is declared rather than amended away.

**Evolving spoke population.** Workstreams ("spokes") are user-defined data; the
population may grow or shrink during observation. All gates are user-level and
invariant to spoke count. Creation of new spokes is ordinary usage, not a protocol
event; spoke creation timestamps are in the log, so any clustering of engagement around
novelty is exploratorily queryable.

## Measures and operational definitions

- **Day boundary.** All distinct-day counts use the Europe/London calendar day.
- **Corona open.** A **deliberate** open event in the graph telemetry table
  (primary-key-deduplicated per day). Per the pinned wording: deliberate opens only;
  ambient HUD glances do not count.
- **Push events.** All notifications are logged and lane-tagged: urgent
  (transition-gated) or digest (scheduled daily summary). From 24 Jul 2026 each row
  also records a delivery outcome: a positive count of accepting endpoints, zero for a
  dispatched attempt no endpoint accepted, or null where the outcome is unknown (the
  row predates instrumentation, or the post-dispatch write itself failed).
- **Tap.** A notification-click event logged by the service worker, joinable to the
  push that produced it.
- **Dismissal.** A notification-close event logged by the service worker. Dismissal
  rate is reported descriptively and is never part of any gate.
- **Engagement construct.** Opens and taps are behavioural-engagement proxies (amount
  and frequency of use, in the sense of the digital-behaviour-change-intervention
  engagement literature, e.g. Perski et al., 2017). Experiential engagement (interest,
  attention) is not measured and is not claimed.
- **Measurement start, Lane A.** **24 Jul 2026 09:32:26 UTC**, the first
  server-verified active service-worker registration. An earlier phase event declared
  measurement live from 23 Jul 15:56:20 UTC; that claim was false as written and has
  been corrected on the log (see Deviations). Zero pushes were dispatched between the
  false start and the re-anchor, so no event was misclassified by the error. Every push
  fired before the re-anchored start is reported as fired-but-unmeasured and enters no
  denominator.
- **Measurement start, Lane B.** The first scheduled digest, **25 Jul 2026 09:00:05
  UTC**. That first digest is atypical: it carried a 23-item accumulated backlog as a
  single push. Lane B's criterion reads on the last 14 digest days before adjudication
  and therefore does not include it, but the fact is recorded here.
- **Missingness rule.** A day is excluded as unmeasurable where telemetry coverage is
  discontinuous: that is, where the anchor chain's coverage watermark fails to advance
  past that day, or where the daily heartbeat records an outage. A night on which no
  anchor was computed is **not** by itself a gap, provided the next anchor's coverage
  spans the intervening period; chain integrity is defined by continuity of coverage,
  not by one anchor per calendar night. Missing telemetry is never counted as
  non-engagement.
- **Named validity dependency: silent client-layer telemetry death.** Push and tap
  telemetry depends on a service worker active on the subscribed device, and that layer
  can fail without any server-side signal. This is not hypothetical: it occurred once
  and produced the false measurement start described above. Two controls follow, both
  standing: the production origin must remain outside any access-gating layer that
  redirects script fetches, and client-side error paths must surface to a visible
  in-app diagnostic rather than to the console alone. Any recurrence is handled by the
  missingness rule, not by reinterpretation.
- **Excluded events.** Developer and stress-test opens are excluded from engagement
  counts. Limitation, stated plainly: the graph telemetry table does not tag the
  synthetic stress fixture, so a stress open is not distinguishable post hoc from a real
  one. This exclusion therefore rests on conduct (no stress sessions are run on the
  frozen surface during its window) rather than on instrumentation, and is auditable
  only by the absence of corresponding development sessions in the append-only log.
  Adding the tag would itself breach the corona freeze, so the limitation is disclosed
  rather than remedied mid-window.

## Confirmatory analyses: the pre-specified gates

Both gates were pinned to the system's own append-only log before external
registration; provenance below. No metric substitution, threshold change, or window
change is permitted after this registration. Anything not stated in this section is
exploratory.

### Gate 1: corona engagement gate (product-internal; registered for completeness)

At least 5 distinct-day deliberate corona opens in 21 Jul – 3 Aug 2026, with at least
2 in 28 Jul – 3 Aug 2026.

*Window-anchoring disclosure.* The 16 Jul pin defines a 14-day window beginning on the
day the corona merges to production. The merge landed 20 Jul 2026. The window was
anchored to 21 Jul – 3 Aug (week-two clause 28 Jul – 3 Aug) by a decision recorded
20 Jul 2026 13:15:05 UTC, before the window opened. The same decision excluded the four
pre-existing telemetry rows of 16, 17, 19 and 20 Jul as verification opens rather than
spontaneous engagement. The effect is to discard the merge-day novelty spike and to
shift the window one day later. The threshold is unchanged from the pin. Both the pin
and the anchoring decision precede the first counted day and are covered by the first
external anchor.

*Falsification caveat*, stated at pinning and repeated here: the deterministic graph
currently renders a small node inventory (approximately 15–30 nodes), so this gate has
limited falsification power regarding the value of the graph itself; it reads on
engagement with the first-stage surface only. Decision consequence: pass opens the next
graph stage; fail triggers a deliberate, recorded decision rather than automatic
continuation.

### Gate 2: loop gate (system-primary), evaluated 18 Aug 2026

**Lane A (urgent).** At least 50% of urgent pushes tapped within 24 hours, across the
window to 18 Aug 2026; minimum n = 4 urgent pushes; below n = 4, Lane A is
inconclusive.

*Pre-specified exclusion*, pinned 24 Jul 2026 09:35:07 UTC before the relevant pushes
fired: the two live acceptance-verification pushes required by the telemetry build,
identifiable by their dedicated test workstream identifier, are excluded from **both
numerator and denominator** and from any delivered-only secondary read. These were
requested verification, not spontaneous system activity.

*Registered population ruling, no segmentation.* A defect fix on 25 Jul 2026 changed
which urgent pushes reach the ledger. Before the fix, a scheduled escalation job ran
inside the configured quiet window; those escalations passed the transition gate, died
at the quiet-hours gate before the ledger insert, and reached no channel but the HUD.
The job was rescheduled outside the quiet window, so from 25 Jul such escalations
produce real ledger rows where previously they produced none. The pin defines the
primary denominator as every ledger row in the window and **stands as written,
unamended**: the population is treated as one, with no pre-/post-fix segmentation. Two
reasons, both fixed in advance of any outcome. First, this is disclosed instrumentation
repair rather than manufactured volume, since those escalations always should have pushed,
and the pin was fixed before findings precisely to foreclose a post-hoc split. Second,
no retroactive exclusion is required or possible: the quiet-hours gate left no rows for
the suppressed pushes, so the pre-fix window carries zero contamination. A descriptive
split by push origin may appear in the secondary read; it never gates.

**Lane B (digest).** Evaluable only if the daily digest has run for at least 10 days by
18 Aug 2026; criterion: a post-digest open within 12 hours on at least 50% of the last
14 digest days.

**Decision rule.** PASS = any evaluable lane passes. FAIL = all evaluable lanes fail. If
no lane is evaluable, one pre-committed 14-day extension applies, after which the gate
decides on whatever is evaluable. Transparency note: the any-lane-passes structure is
deliberately lenient; this is an engineering decision rule, not a hypothesis test, and
**both lanes will be reported in full regardless of gate outcome**.

**Abandonment rule (standing).** If pushes fire but are ignored at Gate 2, the
pre-committed response is to stop adding capability and rescope the system. Gate failure
is treated as **validation of the protocol**, not a null result: a documented,
instrumented n = 1 abandonment is a reportable outcome of equal standing, and the author
pre-commits to publishing the outcome whichever way it goes.

## Secondary and exploratory analyses

- **Build-quiet stratifier (secondary, reported, never gating).** A build-quiet day is a
  calendar day with zero events on the system's own development workstream from any
  non-automation source. Engagement on such a day is defined as at least one telemetry
  open or tap. This stratifier addresses the novelty confound (engagement driven by
  active building) by measuring it rather than scheduling it away.
- **Regime boundary in the digest content stream.** From 26 Jul 2026 19:11:26 UTC the
  recurrence interval of registry-decay items in the digest ceases to be stationary:
  surviving items lengthen their interval, churning items shorten it. Any descriptive
  rate computed over a window spanning that timestamp measures two processes and will be
  partitioned at it.
- **Push-origin split.** Cron-originated versus human-originated urgent pushes, and
  externally-ingested versus internally-generated transitions, may be reported
  descriptively. Neither gates.
- All other analyses, including engagement clustering around spoke creation and any
  phase-contrast descriptives, are exploratory and will be labelled as such.

## Provenance and timeline disclosure

- Gate 1 criteria internally pinned: **16 Jul 2026 13:26:45 UTC**, before the
  observation window opened.
- Gate 1 window anchored and pre-window opens excluded: **20 Jul 2026 13:15:05 UTC**.
- Observation window opened: **21 Jul 2026**.
- Gate 2 numeric pin ratified: **21 Jul 2026 23:25:38 UTC** (day 0 of its evaluation
  window), spine event id `63050c75-ac39-4e47-bc9f-40634510f881`.
- First external anchor: **seq 1, computed 22 Jul 2026 22:26:33 UTC**, 91 events,
  algorithm v1, no discrepancy. Chain head
  `9509be07bb1bdc32f31743aab137e4a5c77d9083697985a2de758598777bfbc1`. OpenTimestamps
  proof confirmed in Bitcoin block **959197**, the earliest of four independently
  confirming calendars (the others landed at 959198, 959199 and 959205); cite the block
  timestamp rather than any job run time, since the block is what a third party verifies
  without trusting the author. The chain head and its timestamp proof are published at
  `https://github.com/AlexAlamri/atlas-anchors`, which is the study's public evidence
  repository and its only public surface. Each anchor appears there as a JSON record
  carrying nine fields (sequence number, computation time, new and total event counts,
  batch hash, previous head, head, algorithm version, and a discrepancy flag) alongside
  its OpenTimestamps proof file. Verification requires nothing from the author: the
  proof resolves against the Bitcoin blockchain independently, and each head recomputes
  from its predecessor and batch hash under the published version 1 rule.
- Interval between the Gate 1 pin and the first external anchor: **6 days, 9 hours**.
  Within that interval, pre-specification of Gate 1 rests on the author-controlled log
  alone. The Gate 2 pin and the Gate 1 window anchoring both fall inside the anchored
  set.
- Lane A measurement start: **24 Jul 2026 09:32:26 UTC**. Lane B measurement start:
  **25 Jul 2026 09:00:05 UTC**.
- External registration (this document): **28 Jul 2026**. Registration is mid-window and
  the elapsed fractions are stated rather than left to be discovered: at registration,
  8 of the 14 Gate 1 days had elapsed, and 5 of the 26 Lane A measured days. Note that
  registration falls on the first day of Gate 1's week-two clause (28 Jul to 3 Aug),
  with week one complete and its data already in the telemetry table. The
  analyst-blinding declaration immediately below is therefore load-bearing rather than
  incidental, and is stated in full for that reason. The append-only log, externally
  anchored from 22 Jul, is the primary evidence that criteria predate data.
- **Analyst-blinding declaration.** In preparing this registration text, only pins,
  phase events, corrections, rulings, anchor metadata and schema definitions were read
  from the log. Gate-outcome data (notification tap and dismissal records, and corona
  open counts) were not queried. No outcome value informed any wording in this
  document.

## Evidence integrity (tamper-evidence)

The event log is append-only by design; corrections are corrective events, never edits.
A nightly job computes a deterministic rolling hash chain over the log, stores it,
commits the head to a public repository (`https://github.com/AlexAlamri/atlas-anchors`),
and stamps it with OpenTimestamps. The
consensus hashing rule is frozen at version 1 and is immutable from anchor 1 onward; any
future change ships as a parallel version, so every past head remains verifiable by
anyone holding the algorithm. Each run recomputes the whole chain from genesis as a
self-check and flags any divergence. First-anchor semantics: everything present in the
log at the first anchor, including the Gate 1 pin and the window anchoring, gains
existed-by-that-date attestation from an independent mechanism.

**Attestation is asynchronous, and the public series may lag.** A timestamp proof is
first calendar-pending and is upgraded to a blockchain attestation over the following
hours to days, so the most recent anchors in the public series are expected to be
pending at any given moment; a verifier checking on a given day will see a tail of
unconfirmed proofs, and this is normal rather than a fault. Publication of an anchor to
the public repository is likewise a separate step from its computation, so the public
series may trail the internal chain by up to a day. Any lapse in publication is
disclosed as a dated gap in the public series and does not retroactively affect anchors
already attested.

**Inclusion proofs, and their limits.** A single event is proven included by three
things: its canonical byte string, the rowhash vector of the batch containing it, and
the public anchor series. Event bodies never leave the database; only hashes are
published. Two limitations are disclosed. First, row hashes in version 1 are
**unsalted**, so releasing a batch's rowhash vector permits a third party to confirm a
*guessed* plaintext for a low-entropy sealed event in that batch. Salting was considered
and is not present in the frozen algorithm; it cannot be retrofitted without a parallel
chain. Second, redaction is not performed in place: a redaction is itself an event, and
the resulting divergence in the chain is treated as intended evidence and disclosed as a
dated epoch break naming the sequence number at which it occurs.

## Deviation policy and deviations to date

Any deviation from this protocol is recorded as a dated, append-only corrective event
stating what deviated and why, and is reported. Corrective events never edit the record
they correct; the original row remains in the log unaltered and the correction sits
beside it. The anchor chain covers corrective events like all others.

**Two deviations have occurred, both before this registration, both disclosed here.**

*Deviation 1. false liveness claim on a phase event (24 Jul 2026).* A phase event of
23 Jul declared tap and dismissal measurement live from that timestamp. It was not: an
access-control layer in front of the production origin caused service-worker
registration to fail, and the failure was masked because ordinary subresource fetches
followed the redirect while script fetches did not. Measurement start was re-anchored to
the first server-verified active registration, 24 Jul 2026 09:32:26 UTC. No event was
misclassified, because zero pushes were dispatched in the interval. Remediation: the
standing invariant and diagnostic-surface requirement recorded under Measures above.

*Deviation 2. phase rows written after the change (25 Jul 2026).* The phase rows for
the digest lane and for the urgent-push population change were written approximately
13.5 hours *after* those changes took effect, and both asserted a date that contradicted
their own timestamps. Phase discipline requires them to land before or with the change.
The breach was detected, disclosed and corrected the same evening; the erroneous rows
were left unedited, per the append-only rule. No gate, threshold or window was amended
in response, because the affected ruling never depended on the phase row's timing, only on the
change being documented. Remediation: from 26 Jul every phase event is written before
deployment with its timestamp read from the database at write time rather than inferred
from working context, and each subsequent phase row states this explicitly.

Both deviations are recorded in the anchored log and are available verbatim under the
release terms below.

## Ethics

No institutional ethics review was sought, and the position taken here is that none is
required. The reasoning is set out rather than asserted, so that a reader can judge it.

The study is self-experimentation. The sole participant is the author; the data are the
author's own tool-usage telemetry; no other person is observed, recruited, measured, or
reported on. No patients are involved, and no NHS patients, staff-as-participants,
tissue, records, or premises are used, so no NHS Research Ethics Committee route
applies. The study has no institutional sponsor and uses no institutional supervision,
funding, facilities, or employer resources, so no university or employer review body
holds jurisdiction over it either. The risks fall on the author alone and are
informational rather than physical, arising from the decision to publish data
describing the author's own behaviour.

Identifiable third-party and clinical-adjacent content is excluded from the study
dataset by the standing two-tier content rule described under Data availability. The
measured variables are interaction telemetry only: counts and timestamps of opens,
pushes, taps, and dismissals.

If a journal or other venue requires a formal determination or waiver as a condition of
publication, one will be sought at that point and the outcome appended to this
registration.

## Conflicts of interest and AI disclosure

The author is simultaneously the system's builder, the study participant, the analyst,
and the beneficiary of both the tool and any publication. This dual role is inherent to
autobiographical design and personal science and is declared rather than disguised.

An AI system (Anthropic's Claude) is a substantial collaborator in system design,
implementation, and analysis tooling. Per ICMJE and COPE guidance, the AI is not an
author and the human author is fully accountable. Distinctively, the system's own
provenance discipline makes the AI contribution auditable: every log event carries a
source tag distinguishing human, AI and automated origin, so the division of
contribution is queryable from the primary data.

For manuscripts arising from this study, a pre-committed authorship protocol governs AI
assistance: first-person, interpretive, and reflexive sections are authored without
generative assistance; AI-assisted drafting is confined to structural, methods, and
background scaffolding, each paragraph of which is rewritten by the author before
inclusion; every AI-surfaced citation is independently verified at source before use;
and manuscripts are version-controlled from first draft, so the drafting history is
available as authorship provenance. The protocol was adopted on 22 Jul 2026 and its
adoption event is covered by the first external anchor. A public extract of the
protocol is attached to this registration. The extract omits one category of content:
personal health information concerning the sole participant, withheld under the same
confidentiality standard that would apply to any participant and consistent with this
study's standing exclusion of clinical and clinical-adjacent material. The extract is
therefore a different file from the internal working document, by design: the digest
recorded in the anchored log is that of the working document, and a reader hashing the
attachment should expect it not to match.

## Data availability

The log is written under a standing two-tier content discipline, registered here as a
commitment because it is what makes selective verbatim release both possible and safe.

The **evidential tier** (gate pins, phase events, corrections and deviations, and
protocol-defining decisions) is written to be daylight-safe at the moment of creation:
no third-party names, no patient-identifiable or patient-adjacent clinical detail, no
commercially confidential specifics, no credentials. These events **will be released
verbatim, with hash-chain inclusion proofs, on reasonable request**, subject to the
inclusion-proof limitation disclosed above. Verbatim release is necessary because hash
verification requires exact bytes.

The **operational tier** (clinical coordination, venture strategy, and soft working
detail) is firewalled. Operational bodies **will not be quoted or paraphrased into any
manuscript, public artefact, or verification excerpt**, and are covered by the anchor
chain in hash form only. Redacted excerpts supporting specific analyses may be provided
on request, with the caveat that redacted text supports reading but not hash
verification.

Publicly available now: the full anchor chain, chain heads and OpenTimestamps proofs.
Publicly available at manuscript submission: aggregate telemetry, gate computations, and
analysis code. Development source and internal governance artefacts are held privately;
the public evidence repository carries the anchor chain, deliberate releases, and
nothing else. Any private artefact requiring existed-by attestation is anchored by
recording its cryptographic digest in the log, so the chain proves the file existed at
that time without the file crossing to public.

One bounded exception to the no-activity-information rule is deliberate and is stated
here because it is load-bearing for this registration's central claim. The public
repository documents, in prose, the gap between the log's origin and the first external
anchor: it names the date of the earliest event in the log, and the identifiers of the
protocol-defining events that predate anchor 1. These are identifiers and dates, never
contents or titles. The disclosure is required rather than incidental: without it, a
third party cannot assess how much of the log predates independent attestation, which is
precisely the limitation this registration asks to be judged on.

## Study timeline

- 21 Jul – 3 Aug 2026: corona gate window (Gate 1; decision 3 Aug).
- 24 Jul – 18 Aug 2026: loop gate measured window (Gate 2; decision 18 Aug, with the one
  pre-committed 14-day extension rule as specified).
- Through 2026: continued telemetry accrual under the same phase discipline. Manuscript
  preparation will proceed under a results-blind discipline: the introduction, methods,
  and analysis sections **will be drafted and their digests recorded in the anchored log
  before gate adjudication**, with pre-written discussion stubs for both PASS and FAIL
  outcomes; results sections are written only after the relevant window closes.
- 2027, forward reference only: a within-person micro-randomised trial on the digest
  decision point is planned as a separately registered protocol; nothing in this
  registration governs it, and randomisation remains off throughout the present study
  (send probability fixed at 1.0, logged per decision point).

## Key references

All references verified at source before use, per the pre-committed authorship protocol.

Epstein, Ping, Fogarty and Munson (2015). A Lived Informatics Model of Personal
Informatics. UbiComp '15, 731-742.
[doi:10.1145/2750858.2804250]{.doi}

Epstein, Caraway, Johnston, Ping, Fogarty and Munson (2016). Beyond Abandonment to Next
Steps: Understanding and Designing for Life after Personal Informatics Tool Use.
CHI '16, 1109-1113.
[doi:10.1145/2858036.2858045]{.doi}

Neustaedter and Sengers (2012). Autobiographical Design in HCI Research: Designing and
Learning through Use-It-Yourself. DIS '12, 514-523.
[doi:10.1145/2317956.2318034]{.doi}

Perski, Blandford, West and Michie (2017). Conceptualising engagement with digital
behaviour change interventions: a systematic review using principles from critical
interpretive synthesis. Translational Behavioral Medicine 7(2), 254-267.
[doi:10.1007/s13142-016-0453-1]{.doi}

Wolf and De Groot (2020). A Conceptual Framework for Personal Science. Frontiers in
Computer Science 2:21.
[doi:10.3389/fcomp.2020.00021.]{.doi} Cited for the self-directed
research framing and its stated distinction from n-of-1 trials in medicine; that paper
defines personal science around personal health questions, and this study poses no
health question, so the framing rather than the topic is what is drawn on.

Vohra, Shamseer, Sampson, Bukutu, Schmid, Tate, Nikles, Zucker, Kravitz, Guyatt, Altman
and Moher, CENT Group (2015). CONSORT extension for reporting N-of-1 trials (CENT) 2015
Statement. BMJ 350:h1738.
[doi:10.1136/bmj.h1738.]{.doi} Cited to locate this study relative to
the reporting-guideline landscape for single-patient designs, not as a guideline being
followed: CENT governs randomised multiple-crossover N-of-1 trials, and this study is
observational with no manipulation.

Klasnja, Hekler, Shiffman, Boruvka, Almirall, Tewari and Murphy (2015). Microrandomized
trials: An experimental design for developing just-in-time adaptive interventions.
Health Psychology 34(Suppl), 1220-1228.
[doi:10.1037/hea0000305.]{.doi} Cited as the design
basis for the separately registered 2027 study, not for the present one.

---