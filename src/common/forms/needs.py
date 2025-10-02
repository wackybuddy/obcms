"""Forms for community needs submission workflows."""

from django import forms
from django.utils import timezone

from communities.models import OBCCommunity
from mana.models import Need, NeedsCategory


class CommunityNeedSubmissionForm(forms.ModelForm):
    """Model form used by community leaders to submit needs directly."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit choices to active communities and categories for cleaner UX
        self.fields["community"].queryset = (
            OBCCommunity.objects.filter(is_active=True)
            .select_related("barangay__municipality__province")
            .order_by("barangay__municipality__province__name", "barangay__name")
        )
        self.fields["category"].queryset = NeedsCategory.objects.order_by("name")

        # Apply consistent Tailwind-ready classes to widgets
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "")
            if isinstance(field.widget, forms.widgets.TextInput):
                field.widget.attrs.setdefault("placeholder", "")

        self.fields["affected_population"].widget.attrs.setdefault("min", "1")
        self.fields["impact_severity"].widget.attrs.setdefault("min", "1")
        self.fields["impact_severity"].widget.attrs.setdefault("max", "5")
        self.fields["estimated_cost"].widget.attrs.setdefault("min", "0")
        self.fields["estimated_cost"].widget.attrs.setdefault("step", "0.01")

    class Meta:
        model = Need
        fields = [
            "title",
            "description",
            "community",
            "category",
            "geographic_scope",
            "affected_population",
            "affected_households",
            "urgency_level",
            "impact_severity",
            "feasibility",
            "estimated_cost",
            "evidence_sources",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "geographic_scope": forms.Textarea(attrs={"rows": 3}),
            "evidence_sources": forms.Textarea(attrs={"rows": 3}),
        }

    def save(self, submitter, commit=True):
        """Persist a community-submitted need with audit metadata."""
        need: Need = super().save(commit=False)
        need.submission_type = Need.SUBMISSION_TYPE_CHOICES[1][0]  # community_submitted
        need.submitted_by_user = submitter
        need.submission_date = timezone.now().date()
        need.identified_by = submitter

        if commit:
            need.save()
            self.save_m2m()
            # Recalculate score after required fields are persisted
            need.priority_score = need.calculate_priority_score()
            need.save(update_fields=["priority_score"])

        return need
