# Regional MANA Workshop Facilitator Training Guide

**For OOBC Workshop Coordinators and Facilitators**

---

## Overview

This guide provides comprehensive training for facilitators managing Regional MANA (Mapping and Needs Assessment) workshops through the OBCMS digital platform. As a facilitator, you'll coordinate participant engagement, monitor progress, and synthesize insights across regions IX and XII.

---

## Table of Contents

1. [Role & Responsibilities](#role--responsibilities)
2. [Pre-Workshop Setup](#pre-workshop-setup)
3. [Managing Participants](#managing-participants)
4. [Monitoring Workshop Progress](#monitoring-workshop-progress)
5. [AI Synthesis & Analysis](#ai-synthesis--analysis)
6. [Exporting Data](#exporting-data)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)
8. [Success Metrics](#success-metrics)

---

## Role & Responsibilities

### As a Facilitator, You Will:

✅ **Before Workshops**
- Import participant rosters
- Send login credentials
- Ensure participants complete onboarding
- Verify technical access for all participants

✅ **During Workshops**
- Monitor submission rates
- Respond to participant questions
- Unlock workshops sequentially
- Track progress across provinces and stakeholder groups

✅ **After Workshops**
- Generate AI syntheses
- Review and approve consolidated insights
- Export data for reporting
- Archive workshop records

### Permissions & Access

Facilitators have permission to:
- View all participant responses
- Reset participant progress (if needed)
- Advance participants to next workshops
- Generate syntheses and exports
- Access provincial and stakeholder-filtered views

---

## Pre-Workshop Setup

### Step 1: Access the Facilitator Dashboard

1. Log in to OBCMS with your facilitator account
2. Navigate to **MANA > Regional Workshops**
3. Select your assessment from the list
4. Click **"Facilitator Dashboard"**

### Step 2: Review Assessment Details

Verify:
- **Assessment title and dates**
- **Target provinces** (IX, XII)
- **Workshop schedule** (5 workshops with dates)
- **Expected participant count**

### Step 3: Import Participants

#### Option A: Single Participant Registration

1. Go to **"Manage Participants"** tab
2. Click **"Add Participant"**
3. Fill in the form:
   - Email (will be their username)
   - First name, Last name
   - Stakeholder type
   - Province, Municipality, Barangay
   - Organization (optional)
   - Temporary password (or leave blank to auto-generate)
4. Click **"Create Participant"**
5. **Save the temporary password** – you'll need to send it to the participant

#### Option B: Bulk CSV Import

1. Prepare a CSV file with columns:
   ```
   email,first_name,last_name,stakeholder_type,province_id,municipality_id,barangay_id,organization,password
   ```

2. Example:
   ```csv
   elder1@community.ph,Juan,Dela Cruz,elder,ZAM,,,Barangay Council,TempPass123
   leader2@org.ph,Maria,Santos,women_leader,ZAN,,,Women's Group,TempPass456
   ```

3. In Facilitator Dashboard, go to **"Manage Participants"**
4. Click **"Bulk Import"**
5. Upload your CSV file
6. Review the preview
7. Click **"Import"**
8. System will create accounts and display results

**⚠️ Important:** Save all usernames and temporary passwords securely. You'll need to communicate these to participants.

### Step 4: Send Invitations

**Email Template:**

```
Subject: Invitation to Regional MANA Workshop Series

Dear [Participant Name],

You are invited to participate in the Regional MANA Workshop Series organized by the Office for Other Bangsamoro Communities (OOBC).

Workshop Platform: [URL]
Your Username: [email]
Temporary Password: [password]

Please log in and complete your profile before Workshop 1 begins on [date].

For technical support, contact: support@oobc.gov.ph

Maraming salamat!
OOBC Team
```

### Step 5: Verify Onboarding

**Target: ≥90% of participants complete onboarding before Workshop 1**

1. Go to **"Participants"** tab
2. Check the **"Progress"** column
3. Identify participants who haven't logged in
4. Follow up via phone/email/text message
5. Provide technical support as needed

---

## Managing Participants

### Viewing Participant List

The participant table shows:
- **Name and email**
- **Stakeholder type**
- **Province**
- **Progress**: X/5 workshops completed (with percentage bar)
- **Actions**: Reset progress button

### Filtering Participants

Use filters to view specific groups:
- **By Province**: See participants from specific provinces
- **By Stakeholder Type**: View farmers, elders, youth leaders, etc.
- **By Completion Status**: Filter who's ahead/behind

### Resetting Participant Progress

**When to Reset:**
- Participant accidentally submitted too early
- Participant wants to revise answers
- Technical issue corrupted responses

**How to Reset:**
1. Find the participant in the list
2. Click **"Reset"** button in their progress row
3. Confirm the action
4. Participant returns to Workshop 1
5. All their previous responses are **deleted**

**⚠️ Warning:** This cannot be undone. Archive responses before resetting if needed.

### Troubleshooting Login Issues

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Forgot password | Admin can reset via Django admin panel |
| Account locked | Check failed login attempts, unlock account |
| Can't access workshop | Verify consent and profile completion |
| Wrong permissions | Ensure user is in `mana_regional_participant` group |

---

## Monitoring Workshop Progress

### Dashboard Overview

Your facilitator dashboard shows:

```
┌─────────────────────────────────────┐
│ Workshop 1: Understanding Context   │
├─────────────────────────────────────┤
│ Total Participants: 50              │
│ Submitted: 45 (90%)                 │
│ Target: ≥85% ✓                      │
└─────────────────────────────────────┘
```

### Workshop Tabs

Navigate between workshops using the tabs:
```
[Workshop 1] [Workshop 2] [Workshop 3] [Workshop 4] [Workshop 5]
    ↑ Active
```

### Filtering Responses

Apply filters to view specific groups:
1. **Province**: Select a province to see only their responses
2. **Stakeholder**: Select a stakeholder type
3. Click **"Apply Filters"**

The view updates instantly (HTMX-powered) without page reload.

### Viewing Responses

#### Question Summary Table
- Shows all questions for the workshop
- Displays response count per question
- Click a row to jump to detailed responses

#### Detailed Response View
For each question, you'll see:
- **Question text and category**
- **All participant responses**
- **Participant name, stakeholder type, province**
- **Submission timestamp**
- **Structured data** (for repeater fields, shown as formatted JSON)

### Advancing Participants

**When to Advance:**
- Workshop deadline has passed
- Target submission rate (≥85%) achieved
- Ready to move to next session

**How to Advance:**
1. Review current workshop submissions
2. Click **"Advance participants to Workshop X"**
3. Confirm the action
4. **All participants** move to the next workshop
5. Participants receive notification (if configured)

**⚠️ Note:** This affects ALL participants in the assessment, regardless of submission status.

### Auto-Unlock

The system can automatically unlock workshops based on schedule:
- Workshop activities have a `scheduled_date`
- System checks dates and unlocks automatically
- You'll see a notification: *"Automatically unlocked X participants based on schedule"*

---

## AI Synthesis & Analysis

### What is AI Synthesis?

AI synthesis uses Large Language Models (LLMs) to:
- Aggregate responses across all participants
- Identify key themes and patterns
- Highlight differences by province or stakeholder type
- Generate priority recommendations
- Save facilitator review time (target: ≥40% reduction)

### Requesting a Synthesis

1. Navigate to the workshop you want to synthesize
2. Scroll to **"AI Synthesis"** section
3. Configure synthesis:
   - **Province Filter** (optional): Synthesize only one province's responses
   - **Stakeholder Filter** (optional): Analyze specific stakeholder type
   - **AI Provider**: Choose Anthropic Claude or OpenAI GPT
   - **Custom Prompt** (advanced): Modify the synthesis instructions
4. Click **"Generate Synthesis"**

### Processing Time

**Target: ≤30 seconds average**

- Synthesis runs in background (if Celery is enabled)
- You'll see status: *"Synthesis queued for background processing"*
- Refresh the page to see results
- Status updates: Queued → Processing → Completed

### Reviewing Synthesis Results

Each synthesis card shows:
- **Status badge**: Processing, Completed, Approved
- **Provider and model** used (e.g., "Anthropic Claude-3")
- **Timestamp**
- **Synthesis text** (collapsible, scrollable)
- **Key themes** (if extracted)
- **Action buttons**: Regenerate, Approve

#### Synthesis Text Structure

The AI generates structured insights:

```
Key Themes:
1. Limited access to healthcare facilities
2. Need for agricultural support
3. Educational gaps in Islamic studies
...

Patterns by Geography:
- Zamboanga del Sur: Focus on farm-to-market roads
- Zamboanga del Norte: Emphasis on water systems
...

Priority Issues:
1. Healthcare infrastructure (mentioned by 80% of participants)
2. Livelihood support (60%)
...

Recommendations:
- Establish community health centers in X municipalities
- Provide agricultural training programs
...
```

### Regenerating a Synthesis

If the first synthesis needs improvement:
1. Click **"Regenerate"** on the synthesis card
2. Optionally modify filters or prompt
3. A new synthesis is created (previous one remains for comparison)

### Approving a Synthesis

Once you've reviewed and are satisfied:
1. Click **"Approve"**
2. Add optional review notes
3. Synthesis status changes to **"Approved"**
4. Approved syntheses can be included in official reports

### Synthesis Best Practices

✅ **Generate multiple syntheses:**
   - One for each province (to compare regional differences)
   - One for each stakeholder type (to understand diverse perspectives)
   - One comprehensive synthesis (all participants combined)

✅ **Review critically:**
   - Verify synthesis aligns with raw responses
   - Check for AI hallucinations or misinterpretations
   - Add facilitator notes where needed

✅ **Use as starting point:**
   - Synthesis assists, doesn't replace facilitator judgment
   - Combine AI insights with your contextual knowledge
   - Validate key findings with participants if possible

---

## Exporting Data

### Export Formats

Three formats available:

| Format | Best For | File Size |
|--------|----------|-----------|
| **CSV** | Excel analysis, data processing | Small |
| **XLSX** | Formatted Excel spreadsheets | Medium |
| **PDF** | Printable reports, archiving | Large |

### Exporting Workshop Responses

1. Navigate to the workshop
2. Apply filters (optional): province, stakeholder
3. Click **"Export [Format]"** button
4. File downloads immediately

**Target Performance: ≤10 seconds for 100 responses**

### Export Contents

All exports include:
- **Participant name**
- **Organization**
- **Province, Municipality, Barangay**
- **Stakeholder type**
- **Submission status and timestamp**
- **Question ID**
- **Response data** (structured data as JSON)

### Using Exported Data

#### CSV/XLSX Analysis

1. Open in Microsoft Excel or Google Sheets
2. Create pivot tables to analyze:
   - Responses by province
   - Responses by stakeholder type
   - Submission timing patterns
3. Filter and sort for deeper insights
4. Create charts and graphs for presentations

#### PDF Reports

- **Formatted** for printing
- **Paginated** with headers
- Suitable for **archiving** and **official records**
- Can be shared with non-technical stakeholders

---

## Troubleshooting Common Issues

### Participant Can't Submit

**Possible Causes:**
1. **Required fields missing** – Check form validation errors
2. **Session timeout** – Ask participant to refresh and log in again
3. **Network issue** – Verify internet connectivity
4. **Browser compatibility** – Recommend Chrome, Firefox, or Edge

**Solution:**
- Have participant try **"Save Draft"** first
- Check if autosave captured their data
- Reset progress as last resort (data will be lost)

### Synthesis Fails

**Error Messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| "No submitted responses found" | No participants have submitted yet | Wait for submissions or check filters |
| "Anthropic synthesis failed: [error]" | API key issue or rate limit | Check settings, verify API quota |
| "Timeout" | Large dataset or slow API | Reduce filters, try again later |

### Export Takes Too Long

**Target: ≤10 seconds for 100 responses**

If exports are slow:
1. Check number of responses (very large datasets take longer)
2. Try CSV instead of PDF (faster)
3. Apply filters to reduce dataset size
4. Contact technical support if consistently slow

### Participant Submitted to Wrong Workshop

1. **Reset their progress** (this deletes all responses)
2. **Manually unlock** the correct workshop
3. Ask participant to resubmit
4. Explain sequential workflow to prevent future confusion

### Dashboard Not Updating

- **Refresh the page** (most HTMX updates are instant, but full refresh helps)
- **Clear browser cache**
- **Check if logged in** (session may have expired)

---

## Success Metrics

### Your Targets

As a facilitator, aim to achieve:

| Metric | Target | How to Track |
|--------|--------|--------------|
| **Onboarding Rate** | ≥90% | "Participants" tab, check profile completion |
| **Submission Rate (per workshop)** | ≥85% | Dashboard, "Submitted: X (Y%)" indicator |
| **Review Time Reduction** | ≥40% | Track your time manually, compare early vs. late workshops |
| **Export Performance** | ≤10 sec (100 responses) | Time exports, report slow performance |
| **Synthesis Performance** | ≤30 sec average | Check synthesis timestamps |
| **Audit Coverage** | 100% | System auto-logs, admin can verify |

### Monitoring Dashboard

Navigate to **"Success Metrics"** (if enabled):
- **Visual charts** showing progress toward targets
- **Real-time updates** as participants submit
- **Historical trends** across workshop series
- **Recommendations** for improvement

### Improving Metrics

**Low Onboarding Rate (<90%)?**
- Send reminder emails/SMS
- Offer one-on-one technical support
- Extend onboarding deadline if needed

**Low Submission Rate (<85%)?**
- Contact non-submitters directly
- Understand blockers (technical, time, content)
- Provide deadline reminders
- Offer extended hours for submissions

**Slow Review Time?**
- Use AI synthesis more extensively
- Focus on provincial/stakeholder summaries
- Delegate detailed review to co-facilitators

---

## Best Practices

### 📋 **Before Each Workshop**
- ✅ Verify all participants are onboarded
- ✅ Send workshop reminder 2 days before
- ✅ Prepare support channels (email, hotline)
- ✅ Test system performance and access

### 📋 **During Each Workshop**
- ✅ Monitor submission rates daily
- ✅ Respond to support requests within 24 hours
- ✅ Send mid-week reminder to non-submitters
- ✅ Track toward ≥85% submission target

### 📋 **After Each Workshop**
- ✅ Generate AI syntheses (multiple perspectives)
- ✅ Review and approve syntheses
- ✅ Export raw data for backup
- ✅ Advance participants once target is met
- ✅ Document lessons learned

### 📋 **End of Workshop Series**
- ✅ Generate comprehensive final synthesis
- ✅ Export all data in all formats
- ✅ Archive workshop records
- ✅ Prepare summary report for OOBC leadership
- ✅ Gather facilitator feedback for process improvement

---

## Facilitator Checklist

Use this checklist for each workshop:

```
□ Participants imported and invited (≥7 days before Workshop 1)
□ ≥90% participants completed onboarding (before Workshop 1)
□ Workshop 1 unlocked and participants notified
□ Mid-workshop reminder sent (Day 3-4)
□ ≥85% submission rate achieved by deadline
□ AI syntheses generated (all provinces + comprehensive)
□ Syntheses reviewed and approved
□ Data exported (CSV, XLSX, PDF)
□ Participants advanced to next workshop
□ Metrics recorded and shared with team
```

---

## Technical Support Contacts

### For Facilitator Issues
- **Email:** facilitator-support@oobc.gov.ph
- **Phone:** [Insert phone number]
- **Office Hours:** Monday-Friday, 8:00 AM - 5:00 PM (PHT)

### For System/Infrastructure Issues
- **IT Support:** it@oobc.gov.ph
- **Emergency Hotline:** [Insert emergency contact]

### Escalation
- **MANA Program Coordinator:** [Name and contact]
- **OBCMS System Administrator:** [Name and contact]

---

## Appendix: Quick Reference

### Participant Stakeholder Types
```
elder, women_leader, youth_leader, farmer, fisherfolk,
religious_leader, traditional_leader, milf_representative,
mnlf_representative, business_leader, teacher, health_worker,
lgu_official, ngo_representative, other
```

### Workshop Sequence
```
workshop_1 → workshop_2 → workshop_3 → workshop_4 → workshop_5
```

### Key Permissions
```
mana_regional_participant    # Participant access
mana_facilitator             # Facilitator full access
can_access_regional_mana     # Base permission
can_facilitate_workshop      # Synthesis + controls
```

---

## Conclusion

As a facilitator, you play a critical role in gathering and synthesizing community insights that will shape OOBC programs. This guide equips you with the tools and knowledge to manage the digital workshop platform effectively.

**Remember:** The platform is designed to support your facilitation, not replace your judgment. Combine digital tools with your contextual expertise for the best outcomes.

**Questions?** Contact the MANA Program Coordinator or refer to this guide.

---

*Version 1.0 | Last Updated: September 2025 | Office for Other Bangsamoro Communities (OOBC)*