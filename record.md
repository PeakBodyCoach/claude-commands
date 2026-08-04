# /record

Launch the Playwright action recorder against a URL, let Tom drive the browser (clicks + typing get captured into annotated screenshots), then stop it and report the recorded steps.

## Usage

```
/record https://example.com
```

## Arguments

`$ARGUMENTS` — the start URL to open. If empty, default to `https://example.com`.

## Configuration

- **Project folder:** `C:\Users\Tom\Documents\playwright-recorder`
- **Script:** `record-steps.mjs` (Node ESM, Playwright)
- **Output folder:** `recording\` inside the project (PNGs + `steps.md` + `steps.json`)
- **Login state:** persists in `.auth\` between runs

## Workflow

Do these steps in order. Do NOT click or type in the browser yourself — Tom does the recording manually.

1. **Resolve the URL.** Use `$ARGUMENTS` as the start URL. If no argument was given, use `https://example.com`.

2. **Launch in the background.** From the project folder, run the recorder as a background task, redirecting output to a log:
   ```
   cd "C:\Users\Tom\Documents\playwright-recorder" && node record-steps.mjs <URL> > record.log 2>&1
   ```
   Use `run_in_background: true`. Keep the returned task ID — you need it to stop later.

3. **Confirm it opened.** Wait a few seconds, then read `record.log`. Confirm it printed `Recording. Ctrl+C to stop.` with no errors. If the log shows an error (e.g. browser failed to launch), report it and stop.

4. **Hand over to Tom.** Tell him the browser window is open and he should do his clicks and typing now. Red boxes mark clicks, green boxes mark typed fields. Tell him to say **"done"** (or "stop") when he has finished. Then wait for him — do not stop the recorder on your own.

5. **Stop on his signal.** When Tom says he's done, stop the background task by its ID (TaskStop). The script autosaves `steps.md`/`steps.json` after every action, so stopping this way does not lose data.

6. **Report.** Read `recording\steps.md`, then tell Tom:
   - how many steps were captured,
   - the path to `recording\steps.md`,
   - a short list of the generated screenshot files.
   If `steps.md` is missing or empty, say so (it means no clicks/typing were captured).

7. **Tidy.** Delete `record.log` (it's just the launch log; the real output is in `recording\`).

## Notes

- The recorder writes `recording\` and `.auth\` relative to the project folder, so it must always be run from `C:\Users\Tom\Documents\playwright-recorder`.
- `recording\`, `.auth\`, and `node_modules\` are gitignored.
