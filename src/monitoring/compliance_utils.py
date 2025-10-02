"""Compliance tagging utilities for GAD, CCET, and other mandates."""

# GAD (Gender and Development) Tagging Checklist
GAD_CHECKLIST = [
    {
        "code": "GAD-1",
        "criterion": "Does the PPA directly address gender disparities or promote gender equality?",
        "examples": "Women's livelihood programs, gender-based violence prevention, women in leadership training",
    },
    {
        "code": "GAD-2",
        "criterion": "Are women/girls the primary or significant beneficiaries?",
        "examples": "Maternal health programs, girls' education scholarships, women entrepreneurs support",
    },
    {
        "code": "GAD-3",
        "criterion": "Does the PPA include sex-disaggregated data collection and monitoring?",
        "examples": "Separate tracking of male/female beneficiaries, gender-responsive indicators",
    },
    {
        "code": "GAD-4",
        "criterion": "Were women meaningfully consulted in the design and planning?",
        "examples": "Women participants in needs assessments, women-led community consultations",
    },
    {
        "code": "GAD-5",
        "criterion": "Does the PPA challenge or transform discriminatory gender norms?",
        "examples": "Men's engagement in caregiving, challenging stereotypes, inclusive policies",
    },
]

# CCET (Climate Change Expenditure Tagging) Checklist
CCET_CHECKLIST = [
    {
        "code": "CCET-1",
        "criterion": "Does the PPA reduce greenhouse gas emissions or carbon footprint?",
        "examples": "Renewable energy projects, energy efficiency, sustainable transport",
    },
    {
        "code": "CCET-2",
        "criterion": "Does the PPA enhance climate resilience or adaptation capacity?",
        "examples": "Flood control infrastructure, drought-resistant crops, early warning systems",
    },
    {
        "code": "CCET-3",
        "criterion": "Does the PPA support ecosystem-based adaptation or conservation?",
        "examples": "Mangrove restoration, watershed protection, biodiversity conservation",
    },
    {
        "code": "CCET-4",
        "criterion": "Does the PPA address climate-related disaster risk reduction?",
        "examples": "Evacuation facilities, climate-proofed infrastructure, community preparedness",
    },
    {
        "code": "CCET-5",
        "criterion": "Does the PPA support climate-smart agriculture or fisheries?",
        "examples": "Climate-adapted seeds, water-efficient irrigation, sustainable fishing practices",
    },
]

# Indigenous Peoples (IP) Benefit Checklist
IP_CHECKLIST = [
    {
        "code": "IP-1",
        "criterion": "Are Indigenous Peoples the primary or significant beneficiaries?",
        "examples": "Ancestral domain titling, indigenous language programs, traditional livelihood support",
    },
    {
        "code": "IP-2",
        "criterion": "Does the PPA protect indigenous rights and cultural heritage?",
        "examples": "Cultural mapping, traditional knowledge preservation, sacred site protection",
    },
    {
        "code": "IP-3",
        "criterion": "Was Free, Prior, and Informed Consent (FPIC) obtained?",
        "examples": "Documented community consultations, tribal leader endorsements, consent protocols",
    },
    {
        "code": "IP-4",
        "criterion": "Does the PPA support indigenous self-determination and governance?",
        "examples": "Capacity-building for indigenous leaders, support for tribal councils",
    },
]

# Peace and Security Checklist
PEACE_CHECKLIST = [
    {
        "code": "PEACE-1",
        "criterion": "Does the PPA support peacebuilding or conflict resolution?",
        "examples": "Dialogue platforms, mediation training, peace education",
    },
    {
        "code": "PEACE-2",
        "criterion": "Does the PPA address root causes of conflict or violence?",
        "examples": "Livelihood for former combatants, justice sector reform, land dispute resolution",
    },
    {
        "code": "PEACE-3",
        "criterion": "Does the PPA promote social cohesion and reconciliation?",
        "examples": "Inter-community sports programs, transitional justice mechanisms, shared spaces",
    },
    {
        "code": "PEACE-4",
        "criterion": "Does the PPA support decommissioned combatants or conflict-affected communities?",
        "examples": "Normalization programs, psychosocial support, economic reintegration",
    },
]

# SDG Alignment Checklist (Simplified - focusing on key SDGs for OOBC)
SDG_CHECKLIST = [
    {
        "code": "SDG-1",
        "sdg": "SDG 1: No Poverty",
        "criterion": "Does the PPA reduce poverty or improve economic opportunities?",
        "examples": "Livelihood programs, cash transfers, microfinance, skills training",
    },
    {
        "code": "SDG-2",
        "sdg": "SDG 2: Zero Hunger",
        "criterion": "Does the PPA address food security or nutrition?",
        "examples": "Agriculture support, nutrition programs, food distribution",
    },
    {
        "code": "SDG-4",
        "sdg": "SDG 4: Quality Education",
        "criterion": "Does the PPA improve access to or quality of education?",
        "examples": "School construction, scholarships, teacher training, madaris support",
    },
    {
        "code": "SDG-5",
        "sdg": "SDG 5: Gender Equality",
        "criterion": "Does the PPA promote gender equality and empower women?",
        "examples": "Women empowerment programs, anti-violence campaigns, leadership training",
    },
    {
        "code": "SDG-10",
        "sdg": "SDG 10: Reduced Inequalities",
        "criterion": "Does the PPA reduce inequalities for marginalized groups?",
        "examples": "Inclusive services, anti-discrimination measures, cultural preservation",
    },
    {
        "code": "SDG-16",
        "sdg": "SDG 16: Peace and Justice",
        "criterion": "Does the PPA promote peace, justice, or strong institutions?",
        "examples": "Justice access programs, governance strengthening, conflict resolution",
    },
]


def evaluate_gad_compliance(form_data):
    """
    Evaluate if a PPA meets GAD tagging criteria.

    Returns a dict with compliance assessment.
    """
    # Example implementation - would be enhanced based on actual form fields
    score = 0
    total_criteria = len(GAD_CHECKLIST)

    assessment = {
        "compliant": False,
        "score": score,
        "total_criteria": total_criteria,
        "percentage": 0,
        "recommendations": [],
    }

    # Check if explicitly tagged
    if form_data.get("compliance_gad"):
        assessment["compliant"] = True
        assessment["score"] = total_criteria
        assessment["percentage"] = 100
    else:
        assessment["recommendations"].append(
            "Review GAD checklist criteria to determine if this PPA qualifies for GAD tagging."
        )

    return assessment


def evaluate_ccet_compliance(form_data):
    """
    Evaluate if a PPA meets CCET criteria.

    Returns a dict with compliance assessment.
    """
    score = 0
    total_criteria = len(CCET_CHECKLIST)

    assessment = {
        "compliant": False,
        "score": score,
        "total_criteria": total_criteria,
        "percentage": 0,
        "recommendations": [],
    }

    if form_data.get("compliance_ccet"):
        assessment["compliant"] = True
        assessment["score"] = total_criteria
        assessment["percentage"] = 100
    else:
        assessment["recommendations"].append(
            "Review CCET checklist criteria to determine if this PPA addresses climate change."
        )

    return assessment


def get_compliance_help_text(field_name):
    """
    Get contextual help text for compliance fields.
    """
    help_texts = {
        "compliance_gad": (
            "Tag this PPA for Gender and Development (GAD) if it meets at least 2 of the 5 GAD criteria. "
            "See checklist for details."
        ),
        "compliance_ccet": (
            "Tag this PPA for Climate Change Expenditure Tagging (CCET) if it addresses mitigation, "
            "adaptation, or disaster risk reduction related to climate change."
        ),
        "benefits_indigenous_peoples": (
            "Check if Indigenous Peoples are primary or significant beneficiaries, or if the PPA "
            "protects indigenous rights and cultural heritage."
        ),
        "supports_peace_agenda": (
            "Check if the PPA supports peacebuilding, conflict resolution, or addresses conflict-affected "
            "communities in the Bangsamoro region."
        ),
        "supports_sdg": (
            "Check if the PPA contributes to Sustainable Development Goals, particularly SDGs 1, 2, 4, 5, 10, or 16."
        ),
    }
    return help_texts.get(field_name, "")
