# ztffps

Provides a Forced Photometry Pipeline based on [ztfquery](https://github.com/mickaelrigault/ztfquery) and [ztflc](https://github.com/mickaelrigault/ztfquery), needs [IPAC](https://irsa.ipac.caltech.edu/account/signon/login.do?josso_back_to=https://irsa.ipac.caltech.edu/frontpage/&ts=517) as well as [Marshal](http://skipper.caltech.edu:8080/cgi-bin/growth/marshal.cgi) or [AMPEL](https://github.com/ampelproject) access.

Note: Requires Python >= 3.6.

## Installation

All required packages should be installed by issuing:

```pip3 install -r requirements.txt```

Note that libpq-dev needs to be present. On Debian/Ubuntu, issue ```sudo apt install libpq-dev```

### Troubleshooting
Make sure that ztfquery and ztflc are installed with the latest version.

In case way too few images are downloaded, check your Marshal and IRSA credentials. These are stored in ```~.ztfquery```. If there is a problem with these, ztfquery will not complain but simply only download publicly accessable images.

In this case also make sure to delete the database-file, otherwise no new downloads will be attempted. The file is located at ```ZTFDATA/forcephotometry/meta/meta_database.json```.

## Usage

The basic file is pipeline.py, which can be run using different flags. Alternatively, the pipeline class can be imported from this file.

### By command

Always:

`[name]` A ZTF name has to be provided, or an ASCII file containing one ZTF name in each line or an arbitrary name if followed by the ra/dec-option as to be provided.

optionally:

`-radec [RA DEC]`	If this is given, the name can be chosen arbitrarily (but a name MUST be provided). Radec must be given in a format that can be parsed by astropy; e.g. `-radec 218.487548 +40.243758`.

#### Additional commands

`-dl`        Downloads the images used for forced photometry from [IPAC](https://irsa.ipac.caltech.edu/account/signon/login.do?josso_back_to=https://irsa.ipac.caltech.edu/frontpage/&ts=517). Needs a valid IPAC account.

`-fit`       Performs the PSF-photometry fit and generates plots of the lightcurve(s).

`-plot`     Plots the lightcurve(s).

`-saltfit`   Fits the lightcurve using SALT2 as provided by [sncosmo](https://github.com/sncosmo/).

`-sciimg`  Experimental: Also downloads the science images from IPAC (note: to create thumbnails if specified)

`-thumbnails` Experimental: Generates thumbnails for all science-images. Science images have to be downloaded (see `-sciimg`)

#### Options

`--nprocess [int]`  Specifies the number of processes spawned for parallel computing. Default is 4. Note: download is always performed with 32 processes in parallel, as IPAC upload-speed is the bottleneck there.

`--daysago [int]`  Determines how old the photometric data should be. Default uses all datapoints available.

`--daysuntil [int]`  Determines how new the photometric data should be. Default uses all datapoints available.

`--snt [float]` Specifies the signal-to-noise ratio for plotting and SALT-fitting.

`--magrange [float float]` Defines upper and lower magnitude bound for plotting the lightcurves. Order is irrelevant.

#### Examples

`./pipeline.py ZTF19abimkwn -dl -fit -saltfit --nprocess 16` downloads all images for ZTF18abtmbaz found on IPAC, performs PSF-fitting, plots a lightcurve and fits the lightcurve with a SALT2 template with 16 processes in parallel.

`./pipeline.py supernovae.txt -dl` Downloads all difference images for ZTF transients found in supernovae.txt. Note: Downloading the images usually takes a considerable amount of time.

`./pipeline.py this_looks_interesting -radec 143.3123 66.42342 -dl -fit -plot --daysago 10 -magrange 18 20` Downloads all images of the last ten days of the location given in ra and dec, performs PSF-fits and plots the lightcurve in the 18--20 magnitude range.

### By importing class
All functionality of the command-line tool is present in the class. Just call it according to the commands available in the pipeline.py file.

## Requirements
- [ztfquery](https://github.com/mickaelrigault/ztfquery) is used to download the image files from IPAC.
- [ztflc](https://github.com/mickaelrigault/ztflc) is used for PSF-fitting.
- [Marshal](http://skipper.caltech.edu:8080/cgi-bin/growth/marshal.cgi) or [AMPEL](https://github.com/ampelproject) credentials are neccessary for the pipeline to work.

## Notes
### Slackbot
There is a bot for Slack included, based on the SlackRTM-API.
You have to create a classic Slack app for this, because the newer version depends on the Events API, which itself seems to need a web server to run.
Classic slack Apps can be created [here](https://api.slack.com/apps?new_classic_app=1). Make sure not to convert to the new permission/privilege system in the process (Slack tries to push you towards it, be careful).
After successfully setting up the App/bot and giving it permissions, change the bot-username to the one of your bot in start_slackbot.py and it should basically work (first start requires you to enter the bot- and bot-user credentials, also provided by Slack).

### Saltfit module
Still experimental! Performs saltfits on the generated lightcurves.
