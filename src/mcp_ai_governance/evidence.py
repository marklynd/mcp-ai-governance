"""Evidence checklists: what an auditor will actually ask for.

Evidence is assembled from two layers:

* a **theme layer** that says what any control on that theme needs (a policy
  theme needs an approved document with a version history and an owner), and
* a **control override layer** for controls where the expected evidence is
  specific enough to be worth stating exactly, for example EU AI Act Art. 12
  logging or Art. 43 conformity assessment.

Each item is typed by what it is: a ``document``, a ``record`` produced by the
control operating, a ``system`` artefact, or an ``interview``. That distinction
matters because the common audit failure is having every document and no
records - a policy that exists but has never produced evidence that anyone
followed it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from .knowledge import Control, control_ids, find_control

EVIDENCE_KINDS: Final[tuple[str, ...]] = ("document", "record", "system", "interview")


@dataclass(frozen=True)
class EvidenceItem:
    """One artefact an auditor would request.

    Attributes:
        kind: One of ``document``, ``record``, ``system`` or ``interview``.
        item: What to produce.
        why: What the auditor is testing by asking for it.
    """

    kind: str
    item: str
    why: str

    def __post_init__(self) -> None:
        """Validate the evidence kind on construction."""
        if self.kind not in EVIDENCE_KINDS:
            raise ValueError(
                f"Unknown evidence kind {self.kind!r}; expected one of "
                f"{', '.join(EVIDENCE_KINDS)}"
            )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable representation."""
        return {"kind": self.kind, "item": self.item, "why": self.why}


def _e(kind: str, item: str, why: str) -> EvidenceItem:
    return EvidenceItem(kind=kind, item=item, why=why)


THEME_EVIDENCE: Final[dict[str, tuple[EvidenceItem, ...]]] = {
    "accountability": (
        _e("document", "Org chart or RACI showing who is accountable for AI risk decisions", "That accountability is assigned to a person, not a committee with no owner"),
        _e("record", "Minutes of the governance forum showing AI decisions being taken", "That the accountability is exercised, not just documented"),
        _e("interview", "The named accountable executive, asked to describe their AI risk decisions in the last quarter", "That the named owner knows they own it"),
    ),
    "policy": (
        _e("document", "The approved policy, with version number, approval date and approver", "That the policy is real, current and formally approved"),
        _e("record", "Distribution or attestation records showing staff have read it", "That the policy reached the people it binds"),
        _e("record", "Evidence of the last scheduled policy review", "That the review cycle in the policy is actually run"),
    ),
    "inventory": (
        _e("system", "Export of the AI system inventory with owner, purpose, risk tier and status per entry", "That the inventory exists and is populated"),
        _e("record", "Evidence of the last reconciliation between the inventory and an independent source such as spend or network data", "That the inventory is complete, not just the systems people volunteered"),
        _e("document", "The procedure for adding a system to the inventory before it goes live", "That new systems cannot bypass the register"),
    ),
    "risk_assessment": (
        _e("document", "The risk assessment methodology, including scoring criteria and risk tolerance thresholds", "That assessments are repeatable rather than improvised"),
        _e("record", "Completed risk assessments for a sample of systems, with dates and assessors", "That the method is applied in practice"),
        _e("record", "The risk register showing treatment decisions and residual risk acceptance sign-off", "That identified risk is dispositioned, not just logged"),
    ),
    "impact_assessment": (
        _e("document", "The impact assessment template, including which groups are considered", "That impact is assessed systematically"),
        _e("record", "A completed impact assessment for a high-exposure system, naming affected groups and mitigations", "That impacts on people are considered, not just on the business"),
        _e("record", "Evidence that assessment findings changed the design or the deployment decision", "That the assessment has teeth"),
    ),
    "data_governance": (
        _e("document", "Data quality criteria and acceptance thresholds for AI training and retrieval data", "That quality is defined before it is measured"),
        _e("record", "Lineage or provenance records for a sampled dataset, back to its source", "That the origin of training data can be established"),
        _e("record", "Data quality test results from the most recent pipeline run", "That the thresholds are enforced"),
        _e("document", "Licences, contracts or consent records establishing the right to use the data", "That the data is lawfully usable for this purpose"),
    ),
    "privacy": (
        _e("document", "Record of processing activities covering the AI system", "That the processing is registered"),
        _e("document", "Lawful basis assessment and, where required, a DPIA", "That the legal basis was established before processing"),
        _e("system", "Evidence of privacy controls in effect, such as minimisation, retention limits or pseudonymisation", "That the controls are implemented, not just planned"),
    ),
    "bias_fairness": (
        _e("document", "Definition of the fairness metrics used and why they were chosen for this context", "That fairness is defined before it is measured"),
        _e("record", "Subgroup performance results from the most recent evaluation, with the population breakdown", "That performance is measured across groups, not just in aggregate"),
        _e("record", "Remediation decisions taken where disparities were found", "That findings lead to action"),
    ),
    "transparency": (
        _e("document", "User-facing disclosure text, and the model or system card", "That users are told what they are dealing with"),
        _e("system", "A screenshot or recording of the disclosure as it appears in the live product", "That the disclosure ships, rather than living in a document"),
        _e("document", "Statement of known limitations and out-of-scope uses provided to deployers", "That limitations are communicated, not discovered"),
    ),
    "documentation": (
        _e("document", "The technical documentation set, with version history", "That documentation exists and is maintained"),
        _e("record", "Evidence that documentation was updated at the last significant system change", "That documentation tracks the system rather than the launch"),
    ),
    "human_oversight": (
        _e("document", "The oversight procedure: who reviews what, at what point, with what authority to override", "That oversight is designed, not assumed"),
        _e("record", "A sample of recorded human decisions, including at least one rejection or override", "That the reviewer can and does say no; all-approve logs indicate rubber-stamping"),
        _e("system", "The interface the reviewer uses, showing the information available at decision time", "That the reviewer has enough context to exercise judgement"),
        _e("interview", "A reviewer, asked what they would do if they disagreed with the model", "That oversight is meaningful rather than nominal"),
    ),
    "testing_evaluation": (
        _e("document", "The test plan, including datasets, metrics and pass or fail acceptance criteria", "That criteria were set before results were known"),
        _e("record", "Results of the most recent evaluation run, tied to the released version", "That the released version is the one that was tested"),
        _e("record", "Evidence of a release blocked or rolled back on evaluation failure", "That the gate is enforcing, not advisory"),
        _e("system", "The evaluation harness and its execution history in CI", "That evaluation is repeatable and automated"),
    ),
    "monitoring": (
        _e("document", "The monitoring plan, listing metrics, thresholds and the on-call owner", "That monitoring is designed against defined thresholds"),
        _e("system", "Live dashboards and configured alert rules", "That the monitoring is running"),
        _e("record", "Alert history and the response taken to a sampled alert", "That alerts are acted on rather than muted"),
    ),
    "logging": (
        _e("document", "The logging specification: what is captured, retention period and access controls", "That logging scope and retention are deliberate"),
        _e("record", "A log extract for a sampled transaction, showing input, output, model version and timestamp", "That an individual decision can be reconstructed"),
        _e("system", "Evidence of tamper resistance, such as append-only storage or write-once retention", "That the record cannot be quietly rewritten"),
    ),
    "security": (
        _e("document", "Threat model for the AI system, covering prompt injection, data exfiltration and model abuse", "That AI-specific threats were considered, not just generic application threats"),
        _e("record", "Most recent penetration test or red team report, with remediation status", "That the system was tested by someone trying to break it"),
        _e("system", "Access control configuration for models, prompts, keys and training data", "That least privilege is implemented"),
    ),
    "resilience": (
        _e("document", "Documented fallback behaviour for model unavailability or degraded output", "That failure modes have a designed response"),
        _e("record", "Results of the most recent failover or degradation test", "That the fallback has been exercised"),
    ),
    "incident_response": (
        _e("document", "AI incident response runbook, including severity definitions and notification thresholds", "That AI incidents have a defined path"),
        _e("record", "Post-incident reviews for AI incidents in the period, or evidence of an exercise if there were none", "That the process has been run at least once"),
        _e("record", "Evidence of notification to affected parties or authorities where thresholds were met", "That reporting obligations are met on time"),
    ),
    "third_party": (
        _e("document", "Vendor assessment for the AI supplier, covering security, data use and model change practices", "That the supplier was assessed before onboarding"),
        _e("document", "Contract clauses covering model changes, data use, audit rights and exit", "That obligations flow down contractually"),
        _e("record", "Evidence of ongoing supplier monitoring, such as reviewing their published model updates", "That assessment is continuous rather than one-off"),
    ),
    "training_awareness": (
        _e("document", "The training curriculum, mapped to roles", "That training is role-appropriate rather than generic"),
        _e("record", "Completion records with dates and coverage percentage by role", "That the workforce actually completed it"),
        _e("record", "Assessment results or knowledge checks", "That completion means comprehension"),
    ),
    "lifecycle": (
        _e("document", "The lifecycle procedure covering development, promotion, change and decommissioning", "That the path to production is defined"),
        _e("record", "Change records for a sampled production release, including approval", "That changes follow the defined path"),
        _e("record", "Evidence of a completed decommissioning, including data and model disposal", "That retirement is handled, which is the most commonly missing stage"),
    ),
    "feedback": (
        _e("system", "The user-facing channel for reporting problems or appealing an outcome", "That the channel exists and is reachable"),
        _e("record", "A sample of submissions with response times and outcomes", "That submissions are triaged rather than collected"),
        _e("record", "Evidence that feedback changed the system or the process", "That the loop closes"),
    ),
    "conformity": (
        _e("document", "Audit plan and scope covering AI systems", "That AI is inside the assurance scope"),
        _e("record", "Internal audit reports and findings for the period", "That the audit was performed"),
        _e("record", "Corrective action records with root cause and closure evidence", "That findings are closed, with cause addressed"),
    ),
    "purpose_scope": (
        _e("document", "Written statement of intended purpose, including explicitly out-of-scope uses", "That the boundary is defined"),
        _e("record", "Evidence of a use case being refused or re-scoped against that boundary", "That the boundary is enforced"),
    ),
}

#: Control-specific evidence that is more precise than the theme default.
CONTROL_OVERRIDES: Final[dict[str, tuple[EvidenceItem, ...]]] = {
    "Art. 12": (
        _e("system", "Demonstration that logging is automatic and cannot be disabled by the deployer", "Art. 12 requires the capability to be technically built in"),
        _e("document", "Log retention policy showing retention appropriate to the intended purpose and at least six months", "Art. 19 sets a minimum retention expectation for provider-held logs"),
    ),
    "Art. 14": (
        _e("system", "Demonstration of the stop function and of how a human interrupts the system", "Art. 14(4)(e) requires the ability to intervene or halt"),
        _e("document", "Evidence that automation bias was considered in the oversight design", "Art. 14(4)(b) names automation bias explicitly"),
    ),
    "Art. 43": (
        _e("document", "Conformity assessment report and the route chosen, internal control or notified body", "Art. 43 requires the correct procedure for the system type"),
        _e("document", "EU declaration of conformity and evidence of CE marking", "Art. 47 and Art. 48"),
        _e("record", "EU database registration confirmation", "Art. 49 requires registration before market placement"),
    ),
    "Art. 50": (
        _e("system", "The machine-readable marking applied to synthetic output, and a verification that it survives a normal export", "Art. 50(2) requires marking to be machine readable and effective"),
    ),
    "Art. 73": (
        _e("record", "Serious incident reports submitted to the market surveillance authority, with submission timestamps", "Art. 73 sets short reporting deadlines from the point of awareness"),
    ),
    "GOVERN 1.6": (
        _e("record", "Evidence that inventory resourcing is proportionate to risk priorities", "GOVERN 1.6 ties inventory effort to risk"),
    ),
    "MANAGE 2.4": (
        _e("record", "Evidence of a system actually being superseded, disengaged or deactivated, or a tested drill", "The control is only demonstrated by having used it"),
    ),
    "9.2": (
        _e("document", "Internal audit programme covering the whole AIMS across the audit cycle", "Clause 9.2 requires planned intervals and full coverage over time"),
        _e("record", "Auditor independence evidence for the AI management system audit", "Auditors must not audit their own work"),
    ),
    "6.1.3": (
        _e("document", "Statement of Applicability showing each Annex A control as applicable or excluded, with justification", "Clause 6.1.3 requires a documented SoA"),
    ),
}

#: Failure modes seen often enough to be worth flagging by theme.
COMMON_FAILURES: Final[dict[str, tuple[str, ...]]] = {
    "policy": (
        "The policy exists but has never been reviewed since approval.",
        "The policy covers employees but not contractors or third-party developers.",
    ),
    "inventory": (
        "The inventory only lists systems the AI team built, missing embedded vendor AI and departmental tools.",
        "There is no control preventing a system from going live before it is registered.",
    ),
    "human_oversight": (
        "Every recorded decision is an approval, which indicates rubber-stamping rather than review.",
        "The reviewer sees the model's recommendation but not the evidence behind it, so cannot meaningfully disagree.",
        "Review is technically possible but the throughput expectation makes it impossible in the time allowed.",
    ),
    "testing_evaluation": (
        "Acceptance criteria were written after results were known.",
        "The evaluation set overlaps the training data, so results are inflated.",
        "Evaluation runs on a version that is not the version deployed.",
    ),
    "logging": (
        "Logs capture the output but not the input or the model version, so a decision cannot be reconstructed.",
        "Retention is shorter than the period in which a challenge could arise.",
        "Anyone with production access can edit or delete log entries.",
    ),
    "monitoring": (
        "Dashboards exist but no threshold is configured to alert anyone.",
        "Alerts fire into a channel nobody owns.",
    ),
    "third_party": (
        "The assessment was done at onboarding and never repeated, despite the vendor shipping model updates continuously.",
        "The contract has no notice requirement for model changes.",
    ),
    "incident_response": (
        "The runbook covers outages but not model behaviour failures such as harmful or fabricated output.",
        "The process has never been exercised.",
    ),
    "data_governance": (
        "Lineage stops at the data warehouse rather than reaching the originating source.",
        "Quality thresholds are documented but not enforced in the pipeline.",
    ),
    "training_awareness": (
        "Completion is measured across all staff rather than the roles that operate AI systems.",
    ),
    "conformity": (
        "Findings are recorded but closed without root cause or evidence.",
    ),
}

DEFAULT_SAMPLING: Final[str] = (
    "Expect the auditor to sample rather than review everything: typically the "
    "most recent period plus one or two named systems chosen by them, not by "
    "you. Evidence that only exists for the system you nominated is a finding."
)


@dataclass(frozen=True)
class EvidenceChecklist:
    """The complete result of an ``evidence_checklist`` call."""

    control: Control
    items: tuple[EvidenceItem, ...]
    auditor_questions: tuple[str, ...]
    common_failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        by_kind: dict[str, list[str]] = {kind: [] for kind in EVIDENCE_KINDS}
        for item in self.items:
            by_kind[item.kind].append(item.item)
        return {
            "control_id": self.control.id,
            "framework": self.control.framework,
            "title": self.control.title,
            "group": self.control.group,
            "citation": self.control.citation,
            "themes": list(self.control.themes),
            "evidence": [item.to_dict() for item in self.items],
            "evidence_by_kind": {
                kind: values for kind, values in by_kind.items() if values
            },
            "auditor_questions": list(self.auditor_questions),
            "common_failures": list(self.common_failures),
            "sampling_guidance": DEFAULT_SAMPLING,
        }


_QUESTION_TEMPLATES: Final[tuple[str, ...]] = (
    "Show me the current version of this and tell me who approved it.",
    "Walk me through the last time this control operated. What did it produce?",
    "What would have happened if the answer had been no?",
    "Who is accountable if this control fails, and how would they find out?",
)


def evidence_checklist(control_id: str) -> EvidenceChecklist:
    """Return the evidence an auditor would request for a control.

    Args:
        control_id: A control identifier from any encoded framework. Matching
            tolerates case and punctuation, so ``"art 14"``, ``"Art. 14"`` and
            ``"Article 14"`` all resolve to the same article.

    Returns:
        An :class:`EvidenceChecklist`.

    Raises:
        TypeError: If ``control_id`` is not a string.
        ValueError: If it is empty or does not match an encoded control.
    """
    if not isinstance(control_id, str):
        raise TypeError("control_id must be a string")
    cleaned = control_id.strip()
    if not cleaned:
        raise ValueError("control_id must not be empty")

    control = find_control(cleaned)
    if control is None:
        available = control_ids()
        raise ValueError(
            f"Unknown control id {control_id!r}. "
            f"{len(available)} controls are encoded; examples: "
            + ", ".join(available[:3])
            + ", "
            + ", ".join(available[-3:])
            + ". Use the 'governance://controls' resource for the full list."
        )

    items: list[EvidenceItem] = []
    seen: set[str] = set()
    for theme in control.themes:
        for item in THEME_EVIDENCE.get(theme, ()):
            if item.item not in seen:
                seen.add(item.item)
                items.append(item)
    for item in CONTROL_OVERRIDES.get(control.id, ()):
        if item.item not in seen:
            seen.add(item.item)
            items.append(item)

    failures: list[str] = []
    for theme in control.themes:
        for failure in COMMON_FAILURES.get(theme, ()):
            if failure not in failures:
                failures.append(failure)

    return EvidenceChecklist(
        control=control,
        items=tuple(items),
        auditor_questions=_QUESTION_TEMPLATES,
        common_failures=tuple(failures),
    )
