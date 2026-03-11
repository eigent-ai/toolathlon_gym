"""Tool definitions for the arXiv MCP server.

This module contains ONLY tool schema definitions (no external dependencies like arxiv).
Both the original tools and the PG adapter import from here to ensure a single source of truth.
"""

import mcp.types as types

search_tool = types.Tool(
    name='search_papers',
    description='Search for papers on arXiv with advanced filtering and query optimization.\n\nQUERY CONSTRUCTION GUIDELINES:\n- Use QUOTED PHRASES for exact matches: "multi-agent systems", "neural networks", "machine learning"\n- Combine related concepts with OR: "AI agents" OR "software agents" OR "intelligent agents"  \n- Use field-specific searches for precision:\n  - ti:"exact title phrase" - search in titles only\n  - au:"author name" - search by author\n  - abs:"keyword" - search in abstracts only\n- Use ANDNOT to exclude unwanted results: "machine learning" ANDNOT "survey"\n- For best results, use 2-4 core concepts rather than long keyword lists\n\nADVANCED SEARCH PATTERNS:\n- Field + phrase: ti:"transformer architecture" for papers with exact title phrase\n- Multiple fields: au:"Smith" AND ti:"quantum" for author Smith\'s quantum papers  \n- Exclusions: "deep learning" ANDNOT ("survey" OR "review") to exclude survey papers\n- Broad + narrow: "artificial intelligence" AND (robotics OR "computer vision")\n\nCATEGORY FILTERING (highly recommended for relevance):\n- cs.AI: Artificial Intelligence\n- cs.MA: Multi-Agent Systems  \n- cs.LG: Machine Learning\n- cs.CL: Computation and Language (NLP)\n- cs.CV: Computer Vision\n- cs.RO: Robotics\n- cs.HC: Human-Computer Interaction\n- cs.CR: Cryptography and Security\n- cs.DB: Databases\n\nEXAMPLES OF EFFECTIVE QUERIES:\n- ti:"reinforcement learning" with categories: ["cs.LG", "cs.AI"] - for RL papers by title\n- au:"Hinton" AND "deep learning" with categories: ["cs.LG"] - for Hinton\'s deep learning work\n- "multi-agent" ANDNOT "survey" with categories: ["cs.MA"] - exclude survey papers\n- abs:"transformer" AND ti:"attention" with categories: ["cs.CL"] - attention papers with transformer abstracts\n\nDATE FILTERING: Use YYYY-MM-DD format for historical research:\n- date_to: "2015-12-31" - for foundational/classic work (pre-2016)\n- date_from: "2020-01-01" - for recent developments (post-2020)\n- Both together for specific time periods\n\nRESULT QUALITY: Results sorted by RELEVANCE (most relevant papers first), not just newest papers.\nThis ensures you get the most pertinent results regardless of publication date.\n\nTIPS FOR FOUNDATIONAL RESEARCH:\n- Use date_to: "2010-12-31" to find classic papers on BDI, SOAR, ACT-R\n- Combine with field searches: ti:"BDI" AND abs:"belief desire intention"  \n- Try author searches: au:"Rao" AND "BDI" for Anand Rao\'s foundational BDI work',
    inputSchema={'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Search query using quoted phrases for exact matches (e.g., \'"machine learning" OR "deep learning"\') or specific technical terms. Avoid overly broad or generic terms.'}, 'max_results': {'type': 'integer', 'description': 'Maximum number of results to return (default: 10, max: 50). Use 15-20 for comprehensive searches.'}, 'date_from': {'type': 'string', 'description': "Start date for papers (YYYY-MM-DD format). Use to find recent work, e.g., '2023-01-01' for last 2 years."}, 'date_to': {'type': 'string', 'description': "End date for papers (YYYY-MM-DD format). Use with date_from to find historical work, e.g., '2020-12-31' for older research."}, 'categories': {'type': 'array', 'items': {'type': 'string'}, 'description': "Strongly recommended: arXiv categories to focus search (e.g., ['cs.AI', 'cs.MA'] for agent research, ['cs.LG'] for ML, ['cs.CL'] for NLP, ['cs.CV'] for vision). Greatly improves relevance."}, 'sort_by': {'type': 'string', 'enum': ['relevance', 'date'], 'description': "Sort results by 'relevance' (most relevant first, default) or 'date' (newest first). Use 'relevance' for focused searches, 'date' for recent developments."}}, 'required': ['query']},
)

download_tool = types.Tool(
    name='download_paper',
    description='Download a paper and create a resource for it',
    inputSchema={'type': 'object', 'properties': {'paper_id': {'type': 'string', 'description': 'The arXiv ID of the paper to download'}, 'check_status': {'type': 'boolean', 'description': 'If true, only check conversion status without downloading', 'default': False}}, 'required': ['paper_id']},
)

list_tool = types.Tool(
    name='list_papers',
    description='List all existing papers available as resources',
    inputSchema={'type': 'object', 'properties': {}, 'required': []},
)

read_tool = types.Tool(
    name='read_paper',
    description='Read the full content of a stored paper in markdown format',
    inputSchema={'type': 'object', 'properties': {'paper_id': {'type': 'string', 'description': 'The arXiv ID of the paper to read'}}, 'required': ['paper_id']},
)
