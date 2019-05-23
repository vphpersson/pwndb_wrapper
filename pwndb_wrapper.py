#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import stderr, exit
from dataclasses import dataclass, field
from typing import Set, Dict, Union
from re import compile as re_compile
from json import dumps as json_dumps
from urllib3 import disable_warnings, exceptions

from requests import Response
from requests_html import HTMLSession

PWNDB_URL = 'https://pwndb2am4tzkvold.tor2web.io/'
PWNDB_RESULTS_SELECTOR = '#container > section:nth-child(5) > pre'

ENTRY_FIELD_LINE_PATTERN = re_compile(r'^\s+\[(?P<field_name>[^]]+)\] => (?P<field_value>.*)$')


@dataclass(frozen=True)
class PwndbEntry:
    id: int = field(hash=True)
    luser: str
    domain: str
    password: str


def parse_pwndb_results(response: Response) -> Set[PwndbEntry]:
    """
    Parse the results contained in a response from pwndb.

    :param response: A response resulting from a search request to pwndb.
    :return: A list of pwndb entries extracted from the response.
    """

    if not str(response.status_code).startswith('2'):
        print('hello no', file=stderr)

    entries: Set[PwndbEntry] = set()

    curr_entry_collection: Dict[str, Union[str, int]] = {}
    for line in response.html.find(PWNDB_RESULTS_SELECTOR, first=True).full_text.split('\n'):

        match = ENTRY_FIELD_LINE_PATTERN.search(line)

        if match:
            curr_entry_collection[match.group('field_name')] = match.group('field_value')
        elif line.startswith(')'):
            curr_entry_collection['id'] = int(curr_entry_collection['id'])
            entries.add(PwndbEntry(**curr_entry_collection))
            curr_entry_collection = {}

    return entries


def search_email(user: str, domain: str, user_use_like: bool = False, domain_use_like: bool = False) -> Set[PwndbEntry]:
    """
    Search pwndb for accounts matching the provided user and domain.

    :param user: A search string for the user portion of an e-mail address.
    :param domain: A search string for the domain portion of an e-mail address.
    :param user_use_like: Search the user portion using a "LIKE" query.
    :param domain_use_like: Search the domain portion using a "LIKE" query.
    :return: A list of pwndb entries.
    """

    return parse_pwndb_results(
        HTMLSession().post(
            url=PWNDB_URL,
            data=dict(
                luser=user,
                domain=domain,
                luseropr=int(user_use_like),
                domainopr=int(domain_use_like),
                submitform='em'
            ),
            verify=False
        )
    )


def search_password(password: str) -> Set[PwndbEntry]:
    """
    Search pwndb for accounts having the provided password.

    :param password: A password to search for.
    :return: A list of pwndb entries.
    """

    return parse_pwndb_results(
        HTMLSession().post(
            url=PWNDB_URL,
            data=dict(
                password=password,
                submitform='pw'
            ),
            verify=False
        )
    )


def get_parser() -> ArgumentParser:
    """
    Initialize the argument parser.
    :return: An initialized argument parser.
    """

    main_parser = ArgumentParser(description='Search pwndb for leaked credentials.')
    main_parser.set_defaults(which=None)

    subparsers = main_parser.add_subparsers()

    # Arguments relating to the "email option".

    email_parser = subparsers.add_parser(
        'email',
        help='Search based on e-mail address.'
    )
    email_parser.set_defaults(which='email')

    email_user_group = email_parser.add_mutually_exclusive_group()

    email_user_group.add_argument(
        '-u',
        help='An exact-match user name search string.',
        dest='user',
        metavar='USER',
        type=str,
    )

    email_user_group.add_argument(
        '-U',
        help='A user name search string to be used in a "LIKE" query.',
        dest='user_like',
        metavar='USER',
        type=str,
    )

    email_domain_group = email_parser.add_mutually_exclusive_group()

    email_domain_group.add_argument(
        '-d',
        help='An exact-match domain name search string.',
        dest='domain',
        metavar='DOMAIN',
        type=str,
    )

    email_domain_group.add_argument(
        '-D',
        help='A domain name search string to be used in a "LIKE" query.',
        dest='domain_like',
        metavar='DOMAIN',
        type=str,
    )

    # Arguments relating to the "passwords" option.

    password_parser = subparsers.add_parser(
        'password',
        help='Search based on password use.'
    )
    password_parser.set_defaults(which='password')

    password_parser.add_argument(
        'passwords',
        help='',
        metavar='PASSWORD',
        type=str,
        nargs='+',
        default=[]
    )

    for parser in [password_parser, email_parser]:
        parser.add_argument(
            '-j', '--json',
            help='Output the entries in JSON.',
            dest='output_json',
            action='store_true'
        )

        parser.add_argument(
            '-r', '--remove-ids',
            help='Do not output IDs of the entries.',
            dest='remove_ids',
            action='store_true'
        )

        parser.add_argument(
            '-m', '--merged-username',
            help='Merge the "luser" and "domain" portions in the output.',
            dest='merged_username',
            action='store_true'
        )

        parser.add_argument(
            '-s', '--sort',
            help='Sort the entries.',
            dest='sort_entries',
            action='store_true'
        )

    return main_parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if not args.which:
        parser.print_help()
        exit(2)

    disable_warnings(exceptions.InsecureRequestWarning)

    pwndb_entries: Set[PwndbEntry] = set()

    if args.which == 'email':
        user = args.user or args.user_like
        domain = args.domain or args.domain_like

        if not user and not domain:
            print('Both domain and user cannot be empty.', file=stderr)
            exit(1)

        pwndb_entries = search_email(
            user=user,
            domain=domain,
            user_use_like=bool(args.user_like),
            domain_use_like=bool(args.domain_like)
        )

    elif args.which == 'password':
        pwndb_entries = set(entry for password in args.passwords for entry in search_password(password))
    else:
        print(f'Bad mode: {args.which}', file=stderr)
        exit(1)

    output_entries = sorted(pwndb_entries, key=lambda x: x.luser) if args.sort_entries else pwndb_entries

    if args.output_json:
        print(json_dumps([
            {
                key if key != 'luser' else 'luser' if not args.merged_username else 'user': value if key != 'luser' else value if not args.merged_username else f'{value}@{pwndb_entry.domain}'
                for key, value in pwndb_entry.__dict__.items()
                if (key != 'id' or not args.remove_ids) and (key != 'domain' or not args.merged_username)
            }
            for pwndb_entry in output_entries
        ]))
    else:
        print(
            '\n\n'.join(
                '\n'.join(
                    f'{key}: {value}' if key != 'luser' else f'{"luser" if not args.merged_username else "user"}: {value if not args.merged_username else value + "@" + pwndb_entry.domain}'
                    for key, value in pwndb_entry.__dict__.items()
                    if (key != 'id' or not args.remove_ids) and (key != 'domain' or not args.merged_username)
                )
                for pwndb_entry in output_entries
            )
        )
