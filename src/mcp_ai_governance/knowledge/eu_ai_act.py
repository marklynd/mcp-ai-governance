"""EU Artificial Intelligence Act - Regulation (EU) 2024/1689.

Source: Regulation (EU) 2024/1689 of the European Parliament and of the Council
of 13 June 2024 laying down harmonised rules on artificial intelligence,
published in the Official Journal on 12 July 2024, in force from 1 August 2024.

Encoded here:
    * The obligation articles most often cited in enterprise readiness work
      (Art. 4, 5, 6, 9-15, 17, 26, 27, 43, 47-49, 50, 53, 55, 72, 73, 99).
    * The Annex III high-risk area list, used by the risk-tier classifier.
    * The Art. 5 prohibited-practice list, used by the risk-tier classifier.

Accuracy notes:
    * Article numbers and Annex III area numbering follow the final adopted
      text of Regulation (EU) 2024/1689. They differ from the 2021 Commission
      proposal and from the 2023 Parliament position, both of which are still
      widely quoted online. If a source cites "Art. 52 transparency", it is
      quoting the old proposal; in the adopted regulation that is Art. 50.
    * Titles are condensed paraphrases written for this project, not the
      official article headings.
    * The application dates in ``APPLICATION_DATES`` reflect Art. 113 as
      adopted. Delegated and implementing acts may refine details.
    * Nothing here is legal advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .base import Control, Framework, assert_unique_ids

FRAMEWORK_KEY: Final[str] = "eu_ai_act"

_CITE = "Regulation (EU) 2024/1689 (EU AI Act)"


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


CONTROLS: Final[tuple[Control, ...]] = assert_unique_ids(
    (
        _c(
            "Art. 4",
            "AI literacy: providers and deployers ensure a sufficient level of AI literacy among staff operating AI systems.",
            "Chapter I: General provisions",
            ("training_awareness",),
            ("ai literacy",),
        ),
        _c(
            "Art. 5",
            "Prohibited AI practices, including manipulative techniques, social scoring, untargeted facial scraping and workplace emotion inference.",
            "Chapter II: Prohibited AI practices",
            ("risk_assessment", "impact_assessment"),
            (
                "prohibited practice",
                "banned use",
                "social scoring",
                "subliminal technique",
                "manipulative technique",
                "exploit vulnerabilities",
                "emotion recognition in the workplace",
                "untargeted scraping",
                "predictive policing",
            ),
        ),
        _c(
            "Art. 6",
            "Classification rules for high-risk AI systems, via Annex I product safety legislation or the Annex III use-case list.",
            "Chapter III: High-risk AI systems",
            ("risk_assessment", "purpose_scope"),
            ("high risk classification", "annex iii", "annex i", "risk tier"),
        ),
        _c(
            "Art. 9",
            "Risk management system: a continuous, iterative process across the whole high-risk system lifecycle.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("risk_assessment", "lifecycle"),
            ("risk management system", "iterative risk process", "risk tolerance"),
        ),
        _c(
            "Art. 10",
            "Data and data governance: training, validation and testing data sets meet quality, relevance and representativeness criteria, including safeguards for special categories of personal data.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("data_governance", "bias_fairness", "privacy"),
            (
                "data governance",
                "training validation and testing",
                "representative data",
                "lawful basis",
            ),
        ),
        _c(
            "Art. 11",
            "Technical documentation drawn up before placing on the market and kept up to date (content per Annex IV).",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("documentation",),
            ("technical documentation", "annex iv"),
        ),
        _c(
            "Art. 12",
            "Record-keeping: high-risk systems technically allow automatic recording of events (logs) over their lifetime.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("logging",),
            ("automatic logging", "record keeping", "logs over lifetime"),
        ),
        _c(
            "Art. 13",
            "Transparency and provision of information to deployers, including instructions for use and known limitations.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("transparency", "documentation", "purpose_scope"),
            (
                "instructions for use",
                "information to deployers",
                "intended purpose",
                "known limitations",
            ),
        ),
        _c(
            "Art. 14",
            "Human oversight: high-risk systems are designed so natural persons can effectively oversee them, including a stop function.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("human_oversight",),
            (
                "human oversight",
                "stop function",
                "stop button",
                "intervene",
                "interrupt the system",
                "deactivate",
                "disengage",
                "automation bias",
            ),
        ),
        _c(
            "Art. 15",
            "Accuracy, robustness and cybersecurity across the lifecycle, including resilience to data poisoning and adversarial inputs.",
            "Chapter III Section 2: Requirements for high-risk systems",
            ("security", "resilience", "testing_evaluation"),
            ("accuracy robustness cybersecurity", "adversarial resilience"),
        ),
        _c(
            "Art. 17",
            "Quality management system for providers of high-risk AI systems, documented as written policies and procedures.",
            "Chapter III Section 3: Obligations of providers and deployers",
            ("policy", "conformity", "documentation", "lifecycle"),
            ("quality management system", "qms", "design control", "change control"),
        ),
        _c(
            "Art. 26",
            "Obligations of deployers of high-risk AI systems, including using the system per instructions and assigning competent human oversight.",
            "Chapter III Section 3: Obligations of providers and deployers",
            ("human_oversight", "accountability", "monitoring"),
            ("deployer obligations", "use per instructions"),
        ),
        _c(
            "Art. 27",
            "Fundamental rights impact assessment for certain deployers of Annex III high-risk systems.",
            "Chapter III Section 3: Obligations of providers and deployers",
            ("impact_assessment",),
            ("fundamental rights impact assessment", "fria"),
        ),
        _c(
            "Art. 43",
            "Conformity assessment procedures for high-risk AI systems, internal control or notified body involvement.",
            "Chapter III Section 5: Standards, conformity assessment, certificates",
            ("conformity",),
            ("conformity assessment", "notified body"),
        ),
        _c(
            "Art. 47",
            "EU declaration of conformity drawn up and kept by the provider.",
            "Chapter III Section 5: Standards, conformity assessment, certificates",
            ("conformity", "documentation"),
            ("declaration of conformity",),
        ),
        _c(
            "Art. 48",
            "CE marking affixed to high-risk AI systems.",
            "Chapter III Section 5: Standards, conformity assessment, certificates",
            ("conformity",),
            ("ce marking",),
        ),
        _c(
            "Art. 49",
            "Registration of high-risk AI systems in the EU database before placing on the market or putting into service.",
            "Chapter III Section 5: Standards, conformity assessment, certificates",
            ("conformity", "inventory"),
            ("eu database", "registration"),
        ),
        _c(
            "Art. 50",
            "Transparency obligations: disclose AI interaction to users, mark synthetic content machine-readably and label deepfakes.",
            "Chapter IV: Transparency obligations",
            ("transparency",),
            (
                "chatbot",
                "ai assistant",
                "talking to an ai",
                "interacting with an ai",
                "mark synthetic content",
                "deepfake disclosure",
                "watermarking",
                "emotion recognition notification",
            ),
        ),
        _c(
            "Art. 53",
            "Obligations for providers of general-purpose AI models: technical documentation, downstream information, copyright policy and training-content summary.",
            "Chapter V: General-purpose AI models",
            ("documentation", "third_party", "transparency"),
            (
                "general purpose ai",
                "gpai",
                "foundation model provider",
                "training data summary",
                "copyright policy",
            ),
        ),
        _c(
            "Art. 55",
            "Additional obligations for GPAI models with systemic risk: model evaluation, adversarial testing, incident reporting and cybersecurity protection.",
            "Chapter V: General-purpose AI models",
            ("testing_evaluation", "security", "incident_response"),
            ("systemic risk", "gpai systemic", "model evaluation", "state of the art evaluation"),
        ),
        _c(
            "Art. 72",
            "Post-market monitoring by providers, based on a documented post-market monitoring plan.",
            "Chapter IX: Post-market monitoring and information sharing",
            ("monitoring",),
            ("post market monitoring", "post market plan"),
        ),
        _c(
            "Art. 73",
            "Reporting of serious incidents to market surveillance authorities within the prescribed deadlines.",
            "Chapter IX: Post-market monitoring and information sharing",
            ("incident_response",),
            ("serious incident", "report to authority", "market surveillance"),
        ),
        _c(
            "Art. 99",
            "Penalties: up to EUR 35 million or 7 percent of worldwide annual turnover for prohibited-practice breaches.",
            "Chapter XII: Penalties",
            ("accountability", "risk_assessment"),
            ("penalty", "fine", "turnover", "enforcement"),
        ),
    )
)

FRAMEWORK: Final[Framework] = Framework(
    key=FRAMEWORK_KEY,
    name="EU Artificial Intelligence Act",
    version="Regulation (EU) 2024/1689 (OJ L, 12 July 2024)",
    source="http://data.europa.eu/eli/reg/2024/1689/oj",
    coverage=(
        "The obligation articles most relevant to enterprise readiness work. "
        "Not the full 113 articles or all 13 annexes. Article numbers follow "
        "the adopted regulation, not the 2021 proposal."
    ),
    controls=CONTROLS,
)


# --------------------------------------------------------------------------
# Reference data for the risk-tier classifier (mcp_ai_governance.risk)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PracticeRule:
    """A pattern that triggers a specific EU AI Act treatment.

    Attributes:
        code: Short stable identifier for the rule.
        label: Human-readable description of the triggering practice.
        citation: Article or annex point in Regulation (EU) 2024/1689.
        signals: Phrases that indicate the practice is present.
        caveats: Statutory carve-outs or conditions a lawyer must confirm.
    """

    code: str
    label: str
    citation: str
    signals: tuple[str, ...]
    caveats: str = ""


# Art. 5(1)(a) to (h) of Regulation (EU) 2024/1689.
PROHIBITED_PRACTICES: Final[tuple[PracticeRule, ...]] = (
    PracticeRule(
        code="P1_MANIPULATION",
        label="Subliminal, purposefully manipulative or deceptive techniques that materially distort behaviour and cause significant harm",
        citation="Art. 5(1)(a)",
        signals=(
            "subliminal",
            "manipulative technique",
            "deceptive technique",
            "distort behaviour",
            "distort behavior",
            "covertly influence",
            "dark pattern",
        ),
    ),
    PracticeRule(
        code="P2_VULNERABILITY",
        label="Exploiting vulnerabilities due to age, disability or a specific social or economic situation",
        citation="Art. 5(1)(b)",
        signals=(
            "exploit vulnerabilities",
            "target children",
            "prey on the elderly",
            "exploit disability",
            "exploit poverty",
            "vulnerable group targeting",
        ),
    ),
    PracticeRule(
        code="P3_SOCIAL_SCORING",
        label="Social scoring leading to detrimental or disproportionate treatment in unrelated contexts",
        citation="Art. 5(1)(c)",
        signals=(
            "social scoring",
            "social credit",
            "citizen score",
            "trustworthiness score of individuals",
            "score citizens",
        ),
    ),
    PracticeRule(
        code="P4_PREDICTIVE_POLICING",
        label="Predicting the risk of a person committing a crime based solely on profiling or personality traits",
        citation="Art. 5(1)(d)",
        signals=(
            "predictive policing",
            "predict criminality",
            "predict who will commit a crime",
            "criminal propensity",
            "pre crime",
        ),
        caveats="Does not apply where the system supports human assessment already based on objective, verifiable facts directly linked to criminal activity.",
    ),
    PracticeRule(
        code="P5_FACE_SCRAPING",
        label="Untargeted scraping of facial images from the internet or CCTV to build facial recognition databases",
        citation="Art. 5(1)(e)",
        signals=(
            "scrape facial images",
            "untargeted scraping",
            "scrape faces",
            "facial recognition database",
            "build a face database from the internet",
        ),
    ),
    PracticeRule(
        code="P6_EMOTION_WORKPLACE",
        label="Inferring emotions in the workplace or in education institutions",
        citation="Art. 5(1)(f)",
        signals=(
            "emotion recognition in the workplace",
            "employee emotions",
            "emotions of employees",
            "student emotions",
            "emotions of students",
            "emotion detection in class",
            "monitor worker mood",
            "sentiment of employees",
        ),
        caveats="Medical or safety reasons are carved out.",
    ),
    PracticeRule(
        code="P7_BIOMETRIC_CATEGORISATION",
        label="Biometric categorisation to infer race, political opinions, trade union membership, religion, sex life or sexual orientation",
        citation="Art. 5(1)(g)",
        signals=(
            "biometric categorisation",
            "biometric categorization",
            "infer race from",
            "infer sexual orientation",
            "infer religion from face",
            "infer political opinion from",
        ),
    ),
    PracticeRule(
        code="P8_REALTIME_RBI",
        label="Real-time remote biometric identification in publicly accessible spaces for law enforcement",
        citation="Art. 5(1)(h)",
        signals=(
            "real time remote biometric identification",
            "live facial recognition in public",
            "real time facial recognition for police",
            "public space biometric surveillance",
        ),
        caveats="Narrow exhaustive exceptions exist (targeted search for victims, imminent threat to life, serious crime suspects) subject to prior judicial authorisation.",
    ),
)

# Annex III of Regulation (EU) 2024/1689, areas 1 to 8.
ANNEX_III_AREAS: Final[tuple[PracticeRule, ...]] = (
    PracticeRule(
        code="A3_1_BIOMETRICS",
        label="Biometrics: remote biometric identification, biometric categorisation and emotion recognition",
        citation="Annex III, point 1",
        signals=(
            "biometric identification",
            "facial recognition",
            "fingerprint matching",
            "iris scan",
            "voice biometric",
            "emotion recognition",
            "gait recognition",
        ),
    ),
    PracticeRule(
        code="A3_2_CRITICAL_INFRA",
        label="Critical infrastructure: safety components in the management and operation of digital infrastructure, road traffic, water, gas, heating and electricity",
        citation="Annex III, point 2",
        signals=(
            "critical infrastructure",
            "power grid",
            "electricity grid",
            "water supply",
            "gas network",
            "road traffic management",
            "safety component",
            "scada",
        ),
    ),
    PracticeRule(
        code="A3_3_EDUCATION",
        label="Education and vocational training: admission, evaluation of learning outcomes, level assignment and exam-cheating monitoring",
        citation="Annex III, point 3",
        signals=(
            "admissions decision",
            "student admission",
            "grade students",
            "evaluate learning outcomes",
            "exam proctoring",
            "cheating detection",
            "vocational training placement",
        ),
    ),
    PracticeRule(
        code="A3_4_EMPLOYMENT",
        label="Employment and worker management: recruitment, selection, promotion, termination, task allocation and performance monitoring",
        citation="Annex III, point 4",
        signals=(
            "resume screening",
            "cv screening",
            "candidate ranking",
            "recruitment",
            "hiring decision",
            "job applicant",
            "promotion decision",
            "termination decision",
            "performance evaluation of employees",
            "task allocation to workers",
            "worker monitoring",
        ),
    ),
    PracticeRule(
        code="A3_5_ESSENTIAL_SERVICES",
        label="Access to essential private and public services: benefits eligibility, creditworthiness, life and health insurance risk pricing, and emergency call triage",
        citation="Annex III, point 5",
        signals=(
            "creditworthiness",
            "credit scoring",
            "loan approval",
            "mortgage decision",
            "public benefits eligibility",
            "welfare eligibility",
            "life insurance pricing",
            "health insurance risk",
            "emergency call triage",
            "dispatch of emergency services",
        ),
        caveats="Credit scoring for the purpose of detecting financial fraud is carved out of Annex III point 5(b).",
    ),
    PracticeRule(
        code="A3_6_LAW_ENFORCEMENT",
        label="Law enforcement: victim risk assessment, polygraphs, evidence reliability assessment, recidivism risk and profiling in criminal investigation",
        citation="Annex III, point 6",
        signals=(
            "law enforcement",
            "police investigation",
            "recidivism risk",
            "polygraph",
            "evidence reliability",
            "criminal profiling",
            "suspect identification",
        ),
    ),
    PracticeRule(
        code="A3_7_MIGRATION",
        label="Migration, asylum and border control: risk assessments, application examination and identity verification at borders",
        citation="Annex III, point 7",
        signals=(
            "asylum application",
            "visa application",
            "border control",
            "immigration decision",
            "migration risk assessment",
            "residence permit",
        ),
    ),
    PracticeRule(
        code="A3_8_JUSTICE",
        label="Administration of justice and democratic processes: assisting judicial authorities and influencing election outcomes or voting behaviour",
        citation="Annex III, point 8",
        signals=(
            "judicial decision",
            "assist a judge",
            "court ruling",
            "sentencing recommendation",
            "influence elections",
            "voting behaviour",
            "voting behavior",
            "electoral campaign targeting",
        ),
    ),
)

# Art. 50 of Regulation (EU) 2024/1689.
TRANSPARENCY_TRIGGERS: Final[tuple[PracticeRule, ...]] = (
    PracticeRule(
        code="T1_HUMAN_INTERACTION",
        label="System interacts directly with natural persons and must disclose that they are dealing with an AI system",
        citation="Art. 50(1)",
        signals=(
            "chatbot",
            "chat bot",
            "virtual assistant",
            "conversational agent",
            "customer support agent",
            "voice assistant",
            "interacts with customers",
            "talks to users",
            "copilot for users",
        ),
        caveats="Not required where it is obvious to a reasonably well-informed person, or for legally authorised criminal-offence detection.",
    ),
    PracticeRule(
        code="T2_SYNTHETIC_CONTENT",
        label="Generative system whose synthetic audio, image, video or text output must be marked in a machine-readable format",
        citation="Art. 50(2)",
        signals=(
            "generate images",
            "generate video",
            "generate audio",
            "synthetic media",
            "text to image",
            "text to speech",
            "voice cloning",
            "generative model output",
            "produces articles",
        ),
    ),
    PracticeRule(
        code="T3_EMOTION_BIOMETRIC_NOTICE",
        label="Emotion recognition or biometric categorisation system: exposed persons must be informed",
        citation="Art. 50(3)",
        signals=(
            "emotion recognition",
            "biometric categorisation",
            "biometric categorization",
        ),
    ),
    PracticeRule(
        code="T4_DEEPFAKE",
        label="Deep fake content must be disclosed as artificially generated or manipulated",
        citation="Art. 50(4)",
        signals=(
            "deepfake",
            "deep fake",
            "face swap",
            "manipulated video of a real person",
            "clone a real voice",
        ),
    ),
)

# Art. 113 of Regulation (EU) 2024/1689.
APPLICATION_DATES: Final[dict[str, str]] = {
    "entry_into_force": "2024-08-01",
    "prohibitions_and_ai_literacy_apply": "2025-02-02",
    "gpai_governance_and_penalties_apply": "2025-08-02",
    "general_application": "2026-08-02",
    "annex_i_embedded_high_risk_apply": "2027-08-02",
}

# Art. 99 of Regulation (EU) 2024/1689.
PENALTY_BANDS: Final[dict[str, str]] = {
    "prohibited": "Up to EUR 35 000 000 or 7 percent of total worldwide annual turnover, whichever is higher (Art. 99(3)).",
    "high-risk": "Up to EUR 15 000 000 or 3 percent of total worldwide annual turnover, whichever is higher (Art. 99(4)).",
    "limited-risk": "Up to EUR 15 000 000 or 3 percent of total worldwide annual turnover for transparency breaches (Art. 99(4)).",
    "minimal-risk": "No AI Act specific penalty band; other law such as GDPR still applies.",
}
