import os
import tempfile
import traceback
from pathlib import Path

import gradio as gr
from huggingface_hub import InferenceClient

APP_TITLE = "LUNA AI Video Generator"
DEFAULT_PROVIDER = os.getenv("HF_PROVIDER", "auto")
DEFAULT_T2V_MODEL = os.getenv("LUNA_T2V_MODEL", "Wan-AI/Wan2.1-T2V-1.3B")
DEFAULT_I2V_MODEL = os.getenv("LUNA_I2V_MODEL", "")
MAX_PROMPT_CHARS = 2500


def _save_video_result(result):
    """Normalize provider output to a local MP4 path without exposing credentials."""
    if isinstance(result, (bytes, bytearray)):
        payload = bytes(result)
    elif isinstance(result, str) and Path(result).is_file():
        source = Path(result)
        target = Path(tempfile.gettempdir()) / f"luna_generated_{next(tempfile._get_candidate_names())}.mp4"
        target.write_bytes(source.read_bytes())
        return str(target)
    else:
        raise RuntimeError(
            "The selected provider returned an unsupported video result. "
            "Try a different model/provider combination."
        )

    target = Path(tempfile.gettempdir()) / f"luna_generated_{next(tempfile._get_candidate_names())}.mp4"
    target.write_bytes(payload)
    if not target.exists() or target.stat().st_size < 1024:
        raise RuntimeError("The provider returned an empty or incomplete video file.")
    return str(target)


def generate_video(prompt, reference_image, mode, provider, t2v_model, i2v_model, identity_check):
    prompt = (prompt or "").strip()
    if not prompt:
        raise gr.Error("Enter a video prompt first.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise gr.Error(f"Keep the prompt under {MAX_PROMPT_CHARS} characters.")

    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise gr.Error(
            "Hugging Face is not connected yet. Add HF_TOKEN in the Space Settings → Secrets, "
            "or set HF_TOKEN in your local environment."
        )

    if identity_check and reference_image is None:
        raise gr.Error(
            "Identity protection is enabled. Upload an approved current LUNA reference image "
            "before generating, or turn off the identity requirement for a non-identity test."
        )

    chosen_provider = (provider or "auto").strip() or "auto"
    client = InferenceClient(provider=chosen_provider, token=token, timeout=600)

    try:
        if mode == "Image-to-video (reference guided)":
            if reference_image is None:
                raise gr.Error("Upload a reference image for image-to-video mode.")
            if not (i2v_model or "").strip():
                raise gr.Error(
                    "Set LUNA_I2V_MODEL in Space variables or enter a supported image-to-video model ID."
                )
            with open(reference_image, "rb") as image_file:
                image_bytes = image_file.read()
            # The Hub SDK's image_to_video method accepts image bytes and returns video bytes.
            result = client.image_to_video(image=image_bytes, prompt=prompt, model=i2v_model.strip())
            method = "image-to-video"
            model_used = i2v_model.strip()
        else:
            result = client.text_to_video(prompt=prompt, model=(t2v_model or DEFAULT_T2V_MODEL).strip())
            method = "text-to-video"
            model_used = (t2v_model or DEFAULT_T2V_MODEL).strip()

        video_path = _save_video_result(result)
        status = (
            f"Generation succeeded.\nMode: {method}\nProvider: {chosen_provider}\nModel: {model_used}\n"
            "Next: inspect the output for face/body consistency, artifacts, framing, and platform suitability. "
            "This app does not auto-publish."
        )
        return video_path, status
    except gr.Error:
        raise
    except Exception as exc:
        # Keep the user-facing message actionable and avoid logging the token or request headers.
        message = str(exc).replace(token, "[REDACTED]") if token else str(exc)
        raise gr.Error(
            f"Video generation failed ({type(exc).__name__}): {message[:700]}\n\n"
            "Check that the model supports the selected task/provider and that your Hugging Face "
            "account has inference credits or access. You can switch provider/model in the controls."
        )


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# LUNA AI Video Generator\n"
        "### Generate real video through Hugging Face Inference Providers\n"
        "This is a generation interface, not a queue placeholder. A successful request returns an MP4. "
        "Provider access, model availability, and free credits are controlled by Hugging Face and its providers."
    )
    with gr.Row():
        with gr.Column(scale=3):
            prompt = gr.Textbox(
                label="Scene prompt",
                placeholder="Example: Luna steps out of a pearl-white luxury car into a rainy neon-lit city, cinematic tracking shot...",
                lines=5,
                max_lines=8,
            )
            reference = gr.Image(label="Approved LUNA reference image (required when identity protection is on)", type="filepath")
            mode = gr.Radio(
                choices=["Text-to-video", "Image-to-video (reference guided)"],
                value="Text-to-video",
                label="Generation mode",
            )
            identity_check = gr.Checkbox(value=True, label="Require a reference image for identity-sensitive production")
            generate = gr.Button("Generate video", variant="primary")
        with gr.Column(scale=2):
            output_video = gr.Video(label="Generated video", format="mp4")
            status = gr.Textbox(label="Generation status", lines=7, interactive=False)

    with gr.Accordion("Model and provider settings", open=False):
        provider = gr.Dropdown(
            choices=["auto", "fal-ai", "replicate", "novita", "together", "wavespeed"],
            value=DEFAULT_PROVIDER if DEFAULT_PROVIDER in ["auto", "fal-ai", "replicate", "novita", "together", "wavespeed"] else "auto",
            label="Inference provider",
            info="Provider availability depends on the selected model and your account/credits.",
        )
        t2v_model = gr.Textbox(label="Text-to-video model ID", value=DEFAULT_T2V_MODEL)
        i2v_model = gr.Textbox(
            label="Image-to-video model ID",
            value=DEFAULT_I2V_MODEL,
            placeholder="Enter a model ID that supports image-to-video through the chosen provider",
        )
        gr.Markdown(
            "The model IDs are configurable because provider catalogs and access change. "
            "Do not paste your Hugging Face token into these fields; add it as the HF_TOKEN secret."
        )

    generate.click(
        fn=generate_video,
        inputs=[prompt, reference, mode, provider, t2v_model, i2v_model, identity_check],
        outputs=[output_video, status],
    )

if __name__ == "__main__":
    demo.queue(max_size=4).launch()
