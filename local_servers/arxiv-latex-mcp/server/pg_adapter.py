"""PostgreSQL adapter replacing arxiv_to_prompt for arxiv-latex-mcp."""

import os
import json
import psycopg2
import psycopg2.extras
from typing import Optional, List


def _get_conn():
    return psycopg2.connect(
        host=os.environ.get('PG_HOST', 'localhost'),
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ.get('PG_DATABASE', 'toolathlon'),
        user=os.environ.get('PG_USER', 'postgres'),
        password=os.environ.get('PG_PASSWORD', 'postgres'),
    )


def process_latex_source(arxiv_id: str, abstract_only: bool = False) -> str:
    """Replace arxiv_to_prompt.process_latex_source with PG lookup."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT title, abstract, full_prompt, sections FROM arxiv_latex.papers WHERE id = %s",
                (arxiv_id,)
            )
            row = cur.fetchone()

        if not row:
            raise ValueError(f"Paper {arxiv_id} not found in database")

        if abstract_only:
            return row['abstract'] or f"No abstract available for {arxiv_id}"

        return row['full_prompt'] or f"No content available for {arxiv_id}"
    finally:
        conn.close()


def list_sections(text: str) -> List[str]:
    """List section headings from the processed text.

    This mimics arxiv_to_prompt.list_sections by parsing section headers
    from the full_prompt text. We look for patterns like:
    # Section Title
    ## Subsection Title
    """
    sections = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            # Count heading level
            level = 0
            for ch in stripped:
                if ch == '#':
                    level += 1
                else:
                    break
            title = stripped[level:].strip()
            if title:
                # Generate section path based on numbering
                sections.append(title)
    return sections


def extract_section(text: str, section_path: str) -> Optional[str]:
    """Extract a specific section from the processed text.

    Mimics arxiv_to_prompt.extract_section.
    """
    lines = text.split('\n')
    in_section = False
    section_level = 0
    result_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            level = 0
            for ch in stripped:
                if ch == '#':
                    level += 1
                else:
                    break
            title = stripped[level:].strip()

            if in_section:
                # If we hit a heading at same or higher level, stop
                if level <= section_level:
                    break
                result_lines.append(line)
            elif title.lower() == section_path.lower() or section_path in title:
                in_section = True
                section_level = level
                result_lines.append(line)
        elif in_section:
            result_lines.append(line)

    if result_lines:
        return '\n'.join(result_lines)

    # Try matching by section number (e.g., "1", "2.1")
    # Look for patterns like "1 Introduction", "2.1 Methods"
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            level = 0
            for ch in stripped:
                if ch == '#':
                    level += 1
                else:
                    break
            title = stripped[level:].strip()
            # Check if section_path matches the number prefix
            if title.startswith(section_path + ' ') or title.startswith(section_path + '.'):
                in_section = True
                section_level = level
                result_lines.append(line)
                for subsequent_line in lines[i+1:]:
                    sub_stripped = subsequent_line.strip()
                    if sub_stripped.startswith('#'):
                        sub_level = sum(1 for ch in sub_stripped if ch == '#')
                        if sub_level <= section_level:
                            break
                    result_lines.append(subsequent_line)
                return '\n'.join(result_lines) if result_lines else None

    return None
