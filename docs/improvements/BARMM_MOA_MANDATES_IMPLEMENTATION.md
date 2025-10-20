# BARMM MOA Mandates and Functions Implementation

## Overview
This document describes the implementation of mandates and powers & functions for BARMM Ministries, Offices, and Agencies (MOAs) in the OBC Coordination Management System.

## Changes Made

### 1. Database Schema Updates

**File**: `src/coordination/models.py`

Added two new fields to the `Organization` model:
- `mandate` (TextField, blank=True): Official mandate of the organization
- `powers_and_functions` (TextField, blank=True): Powers and functions of the organization

These fields are particularly useful for government agencies including BARMM MOAs, National Government Agencies (NGAs), and Local Government Units (LGUs).

### 2. Migration
**File**: `src/coordination/migrations/0006_organization_mandate_and_more.py`

Database migration created to add the two new fields to the organizations table.

### 3. Form Template Updates

**File**: `src/templates/coordination/organization_form.html`

Added a new section "Mandate and Powers & Functions" after the "Basic Information" section:
- Displays with a teal/cyan gradient header
- Shows subtitle: "Particularly for Government Agencies (including BARMM Ministries, Offices, and Agencies)"
- Two large textarea fields for mandate and powers & functions
- Positioned strategically after basic info and before contact information

### 4. Detail View Template Updates

**File**: `src/templates/coordination/organization_detail.html`

Added display of mandate and powers & functions in the organization detail view:
- Conditionally shows section only if either field has data
- Mandate displayed in teal-colored box with gavel icon
- Powers & Functions displayed in cyan-colored box with list-check icon
- Uses `whitespace-pre-line` to preserve formatting
- Positioned after basic information and before key personnel section

### 5. BARMM MOA Reference Data

**File**: `src/coordination/barmm_moa_mandates.py`

Created comprehensive reference data for all 16 BARMM Ministries:

1. Office of the Chief Minister
2. Ministry of Agriculture, Fisheries and Agrarian Reform
3. Ministry of Basic, Higher, and Technical Education
4. Ministry of Environment, Natural Resources and Energy
5. Ministry of Finance, and Budget and Management
6. Ministry of Health
7. Ministry of Human Settlements and Development
8. Ministry of Indigenous Peoples' Affairs
9. Ministry of Interior and Local Government
10. Ministry of Labor and Employment
11. Ministry of Public Order and Safety
12. Ministry of Public Works
13. Ministry of Science and Technology
14. Ministry of Social Services and Development
15. Ministry of Trade, Investments, and Tourism
16. Ministry of Transportation and Communications

Each entry includes:
- Full official mandate text from the Bangsamoro Administrative Code
- Comprehensive list of powers and functions

### 6. Management Command

**File**: `src/coordination/management/commands/populate_barmm_moa_mandates.py`

Created a Django management command to automatically populate mandate and powers & functions for BARMM MOAs:

```bash
# Populate mandates for organizations that don't have them yet
./manage.py populate_barmm_moa_mandates

# Update all matching organizations even if they already have mandates
./manage.py populate_barmm_moa_mandates --update-all
```

The command:
- Searches for organizations by name or acronym
- Only updates organizations that don't already have mandates (unless --update-all is used)
- Provides clear feedback about updated, skipped, and not found organizations
- Uses color-coded output for easy reading

## Usage

### For New Organizations

When adding a new BARMM MOA, NGA, or LGU:

1. Navigate to: `http://localhost:8000/coordination/organizations/add/`
2. Fill in Basic Information section (name, acronym, type, etc.)
3. Fill in "Mandate and Powers & Functions" section
4. Complete other sections as needed
5. Save

### For Existing BARMM MOAs

To automatically populate mandates for existing BARMM MOA organizations:

```bash
cd src
./manage.py populate_barmm_moa_mandates
```

### Viewing Mandates

When viewing an organization detail page, the mandate and powers & functions will be displayed:
- In highlighted boxes for easy reading
- With appropriate icons
- Only if the fields contain data

## URL Reference

- **Add Organization**: `http://localhost:8000/coordination/organizations/add/`
- **Edit Organization**: `http://localhost:8000/coordination/organizations/add/?organization={UUID}`
- **View Organization**: `http://localhost:8000/coordination/organizations/{UUID}/`

## Source

All mandate and powers & functions data is sourced from:
- **Bangsamoro Autonomy Act No. 13** (Bangsamoro Administrative Code)
- Effective as of the latest version of the BAC

## Benefits

1. **Comprehensive Documentation**: All BARMM MOA mandates are now documented in the system
2. **Quick Reference**: Staff can quickly reference an agency's official mandate and functions
3. **Coordination Planning**: Better understanding of agency mandates helps in partnership planning
4. **Compliance**: Ensures partnerships align with official agency mandates
5. **Transparency**: Clear documentation of government agency roles and responsibilities

## Technical Notes

- Fields are optional (blank=True) so they don't disrupt existing organization records
- Uses TextField to accommodate long mandate descriptions
- Frontend uses `whitespace-pre-line` to preserve line breaks in formatted text
- Color-coded display (teal for mandate, cyan for powers) for visual distinction
- Responsive design works on mobile and desktop

## Future Enhancements

Potential improvements for future iterations:
1. Add similar data for National Government Agencies (NGAs)
2. Include LGU mandate templates based on Local Government Code
3. Add search/filter by mandate keywords
4. Create mandate comparison tool for partnership planning
5. Link mandates to specific partnership objectives for alignment checking

## Testing

To test the implementation:

1. Access the organization add form
2. Verify "Mandate and Powers & Functions" section appears after Basic Information
3. Enter sample mandate text
4. Save and verify data is stored
5. View organization detail page
6. Verify mandate and powers appear in highlighted boxes
7. Run the management command to populate BARMM MOA data
8. Verify organizations are updated correctly

## Troubleshooting

### Management Command Not Finding Organizations

If the management command reports organizations as "not found":
1. Verify the organization exists in the database
2. Check the organization name matches exactly (case-insensitive)
3. Try matching by acronym if name doesn't match
4. Create the organization first if it doesn't exist

### Mandate Not Displaying

If mandate doesn't appear on detail page:
1. Verify the field was saved (check in admin or edit form)
2. Ensure template has been updated
3. Clear browser cache
4. Restart Django server if needed

## Maintenance

When BARMM Administrative Code is updated:
1. Update `src/coordination/barmm_moa_mandates.py` with new mandate text
2. Run management command with --update-all flag
3. Document changes in commit message