#FASTAPI setup
from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from fastapi import HTTPException
from app.draft import Draft

app = FastAPI()

#CORS setup
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

#API endpoints

@app.post("/")
async def initialize_draft(host: str, id: str, name: str = "test draft"):
    #first page, league id filled in
    draft = Draft(host, id, name)
    return draft

@app.post("/draft/{host}/{id}")
async def update_draft(draft: Draft, team: int, reset_button: bool = False, reoptimize_button: bool = False):
    # fill in first pick number or team name/id
    # button to reset the picks before you
    # button to reoptimize the draft

    #TODO
    if reset_button:
        draft.update_draft()
        return {"message": "Draft reset"}
    elif reoptimize_button:
        draft.optimize_draft(team)
        return {"message": "Draft reoptimized"}
    else:
        return {"message": "Draft updated"}