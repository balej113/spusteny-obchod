import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Data obchodu - upravene bez diakritiky pre Windows konzolu
produkty = ["jablko", "banan", "mrkva", "zemiak", "mlieko"]
ceny = [0.50, 0.45, 0.30, 0.25, 1.20]
druhy = ["ovocie", "ovocie", "zelenina", "zelenina", "mlecne"]
sklad = [5, 3, 4, 6, 2]
kosik = []

ADMIN_PIN = "1111"

@app.get("/", response_class=HTMLResponse)
def hlavna_stranka(chyba: str = None, blocek: str = None, sprava: str = None, admin: str = None):
    riadky_produktov = ""
    for i in range(len(produkty)):
        if sklad[i] == 0:
            riadky_produktov += f"<p style='color:gray;'>{produkty[i].capitalize()} - {druhy[i]} - {ceny[i]} Eur - <b style='color:red;'>VYPREDANE</b></p>"
        else:
            riadky_produktov += f"""
            <div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;'>
                <span>{produkty[i].capitalize()} ({druhy[i]}) - <b>{ceny[i]} Eur</b> (Skladom: {sklad[i]} ks)</span>
                <form action='/pridat' method='POST' style='margin:0;'>
                    <input type='hidden' name='produkt' value='{produkty[i]}'>
                    <button type='submit' style='background:#28a745; color:white; border:none; padding:3px 10px; cursor:pointer; border-radius:4px;'>Kupit</button>
                </form>
            </div>
            """

    polozky_kosika = "".join([f"<li>{p.capitalize()}</li>" for p in kosik]) if kosik else "<li>Kosik je prazdny</li>"
    celkova_cena = sum([ceny[produkty.index(p)] for p in kosik])

    chyba_html = f"<div style='background:#f8d7da; color:#721c24; padding:10px; border-radius:4px; margin-bottom:15px;'>{chyba}</div>" if chyba else ""
    sprava_html = f"<div style='background:#d4edda; color:#155724; padding:10px; border-radius:4px; margin-bottom:15px;'>{sprava}</div>" if sprava else ""
    
    blocek_html = f"""
    <div style='background:#e2e3e5; border:1px dashed #333; padding:15px; border-radius:4px; margin-top:20px;'>
        <h3 style='text-align:center; margin:0 0 10px 0;'>--- DOKLAD O NAKUPE ---</h3>
        {blocek}
        <form action='/reset' method='POST' style='text-align:center; margin-top:10px;'>
            <button type='submit' style='background:#007bff; color:white; border:none; padding:5px 15px; cursor:pointer; border-radius:4px;'>Novy nakup</button>
        </form>
    </div>
    """ if blocek else ""

    admin_html = ""
    if admin == "true":
        riadky_admin_skladu = ""
        for i in range(len(produkty)):
            riadky_admin_skladu += f"""
            <div style='display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;'>
                <span>{produkty[i].capitalize()} (Aktualne: {sklad[i]} ks)</span>
                <form action='/naskladnit' method='POST' style='margin:0;'>
                    <input type='hidden' name='produkt_index' value='{i}'>
                    <input type='number' name='pocet' value='5' style='width:50px; text-align:center;'>
                    <button type='submit' style='background:#17a2b8; color:white; border:none; padding:3px 10px; cursor:pointer; border-radius:4px;'>Pridat</button>
                </form>
            </div>
            """
        admin_html = f"""
        <div style='background:#fff3cd; border:1px solid #ffeeba; padding:15px; border-radius:8px; margin-top:30px;'>
            <h2 style='margin-top:0; color:#856404; text-align:center;'> ADMIN PANEL</h2>
            {riadky_admin_skladu}
            <p style='text-align:center; margin-bottom:0;'><a href='/'>Odhlasit sa z Admina</a></p>
        </div>
        """
    else:
        admin_html = """
        <div style='margin-top:40px; text-align:center; border-top:1px solid #ccc; padding-top:15px;'>
            <form action='/admin-prihlasenie' method='POST'>
                <label>Vstup pre Admina (Kod): </label>
                <input type='password' name='admin_kod' style='width:60px; text-align:center;'>
                <button type='submit' style='background:#6c757d; color:white; border:none; padding:3px 10px; cursor:pointer; border-radius:4px;'>Vstupit</button>
            </form>
        </div>
        """

    html_kod = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset='UTF-8'><title>FastAPI Obchod + Admin</title></head>
    <body style='font-family:Arial, sans-serif; background:#f4f4f4; padding:20px;'>
        <div style='background:white; max-width:500px; margin:0 auto; padding:20px; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color:#333; text-align:center; margin-top:0;'>=== OBCHOD ===</h1>
            {chyba_html}
            {sprava_html}
            <div>{riadky_produktov}</div>
            <h2 style='margin-top:20px; border-top:2px solid #333; padding-top:10px;'>--- KOSIK ---</h2>
            <ul>{polozky_kosika}</ul>
            <p><b>Cena pred zlavou:</b> {round(celkova_cena, 2)} Eur</p>
            {" " if blocek or admin == "true" else f'''
            <h2 style='margin-top:20px; border-top:2px solid #333; padding-top:10px;'>Pokladna</h2>
            <form action='/dokoncit' method='POST'>
                <p><b>Chcete naskenovat Clubcard? (Zlava 10%)</b><br>
                    <input type='radio' name='clubcard' value='ano'> Ano
                    <input type='radio' name='clubcard' value='nie' checked> Nie
                </p>
                <p><b>Sposob platby:</b><br>
                    <input type='radio' name='platba' value='hotovost' checked onclick="document.getElementById('pin_div').style.display='none'"> Hotovost<br>
                    <input type='radio' name='platba' value='karta' onclick="document.getElementById('pin_div').style.display='block'"> Karta
                </p>
                <div id="pin_div" style="display:none; margin-left:20px; margin-bottom:10px;">
                    <label>Zadajte 4-miestny PIN: </label>
                    <input type='password' name='pin' maxlength='4' style='width:50px; text-align:center;'>
                </div>
                <p><b>Mas kupon? (Zlava 20%)</b><br>
                    <input type='radio' name='kupon' value='ano'> Ano
                    <input type='radio' name='kupon' value='nie' checked> Nie
                </p>
                <button type='submit' style='background:#007bff; color:white; border:none; padding:10px; width:100%; cursor:pointer; font-weight:bold; border-radius:4px; margin-top:10px;'>Dokoncit nakup</button>
            </form>
            '''}
            {blocek_html}
            {admin_html}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html_kod)

@app.post("/pridat")
def pridat(produkt: str = Form(...)):
    if produkt in produkty:
        pozicia = produkty.index(produkt)
        if sklad[pozicia] > 0:
            kosik.append(produkt)
            sklad[pozicia] -= 1
    return HTMLResponse("<script>window.location.href='/';</script>")

@app.post("/admin-prihlasenie")
def admin_prihlasenie(admin_kod: str = Form(...)):
    if admin_kod == ADMIN_PIN:
        return HTMLResponse("<script>window.location.href='/?admin=true';</script>")
    else:
        return HTMLResponse("<script>window.location.href='/?chyba=Nesprávny admin kód!';</script>")

@app.post("/naskladnit")
def naskladnit(produkt_index: int = Form(...), pocet: int = Form(...)):
    if 0 <= produkt_index < len(sklad):
        sklad[produkt_index] += pocet
    return HTMLResponse("<script>window.location.href='/?admin=true&sprava=Tovar bol uspesne naskladneny.';</script>")

@app.post("/dokoncit")
def dokoncit(clubcard: str = Form(...), platba: str = Form(...), pin: str = Form(None), kupon: str = Form(...)):
    cena = sum([ceny[produkty.index(p)] for p in kosik])
    if platba == "karta":
        if not pin or len(pin) != 4 or not pin.isdigit():
            return HTMLResponse("<script>window.location.href='/?chyba=Neplatny PIN kod! Platba kartou zlyhala.';</script>")

    vypis = ""
    if clubcard == "ano": cena *= 0.9; vypis += "<p>• Clubcard: Uplatnena zlava 10%</p>"
    else: vypis += "<p>• Clubcard: Nepouzita</p>"
    if platba == "karta": vypis += "<p>• Platba: Kartou</p>"
    else: vypis += "<p>• Platba: V hotovosti</p>"
    if kupon == "ano": cena *= 0.8; vypis += "<p>• Kupon: Uplatnena zlava 20%</p>"
    else: vypis += "<p>• Kupon: Nepouzity</p>"

    vypis += f"<h4><b>Vysledna cena po zlavach: {round(cena, 2)} Eur</b></h4>"
    return HTMLResponse(f"<script>window.location.href='/?blocek=' + encodeURIComponent(`{vypis}`);</script>")

@app.post("/reset")
def reset():
    global kosik
    kosik.clear()
    return HTMLResponse("<script>window.location.href='/';</script>")

