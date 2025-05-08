from aiogram.types import TelegramObject, ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner
from aiogram import Bot

from typing import List


from database import req
from database.models import Ticket, Channel

import config

from datetime import datetime, timedelta








async def get_json_subscriptions(bot: Bot, user_tg_id: int, channels: List[Channel]):
    result = {
        "allSubscribed": False,
        "details": []
    }

    for channel in channels:
        try:
            u_status = await bot.get_chat_member(
                chat_id=channel.id,
                user_id=user_tg_id
            )


        except Exception as e:
            print('err in check channel', e)
        
        if not (isinstance(u_status, ChatMemberMember) or isinstance(u_status, ChatMemberAdministrator) \
                or isinstance(u_status, ChatMemberOwner)):
            result['details'].append(
                {
                    "channelId": channel.id,
                    "channelName": channel.name,
                    "isSubscribed": False
                }
            )
            
    if len(result['details']) == 0:
        result['allSubscribed'] = True

    return result






# async def generate_ticket_number(eventId: int, max_att = 1000):
#     if max_att < 1:
#         return None

#     event = await req.get_event(event_id=eventId)
#     event_tickets = event.tickets

#     tickets_nums = [event.number for event in event_tickets]

#     # Символы: A-Z и 0-9
#     characters = string.ascii_uppercase + string.digits
    
#     # Генерация билета из 6 случайных символов
#     ticket = ''.join(random.choice(characters) for _ in range(6))
    
#     if ticket in tickets_nums:
#         return generate_ticket_number(eventId, max_att-1)
    
#     return ticket

    

import asyncio
print(asyncio.run(generate_ticket_number(1)))











async def _get_tickets(user: req.User):
    tickets = []
    for ticket in user.tickets:
        tickets.append({
            "id": ticket.id,
            "number": ticket.number,
            "createdAt": ticket.created_at.strftime("%d.%m.%Y, %H:%M")
            })
        
    return tickets


async def get_json_user_tickets(user_id: int):
    user = await req.get_user(user_id=user_id)

    
    return {
            "tickets": await _get_tickets(user=user)
        } 



async def get_json_event_time(eventId: int):
    print(eventId)
    event = await req.get_event(int(eventId))
    
    event_date = event.end_date

    date =  datetime.now() - timedelta(
        days=event_date.day,
        hours=event_date.hour,
        minutes=event_date.minute,
        seconds=event_date.second
    )
    
    return {
     
            "days": date.day,
            "hours": date.hour,
            "minutes": date.minute,
            "seconds": date.second
            
        }



async def get_json_event_winners(eventId: int):
    print(eventId)
    event_winners = await req.get_event_winners(int(eventId))
    # print(event_winners)
    result = []
    
    for i, winner in enumerate(event_winners):
        image_url = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAJQAlAMBIgACEQEDEQH/xAAbAAABBQEBAAAAAAAAAAAAAAAEAAECAwUGB//EADgQAAIBAwIDBQQJBAMBAAAAAAECAwAEERIhBTFBEyJRYXEGgZGxFCMyQlJiodHwM4LB8RVy4TX/xAAZAQADAQEBAAAAAAAAAAAAAAAAAgMBBAX/xAAlEQACAgMBAAIBBAMAAAAAAAAAAQIRAyExEiIyQVFScYEEExT/2gAMAwEAAhEDEQA/AO9Ap6Qp6YuNSxUsUsUARApVKligCNNU6ahgD3W0EmPwmuD4ZxGaCJlVRgyNz9a72+2tJCPwmvI4OLm3d0x949POoybUjdVs6fjHFJ4bBpA2D02rneDcZ4i15GGlYxs2N+lVT8RN4pR5CR4EVCBE1aQ2KWTbQi83o7u7mSOLU0w+NYVzfiUsivkFT8qAa0CqC0xbbqaqt4c3a4O2G+RqNfF2WctqjuPZpccMjHlWvis32fXHDo/StTFPj+qGl0rIqJFWGokU5hXilUsUqygNIUqelXURFSAzT0hRQDEUqlTUANimxUqWKDQa+jaS0kRPtMpArzJvYzijOzFF3J616fe3C2lu0zZwoycVnrxC4lRXjsJCGGd9qlNJsZWcGnsVxIb6E+NXx+x3E0bVmL412hu+IH7Ni3vYVW1zxQ8rNfe4qfj+TdHLn2S4oec8QFST2Qv1ZWF0mrpgV0fbcYY4FvCD5tUZP+ZWN3bsFAUnANLKCS2magvhtobO1SFjkqu58aJIqjhtw1zbJJJ9ojf1ok1sarQPpA1HrUyKYitArpU+KegDQpUqfFdRIVLFPypUANilinp6AI4pYqVKgDL9oDjhcnqB+tEw6VhQAdBQXtMSvDCR+IYHvpxdMEUZXkOtZBfNmZHUUHNsKqO/I4oQ3SdZUH91B8U4xbWMOoyK7ZGw3p3KMVtiK2a42Gomqbt828u/3G+Vee3/ALWXv0yZbcMYSe6QOVR4dx/iV1cyC4yITEwxy3rnyZ4+WUhF+kd7wUYsY8+FHYoPg3/z4j5UaceNTgvii0ukTUTTlhq09eePCmNaYRNKkaVAGhSZtKk+FKn6V0kTOPGII5NFzHJEehIyD76OhljmGqJ1ZfEGs++s1lyXA0+PUelYTpccPk1gt2ednU7e+uWeaeN74XWOMlo7DfwzT1g23G2H9VgQNjWrBfW8y5ViPdVYZozFlilEJpcqh9JiwMHJpmuk0kqM4qlomkzF9tHEfCCSTjUOVcO98HH9bP8Aca9NmkgmjKyxqyH7QYZBoN7LhkbLqs4su2le7XLlh6laZaP1po85a6T8e/vpjPHIE1EHvYOx3r0prWwjOPosWPJRTiKwA2tkH9oqP+hfmQ39HlwkQkYjbf8AIdqshuAGOmKQ90qBoIr04izwQI0G34RUXe0j3CRgDbcYxR/zx/cCb7QPw5xb8LiMvPSNuppNOxUyOpCD+mvVj51Rd38KISgE74xg/ZFV23bTt2s51N0HQDyppZFFeYjKDe2HWwbBZ92Y5JojpVcWdgeVW9KpBaElpkMUqVKmFNDFOKanrpIlMqFs77Vm3Vs3OJtLH4H1Fa7DIxk+6gbwFQdOT45pMqTVspB09GRFbfWHtoUVvEbe+iUYoVGwXOlsbY8KUjjAHLHWqhJFMWXmRuc8q4dRejp2wm3m13HYHZwDTJcKk5jyVyNzWbYTqOKAu24BUeYP8FT4jJplgZVyHkOfhTe7jZnnYZM7RhVzqUNvVMcrz3cAYjQmpjg/ext86puSzM41Yywxkb5x/qpW0TxvuQArbnHPYVFyY9F9xdBr0QMRqCgkCoXFwkMvZa8Men+aFtmMt9LOwAQscHPPc4rPu5RJxVwTkq2B0pJSGSNdp9WxyFJ5+FUmMMSdWSTtk0PdXCRsFyDp2zjYmkkjPgrnapNj0OYQGznJrWtVBHdas0S6+ex8PGtDh4Mg1NufA1TFuQmS6D41I+1vUjTgYFRNehxHIyNKmp6ANCnpqROATnlXSRIyPoXPwrIvbkqRknPLnRUs7OrsuMjlnpXF8Wj4jdXBjguCrZ+7sK5P8jJWkdGKC6b80oEe5Tb8TihIQqzF4mB6sFOR/B5V5x7ScMurbidvbXN5gSDOueXTGD5t0Fc7FxKe0mbsbuVME/Z5bdQf3qKxuWxpZVF0z2CCE/8AKmbmApKgHYn+ZovVquIFl+4f351xnsN7UyX/ABGCxu1yznCv4+tegXcUcV2hXGTTY8fx2a5p7Q00RZlPQ/Z/zUL8pb22RuQQfdRDNmTRnDAYzQ10utME7efyqM1Q6ZlJOyACNWZBnTj+e6grYu/FGlcFUzkfl/8Aa6ewsUNv38Yx8K8x9p/aZ7W+uLTh6AlXKGTPPffHnSLG5Guaj06+7ubYPqmmjjVd85yTjpULfidmsmnt1RTy1HGa8euuI3l0cSzSc8YBrvvZjgH/ADHEIOLXlhHw6ygGcDnK2c7eVUlg8q2xI5/TpI6a4vY1mBjmRl/Kw+VaXCeJRyPpRvh1rOvYuGyXAaG3yy8307mrICgOYyobnjbOK5otxlou9rZ1ytqUGomheHz9rCAelEmvTi7jZxyVMiaVNSrTA53AHMUHLchiYg2554qqeVVB3oFV1T9plh50TzJOjVj0FSdy0kaMjVyyTXLzzuswEZZJAeecAV0t2AbRlQ6R16k1yV2GSXOouB1xlh+9Qz7eiuMbjdtDxqGJJiI7qI5ilxkcuRH+64y/9juKXV0WjVG1HdlIwfT/AFXbQaFjG2dtuXOirWdV7qnB6DG9SUpQY0oRl05jg/AJeC8b4dPMAGXLYTfAHif7q9CLLcyCQ7evWsmY9ss2o6pNIGT035VoWSgxr3tgN66cbtEmlEu7ZXnOnIAwNxufOrJ1QkFzk42PWqQFErFQB3hkjltVraSpL5UgdeVRn0pEFubxoLWVYhqYqdAzjeuUi9lrO6WSa9gWOd31HR4nc1tX7hpY1DLkupwTiiMjvjwPM86i5NcKUn0xIeB8K4dIGsuHdrKTnWygjPvNWzPdyt9cucDuqnJR6UXcuyLntOf5SB8jQzlxHqWNSPxE7N8/lSNt9BJLhSZMMqvhjtjR0rV4e4ZtKoVGMHYVmo6qQxjOTyKitmyCA6joDnqBSJDWG8Kly7oucdc1pZoLh1uEaR8nU3wo016GFVE5cjuQ1KmzSqohlySh1ySD6GhxcBDgD9aoe6Ibuy58udUyzsRkNGT4OteY57OvyHPxONI2yHIA3IrDvL+zm+sjfG+4fb4UPfdsSXSO1lP/AGZPkaz/AKVaMdNygif8RmR/gMr+tWU3IR0jWW4jnb6pn2IyCMZHiPGiLde0bAyw8jQXDjD2uFnhcMuwVgH/AG/WjY4HVlZJgiA5KltXwAp1Gws00t37EhhgEjGBzq1GEII1AY552J9KhFcCT6tWJ0nAJ23rlPaq+vOHXYS6heS3OAksf4fA+Y/arfVaE6zo2vgjYd+7zJU8xVs94stvqVic+FcOOIw3MjRqQFK4IbP8zTcNuOIzz9hYWroCSA8zd3HjgfvXM5NstSSO3trdT2LHffUD4VfLHpJ7xI8aos4Tw+xWOWR5psku437xPh0FQkuI5wYisieOdm9R40rBFMsiBSikEnbdM/rn/FBTmWKHUDjG2ll3NHR8OlUMyMZSdznAyPMUFxa2k1rHGjFsbqH2+Gx/WkoGwMXs4AKiNcc9fhV3D71vpGh2LZ5YFUpZtH3nULjngaj+tF2kZ7ZXjwE5ct6KoLOwsTqgVs1eTQ9kcW6g86uJrvh9Tll0VNTZpU1gcR9IWYMMYkXmAflVEt80ZXUysCe7q+9/75U11FCJi4JWReYzgHz25/pQf02F0IVjpdsgoNIz6868iv1OxsKE/auYhGyhxjaEbe81TccOd9uygK/nxkVmXd/IBIpOw6KckeeTVvDuKdrriuZWbP2erMfcKrFa0SbRq8EgFrfxlHssjoEJI+A/zXT3V5dhW7O3RgvUdfSuJMFwzHQSo/BDkt7zyHrv6Vp2nEY5lFutwVeMHUIXLgf9m5E8+RroxvVimr9JvgmdMEeTspOf2qUs6SW0kN80Wlhg436efn61iSTxJpKSSzMuQMnbf+fzaqpbm3W0VQMFc4ZjsfSqejGjmby0nteJaEbUWY4ZeVd7wGWG3s0immVpwMu3r764+8mLzhoVJ0PqMnjR0N/G2MlAw2CyCptDWdjrnlIWKaHzAzkb+FQ0XwVguh2HIsuCPhsf0rDHEIsszQHJG5RsE+h6CjLOa1mKQlrmN1HdZhqBz4+XpU2ajoIZbwqvavpyNyACD58/0oHiKHti6zx6wOvdz6ZpRMY1UfSS+BgMx1D3/v50LxVw4GmJXbONMkmn4Nj57Vn4NBZtaSfXRyHI2Zh3fXNaHDYwzr3kc+S4P6VnQrOHxGhx9rSGww93X3V0vDYsosjKM9TjBrYR9MG6RoR7RgUjSqJauziOcWaVRyKVZYHnXFCUgZ1Y5i3TyrGnLRqkqMVLuMqOXOlSrzY9Ol8GgxcXccMgGHIUsNjjIqyKJXv722GVitoXkAXYyEHbUeZHpimpVfGSkKDiE99ZIkulIyQuiMaRjOKtuHNpKba2+rQMgOOZ1ask/CnpVR9YqJrIxi3P3iPcDUWgSWTv5OOW/KlSqY5rW1vF2JUIBpIGepyKEvrGDLd05BwDTUqdgBw2yLMAGfAJ61uW8jQiER7YdR7jSpUgyNKE67+FMaVuEjZgOhbmRVkMCTQmSTJITIGdvT0pUqx9NQVw2FBLCoGAwz6HyreUAA4FKlV8S0SmRJqJNKlVWIV0qVKlNP/Z'
        result.append(
            {
                'id':i,
                'ticket':[ticket for ticket in winner.tickets if ticket.is_winner][0].number,
                'name':winner.fullname,
                'image_url': image_url
            }
        )

    # print('res', result)

    return result




    


async def get_json_user(userId, event_id):
    user = await req.get_user(user_id=userId)


    return {
        "id": user.user_id,
        "referralLink": f"{config.BOT_URL}?start={userId}-{event_id}", # t.me/<bot_username>?start=<parameter>
        "tickets": await _get_tickets(user=user)
        }




async def get_json_event_channels(eventId):
    event = await req.get_event(eventId)

    channels_event = event.channels

    channels = []

    for channel in channels_event:
        channels.append(
            {
                "id": channel.id,
                "name": channel.name,
                "url": channel.url,
                "isSubscribed": False # here will be another function
            }
        )

    return {
        "data": channels
        }





