from __future__ import annotations
from typing import Optional

from pyutils.argparse.typed_argument_parser import TypedArgumentParser


class PwndbWrapperArgumentParser(TypedArgumentParser):

    class Namespace:
        which: str
        output_json: bool
        remove_ids: bool
        merged_username: bool
        sort_entries: bool
        user: Optional[str]
        user_like: Optional[str]
        domain: Optional[str]
        domain_like: Optional[str]
        passwords: Optional[list[str]]

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **(
                dict(
                    description='Search Pwndb for leaked credentials.'
                )
                | kwargs
            )
        )

        self.set_defaults(which=None)

    @classmethod
    def make(cls, *args, **kwargs) -> PwndbWrapperArgumentParser:
        pwndb_wrapper_parser = cls(*args, **kwargs)

        subparsers = pwndb_wrapper_parser.add_subparsers()

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

        return pwndb_wrapper_parser
