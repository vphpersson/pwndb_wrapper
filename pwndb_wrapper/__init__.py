from httpx import AsyncClient, Response

from pwndb_wrapper.html_parsers import ResultPageHTMLParser
from pwndb_wrapper.structures import PwndbEntry


PWNDB_URL = 'https://pwndb2am4tzkvold.tor2web.io/'


async def search_email(
    user: str,
    domain: str,
    http_client: AsyncClient,
    user_use_like: bool = False,
    domain_use_like: bool = False
) -> set[PwndbEntry]:
    """
    Search pwndb for accounts matching the provided user and domain.

    :param user: A search string for the user portion of an e-mail address.
    :param domain: A search string for the domain portion of an e-mail address.
    :param http_client: An HTTP client with which to perform the request.
    :param user_use_like: Search the user portion using a "LIKE" query.
    :param domain_use_like: Search the domain portion using a "LIKE" query.
    :return: A set of Pwndb entries.
    """

    result_page_response: Response = await http_client.post(
        url=PWNDB_URL,
        data=dict(
            luser=user,
            domain=domain,
            luseropr=int(user_use_like),
            domainopr=int(domain_use_like),
            submitform='em'
        )
    )
    result_page_response.raise_for_status()

    return ResultPageHTMLParser.parse(html_content=result_page_response.text)


async def search_password(password: str, http_client: AsyncClient) -> set[PwndbEntry]:
    """
    Search Pwndb for accounts having the provided password.

    :param password: A password to search for.
    :param http_client: An HTTP client with which to perform the request.
    :return: A set of Pwndb entries.
    """

    result_page_response: Response = await http_client.post(
        url=PWNDB_URL,
        data=dict(
            password=password,
            submitform='pw'
        )
    )
    result_page_response.raise_for_status()

    return ResultPageHTMLParser.parse(html_content=result_page_response.text)
