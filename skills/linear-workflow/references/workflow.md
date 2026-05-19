# Linear Workflow Reference — Key Pulse Systems

## Workspace Structure

| Team | Products |
| --- | --- |
| Hop In Sports | HopInSports mobile/web app |
| Clavro | Clavro auth platform |
| Key Pulse Systems | Parent company / shared |

## How Work is Organized

### Projects = Product Areas (Theme Projects)

Group issues by what they're about. These are the backlog roadmap — what *could* ship.

| Project | Description |
| --- | --- |
| Event Experience | Teams, co-hosts, check-in, waitlist automation, reminders, custom fields |
| Payments & Monetization | Stripe payments, refunds, memberships, season passes, revenue reporting |
| Recurring & Competitive Play | Recurring events, leagues, tournaments |
| Growth & Engagement | Referrals, social sharing, surveys, analytics, branding, broadcast |
| Infrastructure & Tech Debt | Database integrity, config fixes, technical improvements |

### Projects = Releases (Version Projects)

Group issues into a release with milestones. These are the execution plan — what *will* ship.

Example: `v1.0.0 Release` with milestones: Build & Signing, CI/CD Pipeline, Testing & QA, Feature Completion, Store Listings & Launch.

### How Issues Graduate

```
Theme Project (backlog roadmap)
  -> prioritized for a release
    -> Version Project (execution plan)
      -> Done / Shipped
```

1. New ideas go into a theme project with priority and labels.
2. When committed to a release, move the issue from the theme project into the version project.
3. Version projects use milestones to break the release into phases.
4. When the release ships, mark the version project as Completed.

## Label Groups

### Type (single-select)

| Label | Use When |
| --- | --- |
| Feature | New functionality |
| Bug | Something is broken |
| Improvement | Enhancement to existing functionality |
| Chore | Maintenance, config, housekeeping |

### Platform (single-select)

| Label | Use When |
| --- | --- |
| iOS | iOS-specific work |
| Android | Android-specific work |
| Web | Web app work |
| Server | Backend/Ktor work |
| Shared | Cross-platform shared module |

Only apply Platform when one platform dominates. Skip for full-stack features.

## Conventions

- **One issue per project** — Linear issues can only belong to one project at a time.
- **No cycles** — We use version-based releases, not time-boxed sprints. Cycles would only be added if we adopt a regular sprint cadence within releases.
- **Priorities**: Urgent = blocking release. High = must ship soon. Medium = important but not urgent. Low = nice to have.
- **Clavro issues stay on the Clavro team** — never mix with Hop In Sports.

## Creating a New Release

1. Create project named `vX.Y.Z Release` on the Hop In Sports team.
2. Add milestones for release phases.
3. Pull prioritized tickets from theme projects into the version project.
4. Track progress via the project's built-in progress graph.
5. When shipped, mark the project as Completed.

## Creating a New Feature Ticket

1. Set title and description.
2. Assign to the appropriate theme project.
3. Set priority (Urgent/High/Medium/Low).
4. Add Type label (Feature/Bug/Improvement/Chore).
5. Add Platform label if one platform dominates.
6. Leave in Backlog status until it's pulled into active work.
