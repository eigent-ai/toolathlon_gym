"""
Preprocess for yt-ml-repos-github-notion-excel-email task.

- Clears notion, email, arxiv tables
- Injects ML Tech Reviews channel, playlist, and 7 videos into youtube schema
- Injects 5 ML papers into arxiv.papers
- Injects 1 email from PI asking about ML tool landscape
"""
import argparse
import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

ML_CHANNEL_ID = "UCmlTech2024xyz"
ML_PLAYLIST_ID = "PLmlTech2024ml"

ML_VIDEOS = [
    {
        "video_id": "mlu7idceolY",
        "title": "Flash Attention - Faster Transformer Training Explained",
        "description": "In this video we explore FlashAttention, a revolutionary attention algorithm for faster transformer training. GitHub repo: https://github.com/Dao-AILab/flash-attention. Paper: arxiv 2307.08691.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2023-11-05T10:00:00Z",
        "duration": 1450,
        "view_count": 285000,
        "like_count": 8200,
        "tags": ["Flash Attention", "transformers", "GPU", "attention", "deep learning"],
    },
    {
        "video_id": "dA-NhSBt4To",
        "title": "LoRA - Efficient Fine-tuning of Large Language Models",
        "description": "LoRA (Low-Rank Adaptation) enables parameter-efficient fine-tuning of LLMs. GitHub: https://github.com/microsoft/LoRA. See also arxiv 2106.09685.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2023-10-20T10:00:00Z",
        "duration": 1280,
        "view_count": 198000,
        "like_count": 6100,
        "tags": ["LoRA", "fine-tuning", "LLM", "PEFT", "language models"],
    },
    {
        "video_id": "J87hQFtSmas",
        "title": "Stable Diffusion - Open Source Image Generation Deep Dive",
        "description": "A technical walkthrough of Stable Diffusion for open source image generation. GitHub repo: https://github.com/CompVis/stable-diffusion. Diffusion Models explained.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2023-09-15T10:00:00Z",
        "duration": 1820,
        "view_count": 412000,
        "like_count": 14500,
        "tags": ["Stable Diffusion", "diffusion models", "image generation", "generative AI"],
    },
    {
        "video_id": "9vM4p9NN0Ts",
        "title": "RLHF - Training AI with Human Feedback",
        "description": "Reinforcement Learning from Human Feedback (RLHF) is the technique behind ChatGPT and InstructGPT. GitHub: https://github.com/openai/lm-human-preferences. Paper: 2204.05149.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2023-08-30T10:00:00Z",
        "duration": 1560,
        "view_count": 156000,
        "like_count": 4800,
        "tags": ["RLHF", "reinforcement learning", "human feedback", "alignment", "ChatGPT"],
    },
    {
        "video_id": "izrG86jG1Xk",
        "title": "Mixtral - Mixture of Experts Architecture Explained",
        "description": "Mixture of Experts (MoE) architecture enables efficient scaling of LLMs. Code: https://github.com/mistralai/mistral-src. See Mixtral paper arxiv 2310.06825.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2023-12-01T10:00:00Z",
        "duration": 1340,
        "view_count": 223000,
        "like_count": 7200,
        "tags": ["Mixture of Experts", "MoE", "Mixtral", "architecture", "LLM scaling"],
    },
    {
        "video_id": "wh3uuJTK9O0",
        "title": "bitsandbytes - LLM Quantization Made Easy",
        "description": "Quantization reduces LLM memory requirements dramatically. Library: https://github.com/TimDettmers/bitsandbytes. Related to arxiv 2208.07339 (LLM.int8()).",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2024-01-10T10:00:00Z",
        "duration": 1100,
        "view_count": 142000,
        "like_count": 4400,
        "tags": ["quantization", "bitsandbytes", "8-bit", "model compression", "inference"],
    },
    {
        "video_id": "klTvEwg3oJ4",
        "title": "pgvector - Vector Databases for AI Applications",
        "description": "Vector databases are essential for RAG and semantic search. pgvector adds vector similarity search to PostgreSQL. GitHub: https://github.com/pgvector/pgvector.",
        "channel_id": ML_CHANNEL_ID,
        "channel_title": "ML Tech Reviews",
        "published_at": "2024-02-05T10:00:00Z",
        "duration": 980,
        "view_count": 187000,
        "like_count": 5900,
        "tags": ["vector databases", "pgvector", "RAG", "embeddings", "semantic search"],
    },
]

PAPERS = [
    {
        "id": "2307.08691",
        "title": "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning",
        "authors": [{"name": "Tri Dao"}],
        "summary": "We present FlashAttention-2, an improved version of FlashAttention with better parallelism and work partitioning. It achieves up to 2x speedup over FlashAttention by rewriting the attention algorithm to reduce non-matmul FLOPs, better parallelizing the attention computation, and optimizing work partitioning between warps.",
        "categories": ["cs.LG", "cs.PF"],
        "primary_category": "cs.LG",
        "pdf_url": "https://arxiv.org/pdf/2307.08691",
        "published": "2023-07-17",
    },
    {
        "id": "2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": [{"name": "Edward Hu"}, {"name": "Yelong Shen"}, {"name": "Phillip Wallis"}],
        "summary": "We propose Low-Rank Adaptation, or LoRA, which freezes the pretrained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks.",
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "pdf_url": "https://arxiv.org/pdf/2106.09685",
        "published": "2021-06-17",
    },
    {
        "id": "2310.06825",
        "title": "Mixtral of Experts",
        "authors": [{"name": "Albert Q. Jiang"}, {"name": "Alexandre Sablayrolles"}],
        "summary": "We introduce Mixtral 8x7B, a Sparse Mixture of Experts language model. At every layer, for every token, a router network selects two experts to process the current state and combine their outputs.",
        "categories": ["cs.LG", "cs.CL"],
        "primary_category": "cs.LG",
        "pdf_url": "https://arxiv.org/pdf/2310.06825",
        "published": "2023-10-10",
    },
    {
        "id": "2204.05149",
        "title": "Training language models to follow instructions with human feedback",
        "authors": [{"name": "Long Ouyang"}, {"name": "Jeff Wu"}, {"name": "Xu Jiang"}],
        "summary": "We fine-tune GPT-3 to follow a broad class of written instructions using reinforcement learning from human feedback to align language models to user intent.",
        "categories": ["cs.LG", "cs.CL"],
        "primary_category": "cs.LG",
        "pdf_url": "https://arxiv.org/pdf/2204.05149",
        "published": "2022-03-04",
    },
    {
        "id": "2208.07339",
        "title": "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale",
        "authors": [{"name": "Tim Dettmers"}, {"name": "Mike Lewis"}, {"name": "Younes Belkada"}],
        "summary": "We develop a procedure for Int8 matrix multiplication for feed-forward and attention projection layers in transformers, which cut the memory needed for inference by half while retaining full precision performance.",
        "categories": ["cs.LG"],
        "primary_category": "cs.LG",
        "pdf_url": "https://arxiv.org/pdf/2208.07339",
        "published": "2022-08-15",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        # Clear notion
        try:
            cur.execute("DELETE FROM notion.comments")
        except Exception:
            pass
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        # Clear email
        try:
            cur.execute("DELETE FROM email.attachments")
        except Exception:
            pass
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
        # Clear arxiv
        cur.execute("DELETE FROM arxiv.papers")
        # Clear ML Tech Reviews youtube data (clean slate for this channel)
        cur.execute("DELETE FROM youtube.playlist_items WHERE playlist_id = %s", (ML_PLAYLIST_ID,))
        cur.execute("DELETE FROM youtube.playlists WHERE playlist_id = %s", (ML_PLAYLIST_ID,))
        cur.execute("DELETE FROM youtube.videos WHERE channel_id = %s", (ML_CHANNEL_ID,))
        cur.execute("DELETE FROM youtube.channels WHERE channel_id = %s", (ML_CHANNEL_ID,))
    conn.commit()
    print("[preprocess] Cleared notion, email, arxiv tables and old ML Tech Reviews data")


def inject_ml_tech_youtube(conn):
    with conn.cursor() as cur:
        # Insert channel
        cur.execute("""
            INSERT INTO youtube.channels (channel_id, title, description, subscriber_count, video_count, view_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (channel_id) DO UPDATE SET
                title = EXCLUDED.title,
                video_count = EXCLUDED.video_count
        """, (
            ML_CHANNEL_ID,
            "ML Tech Reviews",
            "Deep technical reviews of machine learning tools, frameworks, and open-source projects.",
            45000, 7, 1603000,
        ))

        # Insert playlist
        cur.execute("""
            INSERT INTO youtube.playlists (playlist_id, title, description, channel_id, item_count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            ML_PLAYLIST_ID,
            "Machine Learning Tools & Frameworks 2024",
            "Curated playlist covering the most important ML tools and frameworks of 2024.",
            ML_CHANNEL_ID, 7,
        ))

        # Insert videos
        for i, v in enumerate(ML_VIDEOS):
            cur.execute("""
                INSERT INTO youtube.videos
                (video_id, title, description, channel_id, channel_title, published_at,
                 duration, view_count, like_count, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    view_count = EXCLUDED.view_count
            """, (
                v["video_id"], v["title"], v["description"],
                v["channel_id"], v["channel_title"], v["published_at"],
                v["duration"], v["view_count"], v["like_count"], v["tags"],  # tags is list -> text[]
            ))
            # Insert playlist item
            cur.execute("""
                INSERT INTO youtube.playlist_items (playlist_id, video_id, position, title, description, published_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                ML_PLAYLIST_ID, v["video_id"], i,
                v["title"], v["description"][:200], v["published_at"],
            ))

    conn.commit()
    print(f"[preprocess] Injected ML Tech Reviews channel with {len(ML_VIDEOS)} videos and playlist")


def inject_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary
            """, (
                p["id"], p["title"], json.dumps(p["authors"]),
                p["summary"], json.dumps(p["categories"]), p["primary_category"],
                p["pdf_url"], p["published"], True,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} ML papers into arxiv.papers")


def inject_email(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            folder_id = cur.fetchone()[0]
            conn.commit()

        cur.execute("""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "ML Tool Landscape Catalog",
            "pi@lab.edu",
            json.dumps(["research@lab.edu"]),
            "2026-03-06 09:00:00+00",
            "Hi team, I would like you to compile a catalog of the ML Tech Reviews channel on the video platform. They have a curated playlist of 7 videos each covering a key open-source ML tool. Please cross-reference each with relevant papers from our library, build a knowledge base page for the team, and send me a summary with the full details in an Excel tracker. Thanks!",
        ))
    conn.commit()
    print("[preprocess] Injected PI email about ML landscape")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_ml_tech_youtube(conn)
        inject_arxiv_papers(conn)
        inject_email(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
