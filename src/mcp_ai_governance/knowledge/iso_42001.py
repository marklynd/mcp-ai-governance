"""ISO/IEC 42001:2023 - Artificial Intelligence Management System (AIMS).

Source: ISO/IEC 42001:2023, *Information technology - Artificial intelligence -
Management system*.

Structure encoded here:
    * Management-system clauses 4 to 10 (the auditable "shall" clauses), which
      follow the ISO harmonised structure shared with ISO/IEC 27001 and
      ISO 9001.
    * The Annex A control objectives and controls, grouped A.2 to A.10.

Accuracy notes (read before relying on this for an audit):
    * ISO standards are copyrighted and not freely redistributable, so no
      clause text is reproduced here. Clause and control **numbers** and
      **short titles** are used, which is standard practice for crosswalks.
    * Titles are condensed paraphrases written for this project.
    * Clause numbering below reflects the published structure. Clause 10
      ordering (10.1 continual improvement, 10.2 nonconformity and corrective
      action) follows the 2023 edition; some earlier ISO management-system
      standards use the reverse order. Verify against your copy of the
      standard before quoting it to an auditor.
"""

from __future__ import annotations

from typing import Final

from .base import Control, Framework, assert_unique_ids

FRAMEWORK_KEY: Final[str] = "iso_42001"

_CITE = "ISO/IEC 42001:2023"


def _c(
    control_id: str,
    title: str,
    group: str,
    themes: tuple[str, ...],
    signals: tuple[str, ...] = (),
) -> Control:
    return Control(
        id=control_id,
        title=title,
        framework=FRAMEWORK_KEY,
        group=group,
        themes=themes,
        signals=signals,
        citation=f"{_CITE}, {control_id}",
    )


_CLAUSES = (
    _c(
        "4.1",
        "Understanding the organisation and its context, including its role as AI provider, producer or user.",
        "Clause 4: Context of the organisation",
        ("purpose_scope", "risk_assessment"),
        ("organisational context", "organizational context", "internal and external issues"),
    ),
    _c(
        "4.2",
        "Understanding the needs and expectations of interested parties.",
        "Clause 4: Context of the organisation",
        ("feedback", "purpose_scope"),
        ("interested parties", "stakeholder requirements"),
    ),
    _c(
        "4.3",
        "Determining the scope of the AI management system.",
        "Clause 4: Context of the organisation",
        ("purpose_scope", "documentation"),
        ("scope statement", "scope of the aims", "management system scope"),
    ),
    _c(
        "4.4",
        "Establishing, implementing, maintaining and continually improving the AI management system.",
        "Clause 4: Context of the organisation",
        ("policy", "conformity"),
        ("management system", "aims"),
    ),
    _c(
        "5.1",
        "Leadership and commitment: top management demonstrates ownership of the AI management system.",
        "Clause 5: Leadership",
        ("accountability",),
        ("top management", "leadership commitment", "board", "ceo", "chief executive"),
    ),
    _c(
        "5.2",
        "Establishing a documented AI policy appropriate to the organisation's purpose.",
        "Clause 5: Leadership",
        ("policy", "documentation"),
        ("ai policy",),
    ),
    _c(
        "5.3",
        "Assigning and communicating organisational roles, responsibilities and authorities.",
        "Clause 5: Leadership",
        ("accountability",),
        ("assign authority", "communicate responsibilities"),
    ),
    _c(
        "6.1.2",
        "AI risk assessment: defining and applying a repeatable process to identify and analyse AI risks.",
        "Clause 6: Planning",
        ("risk_assessment",),
        (
            "risk criteria",
            "repeatable risk assessment",
            "risk tolerance",
            "risk appetite",
            "identify and analyse risks",
        ),
    ),
    _c(
        "6.1.3",
        "AI risk treatment: selecting controls, producing a Statement of Applicability and a treatment plan.",
        "Clause 6: Planning",
        ("risk_assessment", "documentation"),
        ("statement of applicability", "soa", "risk treatment plan"),
    ),
    _c(
        "6.1.4",
        "AI system impact assessment: assessing consequences for individuals, groups and society.",
        "Clause 6: Planning",
        ("impact_assessment",),
        ("ai system impact assessment",),
    ),
    _c(
        "6.2",
        "Setting measurable AI objectives and planning how to achieve them.",
        "Clause 6: Planning",
        ("purpose_scope", "conformity"),
        ("measurable objectives", "objective setting"),
    ),
    _c(
        "6.3",
        "Planning changes to the AI management system in a controlled way.",
        "Clause 6: Planning",
        ("lifecycle", "conformity"),
        ("planned change", "change to the management system"),
    ),
    _c(
        "7.1",
        "Determining and providing the resources needed for the AI management system.",
        "Clause 7: Support",
        ("accountability",),
        ("resource provision", "budget and staffing"),
    ),
    _c(
        "7.2",
        "Ensuring the competence of people whose work affects AI performance.",
        "Clause 7: Support",
        ("training_awareness",),
        ("competence records", "role competence"),
    ),
    _c(
        "7.3",
        "Ensuring personnel are aware of the AI policy and their contribution to it.",
        "Clause 7: Support",
        ("training_awareness",),
    ),
    _c(
        "7.4",
        "Determining internal and external communications relevant to the AI management system.",
        "Clause 7: Support",
        ("transparency", "feedback"),
        ("communication plan",),
    ),
    _c(
        "7.5",
        "Creating and controlling documented information, including version and access control.",
        "Clause 7: Support",
        ("documentation", "logging"),
        ("document control", "version control", "records retention"),
    ),
    _c(
        "8.1",
        "Operational planning and control: implementing the processes needed to meet AI requirements.",
        "Clause 8: Operation",
        ("lifecycle", "policy"),
        ("operational control", "process implementation"),
    ),
    _c(
        "8.2",
        "Performing AI risk assessments at planned intervals and when significant changes occur.",
        "Clause 8: Operation",
        ("risk_assessment", "monitoring"),
    ),
    _c(
        "8.3",
        "Implementing the AI risk treatment plan and retaining the results.",
        "Clause 8: Operation",
        ("risk_assessment", "documentation"),
    ),
    _c(
        "8.4",
        "Performing AI system impact assessments at planned intervals and retaining the results.",
        "Clause 8: Operation",
        ("impact_assessment", "documentation"),
    ),
    _c(
        "9.1",
        "Monitoring, measurement, analysis and evaluation of AI management system performance.",
        "Clause 9: Performance evaluation",
        ("monitoring", "testing_evaluation"),
        ("performance evaluation", "kpi"),
    ),
    _c(
        "9.2",
        "Conducting internal audits at planned intervals.",
        "Clause 9: Performance evaluation",
        ("conformity",),
        ("internal audit programme", "internal audit program", "audit schedule"),
    ),
    _c(
        "9.3",
        "Management review of the AI management system by top management.",
        "Clause 9: Performance evaluation",
        ("conformity", "accountability"),
        ("management review",),
    ),
    _c(
        "10.1",
        "Continual improvement of the suitability, adequacy and effectiveness of the AI management system.",
        "Clause 10: Improvement",
        ("conformity", "lifecycle"),
    ),
    _c(
        "10.2",
        "Managing nonconformities and corrective actions, including root cause analysis.",
        "Clause 10: Improvement",
        ("conformity", "incident_response"),
        ("nonconformity", "corrective action", "capa"),
    ),
)

_ANNEX_A = (
    _c(
        "A.2.2",
        "AI policy: a documented policy for the development or use of AI systems.",
        "Annex A.2: Policies related to AI",
        ("policy",),
        ("ai policy",),
    ),
    _c(
        "A.2.3",
        "Alignment with other organisational policies such as security, privacy and quality.",
        "Annex A.2: Policies related to AI",
        ("policy",),
        ("policy alignment", "existing policies"),
    ),
    _c(
        "A.2.4",
        "Review of the AI policy at planned intervals.",
        "Annex A.2: Policies related to AI",
        ("policy", "conformity"),
        ("policy review",),
    ),
    _c(
        "A.3.2",
        "AI roles and responsibilities are defined and allocated.",
        "Annex A.3: Internal organisation",
        ("accountability",),
    ),
    _c(
        "A.3.3",
        "Reporting of concerns: a route for people to raise concerns about AI systems.",
        "Annex A.3: Internal organisation",
        ("feedback", "incident_response"),
        ("raise a concern", "whistleblow", "speak up channel"),
    ),
    _c(
        "A.4.2",
        "Resource documentation: recording the resources used for AI systems.",
        "Annex A.4: Resources for AI systems",
        ("documentation", "inventory"),
    ),
    _c(
        "A.4.3",
        "Data resources: documenting the data used by AI systems.",
        "Annex A.4: Resources for AI systems",
        ("data_governance", "documentation"),
    ),
    _c(
        "A.4.4",
        "Tooling resources: documenting the tools used across the AI lifecycle.",
        "Annex A.4: Resources for AI systems",
        ("documentation", "lifecycle"),
        ("tooling", "toolchain", "frameworks used"),
    ),
    _c(
        "A.4.5",
        "System and computing resources: documenting the compute and infrastructure used.",
        "Annex A.4: Resources for AI systems",
        ("documentation", "resilience"),
        ("compute resources", "infrastructure capacity", "gpu"),
    ),
    _c(
        "A.4.6",
        "Human resources: documenting the people and competences applied to AI systems.",
        "Annex A.4: Resources for AI systems",
        ("training_awareness", "accountability"),
    ),
    _c(
        "A.5.2",
        "A defined process for assessing the impacts of AI systems on individuals and society.",
        "Annex A.5: Assessing impacts of AI systems",
        ("impact_assessment",),
    ),
    _c(
        "A.5.3",
        "Documentation of AI system impact assessments.",
        "Annex A.5: Assessing impacts of AI systems",
        ("impact_assessment", "documentation"),
    ),
    _c(
        "A.5.4",
        "Assessing AI system impacts on individuals or groups of individuals.",
        "Annex A.5: Assessing impacts of AI systems",
        ("impact_assessment", "bias_fairness"),
    ),
    _c(
        "A.5.5",
        "Assessing societal impacts of AI systems.",
        "Annex A.5: Assessing impacts of AI systems",
        ("impact_assessment",),
        ("societal impact",),
    ),
    _c(
        "A.6.1.2",
        "Objectives and management guidance for responsible AI system development.",
        "Annex A.6: AI system life cycle",
        ("lifecycle", "policy"),
        ("development guidance", "responsible development"),
    ),
    _c(
        "A.6.2.2",
        "AI system requirements and specification are defined and documented.",
        "Annex A.6: AI system life cycle",
        ("purpose_scope", "documentation"),
    ),
    _c(
        "A.6.2.3",
        "Documentation of AI system design and development.",
        "Annex A.6: AI system life cycle",
        ("documentation", "lifecycle"),
        ("design documentation", "architecture decision"),
    ),
    _c(
        "A.6.2.4",
        "AI system verification and validation, including acceptance criteria and test results.",
        "Annex A.6: AI system life cycle",
        ("testing_evaluation",),
        ("verification and validation", "acceptance testing"),
    ),
    _c(
        "A.6.2.5",
        "AI system deployment: controlled release into the operating environment.",
        "Annex A.6: AI system life cycle",
        ("lifecycle",),
        ("deployment plan", "release gate", "controlled rollout"),
    ),
    _c(
        "A.6.2.6",
        "AI system operation and monitoring in production, including operator oversight.",
        "Annex A.6: AI system life cycle",
        ("monitoring", "human_oversight"),
    ),
    _c(
        "A.6.2.7",
        "AI system technical documentation for interested parties.",
        "Annex A.6: AI system life cycle",
        ("documentation", "transparency"),
        ("technical documentation",),
    ),
    _c(
        "A.6.2.8",
        "Recording of event logs generated by AI systems.",
        "Annex A.6: AI system life cycle",
        ("logging",),
        ("event log", "log retention"),
    ),
    _c(
        "A.7.2",
        "Data for development and enhancement of AI systems is managed.",
        "Annex A.7: Data for AI systems",
        ("data_governance",),
    ),
    _c(
        "A.7.3",
        "Acquisition of data: how data is obtained, with rights and consent established.",
        "Annex A.7: Data for AI systems",
        ("data_governance", "privacy", "third_party"),
        (
            "data acquisition",
            "scraping",
            "licensed data",
            "data rights",
            "copyright",
            "lawful basis",
            "training content",
        ),
    ),
    _c(
        "A.7.4",
        "Quality of data for AI systems is defined and maintained.",
        "Annex A.7: Data for AI systems",
        ("data_governance",),
        ("data quality", "completeness", "accuracy of data"),
    ),
    _c(
        "A.7.5",
        "Data provenance is recorded and traceable.",
        "Annex A.7: Data for AI systems",
        ("data_governance", "logging"),
        ("provenance", "data lineage", "chain of custody"),
    ),
    _c(
        "A.7.6",
        "Data preparation: documented transformation, cleaning and feature engineering.",
        "Annex A.7: Data for AI systems",
        ("data_governance",),
        ("data preparation", "preprocessing", "feature engineering"),
    ),
    _c(
        "A.8.2",
        "System documentation and information for users of the AI system.",
        "Annex A.8: Information for interested parties",
        ("transparency", "documentation"),
        (
            "user documentation",
            "instructions for use",
            "information for users",
            "inform users",
            "tell users",
            "disclosure to users",
        ),
    ),
    _c(
        "A.8.3",
        "External reporting: a channel for external parties to report issues.",
        "Annex A.8: Information for interested parties",
        ("feedback", "transparency"),
        ("external reporting", "report an issue"),
    ),
    _c(
        "A.8.4",
        "Communication of incidents to relevant interested parties.",
        "Annex A.8: Information for interested parties",
        ("incident_response", "transparency"),
    ),
    _c(
        "A.8.5",
        "Information for interested parties about the organisation's AI obligations.",
        "Annex A.8: Information for interested parties",
        ("transparency",),
    ),
    _c(
        "A.9.2",
        "Processes for the responsible use of AI systems, including human oversight of outputs.",
        "Annex A.9: Use of AI systems",
        ("policy", "purpose_scope", "human_oversight"),
        ("responsible use", "acceptable use", "deactivate", "disengage", "stop the system"),
    ),
    _c(
        "A.9.3",
        "Objectives for the responsible use of AI systems are defined.",
        "Annex A.9: Use of AI systems",
        ("purpose_scope", "policy"),
    ),
    _c(
        "A.9.4",
        "Intended use of the AI system is defined and adhered to.",
        "Annex A.9: Use of AI systems",
        ("purpose_scope",),
        ("intended use", "intended purpose", "off label use", "out of scope"),
    ),
    _c(
        "A.10.2",
        "Allocating responsibilities within the AI value chain.",
        "Annex A.10: Third-party and customer relationships",
        ("third_party", "accountability"),
        ("value chain", "shared responsibility"),
    ),
    _c(
        "A.10.3",
        "Suppliers: ensuring supplier-provided AI services meet the organisation's requirements.",
        "Annex A.10: Third-party and customer relationships",
        ("third_party",),
        ("supplier requirements", "vendor assessment"),
    ),
    _c(
        "A.10.4",
        "Customers: meeting customer expectations and obligations for AI systems supplied to them.",
        "Annex A.10: Third-party and customer relationships",
        ("third_party", "transparency"),
        ("customer obligations", "downstream customer"),
    ),
)

CONTROLS: Final[tuple[Control, ...]] = assert_unique_ids(_CLAUSES + _ANNEX_A)

FRAMEWORK: Final[Framework] = Framework(
    key=FRAMEWORK_KEY,
    name="ISO/IEC 42001 Artificial Intelligence Management System",
    version="2023",
    source="ISO/IEC 42001:2023 (purchase required; https://www.iso.org/standard/81230.html)",
    coverage=(
        "Auditable clauses 4-10 plus the Annex A control set (A.2 to A.10). "
        "Numbers and short titles only; no ISO text is reproduced. Titles are "
        "paraphrases written for this project."
    ),
    controls=CONTROLS,
)
