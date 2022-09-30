from fastapi import FastAPI, Depends
from typing import Optional
from pydantic import BaseModel
from random import shuffle
import numpy as np
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

#Authentication user
@app.get("/Authentication/")
def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="yourname@example.com", full_name="Name Familyname"
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Shuffle card and tell the value and position of card to front-end
@app.get("/shuffle/")
async def shuffle_cards():
    data = {}
    data['card_position'] = []
    set1 = list(range(1, 7)) #set number of card 1 to 6
    set2 = list(range(1, 7)) #set number of card 1 to 6
    all_set = set1+set2 #merge set number
    shuffle(all_set) #shuffle set number
    reshape_set = np.reshape(all_set, (3,4)) #reshape into row(3) and column(4)
    reshape_set_arr = reshape_set.tolist() #change to list because numpy cannot return to json
    for i in range(0,3):
        for j in range(0,4):
            data1 = {"card_number":reshape_set_arr[i][j], "row":i, "col": j}
            data['card_position'].append(data1)
    return data

#return overall click
Global_Best = 20
@app.get("/playgame/click_status")
async def CLickStatus(Global_Best : int):
    Best_Click = {"click": "-", "My_best" : "-", "Global_Best" : Global_Best} #set click initial
    return Best_Click

#receive card first value from front-end and return click count
click_number = 0
@app.post("/playgame/card1/")
async def Firstcard(card_value : int, click_number):
    click_number = click_number + 1
    result_card1 = {"click": click_number, "card1": card_value }
    return result_card1

#receive card second value from front-end and return click count
@app.post("playgame/card2/")
async def Secondcard(card_value : int, click_number):
    click_number = click_number+1
    result_card2 = {"click": click_number, "card2": card_value }
    return result_card2

#return statys card if it's not matched, it will return Close. On the other hand, it will return Open to front-end
Open_card = 0
@app.get("/playgame/resultcard/")
async def ResultCard(result_card1, result_card2, Open_card : int):
    if result_card1["card1"] == result_card2["card2"]:
        Open_card = Open_card+2
        status_card = {"status_card":"Open", "Open_card":Open_card}
        return status_card
    else:
        status_card = {"status_card":"Close", "Open_card":Open_card}
        return status_card

#check status open card if it at 6, it will be the end of game. Adn update the click status
@app.get("/playgame/endgame/")
async def Update_Click(status_card, result_card2, Best_Click):
    if status_card["Open_card"] == 6:
        click = result_card2["click"]
        if Best_Click["My_Best"] < click: 
            My_best = click
        if Best_Click["My_Best"] >= click: 
            My_best = Best_Click["My_Best"]
        if Best_Click["My_Best"] > Best_Click["Global_best"]:
            Global_Best = Best_Click["My_Best"]
    result_click = {"Click":click, "My_Best":My_best, "Global_best": Global_Best}
    return result_click

#start new game with shuffle card first, and re turn the new click while concerned My Best and Global Best to front-end
@app.get("/newgame/")
async def NewGame(result_click):
    Shuff_card = shuffle_cards()
    return Shuff_card, {"click": "-", "My_best" : result_click["My_Best"], "Global_Best" : result_click["Global_best"]}
    


    






    