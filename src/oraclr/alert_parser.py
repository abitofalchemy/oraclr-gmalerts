"""
Parser for Google Alerts emails to extract URLs and content
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
import re


class AlertParser:
    """Parser for Google Alerts emails"""

    @staticmethod
    def parse_alert_email(html_content: str, email_date: str = None) -> List[Dict]:
        """
        Parse Google Alerts HTML email content to extract article information

        Args:
            html_content: HTML content of the email
            email_date: Date the email was received

        Returns:
            List of dictionaries containing article information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []

        # Find all article links in the Google Alerts email
        # Google Alerts typically uses specific div structures
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')

            # Skip non-article links (like unsubscribe, etc.)
            if 'google.com' in href and '/url?' in href:
                # Extract the actual URL from Google's redirect
                actual_url = AlertParser._extract_url_from_redirect(href)
                if actual_url:
                    article = {
                        'date': email_date or datetime.now().strftime('%Y-%m-%d'),
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'url': actual_url,
                        'topic': link.get_text(strip=True) or 'Unknown',
                        'executive_summary': '',  # To be filled by content fetcher
                        'reference_links': []  # To be filled by content fetcher
                    }
                    articles.append(article)

        return articles

    @staticmethod
    def _extract_url_from_redirect(redirect_url: str) -> str:
        """
        Extract actual URL from Google redirect URL

        Args:
            redirect_url: Google redirect URL

        Returns:
            Actual article URL
        """
        # Google Alert URLs are typically in format:
        # https://www.google.com/url?rct=j&sa=t&url=ACTUAL_URL&...
        match = re.search(r'[?&]url=([^&]+)', redirect_url)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1))
        return redirect_url

    @staticmethod
    def fetch_article_content(url: str) -> Dict:
        """
        Fetch and parse article content from URL

        Args:
            url: Article URL

        Returns:
            Dictionary with executive summary and reference links
        """
        try:
            import requests
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Oraclr/1.0)'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content for summary
            paragraphs = soup.find_all('p')
            text_content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])

            # Truncate to reasonable summary length
            executive_summary = text_content[:500] + '...' if len(text_content) > 500 else text_content

            # Extract reference links
            reference_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http'):
                    reference_links.append(href)

            # Limit to first 5 reference links
            reference_links = reference_links[:5]

            return {
                'executive_summary': executive_summary,
                'reference_links': reference_links
            }

        except Exception as e:
            return {
                'executive_summary': f'Error fetching content: {str(e)}',
                'reference_links': []
            }
