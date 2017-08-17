#!/usr/bin/env python
import webbrowser

from PIL import Image
from random import randint
from time import gmtime, strftime
import praw
import credentials_imgur
import credentials_reddit
import config
import pyimgur


def main():
    cheaplog("Starting new run")
    upvote_diff = get_upvote_diff()
    if upvote_diff > 0:
        add_random_pixels(upvote_diff)
    upload_to_imgur()


def get_upvote_diff():
    old_upvotes = read_old_upvotes()
    current_upvotes = read_current_upvotes()
    save_current_upvotes(current_upvotes)
    cheaplog("Upvote difference: " + str(current_upvotes-old_upvotes))
    return current_upvotes - old_upvotes


def read_old_upvotes():
    with open(config.UPVOTE_FILE, "r") as up_file:
        return int(up_file.readline())


def read_current_upvotes():
    reddit = praw.Reddit(client_id=credentials_reddit.app_id, client_secret=credentials_reddit.app_secret, user_agent='meirl')
    submission = reddit.submission(id=config.SUBMISSION_ID)
    cheaplog("Post has " + str(submission.score) + " upvotes")
    return submission.score


def save_current_upvotes(current_upvotes):
    with open(config.UPVOTE_FILE, "w") as up_file:
        up_file.write(str(current_upvotes))
    cheaplog("Saved " + str(current_upvotes) + " to file")


def add_random_pixels(pixel_count):
    cheaplog("Adding " + str(pixel_count) + " new pixels")
    im = Image.open(config.MEIRL_FILE)
    pixel_map = im.load()

    for i in range(0, pixel_count):
        random_r = randint(0, 255)
        random_g = randint(0, 255)
        random_b = randint(0, 255)
        random_x = randint(0, 149)
        random_y = randint(0, 149)
        pixel_map[random_x, random_y] = (random_r, random_g, random_b)

    im.save(config.MEIRL_FILE)


def upload_to_imgur():
    try:
        imgur = pyimgur.Imgur(credentials_imgur.client_id, credentials_imgur.client_secret, access_token="7db4b613ce63cc776e63f07ebbb8d0208dae6dd3", refresh_token="3e07fb00c94c952054a4a8492d59fc20ee790157")

        #imgur.refresh_access_token()
        #imgur.refresh_token()
        #auth_url = imgur.authorization_url('code')
        #webbrowser.open(auth_url)
        #pin = input('PIN?')
        #imgur.exchange_pin(pin)
        #album = imgur.create_album('ME_IRL')
        #print(album.id)

        #access_token, refresh_token = imgur.exchange_code('7be21cd320d5426dd3b8e15f22a0e293906888d7')

        #print(access_token)
        #print(refresh_token)

        imgur.refresh_access_token()

        album = imgur.get_album(config.IMGUR_GALLERY)

        album.remove_images(album.images)

        for img in album.images:
            img.delete()

        current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        img = imgur.upload_image(config.MEIRL_FILE, album=config.IMGUR_GALLERY, description='Uploaded by me_irl script - ' + current_time)
        cheaplog("Uploaded image to imgur: " + img.link)
    except Exception as e:
        cheaplog("Error in imgur function")
        cheaplog(e)
    return


def cheaplog(message):
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    message_formatted = "[" + current_time + "] " + message + "\n"
    with open(config.LOG_FILE, "a") as log:
        log.write(message_formatted)

if __name__ == "__main__":
    main()
