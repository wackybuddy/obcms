# MANA Regional Workshop System - Test Credentials & Quick Start

**Created:** 2025-09-30
**Status:** ✅ All accounts pre-approved and ready for testing

---

## 🚀 Quick Start

1. **Start the development server** (if not already running):
   ```bash
   cd src
   ./manage.py runserver
   ```

2. **Access the system**: http://localhost:8000

3. **Login with any test account below**

---

## 🔐 Test Credentials

### Admin Account
```
Username: admin
Password: admin123
Role:     Superuser (full system access)
```

### Facilitator Accounts

**Facilitator 1 (All Regions)**
```
Username: test_facilitator1
Password: password123
Access:   All 4 regional assessments
  - Region IX (Zamboanga Peninsula)
  - Region X (Northern Mindanao)
  - Region XII (SOCCSKSARGEN)
  - Region XIII (Caraga)
```

**Facilitator 2 (Limited)**
```
Username: test_facilitator2
Password: password123
Access:   First 2 regional assessments only
  - Region IX (Zamboanga Peninsula)
  - Region X (Northern Mindanao)
```

### Participant Accounts

**120 Participants Total** (30 per region)
```
Usernames: test_participant001 through test_participant120
Password:  password123 (same for all)

Distribution:
  - Participants 001-030: Region IX (Zamboanga Peninsula)
  - Participants 031-060: Region X (Northern Mindanao)
  - Participants 061-090: Region XII (SOCCSKSARGEN)
  - Participants 091-120: Region XIII (Caraga)

Stakeholder Types (rotating):
  - elder
  - women_leader
  - youth_leader
  - farmer
  - religious_leader
  - business_owner
  - teacher
  - health_worker
```

---

## 📊 Test Data Summary

### Assessments (4 Total)

1. **[TEST] Regional Workshop - Region IX (Zamboanga del Sur) 2025**
   - 30 participants enrolled
   - 5 workshop activities created
   - Province: Zamboanga del Sur

2. **[TEST] Regional Workshop - Region X (Bukidnon) 2025**
   - 30 participants enrolled
   - 5 workshop activities created
   - Province: Bukidnon

3. **[TEST] Regional Workshop - Region XII (Cotabato) 2025**
   - 30 participants enrolled
   - 5 workshop activities created
   - Province: Cotabato

4. **[TEST] Regional Workshop - Region XIII (Agusan del Sur) 2025**
   - 30 participants enrolled
   - 5 workshop activities created
   - Province: Agusan del Sur

### Workshop Activities (20 Total)

Each assessment has 5 workshops:
- Workshop 1: Understanding the Community Context
- Workshop 2: Community Aspirations and Priorities
- Workshop 3: Community Collaboration and Empowerment
- Workshop 4: Community Feedback on Existing Initiatives
- Workshop 5: OBCs Needs, Challenges, Factors, and Outcomes

**Current Status:** All participants are at Workshop 1, waiting for facilitator advancement.

---

## 🧪 Testing Workflows

### 1. Facilitator Workflow

**Login as:** test_facilitator1 / password123

**Steps:**
1. Navigate to http://localhost:8000/login/
2. Login with facilitator credentials
3. You'll be redirected to assessment selection dashboard
4. Click on any assessment to view facilitator dashboard
5. Monitor participant progress (0/30 submitted for Workshop 1)
6. Participants can now start workshops
7. After submissions, click "Advance All Participants" button
8. Confirm advancement in modal
9. All 30 participants unlock Workshop 2

**Key URLs:**
- Assessment Selection: http://localhost:8000/mana/facilitator/assessments/
- Facilitator Dashboard: http://localhost:8000/mana/facilitator/{assessment_id}/
- Regional Overview: http://localhost:8000/mana/regional/

### 2. Participant Workflow

**Login as:** test_participant001 / password123 (or any 001-120)

**Steps:**
1. Navigate to http://localhost:8000/login/
2. Login with participant credentials
3. You'll be redirected to assessment selection dashboard
4. Click "Continue Assessment" to access workshop dashboard
5. Click "Start Workshop" for Workshop 1
6. Fill out workshop questions
7. Submit workshop
8. Review your submissions on outputs page
9. See "Waiting for facilitator" banner
10. After facilitator advances, see "Next Workshop Available" banner
11. Receive in-app notification
12. Click notification to start Workshop 2

**Key URLs:**
- Assessment Selection: http://localhost:8000/mana/participant/assessments/
- Workshop Dashboard: http://localhost:8000/mana/participant/{assessment_id}/
- Workshop Detail: http://localhost:8000/mana/participant/{assessment_id}/workshop/{workshop_type}/
- Workshop Outputs: http://localhost:8000/mana/participant/{assessment_id}/workshop/{workshop_type}/outputs/

### 3. Staff/Admin Workflow

**Login as:** admin / admin123

**Steps:**
1. Navigate to http://localhost:8000/login/
2. Login with admin credentials
3. Access MANA Regional Overview: http://localhost:8000/mana/regional/
4. Click "Create MANA Facilitator / Participant Account"
5. Create new facilitator or participant with assessment assignment
6. Access admin panel: http://localhost:8000/admin/
7. Manage assessments, participants, and workshop activities

**Key URLs:**
- Admin Panel: http://localhost:8000/admin/
- Regional Overview: http://localhost:8000/mana/regional/
- Create Account: http://localhost:8000/mana/workshops/create-account/
- Manage Assessments: http://localhost:8000/mana/manage-assessments/

---

## 🔍 Verification Queries

### Check Test Data in Django Shell

```bash
cd src
./manage.py shell
```

```python
from mana.models import Assessment, WorkshopParticipantAccount, WorkshopActivity
from django.contrib.auth import get_user_model
User = get_user_model()

# Verify counts
print(f"Assessments: {Assessment.objects.filter(title__startswith='[TEST]').count()}")  # Should be 4
print(f"Participants: {WorkshopParticipantAccount.objects.count()}")  # Should be 120
print(f"Workshop Activities: {WorkshopActivity.objects.filter(assessment__title__startswith='[TEST]').count()}")  # Should be 20
print(f"Test Users: {User.objects.filter(username__startswith='test_').count()}")  # Should be 122

# Check specific assessment
assessment = Assessment.objects.filter(title__contains='Region IX').first()
print(f"\nRegion IX Assessment: {assessment.title}")
print(f"Participants: {WorkshopParticipantAccount.objects.filter(assessment=assessment).count()}")  # Should be 30
print(f"Workshops: {WorkshopActivity.objects.filter(assessment=assessment).count()}")  # Should be 5
```

---

## 🎯 Test Scenarios

### Scenario 1: Basic Participant Flow
1. Login as `test_participant001`
2. Complete Workshop 1
3. Submit and verify outputs page shows "Waiting for facilitator"
4. Logout

### Scenario 2: Facilitator Advancement
1. Login as `test_facilitator1`
2. Navigate to Region IX assessment
3. Wait for at least 1 participant to submit Workshop 1
4. Click "Advance All Participants to Workshop 2"
5. Confirm advancement
6. Verify all participants (including non-submitters) are advanced

### Scenario 3: Notification System
1. Have a participant logged in during advancement
2. Facilitator advances cohort
3. Participant sees blue notification banner
4. Click "Start Workshop" link from notification
5. Access Workshop 2 directly

### Scenario 4: Large Cohort Testing
1. Login as 10+ participants simultaneously (use different browsers/incognito)
2. Have them all submit Workshop 1
3. Facilitator advances all 30 participants
4. Verify system handles bulk operations smoothly

### Scenario 5: Assignment-Based Access Control
1. Login as `test_facilitator2`
2. Verify can ONLY see first 2 assessments (Region IX and X)
3. Cannot access Region XII or XIII assessments
4. Demonstrates predetermined assignment enforcement

---

## 📝 Notes

- **All accounts are pre-approved** - No need to manually activate users
- **Passwords are the same** - `password123` for all test accounts
- **Test data is persistent** - Run `./manage.py setup_mana_test_data --reset` to recreate
- **Server runs at** - http://localhost:8000 (default Django dev server)
- **Database** - SQLite3 at `src/db.sqlite3`

---

## 🔧 Maintenance Commands

### Reset All Test Data
```bash
cd src
./manage.py setup_mana_test_data --reset
```

### Approve All Test Accounts
```bash
cd src
./manage.py approve_test_participants
```

### Check System Status
```bash
cd src
./manage.py check
```

### View Migrations
```bash
cd src
./manage.py showmigrations mana
```

---

## ✅ System Verification Checklist

- [x] Django server running on port 8000
- [x] 4 regional assessments created
- [x] 120 participants enrolled (30 per region)
- [x] 20 workshop activities created (5 per assessment)
- [x] 2 facilitators with proper permissions
- [x] All users pre-approved and active
- [x] Facilitator assignments configured
- [x] Participant accounts linked to assessments
- [x] Workshop access control enabled
- [x] Notification system operational
- [x] Database migrations applied
- [x] No Django system check errors

**Status:** ✅ **READY FOR COMPREHENSIVE TESTING**

---

*Generated: 2025-09-30*
*For questions or issues, refer to: `/docs/improvements/mana/integration_test_scenarios.md`*