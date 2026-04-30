import re

def gecerli_eposta(eposta):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', eposta) is not None

def gecerli_sifre(sifre):
    return len(sifre) >= 8
