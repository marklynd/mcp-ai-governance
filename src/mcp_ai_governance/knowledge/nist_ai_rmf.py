"""NIST AI Risk Management Framework 1.0 (AI RMF 1.0).

Source: NIST AI 100-1, *Artificial Intelligence Risk Management Framework
(AI RMF 1.0)*, January 2023, and the accompanying NIST AI RMF Playbook.

Structure encoded here:
    * Four core functions: GOVERN, MAP, MEASURE, MANAGE.
    * All 72 subcategories, using the published identifiers (GOVERN 1.1,
      MAP 2.3, MEASURE 2.11, MANAGE 4.3, and so on).

Accuracy note: the identifiers and the function/category structure are taken
from the published framework. The ``title`` strings are **condensed
paraphrases** written for this project so that the mapping output stays
readable; they are not verbatim quotations of NIST's subcategory text. Always
read the source document before relying on a mapping for an audit.
"""

from __future__ import annotations

from typing import Final

from .base import Control, Framework, assert_unique_ids

FRAMEWORK_KEY: Final[str] = "nist_ai_rmf"

_CITE = "NIST AI 100-1 (AI RMF 1.0), Jan 2023"


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


_GOVERN = (
    _c(
        "GOVERN 1.1",
        "Legal and regulatory requirements involving AI are understood, managed and documented.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("policy", "documentation", "risk_assessment"),
        ("legal requirement", "regulatory requirement", "compliance obligation", "applicable law"),
    ),
    _c(
        "GOVERN 1.2",
        "Trustworthy AI characteristics are integrated into organisational policies and practices.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("policy", "accountability"),
        ("trustworthy ai", "responsible ai principles", "ai principles"),
    ),
    _c(
        "GOVERN 1.3",
        "Processes determine the level of risk management effort based on organisational risk tolerance.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("risk_assessment", "policy"),
        ("proportionate controls", "risk based approach"),
    ),
    _c(
        "GOVERN 1.4",
        "The risk management process and its outcomes are established through transparent policies and controls.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("policy", "risk_assessment", "documentation"),
    ),
    _c(
        "GOVERN 1.5",
        "Ongoing monitoring and periodic review of the risk management process are planned, with defined roles and review frequency.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("monitoring", "accountability", "conformity"),
        ("periodic review", "review cadence", "annual review"),
    ),
    _c(
        "GOVERN 1.6",
        "Mechanisms are in place to inventory AI systems, resourced according to risk priorities.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("inventory",),
        ("inventory of ai systems", "ai use case register"),
    ),
    _c(
        "GOVERN 1.7",
        "Processes exist for safely decommissioning and phasing out AI systems.",
        "GOVERN 1: Policies, processes, procedures and practices",
        ("lifecycle",),
        ("decommission", "retire a model", "sunset a system", "end of life"),
    ),
    _c(
        "GOVERN 2.1",
        "Roles, responsibilities and lines of communication for AI risk are documented and clear.",
        "GOVERN 2: Accountability structures",
        ("accountability", "documentation"),
        ("lines of communication",),
    ),
    _c(
        "GOVERN 2.2",
        "Personnel and partners receive AI risk management training to perform their duties.",
        "GOVERN 2: Accountability structures",
        ("training_awareness", "accountability"),
        ("ai literacy", "risk management training"),
    ),
    _c(
        "GOVERN 2.3",
        "Executive leadership takes responsibility for decisions about AI development and deployment risk.",
        "GOVERN 2: Accountability structures",
        ("accountability",),
        (
            "executive leadership",
            "c suite ownership",
            "board",
            "ceo",
            "chief executive",
            "executive sign off",
            "leadership takes responsibility",
        ),
    ),
    _c(
        "GOVERN 3.1",
        "Decision-making about AI risk is informed by a demographically and disciplinarily diverse team.",
        "GOVERN 3: Workforce diversity and inclusion",
        ("accountability", "bias_fairness"),
        ("diverse team", "interdisciplinary", "cross functional review"),
    ),
    _c(
        "GOVERN 3.2",
        "Policies define roles and responsibilities for human-AI configurations and oversight of AI systems.",
        "GOVERN 3: Workforce diversity and inclusion",
        ("human_oversight", "policy", "accountability"),
        ("human ai configuration", "oversight roles"),
    ),
    _c(
        "GOVERN 4.1",
        "Policies foster a critical-thinking and safety-first mindset across the AI lifecycle.",
        "GOVERN 4: Organisational culture",
        ("policy", "training_awareness"),
        ("safety culture", "safety first", "psychological safety"),
    ),
    _c(
        "GOVERN 4.2",
        "Teams document the risks and potential impacts of the AI they build and communicate them broadly.",
        "GOVERN 4: Organisational culture",
        ("documentation", "impact_assessment"),
    ),
    _c(
        "GOVERN 4.3",
        "Practices enable AI testing, incident identification and information sharing.",
        "GOVERN 4: Organisational culture",
        ("testing_evaluation", "incident_response"),
        ("information sharing", "disclosure of incidents"),
    ),
    _c(
        "GOVERN 5.1",
        "Policies collect, prioritise and integrate feedback from people outside the building team.",
        "GOVERN 5: Engagement with AI actors",
        ("feedback",),
        ("external feedback", "public comment"),
    ),
    _c(
        "GOVERN 5.2",
        "Mechanisms let teams regularly fold adjudicated external feedback back into system design.",
        "GOVERN 5: Engagement with AI actors",
        ("feedback", "lifecycle"),
    ),
    _c(
        "GOVERN 6.1",
        "Policies address AI risks from third-party entities, including intellectual property infringement.",
        "GOVERN 6: Third-party software, data and supply chain",
        ("third_party", "policy"),
        ("intellectual property", "copyright", "licence terms", "license terms"),
    ),
    _c(
        "GOVERN 6.2",
        "Contingency processes handle failures or incidents in high-risk third-party data or AI systems.",
        "GOVERN 6: Third-party software, data and supply chain",
        ("third_party", "incident_response", "resilience"),
        ("contingency plan", "vendor outage", "provider failure"),
    ),
)

_MAP = (
    _c(
        "MAP 1.1",
        "Intended purposes, beneficial uses, context-specific norms and deployment settings are understood and documented.",
        "MAP 1: Context is established and understood",
        ("purpose_scope", "documentation"),
        ("intended purpose", "prospective setting"),
    ),
    _c(
        "MAP 1.2",
        "Interdisciplinary AI actors, competencies and demographic diversity are mapped to the lifecycle.",
        "MAP 1: Context is established and understood",
        ("accountability", "training_awareness"),
        ("interdisciplinary", "skills matrix"),
    ),
    _c(
        "MAP 1.3",
        "The organisation's mission and relevant goals for the AI technology are understood and documented.",
        "MAP 1: Context is established and understood",
        ("purpose_scope", "documentation"),
        ("mission alignment", "strategic goal"),
    ),
    _c(
        "MAP 1.4",
        "The business value or context of business use is defined, or the risk of non-defined use is understood.",
        "MAP 1: Context is established and understood",
        ("purpose_scope",),
        ("business case", "expected benefit", "return on investment"),
    ),
    _c(
        "MAP 1.5",
        "Organisational risk tolerances are determined and documented.",
        "MAP 1: Context is established and understood",
        ("risk_assessment", "documentation"),
        ("risk tolerance", "risk threshold"),
    ),
    _c(
        "MAP 1.6",
        "System requirements are elicited from and understood by relevant AI actors.",
        "MAP 1: Context is established and understood",
        ("purpose_scope", "documentation"),
        ("requirements elicitation", "user needs"),
    ),
    _c(
        "MAP 2.1",
        "The specific tasks and the methods used to implement them are defined and documented.",
        "MAP 2: Categorisation of the AI system",
        ("purpose_scope", "documentation"),
        ("task definition", "system categorisation", "system categorization"),
    ),
    _c(
        "MAP 2.2",
        "The system's knowledge limits and how outputs will be used and overseen by humans are documented.",
        "MAP 2: Categorisation of the AI system",
        ("documentation", "human_oversight", "purpose_scope"),
        ("knowledge limits", "known limitations", "model card"),
    ),
    _c(
        "MAP 2.3",
        "Scientific integrity and test, evaluation, verification and validation (TEVV) considerations are documented, including data collection and selection.",
        "MAP 2: Categorisation of the AI system",
        ("testing_evaluation", "documentation", "data_governance"),
        ("scientific integrity", "experimental design", "tevv", "data collection and selection"),
    ),
    _c(
        "MAP 3.1",
        "Potential benefits of the intended functionality and performance are examined and documented.",
        "MAP 3: Capabilities, targeted usage, goals and expectations",
        ("purpose_scope", "documentation"),
        ("expected benefit",),
    ),
    _c(
        "MAP 3.2",
        "Potential costs, including non-monetary costs from errors, are examined and documented.",
        "MAP 3: Capabilities, targeted usage, goals and expectations",
        ("impact_assessment", "risk_assessment"),
        ("cost of failure", "non monetary cost"),
    ),
    _c(
        "MAP 3.3",
        "Targeted application scope is specified and documented against system capability and context.",
        "MAP 3: Capabilities, targeted usage, goals and expectations",
        ("purpose_scope", "documentation"),
        ("application scope", "approved use", "out of scope"),
    ),
    _c(
        "MAP 3.4",
        "Operator and practitioner proficiency with system performance and trustworthiness is defined and assessed.",
        "MAP 3: Capabilities, targeted usage, goals and expectations",
        ("training_awareness", "human_oversight"),
        ("operator proficiency", "user competence"),
    ),
    _c(
        "MAP 3.5",
        "Processes for human oversight are defined, assessed and documented per GOVERN policies.",
        "MAP 3: Capabilities, targeted usage, goals and expectations",
        ("human_oversight", "documentation"),
    ),
    _c(
        "MAP 4.1",
        "Approaches for mapping AI technology and legal risks of components, including third-party data and software, are in place.",
        "MAP 4: Risks and benefits of all components",
        ("third_party", "risk_assessment", "data_governance"),
        ("component risk", "software bill of materials", "sbom"),
    ),
    _c(
        "MAP 4.2",
        "Internal risk controls for system components, including third-party AI technologies, are identified and documented.",
        "MAP 4: Risks and benefits of all components",
        ("third_party", "documentation", "risk_assessment"),
    ),
    _c(
        "MAP 5.1",
        "Likelihood and magnitude of each identified impact are informed by expected use, prior incidents and feedback.",
        "MAP 5: Impacts to individuals, groups, communities and society",
        ("impact_assessment", "risk_assessment"),
        ("likelihood and magnitude", "incident reports"),
    ),
    _c(
        "MAP 5.2",
        "Practices and personnel support regular engagement with AI actors and integrate impact feedback.",
        "MAP 5: Impacts to individuals, groups, communities and society",
        ("feedback", "impact_assessment"),
    ),
)

_MEASURE = (
    _c(
        "MEASURE 1.1",
        "Metrics and measurement approaches for the risks identified in MAP are selected, starting with the most significant.",
        "MEASURE 1: Appropriate methods and metrics",
        ("testing_evaluation", "risk_assessment"),
        ("select metrics", "measurement approach"),
    ),
    _c(
        "MEASURE 1.2",
        "The appropriateness of metrics and effectiveness of controls are regularly assessed and updated.",
        "MEASURE 1: Appropriate methods and metrics",
        ("testing_evaluation", "monitoring"),
        ("control effectiveness", "metric review"),
    ),
    _c(
        "MEASURE 1.3",
        "Independent assessors or internal experts who were not front-line developers take part in assessments.",
        "MEASURE 1: Appropriate methods and metrics",
        ("testing_evaluation", "conformity"),
        ("independent assessment", "second line review", "third party audit"),
    ),
    _c(
        "MEASURE 2.1",
        "Test sets, metrics and TEVV tooling details are documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation", "documentation"),
        ("test set", "evaluation harness"),
    ),
    _c(
        "MEASURE 2.2",
        "Evaluations involving human subjects meet applicable requirements and are representative.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation", "privacy"),
        ("human subject", "irb", "participant consent"),
    ),
    _c(
        "MEASURE 2.3",
        "Performance or assurance criteria are measured and demonstrated under deployment-like conditions.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation",),
        ("assurance criteria", "deployment conditions"),
    ),
    _c(
        "MEASURE 2.4",
        "System functionality and behaviour are monitored once in production.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("monitoring",),
        ("production behaviour", "production behavior", "drift detection"),
    ),
    _c(
        "MEASURE 2.5",
        "The system is demonstrated to be valid and reliable, with generalisation limits documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation", "documentation"),
        ("valid and reliable", "generalisation", "generalization"),
    ),
    _c(
        "MEASURE 2.6",
        "The system is evaluated regularly for safety risks and failure modes, including in out-of-distribution settings.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation", "resilience"),
        ("safety risk", "failure mode", "out of distribution", "unsafe output"),
    ),
    _c(
        "MEASURE 2.7",
        "Security and resilience are evaluated and documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("security", "resilience", "testing_evaluation"),
    ),
    _c(
        "MEASURE 2.8",
        "Risks associated with transparency and accountability are examined and documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("transparency", "accountability", "documentation"),
    ),
    _c(
        "MEASURE 2.9",
        "The model is explained, validated and documented, and outputs are interpreted in context.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("transparency", "documentation"),
        ("model explanation", "feature importance", "interpret output"),
    ),
    _c(
        "MEASURE 2.10",
        "Privacy risk of the system is examined and documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("privacy", "documentation"),
        ("memorisation", "memorization", "training data leakage"),
    ),
    _c(
        "MEASURE 2.11",
        "Fairness and bias identified in MAP are evaluated and the results documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("bias_fairness", "testing_evaluation"),
        ("bias testing", "fairness metric", "subgroup evaluation"),
    ),
    _c(
        "MEASURE 2.12",
        "Environmental impact and sustainability of model training and operation are assessed and documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("impact_assessment", "documentation"),
        ("environmental impact", "carbon", "energy consumption", "sustainability"),
    ),
    _c(
        "MEASURE 2.13",
        "The effectiveness of the TEVV metrics and processes themselves is evaluated and documented.",
        "MEASURE 2: Systems are evaluated for trustworthy characteristics",
        ("testing_evaluation", "conformity"),
        ("meta evaluation", "process effectiveness"),
    ),
    _c(
        "MEASURE 3.1",
        "Approaches, personnel and documentation are in place to identify and track existing, unanticipated and emergent risks.",
        "MEASURE 3: Mechanisms for tracking risks over time",
        ("monitoring", "risk_assessment"),
        ("emergent risk", "risk tracking", "unanticipated risk"),
    ),
    _c(
        "MEASURE 3.2",
        "Risk tracking approaches are considered for risks that are hard to measure with current techniques.",
        "MEASURE 3: Mechanisms for tracking risks over time",
        ("risk_assessment", "monitoring"),
        ("hard to measure", "qualitative tracking"),
    ),
    _c(
        "MEASURE 3.3",
        "Feedback processes let end users and impacted communities report problems and appeal outcomes.",
        "MEASURE 3: Mechanisms for tracking risks over time",
        ("feedback",),
        ("report a problem", "appeal an outcome"),
    ),
    _c(
        "MEASURE 4.1",
        "Measurement approaches are connected to deployment context and validated with domain experts and end users.",
        "MEASURE 4: Feedback about measurement efficacy",
        ("testing_evaluation", "feedback"),
        ("domain expert", "context validity"),
    ),
    _c(
        "MEASURE 4.2",
        "Measurement results are reviewed with domain experts and AI actors to confirm the system performs as intended.",
        "MEASURE 4: Feedback about measurement efficacy",
        ("testing_evaluation", "feedback", "monitoring"),
    ),
    _c(
        "MEASURE 4.3",
        "Measurable performance improvements or declines are identified and documented from consultations.",
        "MEASURE 4: Feedback about measurement efficacy",
        ("monitoring", "documentation"),
        ("performance trend", "improvement or decline"),
    ),
)

_MANAGE = (
    _c(
        "MANAGE 1.1",
        "A determination is made whether the system meets its intended purpose and whether to proceed with deployment.",
        "MANAGE 1: Risks are prioritised and acted on",
        ("human_oversight", "lifecycle", "risk_assessment"),
        ("go no go", "deployment decision", "proceed or halt", "launch approval"),
    ),
    _c(
        "MANAGE 1.2",
        "Treatment of documented risks is prioritised by impact, likelihood and available resources.",
        "MANAGE 1: Risks are prioritised and acted on",
        ("risk_assessment",),
        ("prioritise remediation", "prioritize remediation"),
    ),
    _c(
        "MANAGE 1.3",
        "Responses to high-priority risks are developed, planned and documented, including mitigate, transfer, avoid or accept.",
        "MANAGE 1: Risks are prioritised and acted on",
        ("risk_assessment", "documentation"),
        ("risk response", "mitigation plan", "accept the risk", "transfer the risk"),
    ),
    _c(
        "MANAGE 1.4",
        "Negative residual risks to downstream acquirers and end users are documented.",
        "MANAGE 1: Risks are prioritised and acted on",
        ("risk_assessment", "documentation", "transparency"),
        ("residual risk", "downstream acquirer"),
    ),
    _c(
        "MANAGE 2.1",
        "Resources needed to manage AI risks, and viable non-AI alternatives, are taken into account.",
        "MANAGE 2: Strategies to maximise benefit and minimise harm",
        ("risk_assessment",),
        ("non ai alternative", "resource planning", "build versus buy"),
    ),
    _c(
        "MANAGE 2.2",
        "Mechanisms sustain the value of deployed AI systems over time.",
        "MANAGE 2: Strategies to maximise benefit and minimise harm",
        ("monitoring", "lifecycle"),
        ("sustain value", "ongoing maintenance", "retraining schedule"),
    ),
    _c(
        "MANAGE 2.3",
        "Procedures respond to and recover from previously unknown risks when identified.",
        "MANAGE 2: Strategies to maximise benefit and minimise harm",
        ("incident_response", "resilience"),
        ("unknown risk", "recovery procedure"),
    ),
    _c(
        "MANAGE 2.4",
        "Mechanisms and assigned responsibilities exist to supersede, disengage or deactivate systems behaving inconsistently with intended use.",
        "MANAGE 2: Strategies to maximise benefit and minimise harm",
        ("human_oversight", "incident_response", "lifecycle"),
        ("deactivate", "disengage", "rollback", "kill switch", "shut down the model"),
    ),
    _c(
        "MANAGE 3.1",
        "Risks and benefits from third-party resources are monitored regularly with controls applied and documented.",
        "MANAGE 3: Third-party risks and benefits",
        ("third_party", "monitoring"),
    ),
    _c(
        "MANAGE 3.2",
        "Pre-trained models used in development are monitored as part of regular monitoring and maintenance.",
        "MANAGE 3: Third-party risks and benefits",
        ("third_party", "monitoring"),
        ("pre trained model", "model update from vendor", "version pinning"),
    ),
    _c(
        "MANAGE 4.1",
        "Post-deployment monitoring plans are implemented, covering user input, appeal, override, decommissioning, incident response and change management.",
        "MANAGE 4: Risk treatments are documented and monitored",
        ("monitoring", "incident_response", "human_oversight", "lifecycle", "logging"),
        ("post deployment monitoring", "override mechanism"),
    ),
    _c(
        "MANAGE 4.2",
        "Continual improvement activities are integrated into system updates with regular stakeholder engagement.",
        "MANAGE 4: Risk treatments are documented and monitored",
        ("lifecycle", "feedback", "conformity"),
        ("continual improvement", "continuous improvement"),
    ),
    _c(
        "MANAGE 4.3",
        "Incidents and errors are communicated to relevant AI actors and affected communities, with tracking and recovery processes followed.",
        "MANAGE 4: Risk treatments are documented and monitored",
        ("incident_response", "transparency", "feedback"),
        ("communicate incidents", "notify affected users"),
    ),
)

CONTROLS: Final[tuple[Control, ...]] = assert_unique_ids(
    _GOVERN + _MAP + _MEASURE + _MANAGE
)

FRAMEWORK: Final[Framework] = Framework(
    key=FRAMEWORK_KEY,
    name="NIST AI Risk Management Framework",
    version="1.0 (NIST AI 100-1, January 2023)",
    source="https://doi.org/10.6028/NIST.AI.100-1",
    coverage=(
        "All 72 subcategories across the four core functions are encoded with "
        "their published identifiers. Titles are condensed paraphrases, not "
        "verbatim NIST text."
    ),
    controls=CONTROLS,
)
