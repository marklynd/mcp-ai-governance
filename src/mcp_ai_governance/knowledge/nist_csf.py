"""NIST Cybersecurity Framework 2.0 - category-level subset.

Source: NIST Cybersecurity Framework (CSF) 2.0, NIST CSWP 29, February 2024.

Encoded here at **category** granularity (for example ``GV.SC`` rather than
``GV.SC-01``). AI governance work almost always has to land on an existing
security programme, and category-level mapping is the level at which that
conversation happens. Subcategory-level mapping is deliberately out of scope;
see "Scope and limitations" in the README.

Titles are condensed paraphrases written for this project.
"""

from __future__ import annotations

from typing import Final

from .base import Control, Framework, assert_unique_ids

FRAMEWORK_KEY: Final[str] = "nist_csf"

_CITE = "NIST CSWP 29 (CSF 2.0), Feb 2024"


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
            "GV.OC",
            "Organizational Context: the mission, stakeholder expectations and legal requirements informing risk management.",
            "GOVERN",
            ("purpose_scope", "policy"),
        ),
        _c(
            "GV.RM",
            "Risk Management Strategy: priorities, constraints, risk tolerance and appetite statements.",
            "GOVERN",
            ("risk_assessment",),
        ),
        _c(
            "GV.RR",
            "Roles, Responsibilities and Authorities for cybersecurity risk.",
            "GOVERN",
            ("accountability",),
        ),
        _c(
            "GV.PO",
            "Policy: organisational cybersecurity policy is established and communicated.",
            "GOVERN",
            ("policy",),
        ),
        _c(
            "GV.OV",
            "Oversight: results of risk management activities inform and improve the strategy.",
            "GOVERN",
            ("conformity", "monitoring"),
        ),
        _c(
            "GV.SC",
            "Cybersecurity Supply Chain Risk Management: third-party and supplier risk processes.",
            "GOVERN",
            ("third_party",),
        ),
        _c(
            "ID.AM",
            "Asset Management: inventory of hardware, software, services, data and suppliers.",
            "IDENTIFY",
            ("inventory", "data_governance"),
        ),
        _c(
            "ID.RA",
            "Risk Assessment: identifying vulnerabilities, threats, likelihood and impact.",
            "IDENTIFY",
            ("risk_assessment", "security"),
        ),
        _c(
            "ID.IM",
            "Improvement: improvements identified from evaluations, tests and lessons learned.",
            "IDENTIFY",
            ("conformity", "testing_evaluation"),
        ),
        _c(
            "PR.AA",
            "Identity Management, Authentication and Access Control.",
            "PROTECT",
            ("security",),
        ),
        _c(
            "PR.AT",
            "Awareness and Training for personnel with cybersecurity responsibilities.",
            "PROTECT",
            ("training_awareness",),
        ),
        _c(
            "PR.DS",
            "Data Security: confidentiality, integrity and availability of data at rest, in transit and in use.",
            "PROTECT",
            ("security", "privacy", "data_governance"),
        ),
        _c(
            "PR.PS",
            "Platform Security: secure configuration and maintenance of hardware, software and services.",
            "PROTECT",
            ("security", "lifecycle"),
        ),
        _c(
            "PR.IR",
            "Technology Infrastructure Resilience: architectures that support resilience and availability.",
            "PROTECT",
            ("resilience",),
        ),
        _c(
            "DE.CM",
            "Continuous Monitoring of assets to find anomalies and indicators of compromise.",
            "DETECT",
            ("monitoring", "security"),
        ),
        _c(
            "DE.AE",
            "Adverse Event Analysis: characterising events to determine whether an incident has occurred.",
            "DETECT",
            ("incident_response", "logging"),
        ),
        _c(
            "RS.MA",
            "Incident Management: executing and coordinating the incident response process.",
            "RESPOND",
            ("incident_response",),
        ),
        _c(
            "RS.AN",
            "Incident Analysis: investigation to support response and recovery, including forensic evidence.",
            "RESPOND",
            ("incident_response", "logging"),
        ),
        _c(
            "RS.CO",
            "Incident Response Reporting and Communication with internal and external stakeholders.",
            "RESPOND",
            ("incident_response", "transparency"),
        ),
        _c(
            "RS.MI",
            "Incident Mitigation: containing and eradicating incidents.",
            "RESPOND",
            ("incident_response", "resilience"),
        ),
        _c(
            "RC.RP",
            "Incident Recovery Plan Execution: restoring assets and operations.",
            "RECOVER",
            ("resilience", "incident_response"),
        ),
        _c(
            "RC.CO",
            "Incident Recovery Communication with internal and external stakeholders.",
            "RECOVER",
            ("incident_response", "transparency"),
        ),
    )
)

FRAMEWORK: Final[Framework] = Framework(
    key=FRAMEWORK_KEY,
    name="NIST Cybersecurity Framework",
    version="2.0 (NIST CSWP 29, February 2024)",
    source="https://doi.org/10.6028/NIST.CSWP.29",
    coverage=(
        "All 22 categories across the six CSF 2.0 functions. Subcategory-level "
        "identifiers (for example GV.SC-01) are not encoded."
    ),
    controls=CONTROLS,
)
