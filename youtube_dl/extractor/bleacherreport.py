# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .amp import AMPIE
from ..utils import (
    ExtractorError,
    int_or_none,
    parse_iso8601,
)


class BleacherReportIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?bleacherreport\.com/articles/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://bleacherreport.com/articles/2496438-fsu-stat-projections-is-jalen-ramsey-best-defensive-player-in-college-football',
        'md5': 'a3ffc3dc73afdbc2010f02d98f990f20',
        'info_dict': {
            'id': '2496438',
            'ext': 'mp4',
            'title': 'FSU Stat Projections: Is Jalen Ramsey Best Defensive Player in College Football?',
            'uploader_id': 3992341,
            'description': 'CFB, ACC, Florida State',
            'timestamp': 1434380212,
            'upload_date': '20150615',
            'uploader': 'Team Stream Now ',
        },
        'add_ie': ['Ooyala'],
    }, {
        'url': 'http://bleacherreport.com/articles/2586817-aussie-golfers-get-fright-of-their-lives-after-being-chased-by-angry-kangaroo',
        'md5': 'af5f90dc9c7ba1c19d0a3eac806bbf50',
        'info_dict': {
            'id': '2586817',
            'ext': 'mp4',
            'title': 'Aussie Golfers Get Fright of Their Lives After Being Chased by Angry Kangaroo',
            'timestamp': 1446839961,
            'uploader': 'Sean Fay',
            'description': 'md5:825e94e0f3521df52fa83b2ed198fa20',
            'uploader_id': 6466954,
            'upload_date': '20151011',
        },
        'add_ie': ['Youtube'],
    }]

    def _real_extract(self, url):
        article_id = self._match_id(url)

        article_data = self._download_json('http://api.bleacherreport.com/api/v1/articles/%s' % article_id, article_id)['article']

        thumbnails = []
        primary_photo = article_data.get('primaryPhoto')
        if primary_photo:
            thumbnails = [{
                'url': primary_photo['url'],
                'width': primary_photo.get('width'),
                'height': primary_photo.get('height'),
            }]

        info = {
            '_type': 'url_transparent',
            'id': article_id,
            'title': article_data['title'],
            'uploader': article_data.get('author', {}).get('name'),
            'uploader_id': article_data.get('authorId'),
            'timestamp': parse_iso8601(article_data.get('createdAt')),
            'thumbnails': thumbnails,
            'comment_count': int_or_none(article_data.get('commentsCount')),
            'view_count': int_or_none(article_data.get('hitCount')),
        }

        video = article_data.get('video')
        if video:
            video_type = video['type']
            if video_type == 'cms.bleacherreport.com':
                info['url'] = 'http://bleacherreport.com/video_embed?id=%s' % video['id']
            elif video_type == 'ooyala.com':
                info['url'] = 'ooyala:%s' % video['id']
            elif video_type == 'youtube.com':
                info['url'] = video['id']
            elif video_type == 'vine.co':
                info['url'] = 'https://vine.co/v/%s' % video['id']
            else:
                info['url'] = video_type + video['id']
            return info
        else:
            raise ExtractorError('no video in the article', expected=True)


class BleacherReportCMSIE(AMPIE):
    _VALID_URL = r'https?://(?:www\.)?bleacherreport\.com/video_embed\?id=(?P<id>[0-9a-f-]{36})'
    _TESTS = [{
        'url': 'http://bleacherreport.com/video_embed?id=8fd44c2f-3dc5-4821-9118-2c825a98c0e1',
        'md5': 'f0ca220af012d4df857b54f792c586bb',
        'info_dict': {
            'id': '8fd44c2f-3dc5-4821-9118-2c825a98c0e1',
            'ext': 'flv',
            'title': 'Cena vs. Rollins Would Expose the Heavyweight Division',
            'description': 'md5:984afb4ade2f9c0db35f3267ed88b36e',
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        info = self._extract_feed_info('http://cms.bleacherreport.com/media/items/%s/akamai.json' % video_id)
        info['id'] = video_id
        return info
