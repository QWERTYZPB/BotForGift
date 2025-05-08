import quart, quart_cors
import asyncio

from database import req

import server_utils

from config import bot


app = quart.Quart(__name__)
quart_cors.cors(app, allow_origin=['*'])




@app.route('/channels/<userId>')
async def get_channels(userId):

    userId = int(userId)
    
    return await server_utils.get_json_event_channels(userId)


@app.route('/users/<userId>-<eventId>')
async def get_user(userId, eventId):

    userId, eventId = int(userId), int(eventId)

    return await server_utils.get_json_user(userId, eventId)



@app.route('/tickets/<userId>')
async def get_tickets(userId):
    
    userId = int(userId)

    return await server_utils.get_json_user_tickets(userId)


@app.route('/getEvent/<eventId>', methods=["GET"])
async def get_event(eventId):
    
    eventId = int(eventId)

    return await server_utils.get_json_event_time(eventId)




@app.route('/getWinners/<eventId>', methods=["GET"])
async def get_winners(eventId):
    
    eventId = int(eventId)

    return await server_utils.get_json_event_winners(eventId)





@app.route('/addTicket/<UserId>-<eventId>')
async def create_new_ticket(userId, eventId):
    
    user = await req.get_user(int(userId))
    eventId = await req.get_event(int(eventId))

    # generate_ticket_number -> make func-n

    if user and eventId:
        await req.add_ticket(
            user_id=user.user_id,
            event_id=eventId,  # Добавляем event_id
            number = server_utils.generate_ticket_number()
        )

        return {'ok': True}
    
    return {'ok': False}





@app.route('/check-subscriptions/<userID>-<EventId>', methods=["POST"])
async def check_sub(userID, EventId):
    # print(EventId)
    
    event = await req.get_event(event_id=int(EventId))

    # print(event)

    
    
    result = await server_utils.get_json_subscriptions(bot, int(userID), event.channels)
    # print(result)

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
#         return await send_file(file_path, cache_timeout=0)
#     except FileNotFoundError:
#         return Response(status=404, response="File not found")
#     except Exception:
#         return Response(status=500, response="Internal Server Error")


async def run_server():
    await app.run_task(port=3001, debug=True)
  
if __name__ == '__main__':
    asyncio.run(run_server())

