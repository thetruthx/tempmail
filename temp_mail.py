from pathlib import Path
import urllib.request
import requests
import random
import string
import aiohttp
import asyncio
import re

class TempMail:
    def __init__(self):
        self.API = "https://www.1secmail.com/api/v1/"
        self.domains = asyncio.run(self._fetch(url=f"{self.API}?action=getDomainList"))

    def get_domain(self, domain: str) -> str:
        return domain if domain in self.domains else random.choice(self.domains)

    def get_username(self, size: int, include_digits: bool) -> str:
        char = string.ascii_lowercase
        if include_digits:
            char += string.digits
        username = "".join(random.choice(char) for j in range(size))
        return username

    def generate_email_address(self, size: int = 10, include_digits: bool = True, domain: str = None) -> str:
        username = self.get_username(size, include_digits)
        domain = self.get_domain(domain)
        email_address = f"{username}@{domain}"
        return email_address

    def validate_email_address(self, email_addr: str) -> bool:
        try:
            domain = email_addr.split("@")[1].strip()
        finally:
            regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
            return bool(re.match(regex, str(email_addr)) and domain in self.domains)
        
    def check_mailbox(self, email_addr: str) -> dict:
        url = f"{self.API}?action=getMessages&login={email_addr.split('@')[0]}&domain={email_addr.split('@')[1]}"
        response = asyncio.run(self._fetch(url=url))
        if response:
            mailbox = {
                "id": [],
                "inbox": []}
            for i in response:
                email = {}
                for k, v in i.items():
                    if k in ["from", "subject", "date"]:
                        email[k] = v
                    else: mailbox["id"].append(v)
                mailbox["inbox"].append(email)
            return mailbox
         
    def fetch_single_email(self, email_addr: str, _id: int) -> dict:
        url = f"{self.API}?action=readMessage&login={email_addr.split('@')[0]}&domain={email_addr.split('@')[1]}&id={_id}"
        response = asyncio.run(self._fetch(url=url))
        if response:
            email = dict()
            for k, v in response.items():
                if k in ["from", "subject", "date", "attachments", "body"]:
                    email[k] = v
            return email

    def attachment_download(self, email_addr: str, _id: int, filename: str, path: str = "Downloads"):
        url = f"{self.API}?action=download&login={email_addr.split('@')[0]}&domain={email_addr.split('@')[1]}&id={_id}&file={filename}"
        urllib.request.urlretrieve(url, f"{str(Path.home() / path)}/{filename}")
        
    def delete_mailbox(self, email_addr: str):
        url = "https://www.1secmail.com/mailbox"
        data = {
            "action": "deleteMailbox",
            "login": email_addr.split("@")[0],
            "domain": email_addr.split("@")[1]}
        requests.post(url=url, data=data)

    async def _fetch(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
            