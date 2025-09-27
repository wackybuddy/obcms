"""Public form interfaces for the common app."""

from .auth import CustomLoginForm, UserProfileForm, UserRegistrationForm
from .community import (
    COMMUNITY_PROFILE_FIELDS,
    COMMUNITY_PROFILE_LABELS,
    COMMUNITY_PROFILE_WIDGETS,
    MunicipalityCoverageForm,
    OBCCommunityForm,
)
from .province import ProvinceForm
from .staff import (
    PerformanceTargetForm,
    StaffDevelopmentPlanForm,
    StaffProfileForm,
    StaffTaskForm,
    StaffTeamForm,
    StaffTeamMembershipForm,
    TrainingEnrollmentForm,
    TrainingProgramForm,
)

__all__ = [
    "CustomLoginForm",
    "UserProfileForm",
    "UserRegistrationForm",
    "COMMUNITY_PROFILE_FIELDS",
    "COMMUNITY_PROFILE_LABELS",
    "COMMUNITY_PROFILE_WIDGETS",
    "MunicipalityCoverageForm",
    "OBCCommunityForm",
    "ProvinceForm",
    "StaffProfileForm",
    "StaffTeamForm",
    "StaffTeamMembershipForm",
    "StaffTaskForm",
    "PerformanceTargetForm",
    "TrainingProgramForm",
    "TrainingEnrollmentForm",
    "StaffDevelopmentPlanForm",
]
