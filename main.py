from fastapi import FastAPI
import sqlite3

app = FastAPI()
con = sqlite3.connect("tutorial.db")

async def get_data():
    cur = con.cursor()

    cur.execute("CREATE TABLE base(id, name, latitude, longitude)")
    cur.execute("""
    INSERT INTO base VALUES
        ('1', 'Riga', 56.97475845607155, 24.1670070219384),
        ('2', 'Liepaja', 56.516083346891044, 21.0182217849017),
        ('3', 'Daugavpils', 55.87409588616014, 26.51864225209475),
    """)
    cur.execute("CREATE TABLE interceptor(id, name, speed, range, max_altitude, cost, cost_type)")

    con.commit()
    res = cur.execute("SELECT * FROM base")
    data = res.fetchall()
    return data


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/bases")
def read_all_bases():
    all_bases = get_data()
    return {"bases": str(all_bases)}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
