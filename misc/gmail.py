from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

"""Get a list of Messages from the user's mailbox.
"""

from apiclient import errors


def list_messages_matching_query(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    messages = list_messages_matching_query(service, user_id='me', query='from: wave@wave.com')

    headers = [service.users().messages().get(userId='me', id=m['id']).execute()['payload']['headers'] for m in
               messages]
    # Call the Gmail API
    import pandas as pd
    res = pd.DataFrame(columns=["Date", "Recipient", "Currency", "Amount"])
    amt = rec = date = curr = ''
    i = 0
    dont = True
    for head in headers:
        for h in head:
            if h['name'] == 'Subject':
                v = h['value'].replace('You sent', '')
                if '$' in v:
                    v = v.split('$')
                    curr = 'USD'
                elif '£' in v:
                    curr = 'GBP'
                    v = v.split('£')
                else:
                    dont = False
                rec = v[0]
                amt = v[1]
            if h['name'] == 'Date':
                date = h['value'].replace('+0000', '')
        if dont:
            res.loc[i] = [date, rec, curr, amt]
        else:
            dont = True
        i += 1

    res.to_csv("results.csv", index=False)


if __name__ == '__main__':
    main()
