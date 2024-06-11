import requests
from bs4 import BeautifulSoup

def fetch_coin_data(coin):
    url = f"https://coinmarketcap.com/currencies/{coin.lower()}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        coin_data = {}

        # Extracting the price and growth elements data
        price_growth = soup.find('div', attrs={'class': 'sc-d1ede7e3-0 gNSoet flexStart alignBaseline'})
        
        if price_growth:
            price_tag = price_growth.find('span', attrs={'class': 'sc-d1ede7e3-0 fsQm base-text'})
            if price_tag:
                # Remove "$" and "," from the price
                price = price_tag.text.strip().replace("$", "").replace(",", "")
                coin_data['price'] = price

            # Extract the growth for both positive and negative changes
            growth_tag_positive = price_growth.find('p', attrs={'class': 'sc-71024e3e-0 sc-58c82cf9-1 bgxfSG iPawMI'})
            growth_tag_negative = price_growth.find('p', attrs={'class': 'sc-71024e3e-0 sc-58c82cf9-1 ihXFUo iPawMI'})

            if growth_tag_positive:
                # Handle positive change
                growth = growth_tag_positive.text.strip().replace("%\xa0(1d)", "")
                coin_data['price_change'] = f'+{growth}'
            elif growth_tag_negative:
                # Handle negative change
                growth = growth_tag_negative.text.strip().replace("%\xa0(1d)", "")
                coin_data['price_change'] = f'-{growth}'

        # Extracting market cap content data
        coin_content = soup.find('div', attrs={'class': "sc-d1ede7e3-0 jkmmuA content_folded"})
        if coin_content:
            market_cap_content = coin_content.find('div', attrs={'class':'sc-d1ede7e3-0 bwRagp'})
            if market_cap_content:
                market_cap_price_tag = market_cap_content.find('dd', attrs={'class': 'sc-d1ede7e3-0 hPHvUM base-text'})
                if market_cap_price_tag:
                    market_cap_price = market_cap_price_tag.text.strip()
                    # Extract only the number part from market cap and remove "$"
                    market_cap_price = market_cap_price.split('%')[1].replace("$", "").replace(",", "")
                    coin_data['market_cap'] = market_cap_price
                
                market_cap_rank_tag = market_cap_content.find('span', attrs={'class': 'text slider-value rank-value'})
                if market_cap_rank_tag:
                    market_cap_rank = market_cap_rank_tag.text.strip().replace("#", "")
                    coin_data['market_cap_rank'] = market_cap_rank

        # Extracting coin metrics
        coin_metrics_content = soup.find('dl', attrs={'class':'sc-d1ede7e3-0 bwRagp coin-metrics-table'})
        if coin_metrics_content:
            coin_metrics = coin_metrics_content.find_all('div', attrs={'class':'sc-d1ede7e3-0 bwRagp'})
            if len(coin_metrics) > 1:
                volume_24h_rank = coin_metrics[1].text.strip().split("%")[1]
                volume_24h_price, volume_rank_value = volume_24h_rank.split("#")
                
                # Remove "$" from volume and format properly
                volume = volume_24h_price.replace("$", "").replace(",", "")
                coin_data['volume'] = volume
                coin_data['volume_rank'] = volume_rank_value
                
                if len(coin_metrics) > 2:
                    Volume_Market_cap_24h = coin_metrics[2].text.strip().split()[-1].replace("%", "")
                    coin_data['volume_change'] = Volume_Market_cap_24h

                if len(coin_metrics) > 3:
                    Circulating_supply = " ".join(coin_metrics[3].text.strip().split()[2:])
                    Circulating_supply = Circulating_supply.split(" ")[0]
                    coin_data['circulating_supply'] = Circulating_supply.replace(",", "")

                if len(coin_metrics) > 4:
                    Total_supply = " ".join(coin_metrics[4].text.strip().split()[2:])
                    Total_supply = Total_supply.split(" ")[0]
                    coin_data['total_supply'] = Total_supply.replace(",", "")

                if len(coin_metrics) > 6:
                    fully_diluted_market_cap = coin_metrics[6].text.strip().split()[-1].replace("$", "")
                    coin_data['diluted_market_cap'] = fully_diluted_market_cap.replace(",", "")

        # Extracting the coin stats and info links
        info_links_section = soup.find('div', attrs={'class' : 'sc-d1ede7e3-0 cvkYMS coin-info-links'})
        if info_links_section:
            info_links = info_links_section.find_all('div', attrs={'class': 'sc-d1ede7e3-0 jTYLCR'})
            if len(info_links) > 0:
                contracts_details = info_links[0].text.strip().split()
                if len(contracts_details) > 1:
                    name = contracts_details[0].replace("Contracts", "").replace(':', "").lower()
                    address = contracts_details[1]
                    coin_data['contracts'] = [
                        {
                            "name" : name,
                            "address" : address,
                        }
                    ]

            if len(info_links) > 1:
                website_details = info_links[1].find('div', attrs = {'class':'sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf'})
                if website_details:
                    link_tag = website_details.find('a')
                    if link_tag:
                        link = link_tag['href']
                        coin_data['official_links'] = [
                            {
                                "name": "website",
                                "link" : link
                            }
                        ]

            if len(info_links) > 2:
                socials = info_links[2].find_all('a')
                if len(socials) > 1:
                    twitter = socials[0]['href']
                    telegram = socials[1]['href']
                    coin_data['socials'] = [
                        {
                            "name" : "twitter",
                            "url" : twitter
                        },
                        {
                            "name" : "telegram",
                            "url" : telegram
                        }
                    ]

        return coin_data
    else:
        return {'error': 'Failed to retrieve data'}
