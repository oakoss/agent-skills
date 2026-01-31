---
title: Remote Testing and Tools
description: Remote vs in-person usability testing comparison, moderated vs unmoderated tradeoffs, recommended testing and analysis tools, test frequency guidelines, and session checklists
tags:
  [
    remote-testing,
    tools,
    frequency,
    checklist,
    in-person,
    moderated,
    unmoderated,
  ]
---

# Remote Testing and Tools

## Remote vs In-Person Testing

| Factor                   | Remote Moderated     | In-Person                          | Remote Unmoderated            |
| ------------------------ | -------------------- | ---------------------------------- | ----------------------------- |
| Participant pool         | Global               | Local only                         | Global                        |
| Cost per session         | Low-medium           | High                               | Low                           |
| Session depth            | Deep                 | Deepest                            | Shallow-medium                |
| Body language visibility | Limited (camera)     | Full                               | None                          |
| Technical setup risk     | Medium               | Low                                | Low                           |
| Scheduling flexibility   | High                 | Low                                | Highest                       |
| Scale                    | 5-15 sessions        | 5-10 sessions                      | 20-150 sessions               |
| Best for                 | Most usability tests | Complex products, sensitive topics | Validation, quantitative data |

## Remote Moderated Testing

### Setup Checklist

```yaml
Before the Session:
  - Test screen sharing on the video platform (Zoom, Google Meet, Teams)
  - Verify recording permissions and storage
  - Prepare backup communication method (phone number, alternative platform)
  - Send participant clear instructions with video link, tech requirements
  - Do a dry run with a colleague to test the full flow
  - Prepare the test environment (stable build, test accounts, sample data)

Platform Selection:
  - Zoom: widely available, good recording, breakout rooms for observers
  - Google Meet: no install required, good for quick sessions
  - Microsoft Teams: enterprise environments, built-in recording
  - Lookback: purpose-built for research, timestamped notes, highlight reels
  - dscout: mobile-first, diary studies, longitudinal research

Technical Requirements for Participants:
  - Stable internet connection
  - Screen sharing capability
  - Camera enabled (recommended, not required)
  - Microphone and speakers or headphones
  - Browser or device matching the test environment
```

### Best Practices

```yaml
Session Management:
  - Start 5 minutes early to resolve technical issues
  - Have the participant share their screen before starting tasks
  - Ask them to close other tabs and notifications
  - Record both the participant's screen and the video call
  - Have a note-taker on the call (camera and mic off)

Rapport Building (harder remotely):
  - Spend 2-3 minutes on casual conversation before tasks
  - Use the participant's name throughout the session
  - Acknowledge technical difficulties without frustration
  - Keep your camera on so the participant can see you are engaged

Handling Technical Issues:
  - If screen sharing fails: switch to the participant describing what they see
  - If audio cuts out: use chat as a backup channel
  - If the connection drops: have a phone number to call back
  - If the prototype crashes: note the failure, skip to next task
```

## In-Person Testing

### Lab Setup

```yaml
Room Requirements:
  - Quiet room with minimal distractions
  - Desk with computer or device under test
  - Chair positioned so moderator sits beside or behind the participant
  - Screen recording software running (OBS, Morae, Silverback)
  - External camera for facial expressions (optional)
  - One-way mirror or video feed for observers (optional)

Supplies:
  - Printed consent forms
  - Printed task cards (one task per card)
  - Note-taking sheets for moderator
  - Water and snacks for participants
  - Gift cards or cash for incentives
  - Backup device in case of hardware failure

Observer Guidelines:
  - Observers watch via video feed or one-way mirror
  - No entering the testing room during sessions
  - Take notes independently, compare after all sessions
  - Save questions for the debrief, not during the session
```

## Testing Tools by Category

### Usability Testing Platforms

```yaml
Moderated Testing:
  - Lookback: live moderated sessions with timestamped notes and highlights
  - UserTesting.com: recruit and test, video recordings, moderated and unmoderated
  - dscout: mobile-first research, diary studies, video responses

Unmoderated Testing:
  - Maze: task-based testing with Figma integration, click heatmaps
  - Lyssna (formerly UsabilityHub): first-click, preference, five-second tests
  - UserTesting.com: unmoderated option with think-aloud recording
  - Loop11: task-based testing with analytics

Prototype Testing:
  - Figma prototypes: interactive prototypes that work directly in Maze and Lyssna
  - InVision: clickable prototypes with hotspot analytics
  - Axure: high-fidelity prototypes with conditional logic
```

### Information Architecture Tools

```yaml
Card Sorting:
  - Optimal Workshop (OptimalSort): open, closed, and hybrid card sorts
  - Maze: integrated card sorting within broader test plans
  - UserZoom: enterprise card sorting with analytics

Tree Testing:
  - Optimal Workshop (Treejack): text-based navigation testing
  - UserZoom: tree testing with task-based analysis

First-Click Testing:
  - Lyssna: click heatmaps on static designs
  - Maze: first-click analysis within task flows
  - Optimal Workshop (Chalkmark): standalone first-click testing
```

### Analysis and Reporting

```yaml
Qualitative Analysis:
  - Dovetail: tag and organize qualitative data, generate themes
  - EnjoyHQ: research repository with tagging and search
  - Condens: collaborative analysis with video highlights

Session Recording:
  - Zoom: screen and audio recording, cloud storage
  - Loom: quick screen recordings for sharing highlights
  - OBS Studio: advanced recording with multiple sources (free)

Collaboration:
  - Miro: affinity mapping, journey mapping, collaborative analysis
  - FigJam: collaborative whiteboarding integrated with Figma
  - Notion: research templates, shared databases, team wikis

Metrics Tracking:
  - Spreadsheets (Google Sheets, Excel): flexible, custom formulas
  - Airtable: structured data with views and formulas
  - Dovetail: quantitative analysis alongside qualitative data
```

### Accessibility Testing Tools

```yaml
Automated Scanners:
  - axe DevTools: browser extension, WCAG checks (free)
  - WAVE: visual accessibility report in browser (free)
  - Lighthouse: built into Chrome DevTools (free)
  - pa11y: command-line tool for CI integration (free)

Screen Readers:
  - VoiceOver: built into macOS and iOS (free)
  - NVDA: Windows screen reader (free)
  - JAWS: enterprise Windows screen reader (paid)

Contrast Checkers:
  - WebAIM Contrast Checker: web-based ratio calculator
  - Stark: Figma plugin for contrast and color blindness simulation
  - Color Contrast Analyzer: desktop application (free)
```

## Test Frequency

```yaml
Product Lifecycle Testing Schedule:
  Pre-Launch:
    - Heuristic evaluation of wireframes
    - Prototype testing with 5 users
    - Accessibility audit before development
    - Final usability test on staging environment

  Launch:
    - Monitor support tickets and analytics for UX issues
    - Quick guerrilla test on top 3 user flows

  Post-Launch (ongoing):
    - Test every major feature release with 5 users
    - Quarterly full usability audit (5-8 users, all core tasks)
    - Annual accessibility audit with participants with disabilities

Continuous Testing Cadence:
  Week 1: Test with 5 users on identified problem areas
  Week 2: Fix top issues found
  Week 3: Test with 5 new users to verify fixes
  Week 4: Report results and plan next test cycle
  Repeat until task success rate meets targets (80%+ for core tasks)
```

## Quick Start Checklists

### Planning Phase

- [ ] Define 3-5 measurable test objectives
- [ ] Write research questions
- [ ] Write task scenarios with realistic context
- [ ] Create screening questionnaire
- [ ] Recruit 5-8 participants per persona
- [ ] Prepare consent form
- [ ] Write test script with timing
- [ ] Set up recording tools
- [ ] Run 1-2 pilot sessions

### Testing Phase

- [ ] Welcome participant and collect consent
- [ ] Ask background questions
- [ ] Explain think-aloud protocol with practice task
- [ ] Conduct tasks (do not help)
- [ ] Ask post-task questions after each task
- [ ] Administer SUS survey after all tasks
- [ ] Debrief with open questions
- [ ] Thank participant and provide incentive

### Analysis Phase

- [ ] Review all session recordings and notes
- [ ] Calculate task success rates per task
- [ ] Calculate time on task (median)
- [ ] Calculate error rates per task
- [ ] Calculate SUS score
- [ ] List all issues with severity ratings
- [ ] Identify patterns and key insights
- [ ] Create prioritized recommendations
- [ ] Write report with executive summary
- [ ] Share findings with stakeholders
- [ ] Create fix tickets for critical and high issues
- [ ] Schedule follow-up test to verify fixes
