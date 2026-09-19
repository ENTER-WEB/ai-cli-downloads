# AI CLI downloads

- This is the public distribution repository. Keep setup sources, internal documents, credentials, account settings and Drive identifiers out.
- Publish only the selected EXEs and the generated public usage notes/checksums to Releases.
- Keep each version immutable. Never use upload --clobber or force-push release tags.
- Keep /download/codex and /download/claude stable; they redirect to the exact versions shown on the page.
- Preserve prerelease labels for rc builds. Do not claim trusted signing or broad compatibility without evidence.
- Verify anonymous downloads by SHA-256 after publishing, then verify the live page and both download buttons.
- Deploy only the site directory. Do not deploy the repository root.
