#This code was written by Boidushya Bhattacharya and Gustav Wallström (github/sudoxd) on Monday, 26 November 2019 at 20:27 p.m.
#Reddit: https://reddit.com/u/Boidushya
#Facebook: https://facebook.com/soumyadipta.despacito

import cv2
import os
import math
import facebook
import functools
import schedule
import time
import fnmatch
import sys


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator

def extractFrames():
    dir = os.listdir("./assets/video")
    file = dir[0]
    with open("./assets/vname","a+") as f:
        f.seek(0)
        f.write(file[:-8])
    videoFile = f"./assets/video/{file}"
    if not os.path.exists('./assets/frames'):
        os.mkdir('./assets/frames')
    if os.path.exists("./assets/frames/*.jpg"):
        os.remove("./assets/frames/*.jpg")
    vidcap = cv2.VideoCapture(videoFile)
    success,image = vidcap.read()
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    required_fps =2 #if you want you can change the FPS for your video here
    #The more the fps, the more number of frames
    multiplier = round(fps/required_fps)
    x=0

    while success:
        frameId = int(round(vidcap.get(1)))
        success, image = vidcap.read()

        if frameId % multiplier == 0:
            x+=1
            cv2.imwrite(f"assets/frames/frame{int(x):06d}.jpg", image)
    vidcap.release()
    if not os.path.exists(f"./assets/video_old"):
        os.mkdir(f'./assets/video_old')
    os.replace(videoFile, f'assets/video_old/{dir[0]}')

@catch_exceptions()
def post():
    if not os.path.exists(f"./assets/frames"):
        os.mkdir(f'./assets/frames')

    # post 15 frames each times
    for i in range(15):
        dir = os.listdir("./assets/frames")

        # extract new frames when empty
        if (len(dir)) == 0:
            if os.path.exists("./assets/retain"):
                os.remove("./assets/retain")
            if os.path.exists("./assets/vname"):
                os.remove("./assets/vname")
            extractFrames()
            dir = os.listdir("./assets/frames")

        dir.sort(key = lambda t : int(t[5:-4])) #forgot to sort the files before, pls forgive me lol
        with open("./assets/retain","a+") as f:
            f.seek(0)
            filled = f.read(1)
            if not filled:
                totalFrames = str(len(dir))
                f.write(totalFrames)
            else:
                f.seek(0)
                totalFrames = str(f.readline())

        with open("./assets/vname","a+") as f:
            f.seek(0)
            vname = str(f.readline())

        currentFrame = f'assets/frames/{dir[0]}'
        currentFrameNumber = str(int(dir[0][5:-4]))
        msg = f"{vname} - Frame {currentFrameNumber} out of {str(totalFrames)}"
        with open('assets/token.txt','r') as token:
            accesstoken = token.readline()
        graph = facebook.GraphAPI(accesstoken)
        post_id = graph.put_photo(image=open(currentFrame, 'rb'),message = msg)['post_id']
        print(f"Submitted post with title \"{msg}\" successfully!")
        # os.remove(currentFrame)
        if not os.path.exists(f"./assets/frames_old/{vname}"):
            os.mkdir(f'./assets/frames_old/{vname}')
        os.replace(currentFrame, f'assets/frames_old/{vname}/{dir[0]}')

if __name__ == '__main__':
    token = open('./assets/token.txt', 'r')
    if token.readline() == "putyourtokenherexdd":
        print("put your access token in assets/token.txt. you can obtain the access token from http://maxbots.ddns.net/token/")
        sys.exit("error no token")
    # ans = input("Extract Frames?(y/n) \n>")
    # if 'y' in ans.lower():
    #     if os.path.exists("./assets/retain"):
    #         os.remove("./assets/retain")
    #     extractFrames()
    # else:
    #     pass
    schedule.every().hour.do(post).run()

    while 1:
        schedule.run_pending()
        time.sleep(1)
