import os
import ffmpeg
import logging
import requests
import subprocess
from services.file_management import download_file
from services.ass_toolkit import generate_ass_captions_v1

STORAGE_PATH = "/tmp/"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FONTS_DIR = '/usr/share/fonts/custom'

FONT_PATHS = {}
for font_file in os.listdir(FONTS_DIR):
    if font_file.endswith('.ttf') or font_file.endswith('.TTF') or font_file.endswith('.otf'):
        font_name = os.path.splitext(font_file)[0]
        FONT_PATHS[font_name] = os.path.join(FONTS_DIR, font_file)

# --- Utilities --------------------------------------------------------------

def ass_hex(color_hex: str, opacity: float = 0.0) -> str:
    """#RRGGBB + opacity(0..1) -> &HAABBGGRR for libass."""
    color_hex = color_hex.lstrip('#')
    rr = int(color_hex[0:2], 16)
    gg = int(color_hex[2:4], 16)
    bb = int(color_hex[4:6], 16)
    aa = int(max(0, min(1, opacity)) * 255)
    return f"&H{aa:02X}{bb:02X}{gg:02X}{rr:02X}"

def anchor_to_alignment(anchor: str) -> int:
    """Map anchor string to ASS alignment number."""
    m = {
        "bottom_center": 2,
        "bottom_left": 1,
        "bottom_right": 3,
        "middle_left": 4,
        "middle_center": 5,
        "middle_right": 6,
        "top_left": 7,
        "top_center": 8,
        "top_right": 9
    }
    return m.get(anchor, 2)

# ---------------------------------------------------------------------------

def generate_style_line(options):
    """Generate ASS style line from options."""
    # === Defaults from your JSON/Kapwing ===
    font_name = options.get('font_name', 'NotoSansArabic-VariableFont_wdth,wght')
    font_size = options.get('font_size', 32)
    bold = 1 if options.get('bold', True) else 0

    primary = ass_hex(options.get('word_color', '#FFFFFF'), 0.0)
    outline_col = ass_hex(options.get('outline_hex', '#000000'), 0.0)
    back_col = ass_hex(options.get('background_color', '#000000'), options.get('background_opacity', 0.8))

    alignment = anchor_to_alignment(options.get('anchor', options.get('position', 'bottom_center')))

    style_options = {
        'Name': 'Default',
        'Fontname': font_name,
        'Fontsize': font_size,
        'PrimaryColour': primary,
        'OutlineColour': outline_col,
        'BackColour': back_col,
        'Bold': bold,
        'Italic': 1 if options.get('italic', False) else 0,
        'Underline': 1 if options.get('underline', False) else 0,
        'StrikeOut': 1 if options.get('strikeout', False) else 0,
        'ScaleX': 100,
        'ScaleY': 100,
        'Spacing': 0,
        'Angle': 0,
        'BorderStyle': 3,  # box background
        'Outline': options.get('outline_width', 50),
        'Shadow': options.get('shadow_offset', 0),
        'Alignment': alignment,
        'MarginL': options.get('margin_l', 10),
        'MarginR': options.get('margin_r', 10),
        'MarginV': options.get('margin_v', 10),
        'Encoding': options.get('encoding', 1)
    }
    return f"Style: {','.join(str(v) for v in style_options.values())}"

def process_captioning(video_url, captions, caption_type, options, job_id):
    try:
        video_path = download_file(video_url, STORAGE_PATH)
        subtitle_extension = '.' + caption_type if caption_type else '.ass'
        srt_path = os.path.join(STORAGE_PATH, f"{job_id}{subtitle_extension}")

        if isinstance(options, list):  # convert array to collection
            options = convert_array_to_collection(options)

        caption_style = ""
        if caption_type == 'ass':
            style_string = generate_style_line(options)
            caption_style = (
                "[Script Info]\nTitle: Styled\nScriptType: v4.00+\n"
                "[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
                "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                f"{style_string}\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            )

        # If no captions are provided, fallback to auto-generating ASS via v1 service
        if captions is None:
            logger.info(f"Job {job_id}: No captions provided; generating ASS via v1 service fallback.")
            ass_result = generate_ass_captions_v1(
                video_url,
                captions=None,
                settings={},
                replace=[],
                exclude_time_ranges=[],
                job_id=job_id,
                language='auto'
            )
            if isinstance(ass_result, dict) and 'error' in ass_result:
                raise Exception(ass_result['error'])
            # Use generated ASS path directly
            srt_path = ass_result
            subtitle_extension = '.ass'
        else:
            # Captions provided: write to local file (support URL or inline content)
            if caption_type == 'ass':
                if isinstance(captions, str) and captions.startswith('http'):
                    logger.info(f"Job {job_id}: Downloading ASS captions from URL")
                    resp = requests.get(captions)
                    resp.raise_for_status()
                    subtitle_content = caption_style + resp.text
                else:
                    subtitle_content = caption_style + captions
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(subtitle_content)
            else:
                # SRT/VTT
                if isinstance(captions, str) and captions.startswith('http'):
                    logger.info(f"Job {job_id}: Downloading {caption_type.upper()} captions from URL")
                    resp = requests.get(captions)
                    resp.raise_for_status()
                    with open(srt_path, 'wb') as f:
                        f.write(resp.content)
                else:
                    with open(srt_path, 'w', encoding='utf-8') as f:
                        f.write(captions)

        output_path = os.path.join(STORAGE_PATH, f"{job_id}_captioned.mp4")

        # Force-style only for SRT/VTT
        font_name = options.get('font_name', 'NotoSansArabic-VariableFont_wdth,wght')
        primary = ass_hex(options.get('word_color', '#FFFFFF'), 0.0)
        outline_col = ass_hex(options.get('outline_hex', '#000000'), 0.0)
        back_col = ass_hex(options.get('background_color', '#000000'), options.get('background_opacity', 0.8))
        alignment = anchor_to_alignment(options.get('position', 'bottom_center'))

        if subtitle_extension == '.ass':
            subtitle_filter = f"subtitles='{srt_path}'"
        else:
            style_options = {
                'FontName': font_name,
                'FontSize': options.get('font_size', 32),
                'PrimaryColour': primary,
                'OutlineColour': outline_col,
                'BackColour': back_col,
                'Bold': 1 if options.get('bold', True) else 0,
                'Italic': 1 if options.get('italic', False) else 0,
                'Underline': 1 if options.get('underline', False) else 0,
                'StrikeOut': 1 if options.get('strikeout', False) else 0,
                'Alignment': alignment,
                'MarginV': options.get('margin_v', 10),
                'MarginL': options.get('margin_l', 10),
                'MarginR': options.get('margin_r', 10),
                'Outline': options.get('outline_width', 50),
                'Shadow': options.get('shadow_offset', 0),
                'BorderStyle': 3,  # box background
                'Encoding': options.get('encoding', 1),
                'Spacing': options.get('spacing', 0),
                'Angle': options.get('angle', 0)
            }
            subtitle_filter = f"subtitles={srt_path}:force_style='" + \
                ','.join(f"{k}={v}" for k, v in style_options.items() if v is not None) + "'"

        # Run FFmpeg to burn subtitles into the video
        try:
            logger.info(f"Job {job_id}: Running FFmpeg with filter: {subtitle_filter}")
            ffmpeg.input(video_path).output(
                output_path,
                vf=subtitle_filter,
                acodec='copy'
            ).run(overwrite_output=True)
            logger.info(f"Job {job_id}: FFmpeg processing completed, output file at {output_path}")
        except ffmpeg.Error as e:
            error_message = e.stderr.decode('utf8') if getattr(e, 'stderr', None) else str(e)
            logger.error(f"Job {job_id}: FFmpeg error: {error_message}")
            raise

        return output_path
    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning: {str(e)}")
        raise

def convert_array_to_collection(options):
    logger.info(f"Converting options array to dictionary: {options}")
    return {item["option"]: item["value"] for item in options}