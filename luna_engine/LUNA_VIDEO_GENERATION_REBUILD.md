# LUNA Video Generator Integration

The active engine now points to `luna_video_generator/` as its video-generation execution layer. The existing 40-agent configuration remains the orchestration and social-growth layer; the generation UI makes real requests to a configured model/provider and only reports success when a video file is returned.

## Deploy

1. Create a Hugging Face Space using Gradio, or run the app locally.
2. Add `HF_TOKEN` as a Space secret or local environment variable. Never commit the token.
3. Upload/use the files in `luna_video_generator/`.
4. Select a model/provider that currently supports the requested task and that your account can access.
5. Generate a short test clip, inspect it, and pass it through identity and technical checks before publication.

## Important

The integration files are committed, but the Space itself has not been created or deployed from this repository, and a real video has not yet been generated in this session. Hugging Face/provider access and credits are required for hosted inference. The app reports errors instead of claiming success when a request fails.

The current identity policy in `luna_reference/identity_rules.json` remains authoritative. Do not use retired root-level media assets as identity substitutes. Do not auto-publish without approval.
