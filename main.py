import base64
import pymongo
import tweetnlp

from collections import Counter
from send_email import email_sender


# Import the genre, emotion and name models
topic_classification_model = tweetnlp.load_model('topic_classification', multi_label=False)
emotion_classification_model = tweetnlp.load_model('emotion')
ner_model = tweetnlp.load_model('ner')
sentiment_model = tweetnlp.load_model('sentiment')



def hello_pubsub(request, context=None):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        context (google.cloud.functions.Context, optional): The context object.
        <other parameters>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <optional return>
    """

    # MongoDB Atlas connection settings
    mongodb_uri = 'mongodb+srv://allenjade154:G6KhXePPeYQtPQ9g@cluster0.8jxxf5k.mongodb.net/?retryWrites=true&w=majority'
    database_name = 'test'
    collection_name = 'entries'

    # Connect to MongoDB Atlas
    client = pymongo.MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]

    # Query documents from MongoDB collection and convert to list
    documents = list(collection.find())

    # Create a dictionary to map emails to indices of objects
    email_to_indices = {}

    #map each user email to their document indiices in the list: documents
    for idx, doc in enumerate(documents):
        # Check if the document has the 'email' attribute
        if 'email' in doc:
            email = doc['email']
            # Map email to the index of the object
            if email not in email_to_indices:
                email_to_indices[email] = []
            email_to_indices[email].append(idx)

    #compile classifications of journal entries per user
    email_to_reports = {}
    for email, doc_indices in email_to_indices.items():
        reports = {}
        topics = []
        emotions = []
        sentiments = []
        entities = []
        for doc_index in doc_indices:


            document = documents[doc_index]['text_content']
            topic_result = topic_classification_model.topic(document)['label']
            topics.append(topic_result)
            emotion_result = emotion_classification_model.emotion(document)['label']
            emotions.append(emotion_result)
            sentiment_result = sentiment_model.sentiment(document)
            sentiments.append(sentiment_result['label'])
            ner_result = ner_model.ner(document,return_probability=True)
            for entity in ner_result:
                #im pretty sure its legit lol
                if (entity['probability']) > 0.5:
                    entities.append(entity['entity'])

        reports = {'topics':topics,'emotions':emotions,'sentiments':sentiments,'entities':entities}
        # Map email to the reports
        email_to_reports[email] = reports

    
    #get top 5's
    for email,classification in email_to_reports.items():
        topic_counter = Counter(classification['topics'])
        topic_top_5 = topic_counter.most_common(5)
        emotion_counter = Counter(classification['emotions'])
        emotion_top_5 = emotion_counter.most_common(5)
        sentiment_counter = Counter(classification['sentiments'])
        sentiment_top_5 = sentiment_counter.most_common(5)
        entity_counter = Counter(classification['entities'])
        entity_top_5 = entity_counter.most_common(5)
        
        summaries = {'topics_top5': topic_top_5, 'emotion_top5': emotion_top_5,'sentiment_top5': sentiment_top_5,'entity_top5': entity_top_5}
        email_to_reports[email] = summaries
    
    #send out emails
    for email,top5s in email_to_reports.items():
        email_sender(email,top5s)

    # Prepare the response body
    response_body = {
        'email_to_reports': email_to_reports
    }

    print(response_body)
    return 'OK', 200
