"""Shared constants for the common app."""

STAFF_USER_TYPES = ("oobc_staff", "admin")

STAFF_TEAM_DEFINITIONS = [
    {
        "name": "MANA Team",
        "description": (
            "Mapping and Needs Assessment (MANA) team overseeing geospatial and "
            "socio-economic profiling."
        ),
        "mission": (
            "Deliver updated community baselines and data layers to guide OOBC "
            "interventions."
        ),
        "focus": [
            "Community mapping refresh cycles",
            "Needs assessment data quality",
            "Field team readiness and logistics",
        ],
    },
    {
        "name": "M&E Unit",
        "description": (
            "Monitoring and Evaluation unit tracking programme outcomes and "
            "implementation fidelity."
        ),
        "mission": (
            "Transform field reports into actionable insights for adaptive management "
            "and leadership decisions."
        ),
        "focus": [
            "Indicator performance tracking",
            "Data validation and synthesis",
            "Reporting for management and partners",
        ],
    },
    {
        "name": "Planning and Budgeting Unit",
        "description": (
            "Unit aligning programme priorities with financial planning and resource "
            "mobilisation."
        ),
        "mission": (
            "Translate community priorities into resourced plans and monitor execution "
            "timelines."
        ),
        "focus": [
            "Quarterly budgeting cycles",
            "Resource alignment with MANA outputs",
            "Portfolio risk mitigation",
        ],
    },
    {
        "name": "Coordination Unit",
        "description": (
            "Unit orchestrating cross-agency touchpoints and commitments for OOBC "
            "communities."
        ),
        "mission": (
            "Synchronise engagements with BARMM ministries, LGUs, and partners for "
            "cohesive delivery."
        ),
        "focus": [
            "Inter-agency briefings",
            "Stakeholder alignment",
            "Calendar and follow-up management",
        ],
    },
    {
        "name": "Community Development Unit",
        "description": (
            "Unit crafting development packages and support services for OOBC "
            "communities."
        ),
        "mission": (
            "Co-design livelihood, protection, and social support interventions with "
            "communities."
        ),
        "focus": [
            "Livelihood programming",
            "Community consultations",
            "Capability building initiatives",
        ],
    },
    {
        "name": "Research Unit",
        "description": (
            "Research hub documenting emerging issues, indigenous knowledge, and "
            "policy evidence."
        ),
        "mission": (
            "Convert field intelligence into briefs that feed policy and programme "
            "design."
        ),
        "focus": [
            "Qualitative and quantitative studies",
            "Knowledge management",
            "Evidence synthesis",
        ],
    },
]


RECOMMENDATIONS_AREAS = {
    "economic-development": {
        "name": "Economic Development",
        "categories": ["economic_development"],
        "icon": "fas fa-chart-line",
        "color": "green",
    },
    "social-development": {
        "name": "Social Development",
        "categories": ["social_development"],
        "icon": "fas fa-users",
        "color": "purple",
    },
    "cultural-development": {
        "name": "Cultural Development",
        "categories": ["cultural_development"],
        "icon": "fas fa-mosque",
        "color": "orange",
    },
    "rehabilitation-development": {
        "name": "Rehabilitation & Development",
        "categories": ["infrastructure", "environment"],
        "icon": "fas fa-hammer",
        "color": "blue",
    },
    "protection-rights": {
        "name": "Protection of Rights",
        "categories": ["human_rights"],
        "icon": "fas fa-balance-scale",
        "color": "red",
    },
}
