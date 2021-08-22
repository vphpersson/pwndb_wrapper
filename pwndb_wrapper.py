#!/usr/bin/env python3

from asyncio import run as asyncio_run
from typing import Type
from sys import stderr, exit
from json import dumps as json_dumps

from httpx import AsyncClient
from tabulate import tabulate

from pwndb_wrapper import search_email, search_password
from pwndb_wrapper.cli import PwndbWrapperArgumentParser
from pwndb_wrapper.structures import PwndbEntry


async def main():
    parser = PwndbWrapperArgumentParser.make()
    args: Type[PwndbWrapperArgumentParser.Namespace] = parser.parse_args()

    if not args.which:
        parser.print_help()
        exit(2)

    async with AsyncClient(verify=False, timeout=30.0) as http_client:
        if args.which == 'email':
            user = args.user or args.user_like
            domain = args.domain or args.domain_like

            if not user and not domain:
                print('Both domain and user cannot be empty.', file=stderr)
                exit(1)

            pwndb_entries: set[PwndbEntry] = await search_email(
                user=user,
                domain=domain,
                http_client=http_client,
                user_use_like=bool(args.user_like),
                domain_use_like=bool(args.domain_like)
            )

        elif args.which == 'password':
            pwndb_entries: set[PwndbEntry] = set()
            for password in args.passwords:
                for entry in await search_password(password=password, http_client=http_client):
                    pwndb_entries.add(entry)
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
            if args.merged_username:
                headers = ['id', 'username', 'password']
            else:
                headers = ['id', 'luser', 'domain', 'password']

            if args.remove_ids:
                headers = headers[1:]

            # NOTE: A "donate" entry is present for every search result; I remove it.
            print(
                tabulate(
                    tabular_data=[
                        filter(
                            lambda entry: entry is not None,
                            (
                                pwndb_entry.id if not args.remove_ids else None,
                                pwndb_entry.luser if not args.merged_username else f'{pwndb_entry.luser}@{pwndb_entry.domain}',
                                pwndb_entry.domain if not args.merged_username else None,
                                pwndb_entry.password
                            )

                        )
                        for pwndb_entry in output_entries
                        if pwndb_entry.luser != 'donate'
                    ],
                    headers=headers
                )
            )


if __name__ == '__main__':
    asyncio_run(main())
