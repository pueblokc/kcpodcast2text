"""
Export service for generating transcripts in various formats
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import timedelta
from io import StringIO

from backend.services.transcription import TranscriptionResult, TranscriptionSegment


def format_timestamp(seconds: float, format_type: str = "srt") -> str:
    """Format timestamp for different subtitle formats"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)

    if format_type == "srt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    elif format_type == "vtt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class ExportService:
    """Service for exporting transcriptions in various formats"""

    @staticmethod
    def to_txt(result: TranscriptionResult, include_timestamps: bool = False) -> str:
        """Export as plain text"""
        if not include_timestamps:
            return result.text

        lines = []
        for segment in result.segments:
            timestamp = format_timestamp(segment.start, "simple")
            speaker = f"[{segment.speaker}] " if segment.speaker else ""
            lines.append(f"[{timestamp}] {speaker}{segment.text}")

        return "\n".join(lines)

    @staticmethod
    def to_srt(result: TranscriptionResult) -> str:
        """Export as SRT subtitle format"""
        lines = []

        for i, segment in enumerate(result.segments, 1):
            start = format_timestamp(segment.start, "srt")
            end = format_timestamp(segment.end, "srt")

            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(segment.text)
            lines.append("")  # Blank line between subtitles

        return "\n".join(lines)

    @staticmethod
    def to_vtt(result: TranscriptionResult) -> str:
        """Export as WebVTT subtitle format"""
        lines = ["WEBVTT", ""]

        for segment in result.segments:
            start = format_timestamp(segment.start, "vtt")
            end = format_timestamp(segment.end, "vtt")

            lines.append(f"{start} --> {end}")
            if segment.speaker:
                lines.append(f"<v {segment.speaker}>{segment.text}")
            else:
                lines.append(segment.text)
            lines.append("")  # Blank line

        return "\n".join(lines)

    @staticmethod
    def to_json(result: TranscriptionResult, pretty: bool = True) -> str:
        """Export as JSON"""
        data = result.to_dict()

        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def to_markdown(
        result: TranscriptionResult,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export as Markdown with metadata"""
        lines = []

        # Title
        if title:
            lines.append(f"# {title}")
            lines.append("")

        # Metadata section
        if metadata:
            lines.append("## Metadata")
            lines.append("")
            for key, value in metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        # Transcription info
        lines.append("## Transcription Details")
        lines.append("")
        lines.append(f"- **Language**: {result.language}")
        lines.append(f"- **Provider**: {result.provider}")
        lines.append(f"- **Model**: {result.model}")
        lines.append(f"- **Confidence**: {result.confidence:.2%}")
        lines.append(f"- **Word Count**: {result.word_count}")
        lines.append(
            f"- **Processing Time**: {result.processing_time:.2f} seconds"
        )
        lines.append("")

        # Full transcript
        lines.append("## Full Transcript")
        lines.append("")
        lines.append(result.text)
        lines.append("")

        # Timestamped segments
        if result.segments:
            lines.append("## Timestamped Segments")
            lines.append("")

            for segment in result.segments:
                timestamp = format_timestamp(segment.start, "simple")
                speaker = f"**{segment.speaker}**: " if segment.speaker else ""
                lines.append(f"### [{timestamp}]")
                lines.append(f"{speaker}{segment.text}")
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def to_csv(result: TranscriptionResult) -> str:
        """Export segments as CSV"""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Start", "End", "Duration", "Speaker", "Text", "Confidence"])

        # Rows
        for segment in result.segments:
            duration = segment.end - segment.start
            writer.writerow(
                [
                    segment.start,
                    segment.end,
                    duration,
                    segment.speaker or "",
                    segment.text,
                    segment.confidence or "",
                ]
            )

        return output.getvalue()

    @staticmethod
    def to_pdf(
        result: TranscriptionResult,
        output_path: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Export as PDF using FPDF"""
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        if title:
            pdf.cell(0, 10, title, ln=True, align="C")
            pdf.ln(5)

        # Metadata
        if metadata:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Metadata", ln=True)
            pdf.set_font("Arial", "", 10)

            for key, value in metadata.items():
                pdf.cell(0, 6, f"{key}: {value}", ln=True)
            pdf.ln(5)

        # Transcription details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Transcription Details", ln=True)
        pdf.set_font("Arial", "", 10)

        details = [
            f"Language: {result.language}",
            f"Provider: {result.provider}",
            f"Model: {result.model}",
            f"Confidence: {result.confidence:.2%}",
            f"Word Count: {result.word_count}",
            f"Processing Time: {result.processing_time:.2f} seconds",
        ]

        for detail in details:
            pdf.cell(0, 6, detail, ln=True)
        pdf.ln(5)

        # Full transcript
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Full Transcript", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, result.text)
        pdf.ln(5)

        # Timestamped segments
        if result.segments:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Timestamped Segments", ln=True)

            for segment in result.segments:
                timestamp = format_timestamp(segment.start, "simple")
                pdf.set_font("Arial", "B", 10)
                speaker = f"[{segment.speaker}] " if segment.speaker else ""
                pdf.cell(0, 6, f"[{timestamp}] {speaker}", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, segment.text)
                pdf.ln(2)

        pdf.output(output_path)

    @staticmethod
    def export(
        result: TranscriptionResult,
        format: str,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Export transcription in specified format

        Args:
            result: TranscriptionResult to export
            format: Output format (txt, srt, vtt, json, markdown, csv, pdf)
            output_path: Path to save file (optional, returns string if not provided)
            **kwargs: Additional format-specific options

        Returns:
            Exported content as string (except for PDF which writes to file)
        """
        format = format.lower()

        # Generate content
        if format == "txt":
            content = ExportService.to_txt(
                result, include_timestamps=kwargs.get("include_timestamps", False)
            )
        elif format == "srt":
            content = ExportService.to_srt(result)
        elif format == "vtt":
            content = ExportService.to_vtt(result)
        elif format == "json":
            content = ExportService.to_json(result, pretty=kwargs.get("pretty", True))
        elif format == "markdown" or format == "md":
            content = ExportService.to_markdown(
                result, title=kwargs.get("title"), metadata=kwargs.get("metadata")
            )
        elif format == "csv":
            content = ExportService.to_csv(result)
        elif format == "pdf":
            if not output_path:
                raise ValueError("output_path is required for PDF export")
            ExportService.to_pdf(
                result,
                output_path,
                title=kwargs.get("title"),
                metadata=kwargs.get("metadata"),
            )
            return output_path
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Save to file if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return content


# Global export service instance
export_service = ExportService()
