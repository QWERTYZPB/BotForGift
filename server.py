import quart, quart_cors
import asyncio

from database import req

import server_utils

from config import bot


app = quart.Quart(__name__)
quart_cors.cors(app, allow_origin=['*', 'civerandom.ru'])

APP_PREFIX='/api'


@app.route(APP_PREFIX+'/test')
async def get_test_message():
    return {"ok": True}


@app.route(APP_PREFIX+'/channels/<userId>')
async def get_channels(userId):

    userId = int(userId)
    
    return await server_utils.get_json_event_channels(userId)


@app.route(APP_PREFIX+'/UpdateUser', methods=["POST"])
async def updateUserData():

    data = await quart.request.get_json()


    required_fields = {'username', 'user_id'}
    if not required_fields.issubset(data):
        return quart.jsonify({"error": "Missing required fields"}), 400

    username = data['username']
    fullname = data['fullname']
    user_id = data['user_id']

    try:
        await req.add_user(
            user_id=int(user_id),
            username=username,
            fullname=fullname
        )
    except:
        await req.update_user(
            user_id=int(user_id),
            username=username,
            fullname=fullname
        )



    return quart.jsonify({"ok": True}), 200




@app.route(APP_PREFIX+'/users/<userId>-<eventId>')
async def get_user(userId, eventId):

    userId, eventId = int(userId), int(eventId)

    return await server_utils.get_json_user(userId, eventId)


@app.route(APP_PREFIX+'/tickets/<userId>-<eventId>')
async def get_tickets(userId, eventId):
    
    userId = int(userId)
    eventId = int(eventId)

    return await server_utils.get_json_user_tickets(userId, eventId)


@app.route(APP_PREFIX+'/getEvent/<eventId>', methods=["GET"])
async def get_event(eventId):
    
    eventId = int(eventId)

    return await server_utils.get_json_event_time(eventId)




@app.route(APP_PREFIX+'/getWinners/<eventId>', methods=["GET"])
async def get_winners(eventId):
    
    eventId = int(eventId)
    data = await server_utils.get_json_event_winners(eventId)
    print(data)
    try:
        return {'ok':True, 'result': data}
    except:
        return {'ok': False}




# @app.route(APP_PREFIX+'/addTicket/<UserId>-<eventId>')
# async def create_new_ticket(userId, eventId):
    
#     user = await req.get_user(int(userId))
#     event = await req.get_event(int(eventId))


#     if user and eventId:
#         await req.generate_ticket_number(event.id, user.user_id)

#         return {'ok': True}
    
#     return {'ok': False}





@app.route(APP_PREFIX+'/check-subscriptions/<userID>-<EventId>', methods=["POST"])
async def check_sub(userID, EventId):
    # print(EventId)
    
    event = await req.get_event(event_id=int(EventId))
    user = await req.get_user(int(userID))


    channels = [await req.get_channel(int(i)) for i in event.channel_event_ids.split(',') if i!='']

    
    
    result = await server_utils.get_json_subscriptions(bot, int(userID), channels)

    users_in_event = event.user_event_ids.split(',') if event.user_event_ids else []


    if await server_utils.user_tickets_not_in_event(user, event)\
          and result['allSubscribed'] \
            and (userID not in users_in_event): 

        
        if event.user_event_ids:
            await req.update_event(
                event_id=event.id,
                user_event_ids=event.user_event_ids + ',' + str(userID)
            )
        else:
            await req.update_event(
                event_id=event.id,
                user_event_ids=str(userID)
            )
        
        ticket = await req.generate_ticket_number(event.id, user.user_id)
        
        # print(ticket)

        if not event.tickets_event:
            event.tickets_event = ''
        
        if not user.tickets_ids:
            user.tickets_ids = ''

        await req.update_event(
            event_id=int(EventId),
            tickets_event=event.tickets_event+str(ticket.id)+','
        )

        await req.update_user(
            user_id=user.user_id, 
            tickets_ids=user.tickets_ids+str(ticket.id)+','
            )

    return result

    # return {
    #     "allSubscribed": False,
    #     "details": [
    #         {
    #         "channelId": "channel_123",
    #         "channelName": "channel_123",
    #         "isSubscribed": False
    #         },
    #         # {
    #         # "channelId": "channel_456",
    #         # "channelName": "channel_456",
    #         # "isSubscribed": True
    #         # }
    #     ]
    # }



# @app.route('/<path:requested_path>')
# async def serve_CssAndJs(requested_path):

#     file_path = os.path.join(requested_path)

#     try:
#         return await send_file(file_path, cache_timeout=0 and result)
#     except FileNotFoundError:
#         return Response(status=404, response="File not found")
#     except Exception:
#         return Response(status=500, response="Internal Server Error")


async def run_server():
    await app.run_task(port=3001, debug=True)
  
if __name__ == '__main__':
    asyncio.run(run_server())

