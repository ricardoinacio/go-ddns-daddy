import json
import logging
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

domains = {}

gd_key = ""
gd_secret = ""


class GoDaddySession:
    def __init__(self, api_key: str, api_secret: str) -> None:
        gd_auth_string = f"{api_key}:{api_secret}"
        self._auth_header = {"Authorization": f"sso-key {gd_auth_string}"}
        self._post_headers = self._auth_header | {"Content-Type": "application/json"}

    def a_record_url(domain: str, subdomain: str) -> str:
        return f"https://api.godaddy.com/v1/domains/{domain}/records/A/{subdomain}"

    def get_a_record(self, domain: str, subdomain: str = "@") -> list:
        url = self.a_record_url(domain, subdomain)
        a_record_request = Request(url, headers=self._auth_header)
        with urlopen(a_record_request) as a_record_source:
            a_record = json.load(a_record_source)
        logging.debug(f"<{subdomain}.{domain}> contains {a_record}.")
        return a_record

    def put_a_record(self, ip: str, domain: str, subdomain: str = "@") -> None:
        url = self.a_record_url(domain, subdomain)
        record_data = json.dumps([{"data": ip, "ttl": 600}]).encode("utf-8")
        a_record_update = Request(
            url, method="PUT", headers=self._post_headers, data=record_data
        )
        try:
            with urlopen(a_record_update) as update_response:
                logging.debug(
                    f"Updated A record of the subdomain '{subdomain}', got\n"
                    f"{update_response.status}\n"
                    f"{update_response.read()}"
                )
        except HTTPError as http_error:
            logging.error(http_error.readlines())
            raise http_error


class LocalIpRecord:
    def __init__(self, filename: str = ".go-ddns-daddy-rc") -> None:
        self._local_ip_path = Path.home() / filename

    def load(self) -> Optional[str]:
        try:
            with self._local_ip_path.open("r") as local_ip_source:
                return local_ip_source.readline().strip()

        except FileNotFoundError:
            logging.warning(f"Did not find last IP at {self._local_ip_path}.")
            return None

    def save(self, ip: str) -> None:
        with self._local_ip_path.open("w") as local_ip_dst:
            local_ip_dst.write(ip)


def run():
    # checking current ip
    ip_provider = "https://ipv4.icanhazip.com"
    with urlopen(ip_provider) as public_ip_source:
        public_ip = public_ip_source.read().decode().split()[0].strip()
        print(f"Public IP from <{ip_provider}> is {public_ip}.")

    # check local recorded ip
    local_ip_record = LocalIpRecord()
    if last_ip := local_ip_record.load():
        print(f"Last recorded IP is {last_ip}")

    # if current is the same as the last, just quit
    if public_ip == last_ip:
        print("Current public and last recorded IP are the same. Nothing to do.")
        return

    # since IP changed, let's check each record on GoDaddy
    godaddy = GoDaddySession(gd_key, gd_secret)
    for domain, subdomains in domains.items():
        for subdomain in subdomains:
            logging.info(f"Sync'ing DNS A record for <{subdomain}.{domain}>.")

            a_record = godaddy.get_a_record(domain, subdomain)
            if a_record[0]["data"] == public_ip:
                print(
                    f"IP for <{subdomain}.{domain}> is already set. Nothing to do."
                )
                continue

            godaddy.put_a_record(public_ip, domain, subdomain)

    # update local recorded IP
    local_ip_record.save(public_ip)
    print(f"Recorded {public_ip} as last updated IP at {last_ip_path}.")


if __name__ == "__main__":
    run()
