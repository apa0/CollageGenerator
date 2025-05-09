#1. Need to load in data from JSON file
#4. Has algorithm to match recent track details to 6 photos from wiki art (this is the collage)
#5. Has a function to return the collage to the Controller, which then passes it to the view...
#                                                   (which we dont have right now but thats fine)

import Model
from Model.user_data import SpotifyUser



# Update: Now that we know exactly what user data we are working with, we can clear up our approach to making matches

    # 1. Since our artwork dataset is set to expand, we want to narrow down our artwork pool first,
    # 2. We will do this by either genre to style tagging, or dominant color (if no genre)
                # For dominant color grouping, we can just round our RGB values to have a bit of a looser grouping and more possibility
    # 3. Once we have narrowed this down, we can use the top three colors in the pallete to give us the closest match
    # 4. Can later integrate better algorithms like KD-Trees or ANN (approximate nearest neighbors)


class CollageGenerator:

    # All we need to initialize is the collection for the collage, starting we will do 1 image per track (can expand later)
    def __init__(self, user_features, wikiart_data):
        self.user_features = user_features
        self.wikiart_data = wikiart_data


    #This is the main function that generates the collage
    # Still thinking: will call user_data to access the track data via a getter, or pass something into the function to avoid calls?
    # Here is where we will utilize the color buckets, then search thru that key value using pallate colors (later could add genre/style logic)
    # To generate the best match for the collage, once we have determine that for the track, we add that art work into the collection
    # We do this until we have taken care of all of the user tracks (maybe theres a more efficient way, what if later someone wants this for a playlist?)
    # still: a playlist doesnt mean we have to generate an image for each track, we could end up only taking in distinct color tracks and making same size collage
    # Again these are just train of thought comments to aid development
    def match_images(self):
        # algorithm to select 6 images




        return ["img1.jpg", "img2.jpg", ...]


# Maybe just make this data that the controller (app.py) can access and then print to the view via HTML
    def generate_collage(self):
        # generate final collage image
        return "collage.jpg"