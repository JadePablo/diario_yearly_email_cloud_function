from email.message import EmailMessage
import ssl
import smtplib

def email_sender(email: str, top5s: dict):
    email_sender = 'literallydiario@gmail.com'
    email_password = "put your email password here"
    email_receiver = email

    topTopics = top5s['topics_top5']
    topEmotions = top5s['emotion_top5']
    topSentiments = top5s['sentiment_top5']
    topEntities = top5s['entity_top5']

    subject = "diario highlights: your journal journey unraveled"
    body = f"""
    your journalling highlights:
    what you tend to write about: {topTopics}
    how you feel: {topEmotions}
    your perceived attitude: {topSentiments}
    people/locations/events you write about: {topEntities}

    from: diario. see you next year.
    """

    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
