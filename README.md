# NAPS2 Assistant

This is a GUI python application that piggy-backs off of [NAPS2](https://www.naps2.com/), a popular printer scanner utility, to scan and crop images.

## Setup

Install [NAPS2](https://www.naps2.com/) and follow instructions to set up a profile for your local printer/scanner.

> This is a requirement before running NAPS2 Assistant!
> This app has been tested with NAPS v7.5.3

## Usage

Once you've set up NAPS2 and you are connected to a printer/scanner you're ready For NAPS2 Assistant! To run, opening a console in the root directory of this repository and run `python app.py`. NAPS2 Assistant will look like this:

![](img/app_v2.png)

Set an output directory for the scanned images using the folder icon button, or hit the "Scan" button, and you'll be prompted to enter one.

> You must set a valid output directory before trying to scan images

If you haven't hit the "Scan" button yet, do that. If you've set up NAPS2 and are connected to your printer, you should see a scan progress bar like this:

![](img/app_scanning_v2.png)

> If you do not have NAPS2 set up, you will get a bunch of gobbledygook output in the log window, with the error somewhere in that text. Try exiting, fixing your NAPS2 setup, and rerunning the application.

Your log window should look like this on successful completion of a scan:

![](img/app_scan_done_v2.png)

The original scan will be saved under the filename listed in the console. There will be an additional 1 or more images saved under the same filename with the postfix "cropped_#" depending on how many pictures you scanned in.

# Example Results

Here is an example of the type of images I was cropping, they were some old slides from my grandparents'. If your scanner/images have a different shade of white background, you may need to adjust the `_fuzzy_white_value` variable at the top of `app.py` until you get a desired crop. The `_fuzzy_noise_value` can also be adjusted to account for very small images.

## Single Picture

### Image After NAPS2 Scan
![](img/scan_raw.jpg)

### Image After Cropping
![](img/scan_cropped.jpg)

Aren't I cute?

## Multiple Pictures
> Note, no individual picture rotation adjustments are done for mulitiple images! I might add this at a later time, but just try to put the pictures in relatively square before scanning to get better crops.

### Image After NAPS2 Scan
![](img/scan_raw_multi.jpg)

### Image After Cropping
![](img/scan_multi_cropped_1.jpg)
![](img/scan_multi_cropped_2.jpg)
![](img/scan_multi_cropped_3.jpg)
![](img/scan_multi_cropped_4.jpg)
