import requests
from bs4 import BeautifulSoup
import tensorflow as tf
import mysql.connector
import pandas as pd
import re
import json
import smtplib
from email.mime.text import MIMEText


def extract_data(urls):
    extracted_data = []
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        extracted_data.append(soup.get_text())
    return extracted_data


def process_data(text_data):
    # Load the T5 NLP model
    model = tf.saved_model.load("t5-base")
    # Define the text processing function
    text_processing_fn = model.signatures["text_processing_fn"]
    # Run the text processing function on the input data
    result = text_processing_fn(input=tf.constant(text_data))
    # Return the processed text data
    return result.get("outputs").numpy().tolist()


def clean_and_segment_data(processed_data):
    cleaned_data = []
    for data in processed_data:
        # Clean the data by removing unwanted characters and converting to lowercase
        data = re.sub(r'[^\w\s]', '', data)
        data = data.lower()

        # Segment the data into words
        words = data.split()

        cleaned_data.append(words)

    return cleaned_data


def store_data_in_db(mycursor, data):
    # Insert the data into the database
    for record in data:
        mycursor.execute(
            "INSERT INTO leads (name, county, quote) VALUES (%s, %s, %s)", record)
    # Close the connection to the database
    mycursor.close()


def generate_leads(mycursor, cleaned_data):
    # Cross-reference the data with another table to match names and counties
    for data in cleaned_data:
        query = "SELECT * FROM names_table WHERE name IN {}".format(
            tuple(data))
        mycursor.execute(query)
        result = mycursor.fetchall()

        if result:
            lead_data = {}
            lead_data['name'] = result[0][0]
            lead_data['county'] = result[0][1]

            # Store the lead data in the database
            store_lead_in_db(mycursor, lead_data)


def store_lead_in_db(mycursor, lead_data):
    query = "INSERT INTO leads_table (name, county) VALUES (%s, %s)"
    values = (lead_data['name'], lead_data['county'])
    mycursor.execute(query, values)


def send_email(recipient, subject, body, sender):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    smtp_server_config = load_config("./config/smtp_server_config.json")

    try:
        server = smtplib.SMTP(
            smtp_server_config['host'], smtp_server_config['port'])
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_daily_updates(recipient, leads_count, data_quote, sender):
    subject = "Daily Update: New Leads"
    body = f"There are {leads_count} new leads today. Data quote: {data_quote}"
    send_email(recipient, subject, body, sender)


def send_daily_newsletter(recipient, leads, news, sender):
    subject = "Daily Newsletter"
    leads_text = "\n".join(
        [f"Name: {lead['name']}, County: {lead['county']}" for lead in leads])
    body = f"New Leads:\n{leads_text}\n\nNews:\n{news}"
    send_email(recipient, subject, body, sender)


def integrate_data(data, crm_config):
    # Connect to the CRM platform using the specified API
    connection = requests.post(crm_config['url'], auth=(
        crm_config['username'], crm_config['password']), data=data)
    # Check the status code of the response to ensure a successful connection
    if connection.status_code == 200:
        return True
    else:
        return False


def get_recipients_from_crm(crm_config):
    # Connect to the CRM platform using the specified API
    connection = requests.get(
        crm_config['api_endpoint'], headers=crm_config['headers'])
    response = connection.json()

    # Retrieve the list of recipients from the CRM response
    recipients = [record['email'] for record in response['records']]

    return recipients


def get_data_quote_from_scraped_data(data):
    quotes = []
    for item in data:
        quote = {}
        quote["author"] = item.get("author")
        quote["text"] = item.get("text")
        quotes.append(quote)
    return quotes


def get_latest_news_from_scraped_data(urls):
    # Extract the raw data from the given URLs
    raw_data = extract_data(urls)

    # Process the raw data using the text processing function
    processed_data = process_data(raw_data)

    # Clean and segment the processed data
    cleaned_data = clean_and_segment_data(processed_data)

    # Find the latest news by searching for relevant keywords in the cleaned data
    keywords = ["news", "update", "breaking"]
    latest_news = []
    for data in cleaned_data:
        if any(keyword in data for keyword in keywords):
            latest_news.append(" ".join(data))

    return latest_news


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def load_urls_from_file(file_path):
    with open(file_path, "r") as file:
        urls = file.readlines()
    return urls


if __name__ == '__main__':
    db_config = load_config("./config/db_config.json")
    crm_config = load_config("./config/crm_config.json")
    website_urls = load_urls_from_file("website_urls.txt")
    smtp_server = "smtp.example.com:587"

    # Connect to the MySQL database
    mydb = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    mycursor = mydb.cursor()

    # Call the web scraping function
    extracted_data = extract_data(website_urls)

    # Call the NLP processing function
    processed_data = process_data(extracted_data)

    # Clean and segment the processed data
    cleaned_data = clean_and_segment_data(processed_data)

    # Store the cleaned data in the MySQL database
    store_data_in_db(mycursor, db_config)

    # Cross-reference the data with another table to match names and counties
    generate_leads(mycursor, cleaned_data)

    query = "SELECT * FROM names_table WHERE name"
    mycursor.execute(query)
    leads = mycursor.fetchall()

    # Commit the changes to the database
    mydb.commit()
    mydb.close()

    # Integrate the data into the CRM platform
    success = integrate_data(cleaned_data, crm_config)
    if success:
        print("Data successfully injected into the CRM platform")
    else:
        print("Failed to inject data into the CRM platform")

    # Get the recipients from the CRM platform
    recipients = get_recipients_from_crm(crm_config)

    # Get the leads count and data quote from the scraped data
    leads_count = len(leads)
    data_quote = get_data_quote_from_scraped_data(extracted_data)

    # Send the daily updates email to the recipients
    send_daily_updates(recipients, leads_count,
                       data_quote, sender)

    # Get the latest news from the scraped data
    news = get_latest_news_from_scraped_data(extracted_data)

    # Send the daily newsletter email to the recipients
    send_daily_newsletter(recipients, leads, news, sender)
