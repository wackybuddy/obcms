"""Community data entry forms and field metadata."""

from django import forms
from django.db import models as django_models

from communities.models import CommunityProfileBase, MunicipalityCoverage, OBCCommunity

from ..models import Barangay, Municipality, Province, Region


COMMUNITY_PROFILE_FIELDS = [
    field.name
    for field in CommunityProfileBase._meta.get_fields()
    if isinstance(field, django_models.Field)
    and not field.auto_created
    and field.editable
]

COMMUNITY_PROFILE_WIDGETS = {
    "obc_id": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "e.g., R12-SK-PAL-001"}
    ),
    "community_names": forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Common name(s) used for the community",
        }
    ),
    "purok_sitio": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Specific Purok/Sitio"}
    ),
    "specific_location": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Additional location details"}
    ),
    "languages_spoken": forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Languages spoken (comma-separated)",
        }
    ),
    "other_ethnolinguistic_groups": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Other groups (comma-separated)"}
    ),
    "community_leader": forms.TextInput(attrs={"class": "form-control"}),
    "leader_contact": forms.TextInput(attrs={"class": "form-control"}),
    "estimated_obc_population": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "total_barangay_population": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "households": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "families": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "children_0_9": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "adolescents_10_14": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "youth_15_30": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "adults_31_59": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "seniors_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "women_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "solo_parents_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "pwd_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "farmers_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "fisherfolk_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "indigenous_peoples_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "idps_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "csos_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "associations_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "unemployed_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "migrants_transients_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "religious_leaders_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "established_year": forms.NumberInput(
        attrs={"class": "form-control", "min": "1800", "max": "2030"}
    ),
    "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    "number_of_employed_obc": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_cooperatives": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_social_enterprises": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_micro_enterprises": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_unbanked_obc": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "settlement_type": forms.Select(attrs={"class": "form-control"}),
    "proximity_to_barmm": forms.Select(attrs={"class": "form-control"}),
    "primary_ethnolinguistic_group": forms.Select(attrs={"class": "form-control"}),
    "estimated_poverty_incidence": forms.Select(attrs={"class": "form-control"}),
    "development_status": forms.Select(attrs={"class": "form-control"}),
    "relationship_with_lgu": forms.Select(attrs={"class": "form-control"}),
    "access_formal_education": forms.Select(attrs={"class": "form-control"}),
    "access_als": forms.Select(attrs={"class": "form-control"}),
    "access_madrasah": forms.Select(attrs={"class": "form-control"}),
    "access_healthcare": forms.Select(attrs={"class": "form-control"}),
    "access_clean_water": forms.Select(attrs={"class": "form-control"}),
    "access_sanitation": forms.Select(attrs={"class": "form-control"}),
    "access_electricity": forms.Select(attrs={"class": "form-control"}),
    "access_roads_transport": forms.Select(attrs={"class": "form-control"}),
    "access_communication": forms.Select(attrs={"class": "form-control"}),
    "source_document_reference": forms.Textarea(
        attrs={"class": "form-control", "rows": 2}
    ),
    "primary_livelihoods": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "secondary_livelihoods": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "land_tenure_issues": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "financial_literacy_access": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "brief_historical_background": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "origin_story": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "migration_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "cultural_practices_traditions": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "religious_affiliation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "traditional_leaders_role": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "cultural_preservation_efforts": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "formal_political_representation": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "informal_leadership_structures": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "community_organizations": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "participation_local_governance": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "access_government_info": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "governance_policy_challenges": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "peace_security_priorities": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "specific_project_proposals": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "key_findings_last_assessment": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "assessment_data_sources": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "identified_gaps": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "key_community_leaders": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "relevant_lgu_officials": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    "other_vulnerable_sectors": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "other_cultural_facilities": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
}

COMMUNITY_PROFILE_LABELS = {
    "obc_id": "OBC ID",
    "source_document_reference": "Source Document Reference",
    "community_names": "Community Name(s)",
    "purok_sitio": "Puro/Sitio",
    "specific_location": "Specific Location",
    "settlement_type": "Settlement Type",
    "proximity_to_barmm": "Proximity to BARMM",
    "estimated_obc_population": "Estimated OBC Population",
    "total_barangay_population": "Total Population",
    "households": "Households",
    "families": "Families",
    "primary_ethnolinguistic_group": "Primary Ethnolinguistic Group",
    "other_ethnolinguistic_groups": "Other Ethnolinguistic Groups",
    "languages_spoken": "Languages Spoken",
    "women_count": "Number of Women",
    "solo_parents_count": "Number of Solo Parents",
    "pwd_count": "Number of PWDs",
    "farmers_count": "Number of Farmers",
    "fisherfolk_count": "Number of Fisherfolk",
    "indigenous_peoples_count": "Number of Indigenous Peoples",
    "idps_count": "Number of IDPs",
    "csos_count": "Number of CSOs",
    "associations_count": "Number of Associations",
    "unemployed_count": "Number of Unemployed",
    "migrants_transients_count": "Number of Migrants/Transients",
    "other_vulnerable_sectors": "Other Vulnerable Sectors",
    "estimated_poverty_incidence": "Estimated Poverty Incidence",
    "number_of_employed_obc": "Number of Employed OBC Individuals",
    "number_of_cooperatives": "Number of Cooperatives",
    "number_of_social_enterprises": "Number of Social Enterprises",
    "number_of_micro_enterprises": "Number of Micro-Enterprises",
    "number_of_unbanked_obc": "Number of Unbanked OBC Individuals",
    "financial_literacy_access": "Financial Literacy Access",
    "access_formal_education": "Access to Formal Education",
    "access_als": "Access to ALS",
    "access_madrasah": "Access to Madrasah",
    "access_healthcare": "Access to Healthcare",
    "access_clean_water": "Access to Clean Water",
    "access_sanitation": "Access to Sanitation (Waste Management)",
    "access_electricity": "Access to Electricity",
    "access_roads_transport": "Access to Roads/Transport",
    "access_communication": "Access to Communication",
    "religious_leaders_count": "Number of Ulama / Religious Leaders",
    "brief_historical_background": "Brief Historical Background",
    "established_year": "Established Year",
    "origin_story": "Origin Story",
    "migration_history": "Migration History",
    "cultural_practices_traditions": "Cultural Practices & Traditions",
    "religious_affiliation": "Religious Affiliation",
    "traditional_leaders_role": "Role of Traditional Leaders",
    "cultural_preservation_efforts": "Cultural Preservation Efforts",
    "mosques_count": "Number of Mosques",
    "madrasah_count": "Number of Madrasah",
    "asatidz_count": "Number of Asatidz",
    "other_cultural_facilities": "Other Cultural Facilities / Assets",
    "formal_political_representation": "Formal Political Representation",
    "informal_leadership_structures": "Informal Leadership Structures",
    "community_organizations": "Community Organizations",
    "relationship_with_lgu": "Relationship with LGU",
    "participation_local_governance": "Participation in Local Governance",
    "access_government_info": "Access to Government Information",
    "governance_policy_challenges": "Governance & Policy Challenges",
    "access_public_services_challenges": "Access to Public Services Challenges",
    "land_ownership_security_issues": "Land Ownership & Security Issues",
    "economic_disparities": "Economic Disparities",
    "social_instability_conflict": "Social Instability / Conflict",
    "cultural_miscommunication": "Cultural Miscommunication",
    "gender_inequality_issues": "Gender Inequality Issues",
    "substance_abuse_issues": "Substance Abuse Issues",
    "investment_scam_issues": "Investment Scam Issues",
    "environmental_degradation": "Environmental Degradation",
    "other_challenges": "Other Challenges",
    "challenges_impact": "Impact of Challenges",
    "key_aspirations": "Key Aspirations",
    "infrastructure_priorities": "Infrastructure Priorities",
    "livelihood_program_priorities": "Livelihood Program Priorities",
    "education_priorities": "Education Priorities",
    "healthcare_priorities": "Healthcare Priorities",
    "cultural_preservation_priorities": "Cultural Preservation Priorities",
    "peace_security_priorities": "Peace & Security Priorities",
    "specific_project_proposals": "Specific Project Proposals",
    "development_status": "Development Status",
    "needs_assessment_date": "Needs Assessment Date",
    "key_findings_last_assessment": "Key Findings (Last Assessment)",
    "assessment_data_sources": "Assessment Data Sources",
    "identified_gaps": "Identified Gaps",
    "key_community_leaders": "Key Community Leaders",
    "relevant_lgu_officials": "Relevant LGU Officials",
    "community_leader": "Primary Community Leader",
    "leader_contact": "Community Leader Contact",
    "is_active": "Active Record",
    "notes": "Additional Notes",
}


class MunicipalityCoverageForm(forms.ModelForm):
    """Form for recording municipalities or cities with Bangsamoro presence."""

    region = forms.ModelChoiceField(
        queryset=Region.objects.none(),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )
    class Meta:
        model = MunicipalityCoverage
        fields = (
            "municipality",
            "total_obc_communities",
            "existing_support_programs",
            "auto_sync",
            *COMMUNITY_PROFILE_FIELDS,
        )
        widgets = {
            "municipality": forms.Select(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "total_obc_communities": forms.NumberInput(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                }
            ),
            "existing_support_programs": forms.Textarea(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                }
            ),
            "auto_sync": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                }
            ),
            **COMMUNITY_PROFILE_WIDGETS,
        }
        labels = {
            "municipality": "Municipality / City",
            "total_obc_communities": "Identified Bangsamoro Communities",
            "existing_support_programs": "Existing Support Programs",
            "auto_sync": "Automatically sync totals from barangay communities",
            **COMMUNITY_PROFILE_LABELS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select_attrs = {
            "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
        }

        def resolve_instance(model, value):
            if not value:
                return None
            if isinstance(value, model):
                return value
            try:
                return model.objects.get(pk=value)
            except model.DoesNotExist:
                return None

        region_field = self.fields.get("region")
        province_field = self.fields.get("province")
        municipality_field = self.fields.get("municipality")

        if region_field:
            region_field.queryset = Region.objects.filter(is_active=True).order_by(
                "code", "name"
            )
            region_field.empty_label = "Select region..."
            region_field.widget.attrs.update(select_attrs)

        if province_field:
            province_field.empty_label = "Select province..."
            province_field.widget.attrs.update(select_attrs)

        if municipality_field:
            municipality_field.widget.attrs.update(select_attrs)

        selected_region = None
        selected_province = None
        selected_municipality = None

        if self.instance and getattr(self.instance, "municipality", None):
            selected_municipality = self.instance.municipality
            selected_province = selected_municipality.province
            selected_region = selected_province.region

        if self.initial.get("region"):
            selected_region = resolve_instance(Region, self.initial.get("region"))
        if self.initial.get("province"):
            selected_province = resolve_instance(
                Province, self.initial.get("province")
            )
        if self.initial.get("municipality"):
            selected_municipality = resolve_instance(
                Municipality, self.initial.get("municipality")
            )

        if self.is_bound:
            selected_region = resolve_instance(Region, self.data.get("region")) or selected_region
            selected_province = resolve_instance(
                Province, self.data.get("province")
            ) or selected_province
            selected_municipality = resolve_instance(
                Municipality, self.data.get("municipality")
            ) or selected_municipality

        if province_field:
            if selected_region:
                province_field.queryset = Province.objects.filter(
                    region=selected_region, is_active=True
                ).order_by("name")
            else:
                province_field.queryset = Province.objects.none()

        if municipality_field:
            municipality_queryset = (
                Municipality.objects.filter(is_active=True)
                .select_related("province__region")
                .order_by("province__region__name", "province__name", "name")
            )
            if selected_province:
                municipality_queryset = municipality_queryset.filter(
                    province=selected_province
                )
            else:
                selected_municipality = None

            if selected_region and not selected_province:
                municipality_queryset = municipality_queryset.filter(
                    province__region=selected_region
                )

            existing_coverage_ids = set(
                MunicipalityCoverage.objects.values_list("municipality_id", flat=True)
            )
            if selected_municipality:
                existing_coverage_ids.discard(selected_municipality.id)

            if existing_coverage_ids:
                municipality_queryset = municipality_queryset.exclude(
                    pk__in=existing_coverage_ids
                )

            municipality_field.queryset = municipality_queryset

        if not self.is_bound:
            if region_field and selected_region:
                region_field.initial = selected_region
            if province_field and selected_province:
                province_field.initial = selected_province
            if municipality_field and selected_municipality:
                municipality_field.initial = selected_municipality

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        province = cleaned_data.get("province")
        municipality = cleaned_data.get("municipality")

        if province and region and province.region_id != region.id:
            self.add_error(
                "province", "Selected province does not belong to the chosen region."
            )

        if municipality and province and municipality.province_id != province.id:
            self.add_error(
                "municipality",
                "Selected municipality/city does not belong to the chosen province.",
            )

        return cleaned_data


class OBCCommunityForm(forms.ModelForm):
    """Comprehensive form for creating or editing OBC communities."""

    region = forms.ModelChoiceField(
        queryset=Region.objects.none(),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        required=True,
        label="Municipality / City",
    )

    class Meta:
        model = OBCCommunity
        fields = ["barangay", *COMMUNITY_PROFILE_FIELDS]
        widgets = {
            "barangay": forms.Select(attrs={"class": "form-control"}),
            **COMMUNITY_PROFILE_WIDGETS,
        }
        labels = {
            "barangay": "Barangay",
            **COMMUNITY_PROFILE_LABELS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select_attrs = {
            "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
        }

        def resolve_instance(model, value):
            if not value:
                return None
            if isinstance(value, model):
                return value
            try:
                return model.objects.get(pk=value)
            except model.DoesNotExist:
                return None

        region_field = self.fields.get("region")
        province_field = self.fields.get("province")
        municipality_field = self.fields.get("municipality")
        barangay_field = self.fields.get("barangay")

        if region_field:
            region_field.queryset = Region.objects.filter(is_active=True).order_by(
                "code", "name"
            )
            region_field.empty_label = "Select region..."
            region_field.widget.attrs.update(select_attrs)

        if province_field:
            province_field.empty_label = "Select province..."
            province_field.widget.attrs.update(select_attrs)

        if municipality_field:
            municipality_field.empty_label = "Select municipality/city..."
            municipality_field.widget.attrs.update(select_attrs)

        if barangay_field:
            barangay_field.empty_label = "Select barangay..."
            barangay_field.widget.attrs.update(select_attrs)

        selected_region = None
        selected_province = None
        selected_municipality = None
        selected_barangay = None

        if self.instance and getattr(self.instance, "barangay", None):
            selected_barangay = self.instance.barangay
            selected_municipality = selected_barangay.municipality
            selected_province = selected_municipality.province
            selected_region = selected_province.region

        if self.initial.get("region"):
            selected_region = resolve_instance(Region, self.initial.get("region"))
        if self.initial.get("province"):
            selected_province = resolve_instance(
                Province, self.initial.get("province")
            )
        if self.initial.get("municipality"):
            selected_municipality = resolve_instance(
                Municipality, self.initial.get("municipality")
            )
        if self.initial.get("barangay"):
            selected_barangay = resolve_instance(
                Barangay, self.initial.get("barangay")
            )

        if self.is_bound:
            selected_region = resolve_instance(Region, self.data.get("region")) or selected_region
            selected_province = resolve_instance(
                Province, self.data.get("province")
            ) or selected_province
            selected_municipality = resolve_instance(
                Municipality, self.data.get("municipality")
            ) or selected_municipality
            selected_barangay = resolve_instance(
                Barangay, self.data.get("barangay")
            ) or selected_barangay

        if province_field:
            if selected_region:
                province_field.queryset = Province.objects.filter(
                    region=selected_region, is_active=True
                ).order_by("name")
            else:
                province_field.queryset = Province.objects.none()

        if municipality_field:
            municipality_queryset = (
                Municipality.objects.filter(is_active=True)
                .select_related("province__region")
                .order_by("province__region__name", "province__name", "name")
            )
            if selected_province:
                municipality_queryset = municipality_queryset.filter(
                    province=selected_province
                )
            else:
                selected_municipality = None

            if selected_region and not selected_province:
                municipality_queryset = municipality_queryset.filter(
                    province__region=selected_region
                )

            municipality_field.queryset = municipality_queryset

        if barangay_field:
            barangay_queryset = (
                Barangay.objects.filter(is_active=True)
                .select_related("municipality__province__region")
                .order_by("municipality__province__region__name", "municipality__name", "name")
            )
            if selected_municipality:
                barangay_queryset = barangay_queryset.filter(
                    municipality=selected_municipality
                )
            elif selected_province:
                barangay_queryset = barangay_queryset.filter(
                    municipality__province=selected_province
                )
            elif selected_region:
                barangay_queryset = barangay_queryset.filter(
                    municipality__province__region=selected_region
                )

            barangay_field.queryset = barangay_queryset

        if not self.is_bound:
            if region_field and selected_region:
                region_field.initial = selected_region
            if province_field and selected_province:
                province_field.initial = selected_province
            if municipality_field and selected_municipality:
                municipality_field.initial = selected_municipality
            if barangay_field and selected_barangay:
                barangay_field.initial = selected_barangay

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        province = cleaned_data.get("province")
        municipality = cleaned_data.get("municipality")
        barangay = cleaned_data.get("barangay")

        if province and region and province.region_id != region.id:
            self.add_error(
                "province", "Selected province does not belong to the chosen region."
            )

        if municipality and province and municipality.province_id != province.id:
            self.add_error(
                "municipality",
                "Selected municipality/city does not belong to the chosen province.",
            )

        if barangay and municipality and barangay.municipality_id != municipality.id:
            self.add_error(
                "barangay",
                "Selected barangay does not belong to the chosen municipality/city.",
            )

        return cleaned_data


__all__ = [
    "COMMUNITY_PROFILE_FIELDS",
    "COMMUNITY_PROFILE_WIDGETS",
    "COMMUNITY_PROFILE_LABELS",
    "MunicipalityCoverageForm",
    "OBCCommunityForm",
]
