from pydantic import BaseModel
from fastapi import FastAPI
from core import run_label_flip
from core2 import run_fit
from core3 import run_fit_core3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    number: int
    text: str


@app.post("/check")
async def check_run(item:Item):
    if item.text == "Conv.":
        res_data = run_label_flip(item.number)
        return JSONResponse(content=res_data,media_type="application/json")
    if item.text == "Fully BCaFL":
        res_data = run_fit(item.number)
        return JSONResponse(content=res_data,media_type="application/json")
    if item.text == "Semi-BCaFL":
        res_data = run_fit_core3(item.number)
        return JSONResponse(content=res_data,media_type="application/json")