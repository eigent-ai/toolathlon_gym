import { VideoParams, SearchParams } from '../types.js';
import { pool } from './pg-youtube.js';

export class VideoService {
  async getVideo({ videoId }: VideoParams): Promise<any> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', v.video_id,
          'snippet', json_build_object(
            'title', v.title, 'description', v.description,
            'channelId', v.channel_id, 'channelTitle', v.channel_title,
            'publishedAt', v.published_at, 'tags', v.tags
          ),
          'contentDetails', json_build_object('duration', v.duration),
          'statistics', json_build_object(
            'viewCount', v.view_count::text, 'likeCount', v.like_count::text, 'commentCount', v.comment_count::text
          )
        ) AS video_json
       FROM youtube.videos v WHERE v.video_id = $1`,
      [videoId]
    );
    if (result.rows.length === 0) return null;
    return result.rows[0].video_json;
  }

  async searchVideos({ query, maxResults = 10 }: SearchParams): Promise<any[]> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', v.video_id,
          'snippet', json_build_object(
            'title', v.title, 'description', v.description,
            'channelId', v.channel_id, 'channelTitle', v.channel_title, 'publishedAt', v.published_at
          ),
          'contentDetails', json_build_object('duration', v.duration),
          'statistics', json_build_object('viewCount', v.view_count::text, 'likeCount', v.like_count::text)
        ) AS video_json
       FROM youtube.videos v
       WHERE v.title ILIKE $1 OR v.description ILIKE $1 OR $1 = ANY(v.tags)
       LIMIT $2`,
      [`%${query}%`, maxResults]
    );
    return result.rows.map(r => r.video_json);
  }

  async getVideoStats({ videoId }: VideoParams): Promise<any> {
    const result = await pool.query(
      `SELECT view_count, like_count, comment_count FROM youtube.videos WHERE video_id = $1`,
      [videoId]
    );
    if (result.rows.length === 0) return null;
    const row = result.rows[0];
    return { viewCount: row.view_count?.toString(), likeCount: row.like_count?.toString(), commentCount: row.comment_count?.toString() };
  }

  async getTrendingVideos({ maxResults = 10 }: { maxResults?: number }): Promise<any[]> {
    const result = await pool.query(
      `SELECT json_build_object('id', v.video_id, 'snippet', json_build_object('title', v.title, 'channelTitle', v.channel_title),
          'statistics', json_build_object('viewCount', v.view_count::text)) AS video_json
       FROM youtube.videos v ORDER BY v.view_count DESC LIMIT $1`,
      [maxResults]
    );
    return result.rows.map(r => r.video_json);
  }

  async getRelatedVideos({ videoId, maxResults = 10 }: { videoId: string; maxResults?: number }): Promise<any[]> {
    const result = await pool.query(
      `SELECT json_build_object('id', v.video_id, 'snippet', json_build_object('title', v.title, 'channelTitle', v.channel_title)) AS video_json
       FROM youtube.videos v WHERE v.video_id != $1 LIMIT $2`,
      [videoId, maxResults]
    );
    return result.rows.map(r => r.video_json);
  }
}
