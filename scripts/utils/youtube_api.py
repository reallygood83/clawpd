"""
YouTube Data API v3 wrapper for channel and video analysis
"""
import json
import os
from typing import Dict, List, Optional, Any
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urlparse, parse_qs
import urllib.error


class YouTubeAPI:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube API wrapper with API key"""
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key required. Set YOUTUBE_API_KEY environment variable.")

        self.base_url = "https://www.googleapis.com/youtube/v3"

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """Make HTTP request to YouTube API"""
        params['key'] = self.api_key
        url = f"{self.base_url}/{endpoint}?{urlencode(params)}"

        try:
            req = Request(url)
            req.add_header('User-Agent', 'YouTube-PD-Agent/1.0')

            with urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode('utf-8'))
            raise Exception(f"YouTube API Error: {error_data.get('error', {}).get('message', str(e))}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def extract_channel_id(self, url: str) -> str:
        """Extract channel ID from various YouTube URL formats"""
        parsed = urlparse(url)

        # Handle @username format
        if '@' in parsed.path:
            username = parsed.path.split('@')[1].split('/')[0]
            return self._get_channel_id_by_username(username)

        # Handle /channel/UC... format
        if '/channel/' in parsed.path:
            return parsed.path.split('/channel/')[1].split('/')[0]

        # Handle /c/ format
        if '/c/' in parsed.path:
            custom_name = parsed.path.split('/c/')[1].split('/')[0]
            return self._get_channel_id_by_custom_name(custom_name)

        # Handle /user/ format
        if '/user/' in parsed.path:
            username = parsed.path.split('/user/')[1].split('/')[0]
            return self._get_channel_id_by_username(username)

        raise ValueError(f"Cannot extract channel ID from URL: {url}")

    def _get_channel_id_by_username(self, username: str) -> str:
        """Get channel ID by username/@handle"""
        try:
            data = self._make_request('channels', {
                'part': 'id',
                'forHandle': username if username.startswith('@') else f'@{username}'
            })

            if data['items']:
                return data['items'][0]['id']

            # Fallback: try forUsername (legacy)
            data = self._make_request('channels', {
                'part': 'id',
                'forUsername': username.replace('@', '')
            })

            if data['items']:
                return data['items'][0]['id']

        except Exception:
            pass

        raise ValueError(f"Channel not found for username: {username}")

    def _get_channel_id_by_custom_name(self, custom_name: str) -> str:
        """Get channel ID by custom channel name"""
        # YouTube deprecated direct custom name lookup
        # Use search as fallback
        data = self._make_request('search', {
            'part': 'snippet',
            'type': 'channel',
            'q': custom_name,
            'maxResults': 1
        })

        if data['items']:
            return data['items'][0]['snippet']['channelId']

        raise ValueError(f"Channel not found for custom name: {custom_name}")

    def get_channel_info(self, channel_id: str) -> Dict:
        """Get comprehensive channel information"""
        data = self._make_request('channels', {
            'part': 'snippet,statistics,brandingSettings,contentDetails',
            'id': channel_id
        })

        if not data['items']:
            raise ValueError(f"Channel not found: {channel_id}")

        channel = data['items'][0]

        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
            'view_count': int(channel['statistics'].get('viewCount', 0)),
            'video_count': int(channel['statistics'].get('videoCount', 0)),
            'published_at': channel['snippet']['publishedAt'],
            'thumbnail': channel['snippet']['thumbnails']['high']['url'],
            'country': channel['snippet'].get('country', ''),
            'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
        }

    def get_recent_videos(self, channel_id: str, max_results: int = 30) -> List[Dict]:
        """Get recent videos from channel"""
        channel_info = self.get_channel_info(channel_id)
        uploads_playlist_id = channel_info['uploads_playlist_id']

        # Get video IDs from uploads playlist
        playlist_data = self._make_request('playlistItems', {
            'part': 'snippet',
            'playlistId': uploads_playlist_id,
            'maxResults': max_results
        })

        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]

        if not video_ids:
            return []

        # Get detailed video information
        videos_data = self._make_request('videos', {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids)
        })

        videos = []
        for video in videos_data['items']:
            videos.append({
                'id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'published_at': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'tags': video['snippet'].get('tags', []),
                'thumbnail': video['snippet']['thumbnails']['high']['url']
            })

        return videos

    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed information for a specific video"""
        data = self._make_request('videos', {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id
        })

        if not data['items']:
            raise ValueError(f"Video not found: {video_id}")

        video = data['items'][0]

        return {
            'id': video['id'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'published_at': video['snippet']['publishedAt'],
            'duration': video['contentDetails']['duration'],
            'view_count': int(video['statistics'].get('viewCount', 0)),
            'like_count': int(video['statistics'].get('likeCount', 0)),
            'dislike_count': int(video['statistics'].get('dislikeCount', 0)),
            'comment_count': int(video['statistics'].get('commentCount', 0)),
            'tags': video['snippet'].get('tags', []),
            'category_id': video['snippet']['categoryId'],
            'thumbnail': video['snippet']['thumbnails']['high']['url'],
            'channel_id': video['snippet']['channelId'],
            'channel_title': video['snippet']['channelTitle']
        }

    def analyze_channel_performance(self, channel_id: str) -> Dict:
        """Analyze channel performance metrics"""
        recent_videos = self.get_recent_videos(channel_id, 30)

        if not recent_videos:
            return {'error': 'No videos found'}

        # Calculate metrics
        total_views = sum(v['view_count'] for v in recent_videos)
        total_likes = sum(v['like_count'] for v in recent_videos)
        total_comments = sum(v['comment_count'] for v in recent_videos)

        avg_views = total_views / len(recent_videos)
        avg_likes = total_likes / len(recent_videos)
        avg_comments = total_comments / len(recent_videos)

        # Engagement rate (likes + comments) / views
        engagement_rate = (total_likes + total_comments) / total_views * 100 if total_views > 0 else 0

        # Extract all tags/keywords
        all_tags = []
        for video in recent_videos:
            all_tags.extend(video['tags'])

        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_lower = tag.lower()
            tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1

        # Top tags
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        # Upload frequency analysis
        from datetime import datetime, timedelta
        upload_dates = [datetime.fromisoformat(v['published_at'].replace('Z', '+00:00')) for v in recent_videos]
        upload_dates.sort(reverse=True)

        if len(upload_dates) >= 2:
            time_diffs = []
            for i in range(len(upload_dates) - 1):
                diff_days = (upload_dates[i] - upload_dates[i + 1]).days
                time_diffs.append(diff_days)

            avg_upload_frequency = sum(time_diffs) / len(time_diffs)
        else:
            avg_upload_frequency = 0

        return {
            'video_count': len(recent_videos),
            'avg_views_per_video': round(avg_views),
            'avg_likes_per_video': round(avg_likes),
            'avg_comments_per_video': round(avg_comments),
            'engagement_rate': round(engagement_rate, 2),
            'top_keywords': [tag[0] for tag in top_tags[:10]],
            'avg_upload_frequency_days': round(avg_upload_frequency, 1),
            'top_performing_video': max(recent_videos, key=lambda x: x['view_count']),
            'recent_videos': recent_videos[:5]  # Last 5 videos
        }


def test_youtube_api():
    """Test function for YouTube API"""
    try:
        api = YouTubeAPI()

        # Test channel analysis
        test_url = "https://www.youtube.com/@배움의달인"
        channel_id = api.extract_channel_id(test_url)
        print(f"Channel ID: {channel_id}")

        channel_info = api.get_channel_info(channel_id)
        print(f"Channel: {channel_info['title']}")
        print(f"Subscribers: {channel_info['subscriber_count']:,}")

        performance = api.analyze_channel_performance(channel_id)
        print(f"Avg views: {performance['avg_views_per_video']:,}")
        print(f"Engagement: {performance['engagement_rate']}%")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_youtube_api()