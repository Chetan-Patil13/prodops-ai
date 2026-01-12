Journey 1 — Production Query

User: Supervisor
Input:

“Show today’s production and downtime for Line-3”

System does:

Query production DB

Query downtime DB

Summarize result

Journey 2 — Actionable Intelligence

User: Supervisor
Input:

“Why is OEE low and what should we do?”

System does:

Analyze downtime

Retrieve SOP via RAG

Suggest next steps

Ask confirmation before actions

Journey 3 — Ticket Creation + Notification

User: Supervisor
Input:

“Create a maintenance ticket for hydraulic pressure issue”

System does:

Create ticket in DB

Send email to HOD

Send WhatsApp alert to group

Store context in memory

Journey 4 — Context Continuation

User (next day):

“Continue yesterday’s discussion on Line-3 issue”

System does:

Load user memory

Resume context

Journey 5 — Manager Summary

User: Manager
Input:

“Give me a weekly summary”

System does:

Aggregate data

Summarize trends

No operational actions
