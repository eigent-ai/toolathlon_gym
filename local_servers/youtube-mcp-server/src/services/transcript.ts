import { TranscriptParams } from '../types.js';
import { pool } from './pg-youtube.js';

function parseVideoId(url: string): string {
  if (!url.includes('/') && !url.includes('=')) return url;
  const match = url.match(/[?&]v=([^&]+)/) || url.match(/youtu\.be\/([^?]+)/);
  if (match) return match[1];
  return url;
}

export class TranscriptService {
  async getTranscript({ videoId, language = 'en' }: TranscriptParams): Promise<any> {
    const vid = parseVideoId(videoId);
    let result = await pool.query(
      `SELECT title, content, snippets FROM youtube.transcripts WHERE video_id = $1 AND language = $2`,
      [vid, language]
    );
    if (result.rows.length === 0) {
      result = await pool.query(`SELECT title, content, snippets FROM youtube.transcripts WHERE video_id = $1 LIMIT 1`, [vid]);
    }
    if (result.rows.length === 0) throw new Error(`Transcript not found for video: ${vid}`);
    const row = result.rows[0];
    const snippets = Array.isArray(row.snippets) ? row.snippets : [];
    return {
      videoId: vid,
      language,
      transcript: snippets.map((s: any) => ({ text: s.text, start: s.start, duration: s.duration }))
    };
  }

  async searchTranscript({ videoId, query }: { videoId: string; query: string }): Promise<any> {
    const vid = parseVideoId(videoId);
    const result = await pool.query(`SELECT title, content FROM youtube.transcripts WHERE video_id = $1 LIMIT 1`, [vid]);
    if (result.rows.length === 0) return { matches: [] };
    const content: string = result.rows[0].content || '';
    const lines = content.split('\n').filter(line => line.toLowerCase().includes(query.toLowerCase()));
    return { videoId: vid, query, matches: lines.map(text => ({ text })) };
  }
}
