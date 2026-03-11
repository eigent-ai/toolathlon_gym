import { ChannelParams, ChannelVideosParams, ChannelVideosNavParams } from '../types.js';
import { pool } from './pg-youtube.js';

export class ChannelService {
  private sessions: Map<string, any> = new Map();

  async getChannel({ channelId }: ChannelParams): Promise<any> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', c.channel_id,
          'snippet', json_build_object('title', c.title, 'description', c.description, 'customUrl', c.custom_url, 'publishedAt', c.published_at),
          'statistics', json_build_object('subscriberCount', c.subscriber_count::text, 'videoCount', c.video_count::text, 'viewCount', c.view_count::text),
          'contentDetails', json_build_object('relatedPlaylists', json_build_object('uploads', c.uploads_playlist_id))
        ) AS channel_json
       FROM youtube.channels c WHERE c.channel_id = $1`,
      [channelId]
    );
    if (result.rows.length === 0) return null;
    return result.rows[0].channel_json;
  }

  async listVideos({ channelId, maxResults = 20, sortOrder = 'newest' }: ChannelVideosParams): Promise<any> {
    let orderClause = 'ORDER BY v.published_at DESC';
    if (sortOrder === 'oldest') orderClause = 'ORDER BY v.published_at ASC';
    else if (sortOrder === 'popular') orderClause = 'ORDER BY v.view_count DESC';
    const channelResult = await pool.query(`SELECT title, video_count FROM youtube.channels WHERE channel_id = $1`, [channelId]);
    const channelTitle = channelResult.rows[0]?.title || 'Unknown Channel';
    const totalVideoCount = channelResult.rows[0]?.video_count || 0;
    const listId = `list_${channelId}_${Date.now()}`;
    this.sessions.set(listId, { channelId, maxResults, sortOrder, channelTitle, totalVideoCount, orderClause });
    const videos = await this._getVideosPage(channelId, maxResults, 0, orderClause);
    const totalPages = Math.ceil(totalVideoCount / maxResults);
    return { listId, channelId, channelTitle, sortOrder, currentPage: 1, totalPages, pageSize: maxResults, totalVideos: totalVideoCount, videos, hasNextPage: totalPages > 1, hasPrevPage: false };
  }

  async navigateList({ listId, page }: ChannelVideosNavParams): Promise<any> {
    const session = this.sessions.get(listId);
    if (!session) throw new Error(`List session expired or not found: ${listId}`);
    const offset = (page - 1) * session.maxResults;
    const videos = await this._getVideosPage(session.channelId, session.maxResults, offset, session.orderClause);
    const totalPages = Math.ceil(session.totalVideoCount / session.maxResults);
    return { listId, channelId: session.channelId, channelTitle: session.channelTitle, sortOrder: session.sortOrder, currentPage: page, totalPages, pageSize: session.maxResults, videos, hasNextPage: page < totalPages, hasPrevPage: page > 1 };
  }

  private async _getVideosPage(channelId: string, limit: number, offset: number, orderClause: string): Promise<any[]> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', v.video_id,
          'snippet', json_build_object('title', v.title, 'description', v.description, 'channelId', v.channel_id, 'publishedAt', v.published_at),
          'contentDetails', json_build_object('duration', v.duration),
          'statistics', json_build_object('viewCount', v.view_count::text, 'likeCount', v.like_count::text)
        ) AS video_json
       FROM youtube.videos v WHERE v.channel_id = $1 ${orderClause} LIMIT $2 OFFSET $3`,
      [channelId, limit, offset]
    );
    return result.rows.map(r => r.video_json);
  }

  async getStatistics({ channelId }: ChannelParams): Promise<any> {
    const result = await pool.query(`SELECT subscriber_count, video_count, view_count FROM youtube.channels WHERE channel_id = $1`, [channelId]);
    if (result.rows.length === 0) return null;
    const row = result.rows[0];
    return { subscriberCount: row.subscriber_count?.toString(), videoCount: row.video_count?.toString(), viewCount: row.view_count?.toString() };
  }
}
