# AutoStand-UP-Agent

flowchart TD
    A[Scheduled Trigger - Cron, GitHub Action, Lambda] --> B[Auth & Setup]
    
    B --> C[GitHub API]
    C --> C1[Pull commits in last 24h]
    C --> C2[Fetch PRs created/merged]
    C --> C3[Extract metadata - author, repo, message]

    B --> D[Notion / Jira API]
    D --> D1[Fetch Task DB or Board]
    D --> D2[Parse status - In Progress, Blocked, Done]
    D --> D3[Match user activity with GitHub if possible]

    C3 --> E[Activity Aggregation Engine]
    D3 --> E

    E --> F[LLM Summarizer - Local or API]
    F --> F1[Prompt engineering - What I did / Doing / Blockers]
    F1 --> G[Per-user summaries]

    G --> H[Final Stand-Up Builder]
    H --> H1[Format per-user messages]
    H --> H2[Sort + merge team-wide summary]

    H2 --> I[Output to Slack / Discord]
    I --> I1[Use Webhook or Bot to send to channel]

    I1 --> Z[Done! Daily stand-up delivered]

