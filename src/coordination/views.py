"""Frontend views for the coordination module."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import (OrganizationContactFormSet, OrganizationForm,
                    PartnershipDocumentFormSet, PartnershipForm,
                    PartnershipMilestoneFormSet, PartnershipSignatoryFormSet)
from .models import Organization, Partnership


@login_required
def organization_create(request):
    """Render and process the frontend organization creation form."""

    if not request.user.has_perm("coordination.add_organization"):
        raise PermissionDenied

    form_instance = Organization(created_by=request.user)

    if request.method == "POST":
        form = OrganizationForm(request.POST)
        formset = OrganizationContactFormSet(
            request.POST,
            instance=form_instance,
            prefix="contacts",
        )

        if form.is_valid() and formset.is_valid():
            organization = form.save(commit=False)
            organization.created_by = request.user
            organization.save()
            formset.instance = organization
            formset.save()
            messages.success(request, "Organization successfully created.")
            return redirect("common:coordination_organizations")
    else:
        form = OrganizationForm()
        formset = OrganizationContactFormSet(
            instance=form_instance,
            prefix="contacts",
        )

    context = {
        "form": form,
        "formset": formset,
        "return_url": reverse("common:coordination_organizations"),
    }
    return render(request, "coordination/organization_form.html", context)


@login_required
def partnership_create(request):
    """Render and process the frontend partnership creation form."""

    if not request.user.has_perm("coordination.add_partnership"):
        raise PermissionDenied

    partnership_instance = Partnership(created_by=request.user)

    if request.method == "POST":
        form = PartnershipForm(request.POST, request.FILES)
        signatory_formset = PartnershipSignatoryFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            request.POST,
            request.FILES,
            instance=partnership_instance,
            prefix="documents",
        )

        if (
            form.is_valid()
            and signatory_formset.is_valid()
            and milestone_formset.is_valid()
            and document_formset.is_valid()
        ):
            partnership = form.save(commit=False)
            partnership.created_by = request.user
            partnership.save()
            form.save_m2m()

            signatory_formset.instance = partnership
            milestone_formset.instance = partnership
            document_formset.instance = partnership

            signatory_formset.save()
            milestone_formset.save()
            document_formset.save()

            messages.success(request, "Partnership successfully created.")
            return redirect("common:coordination_partnerships")
    else:
        form = PartnershipForm()
        signatory_formset = PartnershipSignatoryFormSet(
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            instance=partnership_instance,
            prefix="documents",
        )

    context = {
        "form": form,
        "signatory_formset": signatory_formset,
        "milestone_formset": milestone_formset,
        "document_formset": document_formset,
        "return_url": reverse("common:coordination_partnerships"),
    }
    return render(request, "coordination/partnership_form.html", context)
