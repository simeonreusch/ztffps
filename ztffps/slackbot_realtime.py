#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de); part of this code is by Robert Stein (robert.stein@desy.de)
# License: BSD-3-Clause

import os, io
from slack import RTMClient, WebClient
from ztflc.io import LOCALDATA
from pipeline import is_ztf_string
from slackbot import bot_token, user_token


# botuser = "UTF38HMFZ"
botuser = "UT462HHRR"
keywords = [f"<@{botuser}>", "FP"]

def run_on_event(data):
	ts = data['ts']
	channel = data['channel']
	sid = int(float(ts) * 1.e6)
	# cmd = "bash {0} {1} {2} {3}".format(submit_file, sid, ts, channel)
	cmd = f"bash slackbot_spawn_screen_session.sh {channel} {ts}"
	print(cmd)
	os.system(cmd)


@RTMClient.run_on(event="message")
def say_hello(**payload):
	data = payload['data']
	wc = payload['web_client']

	if 'text' in data.keys():
		slacktext = data['text']
		split_message = slacktext.split(" ")
		if split_message[0] in keywords:
			channel_id = data['channel']
			thread_ts = data['ts']
			user = data['user']

			if len(split_message) == 1:


				blocks = 	[{"type": "section", "text": {"type": "mrkdwn", "text": f"Hi <@{user}>. This is a bot for forced photometry! Just type *@fpbot ZTFName* or *FP ZTFName*. This downloads images, fits them and plots the lightcurve. [Only giving a ZTF name as argument is equivalent to *FP ZTFName -download -fit -plot --snt 5*] \nIf you have no ZTFname, but a RA and DEC, please provide an arbitrary name, followed by '-radec [RA] [DEC]'\nOptional arguments:\n"},"fields": [
				{
					"type": "mrkdwn",
					"text": "*-download*: Only downloads the images from IPAC."
				},
				{
					"type": "mrkdwn",
					"text": "*-fit*: Assumes images have already been downloaded, performs PSF fit"
				},
				{
					"type": "mrkdwn",
					"text": "*-plot*: Only plots the lightcurve"
				},
				{
					"type": "mrkdwn",
					"text": "*--daysago*: Only data from [daysago] to now is considered. Default is start of ZTF operations (April 2018)"
				},
{
					"type": "mrkdwn",
					"text": "*--daysuntil*: Only data till [daysuntil] is considered. Default is today"
				},
								{
					"type": "mrkdwn",
					"text": "*--snt*: Signal to noise threshold. Default is 5.0"
				},
												{
					"type": "mrkdwn",
					"text": "*--magrange*: For plotting only; defines range of y-axis. Example: --magrange 17 20 to plot from 17 to 20 mag"
				}
			]}]

				wc.chat_postMessage(channel=channel_id, text=f"Hi <@{user}> This is a bot for forced photometry! Just type @fpbot ZTFName and it will download images from IPAC, perform a PSF fit and plot the lightcurve. Optional arguments\n-downnload: only plots the lightcurve\n-fit: only does the fit\n-plot: only plots the lightcurve\n--daysago: only data from [daysago] to now is considered; default is start of ZTF operations (April 2018)\n--daysuntil: only data till [daysuntil] is considered; default is today\n--snt: signal to noise threshold; default is 5.0\n--magrange: for plotting only; defines range of y-axis. Example: --magrange 17 20 to plot from 17 to 20 mag", blocks=blocks, thread_ts=thread_ts, icon_emoji=':fp-emoji:')
			
			else: 
				if is_ztf_string(split_message[1]):
					ztf_name = split_message[1]		
					blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"You requested forced photometry for *{ztf_name}*. I'll get right to it. Depending on whether the image files need to be downloaded, this can take a few minutes."}}]
					wc.chat_postMessage(channel=channel_id, text=f"You requested forced photometry for {ztf_name}", blocks=blocks, thread_ts=thread_ts, icon_emoji=':fp-emoji:')
					run_on_event(data)

				else:
					if len(split_message) < 3:
						wc.chat_postMessage(channel=channel_id, text=f"You either need to provide a ZTFName (ZTF[YEAR YEAR][7 LETTERS] or an arbitrary name followed by '-radec'", thread_ts=thread_ts, icon_emoji=':fp-emoji:')
					elif split_message[2] == "-radec" or split_message[2] == "--radec":
						name = split_message[1]
						blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"You requested forced photometry for *{name}* based on RA and DEC. I'll get right to it. Depending on whether the image files need to be downloaded, this can take a few minutes."}}]	
						wc.chat_postMessage(channel=channel_id, text=f"You requested forced photometry for *{name}* based on RA and DEC. I'll get right to it. Depending on whether the image files need to be downloaded, this can take a few minutes.", blocks=blocks, thread_ts=thread_ts, icon_emoji=':fp-emoji:')
						run_on_event(data)
					else:
						wc.chat_postMessage(channel=channel_id, text=f"You either need to provide a ZTFName (ZTF[YEAR YEAR][7 LETTERS] or an arbitrary name followed by '-radec'", thread_ts=thread_ts, icon_emoji=':fp-emoji:')

print("Starting realtime Slackbot for forced photometry")
rtm_client = RTMClient(token=bot_token)
rtm_client.start()