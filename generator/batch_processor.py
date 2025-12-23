
import csv
import io
import re
import zipfile
from typing import List, Dict, Any, Optional
import streamlit as st

from .generator import (
    generate_class_outline,
    generate_video_script,
)
from .audio import synthesize_narration_audio
from .markdown_utils import (
    outline_to_markdown,
    video_script_to_markdown,
)

def slugify(value: str) -> str:
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

class BatchProcessor:
    REQUIRED_HEADERS = ['#', 'video_file', 'est_duration', 'brief_description']

    def parse_csv(self, file_buffer: io.BytesIO) -> List[Dict[str, str]]:
        """
        Parses the uploaded CSV file and validates headers.
        Returns a list of dictionaries representing the rows.
        """
        try:
            # Decode bytes to string
            content = file_buffer.getvalue().decode('utf-8')
            f = io.StringIO(content)
            reader = csv.DictReader(f)
            
            # Normalize headers (strip whitespace)
            if reader.fieldnames:
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            # Validate headers
            missing = [h for h in self.REQUIRED_HEADERS if h not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
            rows = list(reader)
            return rows
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

    def process_batch(self, rows: List[Dict[str, str]], progress_callback=None) -> bytes:
        """
        Processes each row in the batch, generates content, and returns a ZIP file as bytes.
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            total = len(rows)
            
            for i, row in enumerate(rows):
                if progress_callback:
                    progress_callback(i / total, f"Processing Class {row['#']}: {row['brief_description'][:30]}...")
                
                class_number = row.get('#', '000').strip()
                description = row.get('brief_description', '')
                video_filename = row.get('video_file', '')
                try:
                    duration_str = row.get('est_duration', '')
                    # Attempt to parse int or float from duration string if possible, strictly for internal type safety if needed,
                    # but logic uses string mostly.
                except:
                    pass

                slug = slugify(description)[:30] # Limit slug length
                folder_name = f"Class_{class_number}_{slug}"
                
                # Context for generation
                # We construct a synthetic "full_text" from the CSV data to feed the existing generators
                context_text = (
                    f"Video File Reference: {video_filename}\n"
                    f"Estimated Duration: {row.get('est_duration', 'N/A')}\n"
                    f"Description/Context: {description}\n"
                )
                
                # 1. Generate Outline
                # We use the description as the primary source + video filename
                outline_title = f"Class {class_number}: {description}"
                outline = generate_class_outline(
                    full_text=context_text,
                    course_title=outline_title,
                    class_type="Video Walkthrough"
                )
                
                # Save Outline
                outline_md = outline_to_markdown(outline)
                zip_file.writestr(f"{folder_name}/class_outline.md", outline_md)
                
                # 2. Generate Script
                video_script = generate_video_script(
                    full_text=context_text,
                    course_title=outline_title,
                    class_type="Video Walkthrough"
                )
                
                # Save Script
                script_md = video_script_to_markdown(video_script)
                zip_file.writestr(f"{folder_name}/video_script.md", script_md)
                
                # 3. Synthesize Audio
                # This returns a dict {filename: bytes}
                audio_files = synthesize_narration_audio(video_script)
                
                for audio_name, audio_bytes in audio_files.items():
                    zip_file.writestr(f"{folder_name}/Audio/{audio_name}", audio_bytes)
        
        if progress_callback:
            progress_callback(1.0, "Structuring final ZIP package...")
            
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
