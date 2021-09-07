from PIL import Image
from io import BytesIO

def generate_gif(im1, im2):
    im1 = im1.resize((round(im1.size[0]*1), round(im1.size[1]*1)))
    im2 = im2.resize((round(im1.size[0]), round(im1.size[1])))

    images = []
    frames = 10

    for i in range(frames+1):
        im = Image.blend(im1, im2, i/frames)
        images.append(im)
        
    for i in range(frames+1):
        im = Image.blend(im1, im2, 1-i/frames)
        images.append(im)


    bio = BytesIO()
    bio.name = 'image.gif'

    images[0].save(bio, 'GIF', save_all=True, append_images=images[1:], duration=150, loop=0, optimize=True)
    bio.seek(0)
    return bio

def overlay_images(background, foreground):
    foreground = foreground.resize((round(background.size[0]), round(background.size[1])))
    background.paste(foreground, (0, 0), foreground)
    bio = BytesIO()
    bio.name = 'image.png'
    background.save(bio, 'PNG')
    bio.seek(0)
    return bio

from functools import wraps
import os
import mongoengine
from telegram.constants import MAX_MESSAGE_LENGTH
from actions.generalActions import User

interaction_dbname = "reiherbot_interaction"
with open("ca-certificate.crt", "w") as text_file:
    text_file.write(os.getenv('DATABASE_CERT'))
mongoengine.connect(alias=interaction_dbname, host="mongodb+srv://" + os.getenv("DATABASE_USERNAME")+":" + os.getenv("DATABASE_PASSWORD") +
                    "@" + os.getenv("DATABASE_HOST") + "/"+interaction_dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")

class Interaction(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    update_id = mongoengine.IntField()
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    username = mongoengine.StringField(max_length=50)
    message = mongoengine.DictField()
    message_text = mongoengine.StringField(max_length=MAX_MESSAGE_LENGTH)
    message_id = mongoengine.IntField()
    date = mongoengine.DateTimeField()
    meta = {'db_alias': interaction_dbname}

def log(logger):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            if update.effective_message.text:
                message_text = update.effective_message.text
            else:
                message_text=None

            Interaction(user=context.user_data["user_id"],
                        update_id=update.update_id,
                        message=update.effective_message.to_dict(),
                        first_name=update.effective_user.first_name,
                        last_name=update.effective_user.last_name,
                        username=update.effective_user.username,
                        message_text=message_text,
                        date=update.effective_message.date,
                        message_id = update.effective_message.message_id
                        ).save()
            
            logger.info(update)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator