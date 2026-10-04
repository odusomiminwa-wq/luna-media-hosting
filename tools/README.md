# Luna Instagram Video Optimizer

Conservative encoder/validator for Luna Reels.

## Output contract
- MP4 container
- H.264/AVC video
- 1080x1920 vertical 9:16 canvas
- 30 fps
- yuv420p
- AAC audio, 48 kHz stereo when audio exists
- fast-start MP4
- strips subtitles/data streams and source metadata

## GitHub Actions
Run Instagram Video Optimizer from the Actions tab and provide a direct HTTPS video URL. The optimized MP4 is returned as a workflow artifact.

A page URL or HTML wrapper is not necessarily a direct video file URL. If a host returns HTML instead of MP4 bytes, the workflow will reject it.
