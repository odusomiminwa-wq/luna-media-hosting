---
title: LUNA AI Video Generator
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 5.33.1
app_file: app.py
pinned: false
---

# LUNA AI Video Generator

A Gradio app that sends real text-to-video or reference-guided image-to-video requests through Hugging Face Inference Providers and returns the generated video when the selected model/provider succeeds.

## Deploy as a Hugging Face Space

1. Create a new Space at https://huggingface.co/new-space.
2. Choose **Gradio**. Free personal accounts may be able to host a Gradio app on ZeroGPU if eligible. **This app's video rendering is performed by an Inference Provider, not by the Space's ZeroGPU**, so the provider's own access and billing rules still apply.
3. Upload the files in this folder to the Space repository (the Space root should contain `app.py`, `requirements.txt`, and this README).
4. In Space **Settings → Variables and secrets**, add a secret named `HF_TOKEN` with inference permissions.
5. Commit the files. The Space will build and start the app.
6. Test a short prompt first. If the default model/provider combination is unavailable, choose a supported model ID and provider in the settings panel.

## Local run

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export HF_TOKEN="hf_..."   # PowerShell: $env:HF_TOKEN="hf_..."
python app.py
```

## Configuration

- `HF_TOKEN`: required secret; never commit this value.
- `HF_PROVIDER`: defaults to `auto`.
- `LUNA_T2V_MODEL`: defaults to `Wan-AI/Wan2.1-T2V-1.3B`.
- `LUNA_I2V_MODEL`: optional default model for image-to-video.

Image-to-video is only available when the chosen model/provider supports that task. If a provider does not support it, the app reports the error rather than pretending to generate a video.

## LUNA identity and safety rules

- Use only the current approved LUNA face/body reference set recorded in `../luna_reference/identity_rules.json`.
- The old image/video in the root of the media-hosting repository are retired from the active identity pipeline. Do not use them as substitutes.
- Keep generated output as a derivative; do not overwrite master/reference assets.
- Review face, hair, freckles, proportions, hands, scene artifacts, and watermark/licensing restrictions before a video is approved.
- This app does not publish to Instagram or TikTok and does not extract or embed copyrighted audio from other creators' Reels. Add platform-native audio during publishing where supported.
- The app's reference-image requirement is a workflow guardrail, not a guarantee that a model will preserve identity perfectly. Human/automated identity review remains required.

## Honest free-tier expectations

Hugging Face's current Inference Providers pricing documentation says free users do not receive included monthly inference credits; they must purchase credits or upgrade to a plan that includes credits. Some public/ZeroGPU Spaces can be free to try, but that is a separate route and can have queue/quota limits. This app does not bypass access limits and cannot promise unlimited free generation. Check the current [Inference Providers pricing](https://huggingface.co/docs/inference-providers/pricing) before scaling.

## Current architecture

The 40-agent LUNA Social Media Content Engine remains the planning, identity, optimization, packaging, publishing, analytics, and growth layer. This app supplies the actual video-generation execution layer. Publishing remains a separate approval-controlled step.
