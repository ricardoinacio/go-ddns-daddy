# go-ddns-daddy

A CLI tool to dynamically updating IP in A records for domains registered with GoDaddy, much like a DDNS service. 

## Features

* Updates the IP addresses of your DNS A Records at GoDaddy.
* Does not poll GoDaddy IP, avoiding unecessary requests.
* Does not require any other dependency than the python3 with its standard library.

## Installation and Usage

Generate a pair of GoDaddy's developer key and secret, then set the variables `gd_key` and `gd_secret` at `app.py` file to those values.

Set the variable `domains` with your domain names and subdomains. Suppose you were setting `example.com` domain and the subdomains `www` and `app`. This is how it should look:

```python
domains = {"example.com": ["www", "app"]}
```

Run the script with `python3 src/app.py`.
