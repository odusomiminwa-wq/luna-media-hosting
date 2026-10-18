# LUNA Clip Inbox — operating notes

This directory documents the clip intake workflow for the LUNA Social Media Content Engine. It is not intended to store large MP4 files in GitHub. Upload generated video files to the connected Google Drive folder **LUNA Clips Inbox** from Android; the Composio workflow will ingest them after Drive authorization and folder ID verification.

## Upload from Android
1. Open Google Drive and complete the connection link supplied in ChatGPT.
2. Upload the generated MP4/MOV to **LUNA Clips Inbox**.
3. Use a descriptive filename, for example `2026-10-18_day1_unreachable_v01.mp4`.
4. In ChatGPT, ask to process the new LUNA clip. The automation must verify the folder ID and fetch the actual file; a filename alone is not enough.
5. The bots validate technical metadata, inspect frames, check LUNA identity/continuity, prepare captions and platform packages, and stop for review if any check fails.
6. Publishing is never triggered by upload alone. Explicit approval is required.

## Intake contract
- Preserve original source bytes and metadata.
- Deduplicate by stable file ID and content hash when available.
- Statuses: RECEIVED, VALIDATED, PROCESSING, REVIEW_REQUIRED, READY_FOR_APPROVAL, APPROVED_TO_PUBLISH, PUBLISHED, REJECTED, BLOCKED.
- Do not promote uploaded clips to identity master references without explicit approval.
- Do not claim visual verification without actually comparing clip frames against the approved face/body masters.
- Never publish without explicit per-run approval.

## Planned folder structure
- 01_INCOMING_CLIPS
- 02_PROCESSING
- 03_REVIEW_REQUIRED
- 04_APPROVED_FINALS
- 05_PUBLISHED_ARCHIVE

Subfolders are created only after Drive is connected and the parent folder is verified.
