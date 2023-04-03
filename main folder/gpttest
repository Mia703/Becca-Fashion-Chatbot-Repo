import pandas as pd
import openai

openai.api_key = "sk-yourkeyhere"

def recommendClothing(interest, color, style):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "Recommend a real clothing item for someone who likes" + interest + "and the color" + color + "and the" +  style + ". Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result

def recommendClothingAfterFeedback(interest, color, style, lastRec, feedback):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "Recommend a real clothing item for someone who likes" + interest + "and the color" + color + "and the" +  style + ". This person gave the following feedback to your last recommendation of " + lastRec + ": " + feedback + "Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return "I think you;d like" + result

def feedbackSentiment(feedback):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "You just recommended a clothing item. This is their response:" + feedback + "Is the sentiment of this response positive, negative, or neutral. Give a one word response."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result


lastRec = recommendClothing("Golf","black","sporty")

feedbackSentiment("Thanks, these look good!")

lastRec = recommendClothingAfterFeedback("golf","black","sporty",lastRec, "I don't really like this to be honest. I'm looking for a pair of socks!")
