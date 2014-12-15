from PIL import Image
import numpy as np
import re, requests
import StringIO

class HeartFinder(object):
	def __init__(self, mask_location):
		"""Creates an object to detect heart shaped Twitter avatars (#gamergate)"""

		self.mask_location = mask_location

		self.mask = Image.open("mask.png")
		self.mask = np.asarray(self.mask, dtype=np.uint8)

		# Work in grayscale if we get a colour mask
		if len(self.mask.shape) == 3:
			self.mask = np.mean(self.mask, axis = 2)

	def is_heart(self, image):
		"""Looks for a heart shaped avatar in the numpy formatted image"""
		
		# Work in grayscale if we get colour images
		if len(image.shape) == 3:
			image = np.mean(image, axis = 2)

		# See if there are any pixels that aren't black after applying the mask.
		return (self.mask * (255 - image)).any()

	def is_heart_user(self, user_dict):
		"""Reads a standard Twitter user JSON structure and determines if the user
			appears to be a heart user"""
		# Figure out what image to fetch.
		image_url = self._bigger_image(user_dict["profile_image_url"])

		# Download the image
		image_handle = requests.get(image_url, stream=True)

		# And load it
		# Use a StringIO because PIL needs to seek()
		file_buffer = StringIO.StringIO(image_handle.content)

		image = Image.open(file_buffer)
		image = np.asarray(image, dtype=np.uint8)

		return self.is_heart(image)

	def _bigger_image(self, url):
		"""Modifies the image url for a user's display picture to ask for the 73px size"""	
		# Replace the bit before .png with "_bigger"
		return re.sub(r"_(normal|bigger|mini)?\.(\w+)$", r"_bigger.\2", url)

if __name__ == "__main__":
	"""Implement script behaviour to take a username, get profile from API and tell if 
	   they have one of the hearts as their avatar"""
	import twitterwrapper as tw
	import sys

	api = tw.Api()

	# Get the Twitter user from the API
	user = api.users.show(screen_name=sys.argv[1]).to_dict()

	# Load the heart finder
	heart_finder = HeartFinder("mask.png")

	# See if they have the heart of a 'gator
	is_gator = heart_finder.is_heart_user(user)

	if is_gator:
		print "not_gator"
	else:
		print "gator"