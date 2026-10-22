import json

ZAKLADNE_PRODUKTY = [
    {"id": 0, "nazov": "jablko", "cena": 0.50, "druh": "ovocie"},
    {"id": 1, "nazov": "banan", "cena": 0.45, "druh": "ovocie"},
    {"id": 2, "nazov": "mrkva", "cena": 0.30, "druh": "zelenina"},
    {"id": 3, "nazov": "zemiak", "cena": 0.25, "druh": "zelenina"},
    {"id": 4, "nazov": "mlieko", "cena": 1.20, "druh": "mliečne"}
]

ADMIN_PIN = "1111"

def handler(event, context):
    path = event.get("path", "")
    api_path = path.replace("/.netlify/functions/web", "")
    if not api_path:
        api_path = "/"

    try:
        req_data = json.loads(event.get("body", "{}")) if event.get("body") else {}
    except:
        req_data = {}

    sklad = req_data.get("sklad", [5, 3, 4, 6, 2])
    kosik = req_data.get("kosik", [])
    celkova_cena = req_data.get("celkova_cena", 0.0)
    clubcard_uplatnena = req_data.get("clubcard_uplatnena", False)
    kupon_uplatneny = req_data.get("kupon_uplatneny", False)

    # 1. Admin login
    if api_path == "/admin-auth":
        pin = req_data.get("pin", "")
        success = (pin == ADMIN_PIN)
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"success": success})}

    # 2. Stav obchodu
    if api_path == "/stav" or api_path == "/":
        produkty_so_skladom = [{**p, "sklad": sklad[p["id"]]} for p in ZAKLADNE_PRODUKTY]
        res_body = {
            "produkty": produkty_so_skladom, "kosik": kosik, 
            "celkova_cena": round(celkova_cena, 2), "sklad": sklad,
            "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(res_body)}

    # 3. Kúpiť produkt
    elif "/kupit/" in api_path:
        try:
            pozicia = int(api_path.split("/")[-1])
            if sklad[pozicia] > 0:
                kosik.append(ZAKLADNE_PRODUKTY[pozicia]["nazov"])
                celkova_cena += ZAKLADNE_PRODUKTY[pozicia]["cena"]
                sklad[pozicia] -= 1
        except:
            pass
        produkty_so_skladom = [{**p, "sklad": sklad[p["id"]]} for p in ZAKLADNE_PRODUKTY]
        res_body = {
            "produkty": produkty_so_skladom, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "sklad": sklad, "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(res_body)}

    # 4. Clubcard zľava
    elif api_path == "/clubcard":
        if not clubcard_uplatnena:
            celkova_cena *= 0.9
            clubcard_uplatnena = True
        produkty_so_skladom = [{**p, "sklad": sklad[p["id"]]} for p in ZAKLADNE_PRODUKTY]
        res_body = {
            "produkty": produkty_so_skladom, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "sklad": sklad, "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(res_body)}

    # 5. Kupón zľava
    elif api_path == "/kupon":
        if not kupon_uplatneny:
            celkova_cena *= 0.8
            kupon_uplatneny = True
        produkty_so_skladom = [{**p, "sklad": sklad[p["id"]]} for p in ZAKLADNE_PRODUKTY]
        res_body = {
            "produkty": produkty_so_skladom, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "sklad": sklad, "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(res_body)}

    # 6. Zaplatiť / Reset košíka
    elif api_path == "/zaplatit":
        produkty_so_skladom = [{**p, "sklad": sklad[p["id"]]} for p in ZAKLADNE_PRODUKTY]
        res_body = {
            "produkty": produkty_so_skladom, "kosik": [], "celkova_cena": 0.0,
            "sklad": sklad, "clubcard_uplatnena": False, "kupon_uplatneny": False
        }
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(res_body)}

    return {"statusCode": 404, "body": "Not Found"}
