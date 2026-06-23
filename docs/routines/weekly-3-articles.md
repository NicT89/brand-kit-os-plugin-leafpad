# Routine: 3 articles every week, on autopilot

Set up a recurring content engine: every Monday, Claude researches topics, builds a calendar of 3 brand-relevant posts, and schedules them on Leafpad for the week.

## The pattern

Two commands do the work:

1. `/brand-kit-os-leafpad:plan-week --count 3` — research + build the calendar
2. `/brand-kit-os-leafpad:execute-calendar` — schedule each post

The plugin doesn't ship its own scheduler — instead it plugs into whatever scheduled-execution your host provides. Below are the setups per host.

## Claude Desktop / Cowork (scheduled sessions)

Cowork can run a saved prompt on a schedule.

1. Make sure your **sources registry** is set up (`~/.brand-kit-os-leafpad/registry.json`) with `topic_cadence` = 3 posts/week and your preferred days/time. See the `topic-sourcing` skill.
2. Optionally run `/brand-kit-os-leafpad:sync-brand-to-kb` once so Leafpad's AI scheduler generates brand-aware posts.
3. In Cowork, create a **scheduled session** for **every Monday at 8:00 AM** with this prompt:

   ```
   Run /brand-kit-os-leafpad:plan-week --count 3 to research and build this week's
   content calendar. Then run /brand-kit-os-leafpad:execute-calendar to schedule all
   three posts via Leafpad's AI scheduler. Report the calendar and the scheduled
   confirmations.
   ```

4. The first few weeks, review the output before posts go live. Once you trust it, let it run hands-off.

### Want hand-crafted drafts instead of AI-scheduled posts?

Change the second command to `--draft-now`:

```
Run /brand-kit-os-leafpad:plan-week --count 3, then
/brand-kit-os-leafpad:execute-calendar --draft-now to fully write all three as
brand-crafted drafts I can review before publishing.
```

This runs the full pipeline (research → draft → cite → SEO → QA) on each post immediately and saves drafts, rather than handing titles to Leafpad's AI. Higher quality and fully brand-controlled; you publish each draft when ready.

## Claude Code (cron / CI)

If you run Claude Code headless, drive it from cron. Example crontab entry for Monday 8am:

```cron
0 8 * * 1 cd /path/to/your/project && claude -p "Run /brand-kit-os-leafpad:plan-week --count 3 then /brand-kit-os-leafpad:execute-calendar" >> ~/content-routine.log 2>&1
```

Make sure the MCP servers are configured at the user or project scope so the headless session can connect, and that Leafpad's OAuth token is already cached (run once interactively first).

## Monthly editorial calendar

For a monthly rhythm, see [`monthly-editorial-calendar.md`](monthly-editorial-calendar.md).

## Tips for quality on autopilot

- **Keep the registry fresh.** Add new trusted sources as you find them — `topic-scout` is only as good as its inputs.
- **Sync brand to KB after brand kit changes.** Re-run `/sync-brand-to-kb` whenever you update voice or governance.
- **Review `topic-scout` fit scores.** If ideas trend below ~75, your registry or brand kit likely needs more detail.
- **Mix sources.** A calendar that's all "company updates" gets stale; the registry's trusted feeds + content-gap analysis keep variety.
- **Watch for duplication.** `topic-scout` dedups against existing Leafpad posts, but a quick scan of the calendar before executing never hurts.
