#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de); part of this code is by Robert Stein (robert.stein@desy.de)
# License: BSD-3-Clause

import time, os, getpass
from slack import RTMClient, WebClient
import pipeline

bot_token_file = ".slack_bot_access_token.txt"
user_token_file = ".slack_access_token.txt"

ztfdata = os.getenv("ZTFDATA")
lc_dir = os.path.join(ztfdata, "forcephotometry")


try:
	with open(bot_token_file, "r") as f:
		bot_token = f.read()
except FileNotFoundError:
		bot_token = getpass.getpass(prompt='Slack Bot Access Token: ', stream=None)
with open(bot_token_file, "wb") as f:
	f.write(bot_token.encode())

try:
	with open(user_token_file, "r") as f:
		user_token = f.read()
except FileNotFoundError:
	user_token = getpass.getpass(prompt='Slack User Token: ', stream=None)
with open(user_token_file, "wb") as f:
	f.write(user_token.encode())


def run_on_event(thread_id, channel_id):

	wc = WebClient(token=bot_token)

	payload = wc.conversations_history(channel=channel_id, oldest=str(float(thread_id) - 1), latest=str(float(thread_id) + 1))

	data = payload["messages"][0]

	user = data['user']

	split_message = data['text'].split(" ")
	
	ztf_name = split_message[1]
	lc_path = os.path.join(lc_dir, "{}.csv".format(ztf_name))
	lc_plotdir = os.path.join(lc_dir, "plots")
	
	do_download = False
	do_fit = False
	do_plot = False
	daysago = None
	daysuntil = None
	snt = 5.0

	if "-plot" in split_message  or "--plot" in split_message:
		do_plot = True

	for i, parameter in enumerate(split_message):
		if parameter == '-snt' or parameter == '--snt' or parameter == '–snt':
			snt = float(split_message[i+1])

	for i, parameter in enumerate(split_message):
		if parameter == "-daysago" or parameter == "--daysago" or parameter == "—daysago":
			try:
				daysago = float(split_message[i+1])
			except ValueError:
				wc.chat_postMessage(channel=channel_id, text=f"Error: --daysago has to be an integer.", thread_ts=thread_id)
				return

	for i, parameter in enumerate(split_message):
		if parameter == "-daysuntil" or parameter == "--daysuntil" or parameter == "–daysuntil":
			try:
				daysuntil = float(split_message[i+1])
			except ValueError:
				wc.chat_postMessage(channel=channel_id, text=f"Error: --daysuntil has to be an integer.", thread_ts=thread_id)
				return

	if do_download == False and do_fit == False and do_plot == False:
		do_download = True
		do_plot = True
		do_fit = True

	try:
		pl = pipeline.ForcedPhotometryPipeline(file_or_name=ztf_name, daysago=daysago, daysuntil=daysuntil, snt=snt)
	except ValueError:
		wc.chat_postMessage(channel=channel_id, text=f"The Marshal is not reachable at the moment. Unfortunately, this happens quite frequently.", thread_ts=thread_id)
		return

	if do_download:
		try:
			wc.chat_postMessage(channel=channel_id, text=f"Checking if all files are present and downloading missing ones. This can take a few minutes.", thread_ts=thread_id)
			pl.download()
		except:
			wc.chat_postMessage(channel=channel_id, text=f"Sorry, I have run into a problem while downloading the image files.", thread_ts=thread_id)

	if do_fit:
		try:
			wc.chat_postMessage(channel=channel_id, text=f"Fitting PSF. This can take a moment.", thread_ts=thread_id)
			pl.psffit()
		except:
			wc.chat_postMessage(channel=channel_id, text=f"Sorry, I have run into a problem while performing the PSF fits.", thread_ts=thread_id)

	if do_plot:
		try:
			wc.chat_postMessage(channel=channel_id, text=f"Plotting lightcurve.", thread_ts=thread_id)
			pl.plot()
			imgpath = os.path.join(lc_plotdir, f"{ztf_name}_SNT_{snt}.png")
			imgdata = open(imgpath, "rb")
			wc.files_upload(file=imgdata, filename=imgpath, channels=channel_id, thread_ts =thread_id, text="And here is your lightcurve.")
		except:
			wc.chat_postMessage(channel=channel_id, text=f"Sorry, I have run into a problem while plotting the lightcurve.", thread_ts=thread_id)

	endtime = time.time()
	duration = endtime - pl.startime

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-channel', '--channel', type=str, help='Slack Channel ID')
	parser.add_argument('-thread', '--thread', type=str, help='Slack Thread ID')

	commandline_args = parser.parse_args()
	channel_id = commandline_args.channel
	thread_id = commandline_args.thread

	run_on_event(thread_id=thread_id, channel_id=channel_id)