from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


class CustomGroupChangeList:
    """Custom changelist for Group model with our UI"""

    def __init__(
        self,
        request,
        model,
        list_display,
        list_display_links,
        list_filter,
        date_hierarchy,
        search_fields,
        list_select_related,
        list_per_page,
        list_max_show_all,
        list_editable,
        model_admin,
        sortable_by,
    ):
        self.request = request
        self.model = model
        self.list_per_page = list_per_page or 20
        self.search_fields = search_fields

        # Get search query
        self.query = request.GET.get("q", "")

        # Get queryset
        queryset = self.get_queryset()

        # Apply search
        if self.query:
            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f"{field}__icontains": self.query})
            queryset = queryset.filter(search_query)

        # Count results
        self.result_count = queryset.count()

        # Pagination
        paginator = Paginator(queryset, self.list_per_page)
        page_number = request.GET.get("p", 1)

        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            page_number = 1

        self.page_obj = paginator.get_page(page_number)
        self.result_list = self.page_obj.object_list

        # Pagination properties
        self.has_previous = self.page_obj.has_previous()
        self.has_next = self.page_obj.has_next()
        self.page_num = self.page_obj.number
        self.previous_page_number = (
            self.page_obj.previous_page_number() if self.has_previous else None
        )
        self.next_page_number = (
            self.page_obj.next_page_number() if self.has_next else None
        )

        # Calculate page range for pagination display
        total_pages = paginator.num_pages
        current_page = self.page_num

        # Show 5 pages around current page
        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)

        self.page_range = range(start_page, end_page + 1)

        # Result indices for display
        if self.result_count > 0:
            self.start_index = (self.page_num - 1) * self.list_per_page + 1
            self.end_index = min(
                self.start_index + self.list_per_page - 1, self.result_count
            )
        else:
            self.start_index = 0
            self.end_index = 0

    def get_queryset(self):
        return Group.objects.all().order_by("name")


def group_changelist_view(request):
    """Custom view for Group changelist"""

    # Create changelist object
    cl = CustomGroupChangeList(
        request=request,
        model=Group,
        list_display=["name"],
        list_display_links=["name"],
        list_filter=[],
        date_hierarchy=None,
        search_fields=["name"],
        list_select_related=False,
        list_per_page=20,
        list_max_show_all=200,
        list_editable=[],
        model_admin=None,
        sortable_by=None,
    )

    context = {
        "cl": cl,
        "title": "Groups",
        "subtitle": None,
        "has_add_permission": True,
        "has_change_permission": True,
        "has_delete_permission": True,
        "has_view_permission": True,
        "opts": Group._meta,
    }

    return render(request, "admin/auth/group/change_list.html", context)
