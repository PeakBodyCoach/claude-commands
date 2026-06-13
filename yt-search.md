Search YouTube using yt-dlp and display the top results.

The user has invoked this skill with the following arguments: $ARGUMENTS

Parse the arguments:
- Everything that is NOT a `-n N` flag is the search query.
- If `-n N` or `--count N` is present, use that as the number of results; otherwise default to 5.
- If `--json` is present, pass it through to the script.

Run this command (adjust the count and query accordingly):

```bash
python $HOME\.claude\commands\youtube_search.py -n <count> <query>
```

Then display the output clearly to the user. Each result should show:
1. **Title**
2. **URL** (clickable YouTube link)
3. **Views**, **Duration**, **Upload Date**
4. **Creator / Channel**

If yt-dlp is not installed, tell the user to run:
```
pip install yt-dlp
```

If no results are found, say so and suggest refining the query.

Example invocations:
- `/yt-search lofi hip hop` → search for "lofi hip hop", 5 results
- `/yt-search -n 10 python tutorial` → search for "python tutorial", 10 results
- `/yt-search --json cats` → output raw JSON for "cats"
