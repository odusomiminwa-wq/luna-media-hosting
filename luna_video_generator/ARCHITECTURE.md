# LUNA Video Generation Layer — Rebuild Notes

## What was added

This folder contains a runnable Gradio interface that calls Hugging Face Inference Providers for real text-to-video generation and supports reference-guided image-to-video when a compatible model/provider is configured.

## The important separation

- The existing 40 agents remain the strategy, creative, identity, optimization, distribution, analytics, and growth workflow.
- The new generation layer is the execution service that calls an actual model.
- An agent manifest describes ownership and order; it does not magically make all 40 roles autonomous LLM agents. Existing integrations (Composio, GitHub workers, platform APIs, model credentials) still need to be connected and tested.
- A successful generation is only recorded when a video file is returned and validated.

## Current request lifecycle

1. User enters a scene prompt and selects a task.
2. App validates required inputs and token presence.
3. App calls the configured Hugging Face inference provider/model.
4. App saves returned video bytes as MP4.
5. App reports the selected provider/model and returns the file.
6. Identity and technical review happen before any publishing step.

## Required secrets and deployment

Set `HF_TOKEN` in Hugging Face Space Settings → Secrets. Do not commit it. Use `README.md` in this folder for deployment steps.

## Known limitation

Provider model/task compatibility changes. Text-to-video has a default model ID; image-to-video needs a model ID explicitly supported by the selected provider. The app returns a clear error on unsupported configurations instead of faking a successful output.
