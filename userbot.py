import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

import json
from telethon import TelegramClient, events ,Button
from telethon.tl.types import InputPhoneContact
import asyncio
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.functions.contacts import GetContactsRequest
import pytz
import datetime
import requests

# Own imports
from credentials import API_ID, API_HASH, PHONE_NUMBER, MODEL_API_HEADERS
import pysqlite3 as sqlite3
import database

api_id = API_ID
api_hash = API_HASH
phone_number = PHONE_NUMBER
client = TelegramClient('anon', api_id, api_hash)

# This model help check score of sentiment
model_api_url = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
model_api_headers = MODEL_API_HEADERS
global is_stopped
is_stopped = False

# Connect to personal database
conn =  sqlite3.connect('database/users.db')
cursor = conn.cursor()


def translate_text(text):
    url = "https://deep-translator-api.azurewebsites.net/google/"
    headers = {
        "Content-Type": "application/json",
    }

    params = {
        "source": "uz",
        "target": "en",
        "text": text,
        "proxies": []
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['translation']
    else:
        return None



def is_positive_response(message):

    message = translate_text(message)
    results = requests.post(model_api_url, headers=model_api_headers, json=message)
    results = results.json()
    if results[0][0]['label'] == 'POSITIVE' and results[0][0]['score'] > 0.75:
        return True
    return False

async def send_message_to_contact(contact_phone, name, message):
    # For adding contact to the contact list (This is main part of the code)
    contact = InputPhoneContact(client_id=0, phone=contact_phone, first_name=name, last_name='')
    result = await client(ImportContactsRequest([contact]))


    contacts = await client(GetContactsRequest(hash=0))

    target_user = next((user for user in contacts.users if user.phone == contact_phone), None)

    if target_user and target_user.id != None:
        await client.send_message(target_user, message)
        print(f"Message sent to {target_user.first_name}")
        await client.send_message(-4110173191, f"Message sent to {target_user.first_name}\nTime : {datetime.datetime.now(pytz.timezone('Asia/Tashkent'))}!")

    else:
        print("Contact not found.")
        await client.send_message(-4110173191, f"User is not found!\nTime : {datetime.datetime.now(pytz.timezone('Asia/Tashkent'))}!")
        return None
    

async def start_conversation():
    print("Starting conversation")
    contacts = database.read_data()
    cnt = 0
    if not contacts:
        await client.send_message(-4110173191, "There are no more contacts to send message.\nPlease check Google Sheets")
        print("Conversation ended")
        return None
    for contact in contacts:
        await send_message_to_contact(contact[1], contact[0], f'Assalomu alaykum {contact[0]}\n\nUmid qilamanki, mahsulotimiz sizga manzur kelgan!\n\nBizning kompaniyamiz mahsulotlaridan xarid qilganingizga bir yil bo\'ldi. Sizga, qayta buyurtma berishingiz uchun eng to\'g\'ri va maqbul vaqt ekanligini eslatmoqchimiz. Sababi ushbu haftada, bir yillik munosabati bilan, qayta buyurtma qilingan barcha mahsulotlarimiz uchun maxsus chegirmalar taklif qilamiz.\n\nSizga qulaylik yaratish maqsadida, buyurtma berishni soddalashtirdik☺️\n\nQuyidagi havolani bosish orqali, qisqa muddat ichida qayta buyurtma berishingiz mumkin!\n\n**Buyurtma berish uchun - [@StrawberryHouse_bot](http://t.me/StrawebarryHouse_bot/store)**\n\nSizga doimo xizmat ko\'rsatishdan mamnunmiz!\nXurmat ila Sevara\nStrawberry House\nBarcha savollar bo\'yicha +998 55 503 5252')
        cnt += 1
        database.move_specific_row()
        await asyncio.sleep(15)
        global is_stopped
        if is_stopped:
            break
    await client.send_message(-4110173191, f"Jami {cnt} ta mijozga xabar yetkazildi.")
    print("Conversation ended")



@client.on(events.NewMessage(incoming=True,outgoing=False))
async def handler(event):

    if '!start' in event.raw_text:
        await start_conversation()
        global is_stopped
        is_stopped = False
    if '!stop' in event.raw_text:
        is_stopped = True
    if '!stat' in event.raw_text:
        cursor.execute('SELECT * FROM responded_users')
        users = cursor.fetchall()
        await event.reply(f"Jami {len(users)} ta mijoz javob berdi.")
    if '!clear' in event.raw_text:
        cursor.execute('DELETE FROM responded_users')
        conn.commit()
        await event.reply("Mijozlar ro'yxati tozalandi.")
    # if not event.is_group:
    #     user_id = event.sender_id
    #     if is_positive_response(event.raw_text):
    #         cursor.execute('SELECT user_id FROM responded_users WHERE user_id = ?', (user_id,))
    #         if cursor.fetchone() is None:
    #             async with client.action(event.chat_id, 'typing'):
    #                 await asyncio.sleep(3)
    #                 await event.reply(f'Sovg\'alar uchun mo\'ljallangan chegirmadagi mahsulotlarimiz bilan, quiydagi **"[Havola](http://t.me/StrawebarryHouse_bot/store)"**ni bosing!\n\n')
    #                 cursor.execute('INSERT INTO responded_users (user_id) VALUES (?)', (user_id,))
    #                 conn.commit()
    #         else:
    #             print(f"{user_id} ga javob berilgan")
    #     else:
    #         print("Negative response")
    #         await event.reply(f'Axa tushinarli, agarda mahsulotlarimizni yaqinlaringizga sovg\'a sifatida xadya qilishni hohlasangiz, **"[LAUNCH](http://t.me/StrawebarryHouse_bot/store)"** knopkasini bosish orqali sotuv botimizdan foydalanishingiz mumkin!')
    #         cursor.execute('INSERT INTO responded_users (user_id) VALUES (?)', (user_id,))
    #         conn.commit()
    else:
        print("Unknown command")

client.start()
client.run_until_disconnected()


