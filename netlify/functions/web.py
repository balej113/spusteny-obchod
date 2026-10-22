import json
import sqlite3
import html

DB_PATH = '/tmp/obchod.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            data TEXT
        )
    ''')
    
    default_state = {
        "produkty": [
            {"id": 0, "nazov": "jablko", "cena": 0.50, "sklad": 10},
            {"id": 1, "nazov": "banán", "cena": 0.45, "sklad": 10},
            {"id": 2, "nazov": "mrkva", "cena": 0.30, "sklad": 10},
            {"id": 3, "nazov": "zemiak", "cena": 0.25, "sklad": 15},
            {"id": 4, "nazov": "mlieko", "cena": 1.20, "sklad": 5}
        ],
        "kosik": [],
        "celkova_cena": 0.0,
        "clubcard_uplatnena": False,
        "kupon_uplatneny": False
    }
    
    cursor.execute('SELECT data FROM store_state WHERE id = 1')
    row = cursor.fetchone()
    if not row:
        cursor.execute('INSERT INTO store_state (id, data) VALUES (1, ?)', (json.dumps(default_state),))
        conn.commit()
    conn.close()

init_db()

def get_state():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM store_state WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def save_state(state):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE store_state SET data = ? WHERE id = 1', (json.dumps(state),))
    conn.commit()
    conn.close()

def handler(event, context):
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")
    
    for prefix in ["/.netlify/functions/web", "/api"]:
        if path.startswith(prefix):
            path = path[len(prefix):]
            
    if not path:
        path = "/"

    state = get_state()

    if method == "GET" and (path == "/stav" or path == "/"):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(state)
        }

    if method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            if "produkty" in body:
                state = body
        except:
            pass

        if path == "/stav":
            save_state(state)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(state)}

        elif path.startswith("/kupit/"):
            try:
                prod_id = int(path.split("/")[-1])
                for p in state.get("produkty", []):
                    if p["id"] == prod_id and p["sklad"] > 0:
                        p["sklad"] -= 1
                        state["kosik"].append(p["nazov"])
                        state["celkova_cena"] += p["cena"]
                save_state(state)
            except Exception as e:
                pass
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(state)}

        elif path == "/clubcard":
            if not state.get("clubcard_uplatnena", False) and state.get("celkova_cena", 0) > 0:
                state["celkova_cena"] *= 0.9
                state["clubcard_uplatnena"] = True
                save_state(state)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(state)}

        elif path == "/kupon":
            if not state.get("kupon_uplatneny", False) and state.get("celkova_cena", 0) > 0:
                state["celkova_cena"] *= 0.8
                state["kupon_uplatneny"] = True
                save_state(state)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(state)}

        elif path == "/zaplatit":
            state["kosik"] = []
            state["celkova_cena"] = 0.0
            state["clubcard_uplatnena"] = False
            state["kupon_uplatneny"] = False
            save_state(state)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(state)}

    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": f"Neznáma cesta: {path}"})
    }
