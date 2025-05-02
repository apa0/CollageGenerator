#1. Need to load in data from JSON file
#4. Has algorithm to match recent track details to 6 photos from wiki art (this is the collage)
#5. Has a function to return the collage to the Controller, which then passes it to the view...
#                                                   (which we dont have right now but thats fine)


# Update: Now that we know exactly what user data we are working with, we can clear up our approach to making matches

    # 1. Since our artwork dataset is set to expand, we want to narrow down our artwork pool first,
    # 2. We will do this by either genre to style tagging, or dominant color (if no genre)
                # For dominant color grouping, we can just round our RGB values to have a bit of a looser grouping and more possibility
    # 3. Once we have narrowed this down, we can use the top three colors in the pallete to give us the closest match
    # 4. Can later integrate better algorithms like KD-Trees or ANN (approximate nearest neighbors)


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