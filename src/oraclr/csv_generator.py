"""
CSV generator for Google Alerts data
"""

import csv
from typing import List, Dict
from datetime import datetime
import os


class CSVGenerator:
    """Generator for CSV files from Google Alerts data"""

    def __init__(self, output_dir: str = 'output'):
        """
        Initialize CSV generator

        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_csv(self, articles: List[Dict], filename: str = None) -> str:
        """
        Generate CSV file from articles data

        Args:
            articles: List of article dictionaries
            filename: Optional custom filename (auto-generated if not provided)

        Returns:
            Path to the generated CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'google_alerts_{timestamp}.csv'

        filepath = os.path.join(self.output_dir, filename)

        # Define CSV columns
        fieldnames = [
            'date',
            'time',
            'url',
            'topic',
            'executive_summary',
            'reference_links'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for article in articles:
                # Convert reference_links list to string
                row = article.copy()
                if isinstance(row.get('reference_links'), list):
                    row['reference_links'] = '; '.join(row['reference_links'])

                writer.writerow(row)

        return filepath

    def append_to_csv(self, articles: List[Dict], filepath: str):
        """
        Append articles to an existing CSV file

        Args:
            articles: List of article dictionaries
            filepath: Path to existing CSV file
        """
        fieldnames = [
            'date',
            'time',
            'url',
            'topic',
            'executive_summary',
            'reference_links'
        ]

        file_exists = os.path.isfile(filepath)

        with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for article in articles:
                # Convert reference_links list to string
                row = article.copy()
                if isinstance(row.get('reference_links'), list):
                    row['reference_links'] = '; '.join(row['reference_links'])

                writer.writerow(row)
