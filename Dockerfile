FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Base system deps
RUN apt-get update && apt-get install -y \
    curl wget git ca-certificates gnupg \
    python3 python3-pip rsync postgresql-client \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libatspi2.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 libxcb1 \
    libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@latest

WORKDIR /workspace

# Create venv OUTSIDE /workspace so it is not shadowed by the volume mount
# camel-ai brings: openai, pyyaml, httpx, tiktoken, etc.
RUN uv venv /opt/venv && uv pip install --python /opt/venv/bin/python \
    "camel-ai" \
    "anthropic" \
    "psycopg2-binary" \
    "openpyxl" \
    "python-docx" \
    "python-pptx" \
    "termcolor" \
    "aiofiles" \
    "psutil" \
    "addict" \
    "arxiv" \
    "bibtexparser" \
    "canvasapi" \
    "prompt_toolkit"

ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# Install Playwright browser
RUN playwright install chromium || true

# Build Node-based and Python MCP servers from /opt/local_servers
# (keeps compiled artifacts outside the volume-mounted /workspace)
COPY local_servers/ /opt/local_servers/
RUN for dir in \
        /opt/local_servers/Calendar-Autoauth-MCP-Server \
        /opt/local_servers/google-forms-mcp \
        /opt/local_servers/mcp-google-sheets \
        /opt/local_servers/youtube-mcp-server \
        /opt/local_servers/filesystem \
        /opt/local_servers/HowToCook-mcp \
        /opt/local_servers/servers; do \
    [ -f "$dir/package.json" ] && \
        echo "=== $dir ===" && cd "$dir" && npm install && (npm run build 2>/dev/null || true) && cd /workspace || true; \
done

RUN for dir in \
        /opt/local_servers/arxiv-mcp-server \
        /opt/local_servers/arxiv-latex-mcp \
        /opt/local_servers/yahoo-finance-mcp \
        /opt/local_servers/emails-mcp \
        /opt/local_servers/mcp-snowflake-server \
        /opt/local_servers/mcp-scholarly \
        /opt/local_servers/Office-Word-MCP-Server \
        /opt/local_servers/Office-PowerPoint-MCP-Server \
        /opt/local_servers/excel-mcp-server \
        /opt/local_servers/pdf-tools-mcp \
        /opt/local_servers/mcp-youtube-transcript \
        /opt/local_servers/cli-mcp-server; do \
    [ -f "$dir/pyproject.toml" ] && \
        echo "=== $dir ===" && cd "$dir" && uv sync || true && cd /workspace || true; \
done

# Copy project code
COPY . .

CMD ["/bin/bash"]
