# Region X Demo - Testing Guide

## Overview
A fully populated Region X MANA workshop demo with 30 participants who have all completed Workshop 1.

## Assessment Details
- **Assessment**: [TEST] Regional Workshop - Region X (Bukidnon) 2025
- **Assessment ID**: `731841af-afe5-41cc-8e13-79d676b2a95e`
- **Province**: Bukidnon
- **Region**: Region X (Northern Mindanao)

## Participants
- **Total**: 30 participants
- **Username Range**: `test_participant031` to `test_participant060`
- **Password**: `password123` (for all participants)
- **Status**: All have completed and submitted Workshop 1

## Facilitator
- **Username**: `test_facilitator1`
- **Password**: `password123`
- **Name**: Facilitator Test1
- **Permissions**: Can facilitate workshops

## Workshop Data
- **Workshop**: Workshop 1: Understanding the Community Context
- **Questions**: 8 questions covering:
  1. Basic services challenges (education, health, water, electricity)
  2. Islamic education facilities status
  3. Livelihood sources and challenges
  4. Government relationship rating
  5. Cultural practices to preserve
  6. Government programs impact
  7. Priority needs
  8. Community participation in governance

- **Responses**: 240 total (30 participants × 8 questions)
- **Status**: All responses submitted with realistic community assessment data

## Testing URLs

### Facilitator Dashboard
```
http://localhost:8000/mana/workshops/assessments/731841af-afe5-41cc-8e13-79d676b2a95e/facilitator/dashboard/
```

### Participant Portal (General)
```
http://localhost:8000/mana/workshops/participant/assessments/
```

### MANA Regional Overview
```
http://localhost:8000/mana/regional-overview/
```

## Test Scenarios

### 1. Facilitator View (Login as `test_facilitator1`)
- View Region X dashboard
- See all 30 participants with submitted Workshop 1 responses
- Review individual participant responses
- Test advancement workflow (advance cohort to Workshop 2)
- Verify notifications are created for participants

### 2. Participant View (Login as `test_participant031` to `test_participant060`)
- View Workshop 1 completed status
- See submitted responses
- Verify cannot access Workshop 2 until facilitator advances
- Test response review functionality

### 3. Regional Overview (Login as admin)
- See Region X assessment in regional overview
- View progress statistics (30/30 participants completed Workshop 1)
- Monitor workshop completion rates

## Sample Response Data

**Question 1 (Basic Services)** - Examples:
- "Our community struggles with limited access to clean water, especially during dry season. The health center is understaffed and lacks essential medicines. Many children walk 5km to reach the nearest secondary school."
- "Education infrastructure is inadequate with overcrowded classrooms. We have frequent power outages affecting businesses..."

**Question 4 (Government Relationship)** - Distribution:
- Good, Fair, Fair, Good, Poor, Fair, Good, Fair, Fair, Good... (10 variations)

**Question 7 (Priority Need)** - Distribution:
- Education, Healthcare, Infrastructure, Livelihood, Water/Sanitation (rotating)

## Management Command

To regenerate the demo data:
```bash
cd src
./manage.py setup_region_x_demo
```

To reset all workshop data:
```bash
./manage.py shell -c "from mana.models import WorkshopResponse, WorkshopQuestionDefinition, WorkshopParticipantAccount; WorkshopResponse.objects.all().delete(); WorkshopQuestionDefinition.objects.all().delete(); WorkshopParticipantAccount.objects.update(completed_workshops=[], current_workshop='workshop_1', facilitator_advanced_to='workshop_1')"
```

## Verification

All data verified:
- ✅ 30 participants enrolled in Region X
- ✅ All 30 completed Workshop 1
- ✅ 240 responses submitted (30 × 8 questions)
- ✅ All responses have realistic community data
- ✅ Participants marked as completed Workshop 1
- ✅ Facilitator assigned to assessment
- ✅ Workshop questions created with correct schema

## Next Steps for Testing

1. **Login as facilitator** (`test_facilitator1` / `password123`)
2. **Navigate to facilitator dashboard** for Region X
3. **Review all 30 participant responses** - verify data displays correctly
4. **Test advancement workflow**:
   - Select all participants
   - Advance cohort from Workshop 1 to Workshop 2
   - Verify notifications are created
   - Verify participant status updates
5. **Login as participant** (`test_participant031` / `password123`)
6. **Verify participant experience**:
   - See Workshop 1 marked as completed
   - Can view submitted responses
   - Workshop 2 becomes accessible after facilitator advancement
7. **Test notification system** - participants should receive advancement notifications

---

**Created**: 2025-09-30
**Status**: ✅ Ready for comprehensive testing
**Command**: `./manage.py setup_region_x_demo`