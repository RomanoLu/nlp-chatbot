# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import json
import requests
from urllib.request import urlopen
import datetime
import pandas as pd
from PIL import Image
from typing import Any, Text, Dict, List
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset

def get_price(dish):
    
    df = pd.read_csv(r"resources/prices.csv")

    filtered_df = df[df.Dish.str.contains(dish, case = False)]

    if filtered_df.empty:
        return None, None
    
    dish_name = filtered_df.iat[0, 0]
    dish_price = filtered_df.iat[0, 1]

    return dish_name, dish_price


class ActionGiveDay(Action):

    def name(self) -> Text:
        return "action_give_day"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        weekday_dict = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        date = datetime.datetime.today()
        weekday = date.weekday()

        weekday = weekday_dict[weekday]

        message = f"Today is {weekday}, {date}."

        dispatcher.utter_message(text = message)

        return []

class ActionGiveFoodPrice(Action):

    def name(self) -> Text:
        return "action_give_food_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dish_images = {
            "pizza": "assets/pizza.jpg",
            "antipasti": "assets/Antipasti.jpg",
            "dolce": "assets/Cannoli.jpg",
            "pasta": "assets/carbonara.png",
            "carne": "assets/Bistecca_alla_fiorentina.jpg"
        }

        if len(tracker.latest_message["entities"]) == 0:
            message = "We don't offer your requested dish. Please take a look at our card: https://drive.google.com/file/d/1jnngcQxGkQL0m_B9C-RSf-GZkVdKJV1m/view?usp=sharing"

            dispatcher.utter_message(text = message)
            return []

        dish = tracker.latest_message["entities"][0]["value"].lower()

        dish_name, dish_price = get_price(dish)

        if dish_name and dish_price:
            message = f"{dish_name} costs {dish_price} € (Euro)."
        else:
            message = "We don't offer your requested dish. Please take a look at our card: https://drive.google.com/file/d/1jnngcQxGkQL0m_B9C-RSf-GZkVdKJV1m/view?usp=sharing"

        dispatcher.utter_message(text = message)

        try:
            img = Image.open(dish_images[dish])
            img.show()
        except:
            pass

        return []

class ActionConfirmReservation(Action):

    def name(self) -> Text:
        return "action_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        email = tracker.get_slot("email")
        time = tracker.get_slot("time")
        date = tracker.get_slot("date")

        message = f"We have noted your reservation.\nWhen? {date}\nTime? {time}\nEmail {email}"

        dispatcher.utter_message(text = message)

        return [AllSlotsReset()]

class ActionConfirmOrder(Action):

    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        selectedfood = tracker.get_slot("selectedfood")

        message = f"We have noted your order.\n{selectedfood} \n Your food will arrive in 30 Minutes"

        dispatcher.utter_message(text = message)

        return [AllSlotsReset()]

class ActionGiveWeather(Action):

    def name(self) -> Text:
        return "action_check_outdoor_places"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            url = 'http://ipinfo.io/json'
            response = urlopen(url)
            data = json.load(response)

            city = data['city']

        except:
            dispatcher.utter_message(text = "If the weather is good, of course you also can sit outside")
            return []

        try:
            url = "https://community-open-weather-map.p.rapidapi.com/weather"

            querystring = {"q":city,"units":"metric"}

            headers = {
                'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
                'x-rapidapi-key': "425ee6975dmshef43068f62519e7p1c9496jsn0ff6d4e77085"
                }

            response = requests.request("GET", url, headers=headers, params=querystring)

            data = response.json()
        
        except:
            dispatcher.utter_message(text = f"If the weather in {city} is good, of course you also can sit outside")
            return []

        if data["weather"][0]["main"] == "Snow":
            weather = f"Unfortunately its snowing in {city}, i would reccomend a place inside our Restaurant"
        elif data["weather"][0]["main"] == "Rain":
            weather = f"Unfortunately its raining in {city}, i would reccomend a place inside our Restaurant"

        else:
            weather = f"We have {data['weather'][0]['main']}."

        if data["main"]["temp"] <= 18.0:
            temperature = f"The temperature is currently {data['main']['temp']} degrees Celsius and it almoust feels like {data['main']['feels_like']} degrees. So i would advise against a outdoor place."
        elif data["main"]["temp"] >= 25.0:
            temperature = f"The temperature is currently {data['main']['temp']} degrees Celsius. Thats the perfect weather, to enjoy a cold drink at our tarrace."
        else:
            temperature = f"I looked up bthe weather for you and it says that there {data['main']['temp']} degrees Celsius. If thats enought for you, you can sit outside."

        message = f"{weather} {temperature}"

        dispatcher.utter_message(text = message)

        return []

class ActionPlayRPS(Action):
   
    def name(self) -> Text:
        return "action_play_rps"
 
    def computer_choice(self):
        generatednum = random.randint(1,3)
        if generatednum == 1:
            computerchoice = "rock"
        elif generatednum == 2:
            computerchoice = "paper"
        elif generatednum == 3:
            computerchoice = "scissors"
       
        return(computerchoice)
 
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
 
        # play rock paper scissors
        user_choice = tracker.get_slot("choice")
        dispatcher.utter_message(text=f"You chose {user_choice}")
        comp_choice = self.computer_choice()
        dispatcher.utter_message(text=f"The computer chose {comp_choice}")
 
        if user_choice == "rock" and comp_choice == "scissors":
            dispatcher.utter_message(text="Congrats, you won!")
        elif user_choice == "rock" and comp_choice == "paper":
            dispatcher.utter_message(text="The computer won this round.")
        elif user_choice == "paper" and comp_choice == "rock":
            dispatcher.utter_message(text="Congrats, you won!")
        elif user_choice == "paper" and comp_choice == "scissors":
            dispatcher.utter_message(text="The computer won this round.")
        elif user_choice == "scissors" and comp_choice == "paper":
            dispatcher.utter_message(text="Congrats, you won!")
        elif user_choice == "scissors" and comp_choice == "rock":
            dispatcher.utter_message(text="The computer won this round.")
        else:
            dispatcher.utter_message(text="It was a tie!")
 
        return []