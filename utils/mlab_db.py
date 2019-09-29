
import pymongo
from keys import *
from work_crawler import extract_composer_name

##################
# SAVE COMPOSERS #
##################

uri = f"mongodb://{mlab['username']}:{mlab['password']}@ds151076.mlab.com:51076/score-study-app"

def save_composer(composer_chart):
    # DB Setup
    client = pymongo.MongoClient(uri, retryWrites=False)
    db = client.get_default_database()

    composers = db['composers']

    # Preparing data for entry
    data = {
        '_id': extract_composer_name(composer_chart),
        'composer_url': composer_chart,
        'visited': False
    }

    try:
        composers.insert_one(data)
    except:
        # composers.update_one({"_id": data['_id']}, data)
        return



def get_composers():
    # DB Setup
    client = pymongo.MongoClient(uri)
    db = client.get_default_database()

    composers = db['composers']

    return list(composers.find({}))


if __name__ == '__main__':
    save_composer("https://imslp.org/index.php?title=Category:Mozart%2C%20Wolfgang%20Amadeus&customcat=ccperson1")
    save_composer("https://imslp.org/index.php?title=Category:Bach%2C%20Johann%20Sebastian&customcat=ccperson1")
    save_composer("https://imslp.org/index.php?title=Category:Beethoven%2C%20Ludwig%20van&customcat=ccperson1")
    
    print(get_composers())

