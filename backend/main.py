from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from login import login
from scrapers import (
    fetch_upcoming_tournaments,
    fetch_tournament_history,
    fetch_nsda_points,
    fetch_tournament_signups,
    fetch_paradigm,
    fetch_account_info,
)
import requests
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/dashboard/")
async def get_dashboard_content(email: str = Form(...), password: str = Form(...)):
    try:
        logging.info("Processing /dashboard/ request")
        session = requests.Session()
        dashboard_content = login(
            "https://www.tabroom.com/user/login/login.mhtml", email, password, session, nsda=False, paradigm=False
        )
        logging.info("Login successful, parsing dashboard content")
        dashboard_soup = BeautifulSoup(dashboard_content, "html.parser")

        upcoming_tournaments = fetch_upcoming_tournaments(dashboard_soup)
        logging.info(f"Fetched upcoming tournaments: {upcoming_tournaments}")
        past_tournaments = fetch_tournament_history(dashboard_soup)
        logging.info(f"Fetched past tournaments: {past_tournaments}")
        signups = fetch_tournament_signups(dashboard_soup)
        logging.info(f"Fetched signups: {signups}")

        return JSONResponse(
            {
                "upcoming_tournaments": upcoming_tournaments,
                "past_tournaments": past_tournaments,
                "signups": signups,
            }
        )
    except Exception as e:
        logging.error(f"Error in /dashboard/: {e}", exc_info=True)  # Log stack trace
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard content: {str(e)}")

@app.post("/nsda/")
async def get_nsda_content(email: str = Form(...), password: str = Form(...)):
    try:
        logging.info("Processing /nsda/ request")
        session = requests.Session()
        nsda_content = login(
            "https://www.tabroom.com/user/login/login.mhtml", email, password, session, nsda=True, paradigm=False
        )
        nsda_soup = BeautifulSoup(nsda_content, "html.parser")
        nsda_points = fetch_nsda_points(nsda_soup)

        return JSONResponse({"nsda_points": nsda_points})
    except Exception as e:
        logging.error(f"Error in /nsda/: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch NSDA content")

@app.post("/paradigm/")
async def get_paradigm_content(email: str = Form(...), password: str = Form(...)):
    try:
        logging.info("Processing /paradigm/ request")
        session = requests.Session()
        paradigm_content = login(
            "https://www.tabroom.com/user/login/login.mhtml", email, password, session, nsda=False, paradigm=True
        )
        paradigm_soup = BeautifulSoup(paradigm_content, "html.parser")
        paradigm = fetch_paradigm(paradigm_soup, email, password)

        return JSONResponse({"paradigm": paradigm})
    except Exception as e:
        logging.error(f"Error in /paradigm/: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch paradigm content")

@app.post("/account/")
async def get_account_content(email: str = Form(...), password: str = Form(...)):
    try:
        logging.info("Processing /account/ request")
        session = requests.Session()
        account_content = login(
            "https://www.tabroom.com/user/login/login.mhtml", email, password, session, nsda=False, paradigm=False, account=True
        )
        account_soup = BeautifulSoup(account_content, "html.parser")
        account_info = fetch_account_info(account_soup)

        return JSONResponse({"account_info": account_info})
    except Exception as e:
        logging.error(f"Error in /account/: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch account content")