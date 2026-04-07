from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import datetime
from user_agents import parse

app = FastAPI(docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

API_KEY = "5b6e0bb107a74c7b8f805ff871c996c9"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):


    async with httpx.AsyncClient() as client:
        city = await detector(request, client)

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "en"
        }
        response = await client.get(BASE_URL, params=params)
        weather_data = None
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                "city": data["name"],
                "temp": round(data["main"]["temp"]),
                "desc": data["weather"][0]["description"].capitalize()
            }

    return templates.TemplateResponse(request, "index.html", {"weather": weather_data})

@app.get("/get_weather", response_class=HTMLResponse)
async def get_weather(request: Request, city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        if response.status_code != 200:
            error_msg = "You are trying to find some shit, can't find it"
            return templates.TemplateResponse(request, "index.html", {"error": error_msg})

        data = response.json()
        weather_data = {
            "city": data["name"],
            "temp": round(data["main"]["temp"]),
            "desc": data["weather"][0]["description"].capitalize()
        }

        return templates.TemplateResponse(request, "index.html", {"weather": weather_data})

async def detector(request, client):
    client_ip = request.client.host
    geo_url = f"http://ip-api.com/json/{client_ip}?lang=en"
    geo_response = await client.get(geo_url)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if geo_data.get("status") == "success":
            city = geo_data.get("city")

    user_agent_row = request.headers.get("user-agent", "Unknown")
    user_agent = parse(user_agent_row)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_info = user_agent.os.family
    browser_info = user_agent.browser.family
    device_model = user_agent.device.family

    log_entry = f"[{timestamp}] IP: {client_ip} | City: {city} | Device:{device_model} | OS: {os_info} | Browser: {browser_info}\n"
    with open("visit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

    return city
