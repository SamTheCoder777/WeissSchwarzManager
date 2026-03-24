import httpx
import re
import argparse
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

class Rarity:
    playset_rarity = ["RR", "R", "U", "C", "CR"]
    playset_td = ["TD"]

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_yuyutei_prices(code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    with httpx.Client(http2=True, headers=headers, timeout=1200.0) as client:
        card_dict = {}
        page = 1

        print(f"{Colors.YELLOW}Searching...{Colors.ENDC}")

        while True:
            if page == 1:
                link = f"https://yuyu-tei.jp/sell/ws/s/search?search_word={code}"
            else:
                link = f"https://yuyu-tei.jp/sell/ws/s/search?search_word={code}&page={page}"

            resp = client.get(link)
            
            if resp.status_code == 200:
                tree = HTMLParser(resp.text)
                print(f"{Colors.YELLOW}{link}{Colors.ENDC}")
                if tree.css_matches("p.m-5.pb-5"):
                    print(f"{Colors.GREEN}DONE{Colors.ENDC}")
                    break
                            
                for card_list in tree.css("div.py-4.cards-list"):
                    rarity = card_list.css_first("span.py-2").text().strip()

                    for card in card_list.css("div.col-md"):
                        
                        card_id = card.css_first("div.card-product span.my-2").text().strip()

                        if card_id.split("/")[0].lower() != code.lower():
                            continue
                        
                        price_text = card.css_first("div.card-product strong.text-end").text().strip().split(" ")[0]

                        card_name = card.css_first("h4.text-primary").text().strip()

                        stock_status = card.css_first("label.form-check-label").text().split(":")[1].strip()

                        if stock_status == "◯":
                            stock_status = -1
                        elif stock_status == "×":
                            stock_status = 0
                        else:
                            stock_status = int(stock_status.split(" ")[0])
        

                        card_dict[card_id] = {"rarity": rarity, "price": int(price_text.replace(",","")), "name": card_name, "stock": stock_status}

                page += 1
            else:
                break
        return card_dict

def calc_playset(code, scale=1):
    yuyu_card_dict = get_yuyutei_prices(code)

    playset_price = 0
    playset_wtd_price = 0
    for card_id in yuyu_card_dict:
        if yuyu_card_dict[card_id]["rarity"] in Rarity.playset_rarity:
            playset_price += yuyu_card_dict[card_id]["price"]*4
            playset_wtd_price += yuyu_card_dict[card_id]["price"]*4
        if yuyu_card_dict[card_id]["rarity"] in Rarity.playset_td:
            playset_wtd_price += yuyu_card_dict[card_id]["price"]*4
    
    print(f"With Scale: {scale}")
    print(f"{Colors.GREEN}------------- PLAYSET -------------{Colors.ENDC}")
    print(f"Price: {playset_price*scale} Yen")
    print(f"{Colors.CYAN}------------- PLAYSET WITH TD-------------{Colors.ENDC}")
    print(f"Price: {playset_wtd_price*scale} Yen")

def calc_single_price(code, card, scale):
    yuyu_card_dict = get_yuyutei_prices(code)
    matches = [key for key in yuyu_card_dict if card in key]

    for match in matches:
        stock = ""
        if yuyu_card_dict[match]['stock'] == -1:
            stock = "◯"
        elif yuyu_card_dict[match]['stock'] == 0:
            stock = "X"
        else:
            stock = str(yuyu_card_dict[match]['stock'])
        print(f"Rarity: {yuyu_card_dict[match]['rarity']} | Price: {yuyu_card_dict[match]['price']*scale} Yen | Stock: {stock}")
        
def calc_deck_price(code, deck_arr, scale=1):
    yuyu_card_dict = get_yuyutei_prices(code)

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
                    else:
                        out_of_stock[card_id] = {"count": 1, "price": yuyu_card_dict[card_id]["price"]}
            else:
                if card_id in in_stock:
                    in_stock[card_id]["count"] += 1
                else:
                    in_stock[card_id] = {"count": 1, "price": yuyu_card_dict[card_id]["price"]}
        else:
            if card_id not in missing_card:
                missing_card.append(card_id)

    total_price = 0
    total_price_wo = 0

    print(f"{Colors.GREEN}------------- IN STOCK -------------{Colors.ENDC}")
    for card_id, data in in_stock.items():
        print(f"{yuyu_card_dict[card_id]['name']} ({card_id}) - rarity: {yuyu_card_dict[card_id]['rarity']} | count: {data['count']} | total price: {data['price'] * data['count']} Yen")
        total_price += data["price"]*data["count"]
    print(f"{Colors.RED}------------- OUT OF STOCK -------------{Colors.ENDC}")
    for card_id, data in out_of_stock.items():
        print(f"{yuyu_card_dict[card_id]['name']} ({card_id}) - rarity: {yuyu_card_dict[card_id]['rarity']} | count: {data['count']} | total price: {data['price'] * data['count']} Yen")
        total_price_wo += data["price"]*data["count"]
    print(f"{Colors.YELLOW}------------- MISSING CARDS -------------{Colors.ENDC}")
    for card_id in missing_card:
        print(card_id)

    print(f"{Colors.GREEN}IN STOCK TOTAL: {total_price} Yen{Colors.ENDC}")
    print(f"{Colors.RED}OUT OF STOCK TOTAL: {total_price_wo} Yen{Colors.ENDC}")
    print(f"{Colors.CYAN}Grand Total: {total_price+total_price_wo} Yen{Colors.ENDC}")

    if scale != 1:
        print(f"{Colors.YELLOW}(Scale Adjusted) IN STOCK Grand TOTAL: {total_price * scale} Yen{Colors.ENDC}")
        print(f"{Colors.YELLOW}(Scale Adjusted) OUT OF STOCK Grand TOTAL: {total_price_wo * scale} Yen{Colors.ENDC}")

def parse_decklist(text):
    pattern = r"([A-Z0-9/]+-[A-Z0-9]+)\s+(\d+)"
    
    matches = re.findall(pattern, text)
    
    final_list = []
    for code, count in matches:
        for _ in range(int(count)):
            final_list.append(code)
            
    return final_list

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--import_type", dest="import_type", choices=["codes", "encore"],
                    help="card list format (code or blake)\nCodes: file with card codes separated by new lines\encore: Card deck txt file exported and saved from encoredecks.com")
parser.add_argument("-f", "--file", type=str, help="card list file path")
parser.add_argument("-c", "--code", type=str, required=True, help="Set code")
parser.add_argument("-sc", "--singlecard", type=str, help="Single card code")
parser.add_argument("-s", "--scale", type=float, default=1, help="set scale to the price")
parser.add_argument("-p", "--playset", action="store_true", help="calculate playset price")

args = parser.parse_args()

if args.singlecard:
    calc_single_price(args.code, args.singlecard, args.scale)
elif args.playset:
    calc_playset(args.code,args.scale)
else:
    if args.import_type == "codes":
        content = read_file(args.file)
        requested_cards = content.replace("-E", "-").replace("-TE", "-T").split("\n")
        calc_deck_price(args.code, requested_cards, scale=args.scale)
    elif args.import_type == "encore":
        content = read_file(args.file)
        requested_cards = parse_decklist(content)
        requested_cards = [item.replace("-E", "-").replace("-TE", "-T") for item in requested_cards]
        calc_deck_price(args.code, requested_cards, scale=args.scale)