# MANA Regional Workshop Facilitator User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Assessment Overview](#assessment-overview)
4. [Monitoring Progress](#monitoring-progress)
5. [Reviewing Submissions](#reviewing-submissions)
6. [Advancing Participants](#advancing-participants)
7. [AI Synthesis](#ai-synthesis)
8. [Export & Reporting](#export--reporting)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

As a MANA Regional Workshop Facilitator, you play a crucial role in coordinating the sequential workshop process. This guide will help you effectively manage participants, monitor progress, and ensure smooth workshop advancement.

### Your Responsibilities

- ✅ Monitor participant progress across all 5 workshops
- ✅ Review and validate workshop submissions
- ✅ Advance participants to next workshops when ready
- ✅ Generate AI-powered synthesis reports
- ✅ Export data for analysis and reporting

### System Access

You can only see assessments that have been **assigned to you** by OOBC staff. If you need access to additional assessments, contact your system administrator.

---

## Getting Started

### Login

1. Navigate to the OBCMS website
2. Click **Login** in the top right
3. Enter your facilitator credentials
4. You'll be redirected to your dashboard

### First-Time Setup

Your account is created by OOBC staff with the following:
- ✅ Facilitator permission (`can_facilitate_workshop`)
- ✅ Assignment to specific regional assessments
- ✅ Email notifications enabled

---

## Assessment Overview

### Accessing Your Assessments

1. Navigate to **MANA** → **Facilitator Dashboard**
2. You'll see a grid of **assigned assessments only**
3. Each card shows:
   - **Assessment Title** (e.g., "Regional Workshop - Cotabato 2025")
   - **Total Participants** enrolled
   - **Number of Workshops** (always 5)
   - **Overall Progress** percentage
   - **Status** badge (Not Started, Active, Completed)

### Opening an Assessment

Click **Open Dashboard** to access the full facilitator workspace for that assessment.

---

## Monitoring Progress

### Dashboard Layout

The facilitator dashboard has three main sections:

1. **Header**
   - Assessment title and description
   - **Progress Bar**: Visual indicator showing X/Y participants submitted
   - Color-coded:
     - 🟢 Green (100%) - All submitted
     - 🟢 Emerald (70-99%) - Most submitted
     - 🔵 Blue (30-69%) - Some submitted
     - 🟡 Amber (0-29%) - Few submitted

2. **Workshop Tabs**
   - Five tabs: Workshop 1, 2, 3, 4, 5
   - Click any tab to switch views
   - Current workshop highlighted in emerald

3. **Responses Panel**
   - Table of participant submissions
   - Filter controls (Province, Stakeholder Type)
   - Export buttons (XLSX, CSV, PDF)

### Understanding Progress Metrics

**Workshop Progress**:
- Shows: "5 / 10" (5 submitted out of 10 enrolled)
- Updates in real-time when participants submit

**Completion Percentage**:
- Calculated as: (Submitted / Total Enrolled) × 100
- Example: 7 out of 10 = 70%

**Cohort Status Icons**:
- ✅ **All participants submitted** - Ready to advance
- 🟡 **Waiting for more submissions** - Some still working
- ⏱️ **Most participants submitted** - Consider advancing soon

---

## Reviewing Submissions

### Viewing Responses

1. Select a **workshop tab** (1-5)
2. Scroll to **Responses Table**
3. Each row shows:
   - Question text
   - Aggregated responses from all participants
   - Individual participant answers (expandable)

### Using Filters

**Filter by Province**:
1. Click **Province dropdown**
2. Select a province (or "All")
3. Click **Apply Filters**
4. Table updates to show only that province

**Filter by Stakeholder Type**:
1. Click **Stakeholder dropdown**
2. Select a type (e.g., "Community Elder")
3. Click **Apply Filters**
4. Table shows only that stakeholder type

**Combine Filters**:
- You can use both filters simultaneously
- Example: "Cotabato" + "Women Leader" shows only women leaders from Cotabato

### Reading Submissions

- **Text Responses**: Full text displayed
- **Number Responses**: Numeric values shown
- **Structured Data**: Formatted as key-value pairs
- **Repeater Fields**: Multiple entries listed

---

## Advancing Participants

### When to Advance

**Recommended Criteria**:
- ✅ At least 70% of participants have submitted
- ✅ You've reviewed the quality of submissions
- ✅ Sufficient data collected for synthesis
- ✅ Timeline allows for next workshop

**Important**: When you advance, **ALL participants** move forward, including those who haven't submitted. Non-submitters can still access the previous workshop but also gain access to the next one.

### Advancement Process

1. **Check Progress**
   - Review the progress bar
   - Verify submission count meets your threshold

2. **Initiate Advancement**
   - Scroll to top of dashboard
   - Look for blue button: **"Advance All Participants to Workshop X"**
   - Click the button

3. **Confirmation Modal**
   - A modal appears showing:
     - Next workshop name
     - Total participant count
     - Current submission status (X/Y submitted)
     - Warning about non-submitters
   - Read the information carefully

4. **Confirm Action**
   - Click **"Confirm Advancement"** to proceed
   - OR click **"Cancel"** to abort

5. **Verification**
   - Toast notification confirms: "Advanced X participants to Workshop Y"
   - Button text updates to show next workshop
   - Participants receive **in-app notifications**

### What Happens After Advancement?

**For Participants**:
- 🔔 **Notification appears** on their dashboard
- 🔓 **Next workshop unlocks** immediately
- ✅ **Previous workshop remains accessible** (read-only if submitted)

**For You**:
- 📊 Progress bar resets for new workshop
- 🔄 Can switch to new workshop tab to monitor
- 📧 Can continue to review previous workshops anytime

### Advancement Best Practices

✅ **DO**:
- Advance during logical break points (end of day, between sessions)
- Communicate advancement schedule to participants beforehand
- Review at least a sample of submissions before advancing
- Advance all workshops eventually (don't leave participants stuck)

❌ **DON'T**:
- Advance too quickly (give participants time to submit)
- Advance late at night (participants won't see notifications)
- Skip workshops (sequence is enforced)
- Wait for 100% submission (unlikely to achieve)

---

## AI Synthesis

### Overview

The AI Synthesis feature generates consolidated summaries of participant responses using artificial intelligence. This helps you quickly understand themes, patterns, and key findings.

### Prerequisites

- AI API keys must be configured by system administrator
- Supported providers: OpenAI (GPT-4), Anthropic (Claude)
- At least 3-5 participant submissions recommended for meaningful synthesis

### Generating Synthesis

1. Scroll to **"AI Synthesis"** section (below responses table)

2. **Configure Filters** (Optional):
   - **Province**: Generate synthesis for specific province only
   - **Stakeholder Type**: Focus on specific stakeholder group
   - Leave blank for all responses

3. **Select Provider**:
   - **OpenAI**: GPT-4 (recommended for detailed analysis)
   - **Anthropic**: Claude (alternative, similar quality)

4. **Custom Prompt** (Optional):
   - Add specific instructions for the AI
   - Example: "Focus on economic development themes"
   - Leave blank to use default template

5. **Click "Generate Synthesis"**
   - Process runs asynchronously (in background)
   - Usually takes 30-60 seconds

### Viewing Synthesis Results

- Synthesis appears in **grid below** the form
- Each card shows:
  - **Status**: Draft, Pending, Approved
  - **Timestamp**: When generated
  - **Provider & Model**: AI system used
  - **Synthesized Text**: Full output

### Synthesis Actions

**Regenerate**:
- Click **"Regenerate"** to create a new version
- Useful if first result is unsatisfactory
- Previous versions remain visible

**Approve**:
- Click **"Approve"** to mark as final
- Indicates this synthesis is ready for reports
- Status changes to "Approved"

### Best Practices for Synthesis

✅ **Wait for sufficient data**: Generate after 50%+ submissions
✅ **Review AI output**: Always validate accuracy before using
✅ **Use filters strategically**: Compare different demographic groups
✅ **Keep multiple versions**: Regenerate to compare perspectives

---

## Export & Reporting

### Available Export Formats

1. **XLSX (Excel)** - Best for analysis, charts, pivot tables
2. **CSV** - Best for data import, statistical software
3. **PDF** - Best for printing, archival, sharing

### Exporting Workshop Data

1. Navigate to desired **workshop tab**
2. Apply any **filters** (Province, Stakeholder) if needed
3. Click export button:
   - **Export XLSX** → Downloads `.xlsx` file
   - **Export CSV** → Downloads `.csv` file
   - **Export PDF** → Downloads `.pdf` file

### Export File Contents

**Columns Included**:
- Participant ID
- Full Name
- Province
- Municipality (if provided)
- Stakeholder Type
- Organization (if provided)
- Question ID
- Question Text
- Response Data
- Submission Timestamp

**File Naming**:
- Format: `workshop_responses_[workshop]_[date].xlsx`
- Example: `workshop_responses_workshop_1_2025-09-30.xlsx`

### Using Exported Data

**Excel Analysis**:
1. Open `.xlsx` file in Microsoft Excel or Google Sheets
2. Use Pivot Tables to aggregate by province/stakeholder
3. Create charts for visualizations
4. Filter and sort as needed

**CSV for Analysis**:
- Import into SPSS, R, Python pandas
- Run statistical analysis
- Generate research reports

**PDF for Sharing**:
- Print for hard copy records
- Email to stakeholders
- Archive for compliance

---

## Best Practices

### Weekly Workflow

**Monday**:
1. Login and check progress across all assessments
2. Send reminder emails/messages to non-submitters
3. Review new submissions from weekend

**Wednesday**:
1. Mid-week progress check
2. Follow up with participants who haven't started
3. Review sample submissions for quality

**Friday**:
1. Final progress check before weekend
2. Decide if ready to advance
3. Generate synthesis reports for completed workshops
4. Advance participants if criteria met

### Communication Tips

✅ **Be transparent**: Tell participants when you plan to advance
✅ **Set expectations**: "We'll advance when 70% submit"
✅ **Send reminders**: "Workshop 2 closes Thursday at 5 PM"
✅ **Acknowledge submissions**: "Great work on Workshop 1!"

### Quality Assurance

**Spot-Check Submissions**:
- Review 20-30% of responses before advancing
- Look for:
  - ✅ Complete responses (all questions answered)
  - ✅ Thoughtful answers (not just "N/A" or empty)
  - ✅ Relevant content (answers match questions)

**Red Flags**:
- ❌ Very short responses (< 10 words)
- ❌ Copy-paste answers (identical across questions)
- ❌ Nonsense text or placeholder data
- ❌ Missing required fields

**What to Do**:
1. Contact participant directly (email/phone)
2. Ask for clarification or resubmission
3. Provide guidance on expected detail level
4. Extend deadline if necessary

### Time Management

**Allocate Time**:
- **10 mins/day**: Quick progress check
- **30 mins/week**: Review submissions thoroughly
- **1 hour/workshop**: Synthesis generation and review
- **2 hours/assessment**: Final reporting and documentation

---

## Troubleshooting

### "I can't see any assessments"

**Cause**: You're not assigned to any assessments

**Solution**:
1. Contact your supervisor or system administrator
2. Verify your facilitator permission is active
3. Request assignment to specific assessments

### "Progress bar shows 0% but I know participants submitted"

**Cause**: You're viewing a different workshop tab

**Solution**:
1. Check which workshop tab is selected (top of dashboard)
2. Switch to the correct workshop tab
3. Verify filters aren't hiding submissions (set to "All")

### "Advance button not appearing"

**Possible Causes**:
- You're already on the last workshop (Workshop 5)
- All participants already advanced
- System error (rare)

**Solution**:
1. Check which workshop tab is currently selected
2. If Workshop 5, advancement complete (no more workshops)
3. If earlier workshop, refresh page
4. Contact admin if problem persists

### "Synthesis generation failed"

**Possible Causes**:
- AI API keys not configured
- No responses to synthesize
- Network error

**Solution**:
1. Verify at least 3 responses exist for selected filters
2. Try different AI provider
3. Wait 5 minutes and try again
4. Contact IT support if persists

### "Export downloads empty file"

**Cause**: Filters are too restrictive or no data exists

**Solution**:
1. Reset filters to "All" for Province and Stakeholder
2. Verify submissions exist in responses table
3. Try different export format
4. Check browser download settings

### "Participants report they didn't receive notification"

**Cause**: Notification system might have delay

**Solution**:
1. Ask participant to refresh their dashboard
2. Verify notification exists in database (contact admin)
3. Communicate advancement via email/SMS as backup
4. Ensure participant has logged in recently

---

## Quick Reference

### Keyboard Shortcuts

- **Ctrl/Cmd + R**: Refresh page
- **Esc**: Close modal
- **Tab**: Navigate form fields

### Status Colors

- 🟢 **Green**: Complete / Submitted
- 🔵 **Blue**: In Progress
- 🟡 **Yellow**: Pending / Waiting
- ⚪ **Gray**: Locked / Not Started
- 🔴 **Red**: Error / Attention Needed

### Icons

- 🚀 **Rocket**: Advancement
- 📊 **Chart**: Progress/Analytics
- 🔔 **Bell**: Notifications
- ✅ **Checkmark**: Completed
- 🔒 **Lock**: Restricted/Locked
- ⏱️ **Clock**: Pending/Time-based

---

## Support & Resources

**Technical Support**: [support@oobc.gov.ph](mailto:support@oobc.gov.ph)
**MANA Coordinator**: [mana.coordinator@oobc.gov.ph](mailto:mana.coordinator@oobc.gov.ph)
**System Administrator**: Contact your IT department

**Additional Documentation**:
- [Participant Tutorial](./participant_tutorial.md)
- [Integration Test Scenarios](./integration_test_scenarios.md)
- [Implementation Progress](./implementation_progress.md)

---

**Version**: 1.0
**Last Updated**: 2025-09-30
**For**: OOBC MANA Regional Workshop Facilitators