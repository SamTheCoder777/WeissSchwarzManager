import httpx
from selectolax.parser import HTMLParser

class Colors:
    """ANSI escape codes for various colors and styles."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m' # Reset to default

def get_yuyutei_prices(link_arr):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Use HTTP/2 for better efficiency and less 'bot-like' behavior
    with httpx.Client(headers=headers, timeout=1200.0) as client:
        card_dict = {}

        for link in link_arr:
            resp = client.get(link)
            
            if resp.status_code == 200:
                tree = HTMLParser(resp.text)
                            
                for card_list in tree.css("div.py-4.cards-list"):
                    rarity = card_list.css_first("span.py-2").text().strip()

                    for card in card_list.css("div.col-md"):
                        
                        card_id = card.css_first("div.card-product span.my-2").text().strip()
                        
                        price_text = card.css_first("div.card-product strong.text-end").text().strip().split(" ")[0]

                        card_name = card.css_first("h4.text-primary").text().strip()

                        stock_status = card.css_first("label.form-check-label").text().split(":")[1].strip()

                        if stock_status == "◯":
                            stock_status = -1
                        elif stock_status == "×":
                            stock_status = 0
                        else:
                            stock_status = int(stock_status.split(" ")[0])
            
                        
                        #print(f"Card: {card_id} | Price: {price_text} Yen | Rarity: {rarity} | Name: {card_name} | Stock: {stock_status}")

                        card_dict[card_id] = {"rarity": rarity, "price": int(price_text.replace(",","")), "name": card_name, "stock": stock_status}
            
        return card_dict
        
def calc_deck_price(link_arr, deck_arr, scale=1):
    yuyu_card_dict = get_yuyutei_prices(link_arr)

    in_stock = {}
    out_of_stock = {}
    missing_card = []

    for card_id in deck_arr:
        if card_id in yuyu_card_dict:
            if yuyu_card_dict[card_id]["stock"] != -1:
                if yuyu_card_dict[card_id]["stock"] >= 1:
                        if card_id in in_stock:
                            in_stock[card_id]["count"] += 1
                            yuyu_card_dict[card_id]["stock"] -= 1
                        else:
                            in_stock[card_id] = {"count": 1, "price": yuyu_card_dict[card_id]["price"]}
                            yuyu_card_dict[card_id]["stock"] -= 1
                else:
                    if card_id in out_of_stock:
                            out_of_stock[card_id]["count"] += 1
                            yuyu_card_dict[card_id]["stock"] -= 1
                    else:
                        out_of_stock[card_id] = {"count": 1, "price": yuyu_card_dict[card_id]["price"]}
                        yuyu_card_dict[card_id]["stock"] -= 1
            else:
                if card_id in in_stock:
                    in_stock[card_id]["count"] += 1
                else:
                    in_stock[card_id] = {"count": 1, "price": yuyu_card_dict[card_id]["price"]}
        else:
            if card_id not in missing_card:
                missing_card.append(card_id)

    total_price = 0
        
    print(f"{Colors.GREEN}------------- IN STOCK -------------{Colors.ENDC}")
    for card_id, data in in_stock.items():
        print(f"{yuyu_card_dict[card_id]['name']} ({card_id}) - rarity: {yuyu_card_dict[card_id]['rarity']} | count: {data['count']} | total price: {data['price'] * data['count']} Yen")
        total_price += data["price"]*data["count"]
    print(f"{Colors.RED}------------- OUT OF STOCK -------------{Colors.ENDC}")
    for card_id, data in out_of_stock.items():
        print(f"{yuyu_card_dict[card_id]['name']} ({card_id}) - rarity: {yuyu_card_dict[card_id]['rarity']} | count: {data['count']}")
        total_price += data["price"]*data["count"]
    print(f"{Colors.YELLOW}------------- MISSING CARDS -------------{Colors.ENDC}")
    for card_id in missing_card:
        print(card_id)
    print(f"{Colors.BLUE}Grand Total: {total_price} Yen{Colors.ENDC}")



#card_dict = get_yuyutei_prices("hol")

requested_card = """HOL/WE44-11
HOL/WE44-11
HOL/W91-E010
HOL/W91-E010
HOL/W91-E010
HOL/WE45-T04
HOL/WE45-T16
HOL/WE45-T16
HOL/WE45-T16
HOL/WE45-T16
HOL/WE44-10
HOL/WE44-10
HOL/WE45-T15
HOL/WE45-T03
HOL/WE45-T03
HOL/WE45-T03
HOL/WE45-T03
HOL/WE45-T07
HOL/WE45-T07
HOL/WE45-T07
HOL/WE45-T07
HOL/WE45-T14
HOL/WE45-T14
HOL/W104-018
HOL/W104-018
HOL/W104-001
HOL/W104-001
HOL/WE45-T01
HOL/WE45-T01
HOL/WE44-26
HOL/WE44-27
HOL/W104-075
HOL/W104-075
HOL/W104-075
HOL/W104-075
HOL/W104-125
HOL/W104-125
HOL/W104-125
HOL/WE45-T12
HOL/WE45-T12
HOL/WE45-T12
HOL/WE45-T12
HOL/WE45-T17
HOL/WE45-T17
HOL/WE45-T17
HOL/WE45-T17
HOL/WE45-T05
HOL/WE45-T05
HOL/WE45-T05
HOL/WE45-T05"""

links = ["https://yuyu-tei.jp/sell/ws/s/hol#entry","https://yuyu-tei.jp/sell/ws/s/holtd#entry","https://yuyu-tei.jp/sell/ws/s/holpb#entry","https://yuyu-tei.jp/sell/ws/s/hol2.0#entry","https://yuyu-tei.jp/sell/ws/s/holpb2.0#entry","https://yuyu-tei.jp/sell/ws/s/holtd2.0#entry"]
requested_card = requested_card.replace("-E","-").replace("-TE","-T").split("\n")
calc_deck_price(links, requested_card)
#print(requested_card)