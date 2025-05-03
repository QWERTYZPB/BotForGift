from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

import re, datetime, asyncio, json



# not in use
def create_media_group_with_caption(list_media_id: list[str], caption: str):
    '''
    list_media: ["p!123-abcd", "v!321-abcd"]
    '''
    use_caption = True
    
    media_builder = MediaGroupBuilder()
    for media in list_media_id:
        media_type, file_id = media.split('!')
        
        if media_type == 'p':
            if use_caption:
                media_builder.add_photo(media=file_id, caption=caption)
                use_caption=False
            else:
                media_builder.add_photo(media=file_id)
            
        

        elif media_type == 'v':
            if use_caption:
                media_builder.add_video(media=file_id, caption=caption)
                use_caption=False
            else:        
                media_builder.add_video(media=file_id)


    return media_builder.build()

        
