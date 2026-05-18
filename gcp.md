Commit and push all changes in the skills and commands folders to GitHub.

Run the following steps silently and report a clean summary at the end.

## Skills repo

```bash
cd C:\Users\Tom\.claude\skills && git add . && git diff --cached --quiet || git commit -m "sync: skills update" && git push
```

## Commands repo

```bash
cd C:\Users\Tom\.claude\commands && git add . && git diff --cached --quiet || git commit -m "sync: commands update" && git push 2>&1
```

## Report to user

After running both, report in this format:

**Skills:** pushed / nothing to commit / ERROR: [message]
**Commands:** pushed / nothing to commit / no remote configured (run `git remote add origin <url>` to connect)

Keep it brief. If there are errors, quote the relevant line so the user knows what to fix.
