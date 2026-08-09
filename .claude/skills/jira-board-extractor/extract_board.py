#!/usr/bin/env python3
"""
Jira Board Data Extractor
Reusable tool for exporting board data: epics, backlog, sprints, issues, subtasks.

Usage:
    python extract_board.py [--board-id 4] [--output json] [--format hierarchy] [--jql "..."] [--epic PAP-4]
    python extract_board.py --email you@example.com --token YOUR_TOKEN [--board-id 4]

Options:
    --board-id      Jira board ID (default: 4)
    --email         Jira email (or load from .env JIRA_EMAIL)
    --token         API token (or load from .env JIRA_API_TOKEN)
    --url           Base URL (or load from .env JIRA_BASE_URL)
    --output        Output format: json, csv, markdown (default: json)
    --format        Data structure: hierarchy (epics→issues→subtasks), flat (all issues), separate (epics + issues)
    --jql           Custom JQL filter, e.g., "priority = High"
    --epic          Export single epic only, e.g., "PAP-4"
    --fields        CSV list of fields to export (default: key,summary,status,assignee,priority,labels)
    --outfile       Output file path (default: board_export.{format})
"""

import os
import sys
import json
import csv
import base64
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("❌ requests library required. Install: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not found. Will use hardcoded credentials only.")
    load_dotenv = lambda *args, **kwargs: None


# Find and load .env from parent directories
def load_env():
    """Search for .env in current and parent directories"""
    current = Path(__file__).parent
    for _ in range(5):  # Search up to 5 levels up
        env_path = current / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            return
        current = current.parent
    # If not found, try default load_dotenv behavior
    load_dotenv()


# Configuration
class Config:
    """Load Jira credentials and settings"""
    
    @staticmethod
    def load():
        load_env()  # Search for .env in parent directories
        return {
            'email': os.getenv('JIRA_EMAIL', '').strip(),
            'token': os.getenv('JIRA_API_TOKEN', '').strip(),
            'base_url': os.getenv('JIRA_BASE_URL', 'https://lukaszpiaseckidev.atlassian.net').strip(),
        }
    
    @staticmethod
    def validate(config):
        if not config['email'] or not config['token']:
            print("❌ Missing JIRA_EMAIL or JIRA_API_TOKEN in .env or environment")
            return False
        return True


# API Client
class JiraClient:
    """Minimal Jira API client with auth and pagination"""
    
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.token = token
        self.headers = self._build_headers()
        self._validated = False
    
    def _build_headers(self):
        auth_str = f"{self.email}:{self.token}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        return {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
        }
    
    def validate(self) -> bool:
        """Test auth with lightweight request"""
        try:
            resp = self.request('/rest/api/3/myself')
            self._validated = True
            return True
        except Exception as e:
            print(f"❌ Auth failed: {e}")
            return False
    
    def request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            if code == 401:
                raise Exception("Unauthorized: invalid email/token")
            elif code == 403:
                raise Exception("Forbidden: no access to board")
            elif code == 404:
                raise Exception("Not found: board/issue does not exist")
            elif code == 429:
                raise Exception("Rate limited: wait and retry")
            else:
                raise Exception(f"HTTP {code}: {e.response.text[:200]}")
    
    def fetch_paginated(self, endpoint: str, params: Dict, key: str = 'issues') -> List[Dict]:
        """Fetch paginated results (maxResults + startAt style)"""
        results = []
        start_at = 0
        
        while True:
            page_params = {**params, 'startAt': start_at, 'maxResults': 100}
            data = self.request(endpoint, page_params)
            
            batch = data.get(key, [])
            if not batch:
                break
            
            results.extend(batch)
            
            if data.get('isLast', True):
                break
            
            start_at += 100
        
        return results
    
    # Board endpoints
    
    def get_board(self, board_id: int) -> Dict:
        """Fetch board metadata"""
        return self.request(f'/rest/agile/1.0/board/{board_id}')
    
    def get_epics(self, board_id: int) -> List[Dict]:
        """Fetch all epics for board"""
        data = self.request(f'/rest/agile/1.0/board/{board_id}/epic')
        return data.get('values', [])
    
    def get_sprints(self, board_id: int) -> List[Dict]:
        """Fetch all sprints for board"""
        data = self.request(f'/rest/agile/1.0/board/{board_id}/sprint')
        return data.get('values', [])
    
    def get_backlog(self, board_id: int) -> List[Dict]:
        """Fetch backlog issues"""
        return self.fetch_paginated(
            f'/rest/software/1.0/board/{board_id}/backlog',
            {},
            key='issues'
        )
    
    def get_board_issues(self, board_id: int) -> List[Dict]:
        """Fetch all issues on board"""
        return self.fetch_paginated(
            f'/rest/software/1.0/board/{board_id}/issue',
            {},
            key='issues'
        )
    
    def search_issues(self, jql: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """Search issues by JQL"""
        params = {
            'jql': jql,
            'maxResults': 100,
        }
        if fields:
            params['fields'] = ','.join(fields)
        
        return self.fetch_paginated('/rest/api/3/search', params, key='issues')


# Exporters
class Exporter:
    """Base exporter class"""
    
    @staticmethod
    def export_json(data: Any, outfile: str):
        """Export as JSON"""
        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported to {outfile}")
    
    @staticmethod
    def export_csv(data: List[Dict], outfile: str):
        """Export as CSV"""
        if not data:
            print("No data to export")
            return
        
        keys = set()
        for row in data:
            keys.update(row.keys())
        keys = sorted(list(keys))
        
        with open(outfile, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ Exported to {outfile}")
    
    @staticmethod
    def export_markdown(tree: List[str], outfile: str):
        """Export as Markdown tree"""
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree))
        print(f"✅ Exported to {outfile}")


# Data formatters
def format_hierarchy(epics: List[Dict], all_issues: List[Dict]) -> Dict:
    """Group issues by epic in hierarchical structure"""
    # Build issue -> epic mapping
    issue_to_epic = {}
    for issue in all_issues:
        fields = issue.get('fields', {})
        epic_key = None
        if 'parent' in fields and fields['parent']:
            epic_key = fields['parent'].get('key')
        elif 'customfield_10005' in fields and fields['customfield_10005']:
            epic_key = fields['customfield_10005'].get('key')
        if epic_key:
            issue_to_epic[issue['key']] = epic_key
    
    # Organize by epic
    result = {}
    for epic in epics:
        epic_key = epic['key']
        result[epic_key] = {'name': epic.get('name', ''), 'issues': []}
        for issue in all_issues:
            if issue_to_epic.get(issue['key']) == epic_key:
                assignee = issue.get('fields', {}).get('assignee')
                assignee_name = assignee.get('displayName', '') if assignee else ''
                issue_data = {
                    'key': issue['key'],
                    'summary': issue.get('fields', {}).get('summary', ''),
                    'status': issue.get('fields', {}).get('status', {}).get('name', ''),
                    'assignee': assignee_name,
                    'subtasks': [
                        {
                            'key': st['key'],
                            'summary': st.get('fields', {}).get('summary', ''),
                            'status': st.get('fields', {}).get('status', {}).get('name', ''),
                        }
                        for st in issue.get('fields', {}).get('subtasks', [])
                    ]
                }
                result[epic_key]['issues'].append(issue_data)
    return result


def format_flat(all_issues: List[Dict]) -> List[Dict]:
    """Flatten all issues into single list"""
    result = []
    for issue in all_issues:
        fields = issue.get('fields', {})
        result.append({
            'key': issue['key'],
            'summary': fields.get('summary', ''),
            'status': fields.get('status', {}).get('name', ''),
            'assignee': fields.get('assignee', {}).get('displayName', ''),
            'priority': fields.get('priority', {}).get('name', ''),
            'labels': ', '.join(fields.get('labels', [])),
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'issuetype': fields.get('issuetype', {}).get('name', ''),
        })
    return result


def format_tree_text(epics: List[Dict], all_issues: List[Dict]) -> List[str]:
    """Format as ASCII tree for markdown/text"""
    lines = []
    
    # Same grouping as hierarchy
    issue_to_epic = {}
    for issue in all_issues:
        fields = issue.get('fields', {})
        epic_key = None
        if 'parent' in fields and fields['parent']:
            epic_key = fields['parent'].get('key')
        if epic_key:
            issue_to_epic[issue['key']] = epic_key
    
    for epic in epics:
        epic_key = epic['key']
        epic_name = epic.get('name', '')
        lines.append(f"📌 EPIC: {epic_key}" + (f" - {epic_name}" if epic_name else " (unnamed)"))
        
        epic_issues = [i for i in all_issues if issue_to_epic.get(i['key']) == epic_key]
        
        if not epic_issues:
            lines.append("   (no issues)")
        else:
            for idx, issue in enumerate(epic_issues):
                is_last = (idx == len(epic_issues) - 1)
                prefix = "  └─" if is_last else "  ├─"
                summary = issue.get('fields', {}).get('summary', '')
                status = issue.get('fields', {}).get('status', {}).get('name', '')
                lines.append(f"{prefix} 📋 {issue['key']}: {summary} [{status}]")
                
                subtasks = issue.get('fields', {}).get('subtasks', [])
                for st_idx, st in enumerate(subtasks):
                    st_is_last = (st_idx == len(subtasks) - 1)
                    st_prefix_left = "     " if is_last else "  │  "
                    st_prefix = "└─" if st_is_last else "├─"
                    st_summary = st.get('fields', {}).get('summary', '')
                    st_status = st.get('fields', {}).get('status', {}).get('name', '')
                    lines.append(f"{st_prefix_left}{st_prefix} 🔹 {st['key']}: {st_summary} [{st_status}]")
        
        lines.append("")
    
    return lines


# Main orchestration
def main():
    parser = argparse.ArgumentParser(
        description='Export Jira board data in various formats and structures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--board-id', type=int, default=4, help='Board ID (default: 4)')
    parser.add_argument('--email', type=str, help='Jira email (overrides .env)')
    parser.add_argument('--token', type=str, help='Jira API token (overrides .env)')
    parser.add_argument('--url', type=str, help='Jira base URL (overrides .env)')
    parser.add_argument('--output', choices=['json', 'csv', 'markdown'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--format', choices=['hierarchy', 'flat', 'separate'], default='hierarchy',
                        help='Data structure: hierarchy (epics→issues) or flat (all issues) (default: hierarchy)')
    parser.add_argument('--jql', type=str, help='Custom JQL filter, e.g., "priority = High"')
    parser.add_argument('--epic', type=str, help='Export single epic only, e.g., "PAP-4"')
    parser.add_argument('--fields', type=str, help='CSV list of fields to include')
    parser.add_argument('--outfile', type=str, help='Output file path (auto-generated if omitted)')
    
    args = parser.parse_args()
    
    # Load config (CLI overrides .env)
    config = Config.load()
    if args.email:
        config['email'] = args.email
    if args.token:
        config['token'] = args.token
    if args.url:
        config['base_url'] = args.url
    
    if not Config.validate(config):
        sys.exit(1)
    
    # Initialize client
    client = JiraClient(config['base_url'], config['email'], config['token'])
    if not client.validate():
        sys.exit(1)
    
    print(f"✅ Authenticated as {config['email']}")
    
    # Fetch data
    board_id = args.board_id
    board = client.get_board(board_id)
    print(f"📊 Fetching board {board_id}: {board.get('name', 'Unknown')}")
    
    epics = client.get_epics(board_id)
    print(f"   - {len(epics)} epics")
    
    if args.jql:
        all_issues = client.search_issues(args.jql)
        print(f"   - {len(all_issues)} issues (filtered by JQL)")
    else:
        all_issues = client.get_board_issues(board_id)
        print(f"   - {len(all_issues)} issues")
    
    # Filter by epic if requested
    if args.epic:
        epic_key = args.epic.upper()
        epic_issues = []
        for issue in all_issues:
            fields = issue.get('fields', {})
            parent = fields.get('parent', {})
            if parent and parent.get('key') == epic_key:
                epic_issues.append(issue)
        all_issues = epic_issues
        print(f"   - Filtered to {len(all_issues)} issues in {epic_key}")
    
    # Format data
    if args.format == 'hierarchy':
        data = format_hierarchy(epics, all_issues)
    elif args.format == 'flat':
        data = format_flat(all_issues)
    elif args.format == 'separate':
        data = {
            'board': board,
            'epics': epics,
            'issues': format_flat(all_issues)
        }
    
    # Export
    ext_map = {'json': 'json', 'csv': 'csv', 'markdown': 'md'}
    ext = ext_map[args.output]
    outfile = args.outfile or f"board_{board_id}_export.{ext}"
    
    if args.output == 'json':
        Exporter.export_json(data, outfile)
    elif args.output == 'csv' and isinstance(data, list):
        Exporter.export_csv(data, outfile)
    elif args.output == 'markdown':
        if isinstance(data, list):
            lines = data
        else:
            lines = format_tree_text(epics, all_issues)
        Exporter.export_markdown(lines, outfile)
    
    print("✅ Done")


if __name__ == '__main__':
    main()
