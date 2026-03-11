import { PlaylistParams, PlaylistItemsParams, SearchParams } from '../types.js';
import { pool } from './pg-youtube.js';

export class PlaylistService {
  async getPlaylist({ playlistId }: PlaylistParams): Promise<any> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', p.playlist_id,
          'snippet', json_build_object('title', p.title, 'description', p.description, 'channelId', p.channel_id, 'publishedAt', p.published_at),
          'contentDetails', json_build_object('itemCount', p.item_count),
          'status', json_build_object('privacyStatus', 'public')
        ) AS playlist_json
       FROM youtube.playlists p WHERE p.playlist_id = $1`,
      [playlistId]
    );
    if (result.rows.length === 0) return null;
    return result.rows[0].playlist_json;
  }

  async getPlaylistItems({ playlistId, maxResults = 50 }: PlaylistItemsParams): Promise<any> {
    const itemsResult = await pool.query(
      `SELECT pi.video_id, pi.position, pi.title, pi.description, pi.published_at
       FROM youtube.playlist_items pi WHERE pi.playlist_id = $1 ORDER BY pi.position LIMIT $2`,
      [playlistId, maxResults]
    );
    const videoIds = itemsResult.rows.map(r => r.video_id);
    let videosMap: Record<string, any> = {};
    if (videoIds.length > 0) {
      const vr = await pool.query(
        `SELECT v.video_id, json_build_object(
            'id', v.video_id,
            'snippet', json_build_object('title', v.title, 'description', v.description, 'channelId', v.channel_id, 'publishedAt', v.published_at),
            'contentDetails', json_build_object('duration', v.duration),
            'statistics', json_build_object('viewCount', v.view_count::text, 'likeCount', v.like_count::text)
          ) AS video_json
         FROM youtube.videos v WHERE v.video_id = ANY($1)`,
        [videoIds]
      );
      for (const row of vr.rows) videosMap[row.video_id] = row.video_json;
    }
    const enhancedItems = itemsResult.rows.map(item => ({
      playlistItem: {
        id: `${playlistId}_${item.position}`,
        snippet: { playlistId, position: item.position, title: item.title, description: item.description, publishedAt: item.published_at, resourceId: { kind: 'youtube#video', videoId: item.video_id } },
        contentDetails: { videoId: item.video_id }
      },
      videoDetails: videosMap[item.video_id] || null
    }));
    return { items: enhancedItems, totalResults: itemsResult.rows.length, nextPageToken: null, prevPageToken: null };
  }

  async searchPlaylists({ query, maxResults = 10 }: SearchParams): Promise<any[]> {
    const result = await pool.query(
      `SELECT json_build_object(
          'id', json_build_object('kind', 'youtube#playlist', 'playlistId', p.playlist_id),
          'snippet', json_build_object('title', p.title, 'description', p.description, 'channelId', p.channel_id)
        ) AS playlist_json
       FROM youtube.playlists p WHERE p.title ILIKE $1 OR p.description ILIKE $1 LIMIT $2`,
      [`%${query}%`, maxResults]
    );
    return result.rows.map(r => r.playlist_json);
  }
}
