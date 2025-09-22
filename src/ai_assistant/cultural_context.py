"""
Bangsamoro Cultural Context Module for AI Assistant

This module provides cultural context and sensitivity guidelines for AI responses
when working with Bangsamoro communities outside BARMM.
"""

from typing import Dict, List

from django.utils import timezone


class BangsomoroCulturalContext:
    """Provides cultural context and guidelines for Bangsamoro communities."""

    def __init__(self):
        """Initialize cultural context data."""
        self.ethnolinguistic_groups = [
            "Maranao",
            "Maguindanao",
            "Tausug",
            "Sama-Bajau",
            "Yakan",
            "Iranun",
            "Kalagan",
            "Kalibugan",
            "Sangil",
            "Molbog",
        ]

        self.traditional_governance = [
            "Datu (traditional leader)",
            "Sultan (paramount ruler)",
            "Rido (clan conflict resolution)",
            "Adat (customary law)",
            "Taritib (traditional order)",
        ]

        self.islamic_principles = [
            "Shariah compatibility",
            "Halal compliance",
            "Islamic education (Madaris)",
            "Religious observances",
            "Community consultation (Shura)",
        ]

        self.economic_patterns = [
            "Agriculture (rice, corn, coconut)",
            "Fishing and aquaculture",
            "Traditional crafts and weaving",
            "Small-scale trading",
            "Halal industry development",
        ]

        self.cultural_values = {
            "maratabat": "Honor and dignity - central to Bangsamoro identity",
            "kapamilya": "Extended family system and mutual support",
            "pakikipagkapwa": "Shared identity and communal responsibility",
            "utang_na_loob": "Debt of gratitude and reciprocity",
            "respeto": "Respect for elders and traditional authority",
            "malasakit": "Compassionate care and concern for others",
        }

        self.historical_context = {
            "colonial_impact": "Spanish, American, and Japanese colonial experiences",
            "armed_conflict": "Decades of armed conflict and displacement",
            "marginalization": "Historical marginalization and discrimination",
            "autonomy_struggle": "Long struggle for self-determination",
            "peace_process": "Ongoing peace and reconciliation efforts",
        }

    def get_base_context(self) -> str:
        """Get basic cultural context for AI responses."""
        return f"""BANGSAMORO CULTURAL CONTEXT:

The Bangsamoro people are the largest Muslim community in the Philippines, with rich cultural traditions and diverse ethnolinguistic groups including {', '.join(self.ethnolinguistic_groups[:5])}, and others.

Key Cultural Principles:
- MARATABAT (Honor and Dignity): Central to Bangsamoro identity and decision-making
- Islamic Values: All recommendations must respect Islamic principles and Shariah compatibility
- Traditional Governance: Recognition of Datu, Sultan, and customary law (Adat) systems
- Community Consultation: Decisions should involve proper consultation (Shura)
- Extended Family Systems: Consider clan and kinship networks in planning

Geographic Focus:
- Primary service area: Regions IX (Zamboanga Peninsula) and XII (SOCCSKSARGEN)
- Communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)
- Diaspora communities maintaining cultural connections

Historical Sensitivity:
- Trauma-informed approaches recognizing historical marginalization
- Respect for ongoing peace processes and reconciliation efforts
- Understanding of displacement and conflict impacts on communities"""

    def get_detailed_context(self) -> str:
        """Get comprehensive cultural context for specialized guidance."""
        return f"""{self.get_base_context()}

DETAILED CULTURAL CONSIDERATIONS:

Traditional Governance and Leadership:
{chr(10).join(f"- {item}" for item in self.traditional_governance)}

Islamic Integration Requirements:
{chr(10).join(f"- {item}" for item in self.islamic_principles)}

Economic and Livelihood Patterns:
{chr(10).join(f"- {item}" for item in self.economic_patterns)}

Core Cultural Values:
{chr(10).join(f"- {key.upper()}: {value}" for key, value in self.cultural_values.items())}

Historical Trauma Considerations:
{chr(10).join(f"- {key.replace('_', ' ').title()}: {value}" for key, value in self.historical_context.items())}

Language Considerations:
- Multiple languages: Filipino, English, Arabic, and various Bangsamoro languages
- Islamic terminology should be used appropriately and respectfully
- Code-switching between languages is common and acceptable

Gender and Age Considerations:
- Respect for traditional gender roles while promoting inclusive participation
- Special consideration for women's participation in culturally appropriate ways
- Youth engagement through Islamic education and traditional mentorship
- Elder consultation and wisdom integration

Religious Observances:
- Prayer times (Salah) and Friday prayers (Jummah)
- Ramadan fasting period considerations
- Hajj and Umrah pilgrimage seasons
- Islamic holidays and celebrations (Eid al-Fitr, Eid al-Adha)

Educational Integration:
- Madaris (Islamic schools) integration with public education
- Arabic language instruction importance
- Islamic studies curriculum considerations
- Traditional knowledge preservation and transmission"""

    def get_policy_guidelines(self) -> Dict[str, List[str]]:
        """Get specific guidelines for policy development."""
        return {
            "consultation_requirements": [
                "Engage traditional leaders (Datu, Sultan) early in planning",
                "Conduct proper community consultation (Shura) processes",
                "Include women through culturally appropriate mechanisms",
                "Involve religious leaders (Imam, Ustadz) in relevant policies",
                "Ensure youth participation through educational institutions",
            ],
            "implementation_considerations": [
                "Schedule around Islamic prayer times and religious observances",
                "Provide Halal food options in all programs",
                "Respect traditional conflict resolution mechanisms (Rido settlement)",
                "Consider extended family decision-making processes",
                "Allow for consensus-building time (not rushed decisions)",
            ],
            "communication_strategies": [
                "Use respectful Islamic greetings (Assalamu Alaikum)",
                "Incorporate Arabic and local language terms appropriately",
                "Acknowledge traditional authority structures",
                "Frame benefits in terms of community welfare (Maslaha)",
                "Emphasize alignment with Islamic values and teachings",
            ],
            "risk_mitigation": [
                "Address potential clan conflicts (Rido) proactively",
                "Ensure equitable distribution among ethnolinguistic groups",
                "Avoid disrupting traditional economic patterns without alternatives",
                "Respect religious boundaries and prohibitions",
                "Consider historical trauma and trust-building needs",
            ],
        }

    def validate_cultural_appropriateness(self, policy_content: str) -> Dict[str, any]:
        """Validate policy content for cultural appropriateness."""
        issues = []
        recommendations = []

        # Check for Islamic compatibility
        if "alcohol" in policy_content.lower() or "pork" in policy_content.lower():
            issues.append("Content may conflict with Islamic dietary restrictions")
            recommendations.append(
                "Ensure all food-related policies specify Halal requirements"
            )

        # Check for traditional authority recognition
        if (
            "government" in policy_content.lower()
            and "traditional" not in policy_content.lower()
        ):
            recommendations.append(
                "Consider mentioning coordination with traditional leaders"
            )

        # Check for gender sensitivity
        if "women" in policy_content.lower():
            if "culturally appropriate" not in policy_content.lower():
                recommendations.append(
                    "Specify culturally appropriate mechanisms for women's participation"
                )

        # Check for religious considerations
        if (
            "education" in policy_content.lower()
            and "madaris" not in policy_content.lower()
        ):
            recommendations.append(
                "Consider integration with Islamic education (Madaris) systems"
            )

        # Check for economic considerations
        if (
            "economic" in policy_content.lower()
            or "livelihood" in policy_content.lower()
        ):
            if "halal" not in policy_content.lower():
                recommendations.append(
                    "Include Halal industry development opportunities"
                )

        return {
            "cultural_issues": issues,
            "recommendations": recommendations,
            "appropriateness_score": max(0, 10 - len(issues) * 2),
            "assessment_date": timezone.now().isoformat(),
        }

    def get_appropriate_terminology(self) -> Dict[str, str]:
        """Get culturally appropriate terminology for common concepts."""
        return {
            "community_meeting": "Shura (community consultation)",
            "leader": "Datu, Sultan, or traditional leader",
            "conflict_resolution": "Rido settlement or traditional mediation",
            "community_service": "Bayanihan or mutual assistance",
            "respect": "Respeto or Maratabat",
            "consultation": "Pakikipagkunware or Shura",
            "agreement": "Kasunduan or traditional compact",
            "development": "Pag-unlad with cultural preservation",
            "education": "Edukasyon including Madaris",
            "healthcare": "Kalusugan with Islamic healing integration",
            "economic_development": "Pag-unlad ng ekonomiya with Halal focus",
            "women_participation": "Pakikilahok ng kababaihan sa kulturang paraan",
            "youth_engagement": "Pakikilahok ng kabataan sa pamamagitan ng edukasyon",
        }

    def get_seasonal_considerations(self) -> Dict[str, List[str]]:
        """Get seasonal and religious calendar considerations."""
        return {
            "ramadan_considerations": [
                "Adjust meeting times to accommodate fasting schedules",
                "Provide iftar (breaking fast) meals during evening meetings",
                "Reduce intensive activities during daytime hours",
                "Plan for increased charitable activities (Zakat)",
                "Respect increased focus on spiritual activities",
            ],
            "hajj_season": [
                "Acknowledge community members on pilgrimage",
                "Respect reduced availability of some community leaders",
                "Plan for celebration and reintegration of returning pilgrims",
                "Consider economic impact of pilgrimage expenses",
            ],
            "eid_celebrations": [
                "Plan community activities around Eid al-Fitr and Eid al-Adha",
                "Respect increased family gathering time",
                "Consider gift-giving and charitable traditions",
                "Acknowledge increased community solidarity periods",
            ],
            "academic_calendar": [
                "Coordinate with Madaris school calendars",
                "Respect Islamic Studies intensive periods",
                "Consider Arabic language learning schedules",
                "Align with both public and Islamic school breaks",
            ],
        }

    def get_stakeholder_mapping(self) -> Dict[str, Dict[str, any]]:
        """Get traditional stakeholder mapping for Bangsamoro communities."""
        return {
            "traditional_leaders": {
                "roles": ["Datu", "Sultan", "Bai (female leader)", "Panglima"],
                "responsibilities": [
                    "Community governance",
                    "Conflict resolution",
                    "Cultural preservation",
                ],
                "engagement_approach": "Formal consultation with proper protocol and respect",
            },
            "religious_leaders": {
                "roles": [
                    "Imam",
                    "Ustadz",
                    "Qadi (Islamic judge)",
                    "Religious scholars",
                ],
                "responsibilities": [
                    "Spiritual guidance",
                    "Islamic education",
                    "Religious compliance",
                ],
                "engagement_approach": "Religious consultation on Islamic compatibility",
            },
            "women_leaders": {
                "roles": ["Bai", "Women's organization leaders", "Mothers' groups"],
                "responsibilities": [
                    "Women's welfare",
                    "Family guidance",
                    "Cultural transmission",
                ],
                "engagement_approach": "Culturally appropriate women-only or mixed consultations",
            },
            "youth_leaders": {
                "roles": [
                    "Student leaders",
                    "Madaris graduates",
                    "Youth organization heads",
                ],
                "responsibilities": [
                    "Youth development",
                    "Education advocacy",
                    "Cultural continuity",
                ],
                "engagement_approach": "Educational institution partnerships and youth programs",
            },
            "economic_leaders": {
                "roles": [
                    "Merchants",
                    "Farmers' leaders",
                    "Fisherfolk leaders",
                    "Craft producers",
                ],
                "responsibilities": [
                    "Economic development",
                    "Livelihood coordination",
                    "Market access",
                ],
                "engagement_approach": "Economic consultation focusing on Halal and traditional livelihoods",
            },
        }
