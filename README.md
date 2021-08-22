# pwndb_wrapper

A scraper for the leaked-credentials website _Pwndb_.

The website is hosted in the Tor network, but is also available at https://pwndb2am4tzkvold.tor2web.io, which is the address that this program uses.

Please note that the site has historically often been down, and the connectivity is not superb, resulting in frequent connection timeouts.

## Usage

```
usage: pwndb_wrapper.py [-h] {email,password} ...

Search Pwndb for leaked credentials.

positional arguments:
  {email,password}
    email           Search based on e-mail address.
    password        Search based on password use.

optional arguments:
  -h, --help        show this help message and exit
```

### email 

```
usage: pwndb_wrapper.py email [-h] [-u USER | -U USER] [-d DOMAIN | -D DOMAIN] [-j] [-r] [-m] [-s]

Search Pwndb for leaked credentials.

optional arguments:
  -h, --help            show this help message and exit
  -u USER               An exact-match user name search string.
  -U USER               A user name search string to be used in a "LIKE" query.
  -d DOMAIN             An exact-match domain name search string.
  -D DOMAIN             A domain name search string to be used in a "LIKE" query.
  -j, --json            Output the entries in JSON.
  -r, --remove-ids      Do not output IDs of the entries.
  -m, --merged-username
                        Merge the "luser" and "domain" portions in the output.
  -s, --sort            Sort the entries.
```

### password

```
usage: pwndb_wrapper.py password [-h] [-j] [-r] [-m] [-s] PASSWORD [PASSWORD ...]

Search Pwndb for leaked credentials.

positional arguments:
  PASSWORD

optional arguments:
  -h, --help            show this help message and exit
  -j, --json            Output the entries in JSON.
  -r, --remove-ids      Do not output IDs of the entries.
  -m, --merged-username
                        Merge the "luser" and "domain" portions in the output.
  -s, --sort            Sort the entries.
```

## Examples

### E-mail domain search

```shell
$ ./pwndb_wrapper.py email -d 'example.com' -m -r
```

Output (truncated):

```
username                                            password
--------------------------------------------------  --------------------------------
3mmy@example.com                                    491292rr
2_short_4_u@example.com                             jackass123
1986@example.com                                    fatima
121user@example.com                                 ramix572
1981-6@example.com                                  332533
672moya13@example.com                               cholitamoy
...
```

### Password search

```shell
$ ./pwndb_wrapper.py password 'symaskin'
```

Output (truncated):

```
        id  luser                domain          password
----------  -------------------  --------------  ----------
 502361729  gunilla.bjerthin     telia.com       symaskin
 809988751  Mariamaare           hotmail.com     symaskin
1232328644  tejprulle            yandex.ru       symaskin
  32216018  aasebrit.meltvik     yahoo.com       symaskin
  70069105  alicejohnsson        hotmail.com     symaskin
1198839675  stinalindhoff        gmail.com       symaskin
1370451307  yngvildlund          hotmail.com     symaskin
1216803381  symaskin             telia.com       symaskin
...
```