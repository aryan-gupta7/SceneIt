


# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "What LLM am i using?",
#         }
#     ],
#     model="llama3-70b-8192",
# )

# print(chat_completion.choices[0].message.content)

def analyse_email(email):
    import json
    from groq import Groq
    API_KEY = ""

    with open('key.json', 'r') as file:
        data = json.load(file)
        API_KEY = data['API_KEY']

    client = Groq(
        api_key=API_KEY,
    )
    analysis = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                # "content": f"Analyse the following email and if it is a mail for an event organized by some club, either it is from STC IITR or the clubs name. If it is a non club mail, skip it and don't give any output. Now if it is from a club, you have to give me output in the following format: 'Event Name - \nEvent Date - \nEvent Location - \nEvent Timing - \nEvent Type - Technical/Cultural\nEvent Description - (2 liner description of the event)' Following is the mail given. Subject: {email['subject']} Content: {email['content']}",

                "content":f"You will be given a mail and before giving any output you have to check if the mail is from a club or for some workshop/event by a club or not. If this is the case then you have to give me output in the following format: 'Event Name: \nEvent Date: %Y-%m-%d\nEvent Location: \nEvent Timing: %H:%M\nEvent Type: Technical/Non Technical\nEvent Tag: (judge this out of the following only- if it is a technical event, sort it from (Finance , CP , Development , Data Science/AI , Cyber Security ,  Block Chain , AI + ROBOTICS , Design , Quantum Computing , Machine Learning) and if it is non technical event, sort it from (Heritage , Language Exploration , Culinary , Lights Section , Alumini Relations , E- Cell , Photography , Fine Arts , Audio Section , Quizzing Section , Debating , Dramatics , Cheoregraphy and Dance Section , Cinematic Section , Musics section , Sports events))\nEvent Description: (2 liner description of the event)' Remember no output should be given for mails which are not from a club or for some workshop/event by a club, No output. Following is the mail given. Subject: {email['subject']} Content: {email['content']}",

            }
        ],
        model="llama3-70b-8192",
    )
    return analysis.choices[0].message.content

