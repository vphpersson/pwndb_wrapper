from logging import getLogger
from typing import Union
from html.parser import HTMLParser
from re import compile as re_compile

from pwndb_wrapper.structures import PwndbEntry

LOG = getLogger(__name__)

ENTRY_FIELD_LINE_PATTERN = re_compile(r'^\s+\[(?P<field_name>[^]]+)\] => (?P<field_value>.*)$')


class ResultPageHTMLParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pwndb_entries: set[PwndbEntry] = set()
        self._handle_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == 'pre':
            self._handle_data = True

    def handle_data(self, data: str):
        if not self._handle_data:
            return

        # An entry spans multiple lines, until a ")" is reached.
        current_entry_collection: dict[str, Union[str, int]] = {}

        for line in data.splitlines():
            if match := ENTRY_FIELD_LINE_PATTERN.search(line):
                current_entry_collection[match.group('field_name')] = match.group('field_value')
            elif line.startswith(')'):
                current_entry_collection['id'] = int(current_entry_collection['id'])
                self.pwndb_entries.add(PwndbEntry(**current_entry_collection))
                current_entry_collection = {}

        self._handle_data = False

    def error(self, message: str):
        LOG.error(message)

    @classmethod
    def parse(cls, html_content: str) -> set[PwndbEntry]:
        parser = cls()
        parser.feed(data=html_content)

        return parser.pwndb_entries
