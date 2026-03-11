from typing import Any, List, Dict, Optional, Tuple
import PyPDF2
import io
import os
import argparse
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import logging
import sys
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import requests
import json

# Global variables
mcp = FastMCP("pdf-tools")
WORKSPACE_PATH = None
TEMPFILE_DIR = None

# Search cache and session management
@dataclass
class SearchResult:
    text: str
    page_number: int
    start_index: int
    end_index: int
    context_before: str
    context_after: str

@dataclass
class SearchSession:
    search_id: str
    pdf_path: str
    pattern: str
    results: List[SearchResult]
    current_page: int
    page_size: int
    total_results: int
    last_accessed: datetime
    cached_content: Optional[Dict[int, str]] = None

# Global cache for search sessions and PDF content
search_sessions: Dict[str, SearchSession] = {}
pdf_content_cache: Dict[str, Dict[int, str]] = {}  # file_path -> {page_num -> content}
cache_lock = threading.Lock()

# Cache cleanup settings
MAX_CACHE_AGE_MINUTES = 30
MAX_CACHED_PDFS = 10

def setup_server(workspace_path: str = None, tempfile_dir: str = None):
    """Setup the MCP server with optional workspace path and temporary file directory
    
    Args:
        workspace_path: Workspace directory path for PDF operations restriction
        tempfile_dir: Directory to store temporary files downloaded from URLs
    """
    global WORKSPACE_PATH, TEMPFILE_DIR
    
    # change working dir to workspace_path
    if workspace_path: 
        os.chdir(workspace_path)
        sys.path.append(workspace_path)
    
    # Global workspace path
    WORKSPACE_PATH = Path(workspace_path).resolve() if workspace_path else None
    
    # Setup temporary file directory
    if tempfile_dir:
        TEMPFILE_DIR = Path(tempfile_dir).resolve()
    else:
        TEMPFILE_DIR = Path.home() / ".pdf_tools_temp"
    
    # Create tempfile directory if it doesn't exist
    TEMPFILE_DIR.mkdir(parents=True, exist_ok=True)

def is_url(path: str) -> bool:
    """Check if a path is a URL
    
    Args:
        path: Path string to check
        
    Returns:
        True if path is a URL, False otherwise
    """
    return path.startswith(('http://', 'https://'))

def download_pdf_from_url(url: str) -> str:
    """Download PDF from URL to temporary file with validation
    
    Args:
        url: URL to download PDF from
        
    Returns:
        Path to downloaded temporary file
        
    Raises:
        Exception: If download fails or file is not a valid PDF
    """
    try:
        # Check content type with HEAD request first (optional check)
        try:
            head_response = requests.head(url, timeout=10, allow_redirects=True)
            content_type = head_response.headers.get('content-type', '').lower()
            if content_type and not any(pdf_type in content_type for pdf_type in [
                'application/pdf', 
                'application/x-pdf',
                'application/acrobat'
            ]):
                logging.warning(f"Content-Type is not PDF: {content_type}")
        except requests.RequestException:
            # Continue if HEAD request fails, some servers don't support it
            pass
        
        # Download the file
        response = requests.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Generate unique filename
        temp_filename = f"{uuid.uuid4()}.pdf"
        temp_path = TEMPFILE_DIR / temp_filename
        
        # Save to temporary file
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Validate PDF magic bytes
        with open(temp_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                os.remove(temp_path)
                raise Exception("Downloaded file is not a valid PDF format")
        
        # Validate with PyPDF2
        try:
            with open(temp_path, 'rb') as f:
                PyPDF2.PdfReader(f)
        except Exception:
            os.remove(temp_path)
            raise Exception("PDF file appears to be corrupted or unreadable")
        
        return str(temp_path)
        
    except requests.RequestException as e:
        raise Exception(f"Failed to download PDF from URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing PDF download: {str(e)}")

def load_url_mapping() -> Dict[str, str]:
    """Load URL to temporary file mapping from JSON file
    
    Returns:
        Dictionary mapping URLs to temporary file paths
    """
    mapping_file = TEMPFILE_DIR / "url_tempfile_mapping.json"
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logging.warning("Failed to load URL mapping file, starting with empty mapping")
    return {}

def save_url_mapping(mapping: Dict[str, str]):
    """Save URL to temporary file mapping to JSON file
    
    Args:
        mapping: Dictionary mapping URLs to temporary file paths
    """
    mapping_file = TEMPFILE_DIR / "url_tempfile_mapping.json"
    try:
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logging.error(f"Failed to save URL mapping: {str(e)}")

def resolve_path(path: str) -> str:
    """Resolve path - download if URL, return as-is if local path
    
    Args:
        path: File path or URL
        
    Returns:
        Local file path (downloaded temporary file for URLs)
        
    Raises:
        Exception: If URL download fails or validation fails
    """
    if not is_url(path):
        return path
    
    # Check if URL is already mapped
    url_mapping = load_url_mapping()
    if path in url_mapping:
        temp_path = url_mapping[path]
        # Verify the temp file still exists
        if Path(temp_path).exists():
            return temp_path
        else:
            # Remove invalid mapping
            del url_mapping[path]
            save_url_mapping(url_mapping)
    
    # Download PDF from URL
    temp_path = download_pdf_from_url(path)
    
    # Update mapping
    url_mapping[path] = temp_path
    save_url_mapping(url_mapping)
    
    return temp_path

def validate_path(file_path: str) -> tuple[bool, str]:
    """Validate if the file path is within the allowed workspace
    
    Args:
        file_path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if WORKSPACE_PATH is None:
        return True, ""
    
    try:
        resolved_path = Path(file_path).resolve()
        if not resolved_path.is_relative_to(WORKSPACE_PATH):
            return False, f"Error: Path '{file_path}' is outside the allowed workspace '{WORKSPACE_PATH}'"
        return True, ""
    except Exception as e:
        return False, f"Error validating path: {str(e)}"

def validate_page_range(start_page: int, end_page: int, total_pages: int) -> tuple[int, int]:
    """Validate and correct page range to ensure it's within valid bounds"""
    # Handle negative page numbers
    if start_page < 1:
        start_page = 1
    if end_page < 1:
        end_page = 1
    
    # Handle pages exceeding total page count
    if start_page > total_pages:
        start_page = total_pages
    if end_page > total_pages:
        end_page = total_pages
    
    # Ensure start page is not greater than end page
    if start_page > end_page:
        start_page, end_page = end_page, start_page
    
    return start_page, end_page

def cleanup_cache():
    """Clean up old search sessions and PDF content cache"""
    with cache_lock:
        current_time = datetime.now()
        
        # Remove old search sessions
        expired_sessions = [
            session_id for session_id, session in search_sessions.items()
            if current_time - session.last_accessed > timedelta(minutes=MAX_CACHE_AGE_MINUTES)
        ]
        for session_id in expired_sessions:
            del search_sessions[session_id]
        
        # Limit PDF cache size
        if len(pdf_content_cache) > MAX_CACHED_PDFS:
            # Remove oldest entries (simple strategy - could be improved with LRU)
            oldest_keys = list(pdf_content_cache.keys())[:len(pdf_content_cache) - MAX_CACHED_PDFS + 1]
            for key in oldest_keys:
                del pdf_content_cache[key]

def get_cached_pdf_content(pdf_path: str) -> Optional[Dict[int, str]]:
    """Get cached PDF content by path"""
    with cache_lock:
        return pdf_content_cache.get(pdf_path)

def cache_pdf_content(pdf_path: str, content: Dict[int, str]):
    """Cache PDF content by path"""
    with cache_lock:
        # Only cleanup if cache is getting full
        if len(pdf_content_cache) >= MAX_CACHED_PDFS:
            cleanup_cache()
        pdf_content_cache[pdf_path] = content

def extract_all_text_from_pdf(pdf_path: str) -> Dict[int, str]:
    """Extract text from all pages of a PDF and return as dict {page_num: text}"""
    # Check cache first
    cached_content = get_cached_pdf_content(pdf_path)
    if cached_content is not None:
        return cached_content
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = {}
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                content[page_num + 1] = text  # Store with 1-indexed page numbers
            
            # Cache the content
            cache_pdf_content(pdf_path, content)
            return content
            
    except Exception as e:
        logging.error(f"Error extracting PDF text: {str(e)}")
        return {}

def find_regex_matches(text: str, pattern: str, page_number: int, context_size: int = 100) -> List[SearchResult]:
    """Find all regex matches in text and return SearchResult objects with context"""
    try:
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            start_idx = match.start()
            end_idx = match.end()
            
            # Get context before and after the match
            context_start = max(0, start_idx - context_size)
            context_end = min(len(text), end_idx + context_size)
            
            context_before = text[context_start:start_idx]
            context_after = text[end_idx:context_end]
            matched_text = text[start_idx:end_idx]
            
            result = SearchResult(
                text=matched_text,
                page_number=page_number,
                start_index=start_idx,
                end_index=end_idx,
                context_before=context_before,
                context_after=context_after
            )
            matches.append(result)
        
        return matches
    except re.error as e:
        logging.error(f"Invalid regex pattern '{pattern}': {str(e)}")
        return []

def extract_text_from_pdf(pdf_content: bytes, start_page: int, end_page: int) -> str:
    """Extract text from PDF content for specified page range"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        total_pages = len(pdf_reader.pages)
        
        # Validate and correct page range
        start_page, end_page = validate_page_range(start_page, end_page, total_pages)
        
        # Extract text
        extracted_text = []
        for page_num in range(start_page - 1, end_page):  # PyPDF2 uses 0-index
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text.strip():  # Only add non-empty pages
                extracted_text.append(f"=== Page {page_num + 1} ===\n{text}")
        
        if not extracted_text:
            return f"PDF total pages: {total_pages}\nSpecified page range ({start_page}-{end_page}) has no extractable text content."
        
        result = f"PDF total pages: {total_pages}\nExtracted page range: {start_page}-{end_page}\n\n"
        result += "\n\n".join(extracted_text)
        return result
        
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def validate_page_size(page_size: int) -> Tuple[int, str]:
    """Validate page size and return corrected value with warning if needed"""
    warning = ""
    if page_size < 10 or page_size > 50:
        warning = f"Warning: Page size {page_size} is out of range (10-50). Using default value 10.\n"
        page_size = 10
    return page_size, warning

@mcp.tool()
async def read_pdf_pages(pdf_file_path: str, start_page: int = 1, end_page: int = 1) -> str:
    """Read content from PDF file for specified page range.
    
    Supports both local file paths and URLs. For URLs, the PDF will be downloaded
    to a temporary directory and cached for future use.
    
    Note: Avoid reading too many pages at once (recommended: <50 pages) to prevent errors.

    Args:
        pdf_file_path: Path to the PDF file or URL to PDF
        start_page: Starting page number (default: 1)
        end_page: Ending page number (default: 1)
        
    Returns:
        Extracted text content from the specified pages
    """
    try:
        # Resolve path (download if URL, validate if local path)
        actual_path = resolve_path(pdf_file_path)
        
        # Validate local path if not URL
        if not is_url(pdf_file_path):
            is_valid, error_msg = validate_path(pdf_file_path)
            if not is_valid:
                return error_msg
    
    except Exception as e:
        return f"Error resolving path: {str(e)}"
    
    # Warning for large page ranges
    if end_page - start_page > 50:
        warning = "Warning: Reading more than 50 pages at once may cause performance issues or errors.\n"
    else:
        warning = ""
    
    try:
        # Read PDF file
        with open(actual_path, 'rb') as file:
            pdf_content = file.read()
        
        # Extract text using the original function
        result = extract_text_from_pdf(pdf_content, start_page, end_page)
        return warning + result if warning else result
        
    except FileNotFoundError:
        return f"Error: File not found '{actual_path}'"
    except PermissionError:
        return f"Error: No permission to read file '{actual_path}'"
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"

@mcp.tool()
async def get_pdf_info(pdf_file_path: str) -> str:
    """Get basic information about a PDF file including page count.
    
    Supports both local file paths and URLs. For URLs, the PDF will be downloaded
    to a temporary directory and cached for future use.

    Args:
        pdf_file_path: Path to the PDF file or URL to PDF
        
    Returns:
        Basic information about the PDF file
    """
    try:
        # Resolve path (download if URL, validate if local path)
        actual_path = resolve_path(pdf_file_path)
        
        # Validate local path if not URL
        if not is_url(pdf_file_path):
            is_valid, error_msg = validate_path(pdf_file_path)
            if not is_valid:
                return error_msg
    
    except Exception as e:
        return f"Error resolving path: {str(e)}"
    
    try:
        with open(actual_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get all needed information within the with block
            total_pages = len(pdf_reader.pages)
            info = pdf_reader.metadata
            
            result = "PDF file information:\n"
            result += f"Total pages: {total_pages}\n"
            
            if info:
                result += f"Title: {info.get('/Title', 'Unknown')}\n"
                result += f"Author: {info.get('/Author', 'Unknown')}\n"
                result += f"Creator: {info.get('/Creator', 'Unknown')}\n"
                result += f"Creation date: {info.get('/CreationDate', 'Unknown')}\n"
            
            return result
        
    except FileNotFoundError:
        return f"Error: File not found '{actual_path}'"
    except Exception as e:
        return f"Error getting PDF information: {str(e)}"

@mcp.tool()
async def merge_pdfs(pdf_paths: List[str], output_path: str) -> str:
    """Merge multiple PDF files into one.
    
    Supports both local file paths and URLs. URLs will be downloaded to temporary
    files before merging. Mixed local and URL paths are supported.

    Args:
        pdf_paths: List of paths to PDF files to merge (in order) - can include URLs
        output_path: Path where the merged PDF will be saved (must be local path)
        
    Returns:
        Success message with merge details or error message
    """
    # Resolve all input paths (download URLs if needed)
    actual_paths = []
    for pdf_path in pdf_paths:
        try:
            actual_path = resolve_path(pdf_path)
            
            # Validate local path if not URL
            if not is_url(pdf_path):
                is_valid, error_msg = validate_path(pdf_path)
                if not is_valid:
                    return error_msg
            
            actual_paths.append(actual_path)
            
        except Exception as e:
            return f"Error resolving path '{pdf_path}': {str(e)}"
    
    # Validate output path (must be local)
    if is_url(output_path):
        return "Error: Output path cannot be a URL, must be a local file path"
    
    is_valid, error_msg = validate_path(output_path)
    if not is_valid:
        return error_msg
    
    try:
        pdf_writer = PyPDF2.PdfWriter()
        total_pages_merged = 0
        
        for i, actual_path in enumerate(actual_paths):
            original_path = pdf_paths[i]
            try:
                with open(actual_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pages_count = len(pdf_reader.pages)
                    
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                    
                    total_pages_merged += pages_count
                    logging.info(f"Added {pages_count} pages from {original_path}")
            
            except Exception as e:
                return f"Error reading PDF '{original_path}': {str(e)}"
        
        # Write the merged PDF
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Successfully merged {len(pdf_paths)} PDFs into '{output_path}'\nTotal pages: {total_pages_merged}"
        
    except Exception as e:
        return f"Error merging PDFs: {str(e)}"

@mcp.tool()
async def extract_pdf_pages(source_path: str, page_numbers: List[int], output_path: str) -> str:
    """Extract specific pages from a PDF and create a new PDF.
    
    Supports URLs for source PDF. The source PDF will be downloaded to a temporary
    directory if it's a URL. Output path must be a local file path.

    Args:
        source_path: Path to the source PDF file or URL to PDF
        page_numbers: List of page numbers to extract (1-indexed)
        output_path: Path where the new PDF will be saved (must be local path)
        
    Returns:
        Success message with extraction details or error message
    """
    # Resolve source path (download if URL)
    try:
        actual_source_path = resolve_path(source_path)
        
        # Validate local path if not URL
        if not is_url(source_path):
            is_valid, error_msg = validate_path(source_path)
            if not is_valid:
                return error_msg
    
    except Exception as e:
        return f"Error resolving source path: {str(e)}"
    
    # Validate output path (must be local)
    if is_url(output_path):
        return "Error: Output path cannot be a URL, must be a local file path"
        
    is_valid, error_msg = validate_path(output_path)
    if not is_valid:
        return error_msg
    
    try:
        with open(actual_source_path, 'rb') as source_file:
            pdf_reader = PyPDF2.PdfReader(source_file)
            total_pages = len(pdf_reader.pages)
            pdf_writer = PyPDF2.PdfWriter()
            
            extracted_pages = []
            
            for page_num in page_numbers:
                if 1 <= page_num <= total_pages:
                    pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                    extracted_pages.append(page_num)
                else:
                    logging.warning(f"Page {page_num} is out of range (1-{total_pages}), skipping")
            
            if not extracted_pages:
                return f"Error: No valid pages to extract from PDF (total pages: {total_pages})"
            
            # Write the new PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully extracted {len(extracted_pages)} pages from '{source_path}' to '{output_path}'\nExtracted pages: {extracted_pages}\nSource PDF total pages: {total_pages}"
            
    except FileNotFoundError:
        return f"Error: File not found '{actual_source_path}'"
    except Exception as e:
        return f"Error extracting pages: {str(e)}"

@mcp.tool()
async def search_pdf_content(pdf_file_path: str, pattern: str, page_size: int = 10) -> str:
    """Search for regex pattern in PDF content and return paginated results.
    
    Supports both local file paths and URLs. For URLs, the PDF will be downloaded
    to a temporary directory and cached for future use.
    
    Args:
        pdf_file_path: Path to the PDF file or URL to PDF
        pattern: Regular expression pattern to search for
        page_size: Number of results per page (10-50, default: 10)
    
    Returns:
        Search results with UUID for pagination, or error message
    """
    try:
        # Resolve path (download if URL, validate if local path)
        actual_path = resolve_path(pdf_file_path)
        
        # Validate local path if not URL
        if not is_url(pdf_file_path):
            is_valid, error_msg = validate_path(pdf_file_path)
            if not is_valid:
                return error_msg
    
    except Exception as e:
        return f"Error resolving path: {str(e)}"
    
    # Validate page size
    page_size, warning = validate_page_size(page_size)
    
    try:
        # Extract all text from PDF using actual path
        pdf_content = extract_all_text_from_pdf(actual_path)
        if not pdf_content:
            return "Error: Could not extract text from PDF or PDF is empty"
        
        # Find all matches across all pages
        all_results = []
        for page_num, page_text in pdf_content.items():
            page_matches = find_regex_matches(page_text, pattern, page_num)
            all_results.extend(page_matches)
        
        if not all_results:
            return f"No matches found for pattern: {pattern}"
        
        # Create search session
        search_id = str(uuid.uuid4())[:8]  # Short UUID
        session = SearchSession(
            search_id=search_id,
            pdf_path=pdf_file_path,
            pattern=pattern,
            results=all_results,
            current_page=1,
            page_size=page_size,
            total_results=len(all_results),
            last_accessed=datetime.now(),
            cached_content=pdf_content
        )
        
        with cache_lock:
            # Only cleanup if we have too many sessions
            if len(search_sessions) > 20:  # reasonable limit
                cleanup_cache()
            search_sessions[search_id] = session
        
        # Format first page of results
        start_idx = 0
        end_idx = min(page_size, len(all_results))
        current_results = all_results[start_idx:end_idx]
        
        result = warning if warning else ""
        result += f"Search ID: {search_id}\n"
        result += f"Pattern: {pattern}\n"
        result += f"Total matches: {len(all_results)}\n"
        result += f"Page: 1/{(len(all_results) + page_size - 1) // page_size}\n"
        result += f"Results per page: {page_size}\n\n"
        
        for i, match in enumerate(current_results, 1):
            result += f"Match {start_idx + i}:\n"
            result += f"  Page: {match.page_number}\n"
            result += f"  Text: \"{match.text}\"\n"
            result += f"  Context: ...{match.context_before}[{match.text}]{match.context_after}...\n\n"
        
        if len(all_results) > page_size:
            result += f"Use search_pdf_next_page, search_pdf_prev_page, or search_pdf_go_page with search_id '{search_id}' to navigate."
        
        return result
        
    except FileNotFoundError:
        return f"Error: File not found '{actual_path}'"
    except Exception as e:
        return f"Error searching PDF: {str(e)}"

@mcp.tool()
async def search_pdf_next_page(search_id: str) -> str:
    """Get next page of search results.
    
    Args:
        search_id: Search session ID from previous search
    
    Returns:
        Next page of search results or error message
    """
    with cache_lock:
        session = search_sessions.get(search_id)
        if not session:
            return f"Error: Search session '{search_id}' not found or expired"
        
        session.last_accessed = datetime.now()
        
        total_pages = (len(session.results) + session.page_size - 1) // session.page_size
        if session.current_page >= total_pages:
            return f"Already on last page ({session.current_page}/{total_pages})"
        
        session.current_page += 1
        
        start_idx = (session.current_page - 1) * session.page_size
        end_idx = min(start_idx + session.page_size, len(session.results))
        current_results = session.results[start_idx:end_idx]
        
        result = f"Search ID: {search_id}\n"
        result += f"Pattern: {session.pattern}\n"
        result += f"Total matches: {session.total_results}\n"
        result += f"Page: {session.current_page}/{total_pages}\n\n"
        
        for i, match in enumerate(current_results, 1):
            result += f"Match {start_idx + i}:\n"
            result += f"  Page: {match.page_number}\n"
            result += f"  Text: \"{match.text}\"\n"
            result += f"  Context: ...{match.context_before}[{match.text}]{match.context_after}...\n\n"
        
        return result

@mcp.tool()
async def search_pdf_prev_page(search_id: str) -> str:
    """Get previous page of search results.
    
    Args:
        search_id: Search session ID from previous search
    
    Returns:
        Previous page of search results or error message
    """
    with cache_lock:
        session = search_sessions.get(search_id)
        if not session:
            return f"Error: Search session '{search_id}' not found or expired"
        
        session.last_accessed = datetime.now()
        
        if session.current_page <= 1:
            return f"Already on first page (1)"
        
        session.current_page -= 1
        
        start_idx = (session.current_page - 1) * session.page_size
        end_idx = min(start_idx + session.page_size, len(session.results))
        current_results = session.results[start_idx:end_idx]
        
        total_pages = (len(session.results) + session.page_size - 1) // session.page_size
        
        result = f"Search ID: {search_id}\n"
        result += f"Pattern: {session.pattern}\n"
        result += f"Total matches: {session.total_results}\n"
        result += f"Page: {session.current_page}/{total_pages}\n\n"
        
        for i, match in enumerate(current_results, 1):
            result += f"Match {start_idx + i}:\n"
            result += f"  Page: {match.page_number}\n"
            result += f"  Text: \"{match.text}\"\n"
            result += f"  Context: ...{match.context_before}[{match.text}]{match.context_after}...\n\n"
        
        return result

@mcp.tool()
async def search_pdf_go_page(search_id: str, page_number: int) -> str:
    """Go to specific page of search results.
    
    Args:
        search_id: Search session ID from previous search
        page_number: Page number to go to (1-indexed)
    
    Returns:
        Specified page of search results or error message
    """
    with cache_lock:
        session = search_sessions.get(search_id)
        if not session:
            return f"Error: Search session '{search_id}' not found or expired"
        
        session.last_accessed = datetime.now()
        
        total_pages = (len(session.results) + session.page_size - 1) // session.page_size
        
        if page_number < 1 or page_number > total_pages:
            return f"Error: Page number {page_number} is out of range (1-{total_pages})"
        
        session.current_page = page_number
        
        start_idx = (session.current_page - 1) * session.page_size
        end_idx = min(start_idx + session.page_size, len(session.results))
        current_results = session.results[start_idx:end_idx]
        
        result = f"Search ID: {search_id}\n"
        result += f"Pattern: {session.pattern}\n"
        result += f"Total matches: {session.total_results}\n"
        result += f"Page: {session.current_page}/{total_pages}\n\n"
        
        for i, match in enumerate(current_results, 1):
            result += f"Match {start_idx + i}:\n"
            result += f"  Page: {match.page_number}\n"
            result += f"  Text: \"{match.text}\"\n"
            result += f"  Context: ...{match.context_before}[{match.text}]{match.context_after}...\n\n"
        
        return result

@mcp.tool()
async def search_pdf_info(search_id: str) -> str:
    """Get information about a search session.
    
    Args:
        search_id: Search session ID from previous search
    
    Returns:
        Information about the search session
    """
    with cache_lock:
        session = search_sessions.get(search_id)
        if not session:
            return f"Error: Search session '{search_id}' not found or expired"
        
        session.last_accessed = datetime.now()
        
        total_pages = (len(session.results) + session.page_size - 1) // session.page_size
        
        result = f"Search Session Information:\n"
        result += f"Search ID: {search_id}\n"
        result += f"PDF Path: {session.pdf_path}\n"
        result += f"Pattern: {session.pattern}\n"
        result += f"Total matches: {session.total_results}\n"
        result += f"Current page: {session.current_page}/{total_pages}\n"
        result += f"Results per page: {session.page_size}\n"
        result += f"Last accessed: {session.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return result

def main():
    """Main function to run the MCP server"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PDF Tools MCP Server')
    parser.add_argument('--workspace_path', type=str, default=None, 
                        help='Workspace directory path. All PDF operations will be restricted to this directory and its subdirectories.')
    parser.add_argument('--tempfile_dir', type=str, default=None,
                        help='Directory to store temporary files downloaded from URLs. Defaults to ~/.pdf_tools_temp')
    args = parser.parse_args()
    
    # Setup server
    setup_server(args.workspace_path, args.tempfile_dir)
    
    # Log workspace restriction if set
    if WORKSPACE_PATH:
        logging.info(f"Workspace restricted to: {WORKSPACE_PATH}")
    
    # Log temporary file directory
    if TEMPFILE_DIR:
        logging.info(f"Temporary files directory: {TEMPFILE_DIR}")
    
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()