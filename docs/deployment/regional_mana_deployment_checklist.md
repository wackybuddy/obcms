# Regional MANA Workshop Deployment Checklist

**Pre-Deployment, Deployment, and Post-Deployment Tasks**

---

## Overview

This checklist ensures the successful deployment and rollout of the Regional MANA Workshop digital platform. Follow each section in order for a smooth launch.

---

## Phase 1: Pre-Deployment (2-3 Weeks Before Launch)

### Technical Infrastructure

- [ ] **Database Migrations**
  ```bash
  cd src
  ./manage.py makemigrations
  ./manage.py migrate
  ```
  - [ ] Verify `WorkshopParticipantAccount` table exists
  - [ ] Verify `WorkshopResponse` table exists
  - [ ] Verify `WorkshopSynthesis` table exists
  - [ ] Verify `WorkshopAccessLog` table exists
  - [ ] Verify `WorkshopQuestionDefinition` table exists
  - [ ] Verify `WorkshopMetricsSnapshot` table exists (if metrics implemented)
  - [ ] Verify `PerformanceLog` table exists (if metrics implemented)
  - [ ] Verify `OnboardingTracker` table exists (if metrics implemented)

- [ ] **Management Commands**
  ```bash
  # Ensure MANA roles and permissions
  ./manage.py ensure_mana_roles

  # Sync workshop question schema
  ./manage.py sync_mana_question_schema

  # Seed sample workshops (for testing)
  ./manage.py seed_mana_workshops
  ```

- [ ] **Environment Variables**
  - [ ] `ANTHROPIC_API_KEY` configured (if using Claude for synthesis)
  - [ ] `OPENAI_API_KEY` configured (if using OpenAI for synthesis)
  - [ ] `AI_SYNTHESIS_MODEL` set (optional, defaults per provider)
  - [ ] `MANA_ASYNC_ENABLED` set to `True` (if Celery configured)
  - [ ] `REDIS_URL` configured (if using Celery for async tasks)

- [ ] **Celery & Background Tasks** (Optional but Recommended)
  - [ ] Redis server running
  - [ ] Celery worker started: `celery -A obc_management worker -l info`
  - [ ] Celery beat started (for scheduled tasks): `celery -A obc_management beat -l info`
  - [ ] Test synthesis task queuing: Check Celery logs

- [ ] **Static Files & Templates**
  ```bash
  ./manage.py collectstatic --noinput
  ```
  - [ ] Verify HTMX loaded in base template
  - [ ] Verify Tailwind CSS compiled
  - [ ] Test template rendering (visit participant dashboard URL while logged in as test participant)

- [ ] **Permissions & Groups**
  - [ ] `mana_regional_participant` group exists
  - [ ] `mana_facilitator` group exists
  - [ ] `mana_admin` group exists
  - [ ] Custom permissions exist:
    - [ ] `can_access_regional_mana`
    - [ ] `can_view_provincial_obc`
    - [ ] `can_facilitate_workshop`

### Test Data Setup

- [ ] **Create Test Assessment**
  ```bash
  # Via Django Admin or management command
  ```
  - [ ] Assessment created with regional level
  - [ ] Province assigned (e.g., Zamboanga del Sur)
  - [ ] 5 WorkshopActivity records created (workshop_1 through workshop_5)

- [ ] **Create Test Facilitator**
  - [ ] User account created
  - [ ] Added to `mana_facilitator` group
  - [ ] Assigned facilitator permissions
  - [ ] Can log in and access facilitator dashboard

- [ ] **Create Test Participants** (at least 5)
  - [ ] User accounts created
  - [ ] WorkshopParticipantAccount created for each
  - [ ] Diverse stakeholder types represented
  - [ ] Different provinces represented
  - [ ] Temporary passwords saved

### Testing

- [ ] **Participant Workflow**
  - [ ] Participant can log in with temporary password
  - [ ] Forced password change works
  - [ ] Onboarding form displays correctly
  - [ ] Profile completion redirects to dashboard
  - [ ] Workshop 1 is unlocked
  - [ ] Workshops 2-5 are locked
  - [ ] Can open Workshop 1
  - [ ] Can answer all question types (text, textarea, select, repeater, structured)
  - [ ] Autosave works (wait 1-2 seconds, check indicator)
  - [ ] Save draft works
  - [ ] Submit workshop works
  - [ ] Workshop 2 unlocks after submission
  - [ ] Completed workshop remains accessible for review

- [ ] **Facilitator Workflow**
  - [ ] Facilitator can log in
  - [ ] Can access facilitator dashboard
  - [ ] Can view all participants
  - [ ] Can add single participant
  - [ ] Can bulk import participants via CSV
  - [ ] Can view workshop responses
  - [ ] Filters work (province, stakeholder)
  - [ ] Can generate AI synthesis (if API keys configured)
  - [ ] Can regenerate synthesis
  - [ ] Can approve synthesis
  - [ ] Can export CSV
  - [ ] Can export XLSX (if openpyxl installed)
  - [ ] Can export PDF (if reportlab installed)
  - [ ] Can reset participant progress
  - [ ] Can advance all participants

- [ ] **HTMX Interactions**
  - [ ] Autosave updates status without page reload
  - [ ] Filters update responses without page reload
  - [ ] Workshop navigation updates without page reload
  - [ ] Synthesis generation shows toast notification
  - [ ] Participant reset shows confirmation and updates table

- [ ] **Performance**
  - [ ] Export of 100 responses completes in ≤10 seconds
  - [ ] Synthesis completes in ≤30 seconds average
  - [ ] Dashboard loads in ≤3 seconds with 50 participants
  - [ ] No JavaScript console errors
  - [ ] No 500 server errors in logs

- [ ] **Security**
  - [ ] Participant cannot access facilitator dashboard
  - [ ] Participant cannot access other participants' responses
  - [ ] Participant cannot skip workshops
  - [ ] Facilitator requires proper permissions
  - [ ] CSRF protection enabled
  - [ ] SQL injection prevented (parameterized queries)
  - [ ] XSS prevention (template auto-escaping)

- [ ] **Browser Compatibility**
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Edge (latest)
  - [ ] Safari (if Mac/iOS users expected)
  - [ ] Mobile browsers (Chrome/Safari mobile)

### Documentation

- [ ] **User Guides Complete**
  - [ ] Participant user guide available
  - [ ] Facilitator training guide available
  - [ ] Technical documentation updated

- [ ] **Training Materials**
  - [ ] Facilitator training slides/video prepared
  - [ ] Participant orientation materials prepared
  - [ ] FAQ document created

---

## Phase 2: Deployment (Launch Week)

### Pre-Launch

- [ ] **Backup Current System**
  ```bash
  # Backup database
  pg_dump obcms_db > backup_pre_mana_$(date +%Y%m%d).sql

  # Backup code
  git tag -a regional-mana-v1.0 -m "Regional MANA Workshop Launch"
  git push origin regional-mana-v1.0
  ```

- [ ] **Deploy to Production**
  - [ ] Pull latest code
  - [ ] Run migrations
  - [ ] Collect static files
  - [ ] Restart application server
  - [ ] Restart Celery workers (if applicable)
  - [ ] Clear cache (if applicable)

- [ ] **Post-Deployment Verification**
  - [ ] Application starts without errors
  - [ ] Database connectivity verified
  - [ ] Static files served correctly
  - [ ] HTTPS enabled and working
  - [ ] Background workers running (check Celery status)

### Launch Day

- [ ] **Final Checks** (30 minutes before launch)
  - [ ] System health check passed
  - [ ] API keys working (test synthesis with small dataset)
  - [ ] Email delivery working (if sending notifications)
  - [ ] Support channels active (email, hotline)

- [ ] **Create Production Assessment**
  - [ ] Real assessment record created
  - [ ] Correct provinces assigned
  - [ ] 5 workshops created with correct dates
  - [ ] Workshop descriptions finalized
  - [ ] Questions schema loaded and verified

- [ ] **Import Real Participants**
  - [ ] Participant roster CSV prepared
  - [ ] CSV validated (correct columns, data format)
  - [ ] Bulk import executed
  - [ ] Import results reviewed (success count, errors)
  - [ ] Temporary passwords securely stored

- [ ] **Send Invitations**
  - [ ] Email template finalized
  - [ ] Invitations sent to all participants
  - [ ] Login credentials communicated securely
  - [ ] Participants notified of onboarding deadline

### Monitoring (First 24 Hours)

- [ ] **Track Onboarding**
  - [ ] Monitor login rate (hourly)
  - [ ] Track profile completion rate
  - [ ] Identify and assist struggling participants
  - [ ] Target: ≥50% onboarded within 24 hours

- [ ] **System Monitoring**
  - [ ] Server CPU/memory usage normal
  - [ ] Database performance acceptable
  - [ ] No error spikes in logs
  - [ ] Response times within acceptable range

- [ ] **Support Requests**
  - [ ] Support email monitored continuously
  - [ ] Hotline staffed during business hours
  - [ ] Common issues documented
  - [ ] Quick responses to urgent issues

---

## Phase 3: Post-Deployment (First Week)

### Daily Monitoring

- [ ] **Onboarding Progress**
  - Day 1: [ ] ≥50% participants logged in
  - Day 2: [ ] ≥70% participants logged in
  - Day 3: [ ] ≥85% participants completed profiles
  - Day 5: [ ] ≥90% participants onboarded (TARGET)

- [ ] **Technical Health**
  - [ ] Review error logs daily
  - [ ] Check Celery queue health
  - [ ] Monitor database size and performance
  - [ ] Verify backup jobs running

- [ ] **Support Requests**
  - [ ] Track and resolve support tickets
  - [ ] Identify recurring issues
  - [ ] Update FAQ based on common questions
  - [ ] Escalate critical issues immediately

### Workshop 1 Launch (Usually Day 7-10)

- [ ] **Pre-Workshop**
  - [ ] Send reminder email 2 days before
  - [ ] Verify all participants onboarded
  - [ ] Confirm facilitators trained and ready
  - [ ] Workshop 1 unlocked for all participants

- [ ] **During Workshop 1**
  - [ ] Monitor submission rate daily
  - [ ] Track progress toward ≥85% target
  - [ ] Send mid-workshop reminder (Day 3-4)
  - [ ] Respond to content questions promptly

- [ ] **After Workshop 1**
  - [ ] Generate AI syntheses
  - [ ] Review syntheses for quality
  - [ ] Export data for backup
  - [ ] Advance participants to Workshop 2
  - [ ] Record metrics (submission rate, review time)

### Success Metrics Review (End of Week 1)

- [ ] **Calculate and Record**
  - [ ] Onboarding completion rate: ___% (target: ≥90%)
  - [ ] Workshop 1 submission rate: ___% (target: ≥85%)
  - [ ] Average export time: ___s (target: ≤10s)
  - [ ] Average synthesis time: ___s (target: ≤30s)
  - [ ] Support ticket response time: ___hours

- [ ] **Lessons Learned**
  - [ ] Document what went well
  - [ ] Document issues encountered
  - [ ] Identify improvements for next workshops
  - [ ] Share findings with team

---

## Phase 4: Ongoing Operations (Workshops 2-5)

### Weekly Checklist (Repeat for Each Workshop)

- [ ] **Monday: Workshop Preparation**
  - [ ] Verify previous workshop completion
  - [ ] Unlock next workshop
  - [ ] Send workshop opening notification
  - [ ] Ensure facilitator availability

- [ ] **Wednesday: Mid-Workshop Check**
  - [ ] Review submission rate
  - [ ] Send reminder to non-submitters
  - [ ] Address any blockers
  - [ ] Provide technical support

- [ ] **Friday: Workshop Close**
  - [ ] Final submission reminder
  - [ ] Generate syntheses
  - [ ] Export data
  - [ ] Prepare for next workshop

- [ ] **Saturday/Sunday: Review & Analysis**
  - [ ] Review AI syntheses
  - [ ] Approve final syntheses
  - [ ] Archive workshop data
  - [ ] Advance participants (Monday AM)

### Monthly Review

- [ ] **Performance Metrics**
  - [ ] Average submission rates across workshops
  - [ ] Facilitator review time trends
  - [ ] System performance metrics
  - [ ] Support ticket analysis

- [ ] **Data Quality**
  - [ ] Review response quality
  - [ ] Identify gaps or unclear responses
  - [ ] Adjust questions for future assessments (if needed)

---

## Phase 5: Workshop Series Completion

### Final Workshop (Workshop 5)

- [ ] **Closing Activities**
  - [ ] All participants complete Workshop 5
  - [ ] Final comprehensive synthesis generated
  - [ ] All data exported in all formats (CSV, XLSX, PDF)
  - [ ] Syntheses approved by lead facilitator

### Data Archiving

- [ ] **Complete Dataset Export**
  - [ ] All workshop responses (raw data)
  - [ ] All approved syntheses
  - [ ] Participant roster with anonymized IDs
  - [ ] Metadata (dates, statistics)

- [ ] **Database Backup**
  ```bash
  pg_dump obcms_db > backup_mana_complete_$(date +%Y%m%d).sql
  ```

- [ ] **File Archive**
  - [ ] Store in secure, backed-up location
  - [ ] Follow data retention policy
  - [ ] Document archive location

### Reporting

- [ ] **Final Report Preparation**
  - [ ] Comprehensive synthesis across all 5 workshops
  - [ ] Provincial comparisons
  - [ ] Stakeholder perspective analysis
  - [ ] Key findings and recommendations
  - [ ] Success metrics summary

- [ ] **Presentation Materials**
  - [ ] Executive summary for leadership
  - [ ] Detailed report for program teams
  - [ ] Community feedback summary (if shared back)

### Retrospective

- [ ] **Team Debrief**
  - [ ] What worked well?
  - [ ] What could be improved?
  - [ ] Technical issues encountered?
  - [ ] Process improvements for next assessment?

- [ ] **Participant Feedback** (Optional)
  - [ ] Survey participants about platform experience
  - [ ] Gather suggestions for improvement
  - [ ] Thank participants for their time

---

## Rollback Plan (If Needed)

### When to Rollback

Consider rollback if:
- Critical security vulnerability discovered
- Data corruption or loss
- System downtime exceeds acceptable limits
- Participant data privacy breach

### Rollback Steps

1. [ ] **Notify stakeholders immediately**
2. [ ] **Stop Celery workers** (if running)
3. [ ] **Restore database from backup**
   ```bash
   psql obcms_db < backup_pre_mana_YYYYMMDD.sql
   ```
4. [ ] **Revert code to previous version**
   ```bash
   git checkout <previous-tag>
   ```
5. [ ] **Restart application**
6. [ ] **Verify system stability**
7. [ ] **Communicate with participants** (explain delay, new timeline)
8. [ ] **Root cause analysis** (identify and fix issue before re-deployment)

---

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| **System Administrator** | [Name] | [Email / Phone] |
| **Database Administrator** | [Name] | [Email / Phone] |
| **MANA Program Coordinator** | [Name] | [Email / Phone] |
| **IT Support Lead** | [Name] | [Email / Phone] |
| **OOBC Director** | [Name] | [Email / Phone] |

---

## Sign-Off

**Deployment Approved By:**

- [ ] **Technical Lead**: _________________ Date: _______
- [ ] **MANA Program Coordinator**: _________________ Date: _______
- [ ] **IT Manager**: _________________ Date: _______
- [ ] **OOBC Director**: _________________ Date: _______

---

*Version 1.0 | Last Updated: September 2025 | Office for Other Bangsamoro Communities (OOBC)*