#1. Need to load in data from JSON file
#4. Has algorithm to match recent track details to 6 photos from wiki art (this is the collage)
#5. Has a function to return the collage to the Controller, which then passes it to the view...
#                                                   (which we dont have right now but thats fine)

class CollageGenerator:
    def __init__(self, user_features, wikiart_data):
        self.user_features = user_features
        self.wikiart_data = wikiart_data

    def match_images(self):
        # algorithm to select 6 images
        return ["img1.jpg", "img2.jpg", ...]

    def generate_collage(self):
        # generate final collage image
        return "collage.jpg"