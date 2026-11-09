"""
Command-line interface for Oraclr
"""

import click
from .gmail_client import GmailClient
from .alert_parser import AlertParser
from .csv_generator import CSVGenerator
from datetime import datetime


@click.group()
@click.version_option()
def main():
    """
    Oraclr - Process Google Alerts from Gmail and generate CSV reports
    """
    pass


@main.command()
@click.option('--credentials', default='credentials.json',
              help='Path to Google OAuth credentials file')
@click.option('--max-results', default=10, type=int,
              help='Maximum number of emails to fetch')
@click.option('--output-dir', default='output',
              help='Directory to save CSV files')
@click.option('--fetch-content/--no-fetch-content', default=False,
              help='Fetch article content for summaries')
def fetch(credentials, max_results, output_dir, fetch_content):
    """
    Fetch Google Alerts from Gmail and generate CSV report
    """
    click.echo('🔍 Initializing Oraclr...')

    # Initialize Gmail client
    gmail_client = GmailClient(credentials_path=credentials)

    click.echo('🔐 Authenticating with Gmail...')
    gmail_client.authenticate()

    click.echo(f'📧 Fetching up to {max_results} Google Alerts emails...')
    emails = gmail_client.get_google_alerts(max_results=max_results)

    if not emails:
        click.echo('❌ No Google Alerts emails found.')
        return

    click.echo(f'✅ Found {len(emails)} emails. Processing...')

    # Parse emails and extract articles
    all_articles = []
    parser = AlertParser()

    for email in emails:
        html_content = gmail_client.extract_message_body(email)
        email_date = datetime.fromtimestamp(
            int(email.get('internalDate', 0)) / 1000
        ).strftime('%Y-%m-%d')

        articles = parser.parse_alert_email(html_content, email_date)

        # Optionally fetch article content
        if fetch_content and articles:
            click.echo(f'📰 Fetching content for {len(articles)} articles...')
            for article in articles:
                content = parser.fetch_article_content(article['url'])
                article['executive_summary'] = content['executive_summary']
                article['reference_links'] = content['reference_links']

        all_articles.extend(articles)

    if not all_articles:
        click.echo('❌ No articles found in emails.')
        return

    click.echo(f'📝 Generating CSV with {len(all_articles)} articles...')

    # Generate CSV
    csv_gen = CSVGenerator(output_dir=output_dir)
    filepath = csv_gen.generate_csv(all_articles)

    click.echo(f'✅ CSV file generated: {filepath}')


@main.command()
@click.argument('url')
def parse_url(url):
    """
    Parse a single URL and display information
    """
    click.echo(f'🔗 Fetching content from: {url}')

    parser = AlertParser()
    content = parser.fetch_article_content(url)

    click.echo('\n📄 Executive Summary:')
    click.echo(content['executive_summary'])

    click.echo('\n🔗 Reference Links:')
    for link in content['reference_links']:
        click.echo(f'  - {link}')


if __name__ == '__main__':
    main()
