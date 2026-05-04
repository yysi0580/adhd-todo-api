# Calendar Import TODO

Calendar Import is planned as a one-time candidate ingestion flow.

The app should not turn calendar events directly into fixed tasks. Imported events
should become suggestion candidates that the user can choose, pass, capture only,
or make smaller.

Planned shape:

1. User connects Google Calendar through OAuth.
2. Backend reads a limited date range after explicit user action.
3. Imported event titles/descriptions are transformed into Brain Dump context or
   suggestion candidates.
4. User chooses from candidates before any Action is created.

Privacy notes:

- Avoid storing raw calendar descriptions unless needed.
- If raw event text is stored, document retention and deletion behavior.
- Do not expose external calendar metadata to other users.
- Keep OAuth tokens encrypted or use a managed secret store before production.

Frontend should keep calendar import buttons disabled/planned until the OAuth and
privacy flow are implemented.
