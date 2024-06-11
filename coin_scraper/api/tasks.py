from celery import shared_task
from .models import Job, Task
import requests
from bs4 import BeautifulSoup

@shared_task
def scrape_coin_data(job_id, coin):
    # getting the url here.
    url = f"https://coinmarketcap.com/currencies/{coin.lower()}/"
    # making request to the website.
    response = requests.get(url)
    
    if response.status_code == 200:
        # parsing the text from the website here.
        soup = BeautifulSoup(response.text, 'html.parser')

        # getting the complete coin_stats here.
        stats = soup.find_all('div', attrs={'class' : 'sc-4c05d6ef-0 sc-55349342-0 dlQYLv gELPTu coin-stats'})
        
        # getting the price and growth elements data here.
        price_growth = soup.find('div', attrs={'class': 'sc-d1ede7e3-0 gNSoet flexStart alignBaseline'})
        price = price_growth.find('span', attrs={'class': 'sc-d1ede7e3-0 fsQm base-text'}).text.strip().remove("$")
        
        try: # for negative change.
            growth = price_growth.find('p', attrs={'class': 'sc-71024e3e-0 sc-58c82cf9-1 ihXFUo iPawMI'}).text.strip().remove("% (1d)")
            price_change = f'-{growth}'
        except: # for positive change.
            growth = price_growth.find('p', attrs={'class': 'sc-71024e3e-0 sc-58c82cf9-1 bgxfSG iPawMI'}).text.strip().remove("% (1d)")
            price_change = f'+{growth}'

        # getting the other contents here.
        coin_content = soup.find('div', attrs={'class': "sc-d1ede7e3-0 jkmmuA content_folded"})

        # getting market-cap-content data here
        market_cap_content = coin_content.find('div', attrs={'class':'sc-d1ede7e3-0 bwRagp'})
        market_cap_price = market_cap_content.find('dd', attrs={'class': 'sc-d1ede7e3-0 hPHvUM base-text'}).text.strip()
        market_cap_rank_value = market_cap_content.find('span', attrs={'class': 'text slider-value rank-value'}).text.strip()
        market_cap_rank = market_cap_rank_value.remove("#")

        # formatting the market-cap-price
        market_cap_price = market_cap_price.split('%')[1]
        market_cap = "".join(market_cap_price.remove("$").split(','))

        # getting coin metrics content here.
        coin_metrics_content = soup.find('dl', attrs={'class':'sc-d1ede7e3-0 bwRagp coin-metrics-table'})
        coin_metrics = coin_metrics_content.find_all('div', attrs={'class':'sc-d1ede7e3-0 bwRagp'})

        volume_24h_rank = coin_metrics[1].text.strip().split("%")[1]
        volume_24h_price, volume_rank_value = volume_24h_rank.split("#")
        Volume_Market_cap_24h = coin_metrics[2].text.strip().split()[-1]

        volume = "".join(volume_24h_price.remove("$").split(','))
        volume_rank = volume_rank_value
        volume_change = Volume_Market_cap_24h.remove("%")

        Circulating_supply = " ".join(coin_metrics[3].text.strip().split()[2:])
        Circulating_supply = Circulating_supply.split(" ")[0]
        circulating_supply = "".join(Circulating_supply.split(","))

        Total_supply = " ".join(coin_metrics[4].text.strip().split()[2:])
        Total_supply = Total_supply.split(" ")[0]
        total_supply = "".join(Total_supply.split(","))

        fully_diluted_market_cap = coin_metrics[6].text.strip().split()[-1].remove("$")
        diluted_market_cap = "".join(fully_diluted_market_cap.split(","))

        # getting the complete coin_stats here.
        info_links_section = soup.find('div', attrs={'class' : 'sc-d1ede7e3-0 cvkYMS coin-info-links'})
        info_links = info_links_section.find_all('div', attrs={'class': 'sc-d1ede7e3-0 jTYLCR'})
        
        # getting the contarcts details
        contracts_details = info_links[0].text.strip().split()
        name = contracts_details[0].replace("Contracts", "").replace(':', "").lower()
        address = contracts_details[1]

        # getting the website link here.
        website_details = info_links[1].find('div', attrs = {'class':'sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf'})
        link = website_details.find('a')['href']

        # getting the socials here.
        socials = info_links[2].find_all('a')
        twitter = socials[0]['href']
        telegram = socials[1]['href']

        # storing all the fetched data here.    
        data = {
            "price": price,
            "price_change": price_change,
            "market_cap": market_cap,
            "market_cap_rank": market_cap_rank,
            "volume": volume,
            "volume_rank": volume_rank,
            "volume_change": volume_change,
            "circulating_supply": circulating_supply,
            "total_supply": total_supply,
            "diluted_market_cap": diluted_market_cap,
            "contracts": [
                {
                "name" : name,
                "address" : address,
                }
            ],
            "official_links": [
                {
                    "name": "website",
                    "link" : link
                }
            ],
            "socials" : [
                {
                    "name" : "twitter",
                    "url" : twitter
                },
                {
                    "name" : "telegram",
                    "url" : telegram
                }
            ]
        }

        task = Task.objects.filter(job__job_id=job_id, coin=coin).first()
        task.output = data
        task.status = 'completed'
        task.save()
    else:
        task = Task.objects.filter(job__job_id=job_id, coin=coin).first()
        task.status = 'failed'
        task.save()