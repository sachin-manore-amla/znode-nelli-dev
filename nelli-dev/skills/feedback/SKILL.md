---
name: feedback
description: Send feedback about Nelli-Dev - builds a sanitized note (secrets, host names, emails and paths removed), shows it, and saves it as a local file only after you confirm. Nothing is sent. Use when the developer runs /nelli-dev:feedback.
argument-hint: "[short note, optional]"
---

# Nelli-Dev feedback

Goal: a short, safe note the developer can send to Znode. Nothing is sent by Nelli-Dev. Scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts`.

1. Get the note: use `$ARGUMENTS` if given, otherwise ask for one or two sentences (what went wrong or what would help). Ask which command it concerns (optional) and whether they want to paste the confidence line Nelli-Dev gave (optional; never add one yourself).
2. Preview: `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_feedback.py preview --note "<note>" [--command <name>] [--confidence "<pasted line>"]`. For text with quotes, use `--note-stdin` and pipe it in. Show the preview exactly as printed. Tell the developer that tokens, keys, emails, host names and drive paths were removed automatically and that they should still read it.
3. Ask: "Save this file locally?" Options: "Yes, save it (Recommended)", "Edit the note", "Cancel". Do not save before a clear yes.
4. On yes: run the same command with `save ... --confirmed`. Tell them the path it printed and how to send it: https://support.znode.com, or `<support contact to be confirmed by Znode>`. Say plainly that Nelli-Dev sent nothing.

## Rules
- Never paste code, customer paths, prompts or responses into the note yourself. Only the developer's own words.
- Nothing is written before the confirmation. Nothing leaves the machine.
- Check `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py status` only to mention the level; the developer asking for feedback explicitly is enough to write the local file.
