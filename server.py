import quart, quart_cors
import asyncio

from database.models import User
import server_utils



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


@app.route('/getEvent/<eventId>', methods=["POST"])
async def get_event(eventId):
    
    eventId = int(eventId)

    return await server_utils.get_json_event_time(eventId)




@app.route('/addTicket/<UserId>-<eventId>')
async def add_ticket(userId, eventId):
    pass




@app.route('/check-subscriptions/<userID>', methods=["POST"])
async def check_sub(userID):
    return {
        "allSubscribed": True,
        "details": []
    }

    
    # return {
    # "allSubscribed": False,
    # "details": [
    #     {
    #     "channelId": "channel_123",s
    #     "channelName": "channel_123",
    #     "isSubscribed": False
    #     },
    #     {
    #     "channelId": "channel_456",
    #     "channelName": "channel_456",
    #     "isSubscribed": True
    #     }
    # ]
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

