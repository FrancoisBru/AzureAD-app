# Define imports
import msal
import requests
import json
import sys
import click

def acquire_token(id, secret):

# Enter the details of your AAD app registration
    client_id = id
    client_secret = secret
    authority = 'https://login.microsoftonline.com/860cec36-ec77-482a-a750-04750df95efd'
    scope = ['https://graph.microsoft.com/.default']

    # Create an MSAL instance providing the client_id, authority and client_credential parameters
    client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret) 

    # First, try to lookup an access token in cache
    token_result = client.acquire_token_silent(scope, account=None)

    # If the token is available in cache, save it to a variable
    if token_result:
        access_token = 'Bearer ' + token_result['access_token']
        print('Access token was loaded from cache')

    # If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
    if not token_result:
        token_result = client.acquire_token_for_client(scopes=scope)
        access_token = token_result['access_token']

    print("Token successfully obtained")
    return access_token

def outputJSONFormat(rep): #Output the result in a clean way
    output = json.dumps(rep, sort_keys= True, indent=4) #convert a python object into a JSON string
    dict_format = json.loads(output)     #convert the JSON string into a dictionnary
    #print(dict_format) 
    return dict_format

#GET
#Make a get request thanks to library request in order to obtain the user id
def get_user(url_api, headers):
    resp = requests.get(url= url_api, headers=headers)
    print("Response code is : " +str(resp.status_code))
    dict = outputJSONFormat(resp.json())
    id_user = dict['value'][0]['id'] #get the user id
    if (resp.status_code != 200): #if result is different than 200 http code, print an error and its reason
        print (f"Le code de la réponse est : {resp.status_code} \nLa requête a échoué pour les raisons suivantes :")
        print (resp.raise_for_status())
        sys.exit()
    else:
        print("Request successfully executed")
    return id_user

#Make a get request to obtain the roles available in the azure AD
def get_role(url_api2,headers):
    resp2 = requests.get(url_api2, headers=headers)
    print("Response code is  : " + str(resp2.status_code))
    dict = outputJSONFormat(resp2.json())
    id_role = dict['value'][0]['id'] #get the role id
    if (resp2.status_code != 200): #if result is unsuccesful, print an error and its reason
        print (f"Le code de la réponse est : {resp2.status_code} \nLa requête a échoué pour les raisons suivantes :")
        print (resp2.raise_for_status())
        sys.exit()
    else:
        print("Request successfully executed")
    return id_role

#post request with the user id and role id collected to assign a role to an user
#the payload variable is sent to azure (payload is inside process automation method)
def post_role(url_api3, headers, payload):
    resp3 = requests.post(url_api3,json = payload, headers=headers)
    if (resp3.status_code != 201):
        print (f"Le code de la réponse est : {resp3.status_code} \nLa requête a échoué pour les raisons suivantes :")
        print (resp3.raise_for_status())
        sys.exit()
    else:
        print("POST request was successfully executed and data have been modified in the Azure AD")

#use click library to collect essential informations for the script to run
@click.command()
@click.option('--id', prompt = 'Client ID', prompt_required = True, help = 'Provide client_id from Azure AD')
@click.option('--secret', prompt = 'Client Secret', prompt_required = True, help = 'Provide Client Secret from Azure AD')
@click.option('--url_api', prompt = 'URL user', prompt_required = True, help = 'Provide URL for a specific user')
@click.option('--url_api2', prompt = 'URL role definitions', prompt_required = True, help = 'Provide URL for a specific role')
@click.option('--url_api3', prompt = 'URL role assignements', prompt_required = True, help = 'Provide URL to assign a role')

#this methods supervises the other methods if an error arise the process is stopped
def process_automation(id, secret, url_api, url_api2, url_api3):
    token = acquire_token(id,secret)
    headers = {
        'Authorization' : token
    }
    content_user = get_user(url_api=url_api, headers=headers)
    content_role = get_role(url_api2=url_api2, headers=headers)
    payload = {
        "@odata.type": "#microsoft.graph.unifiedRoleAssignment",
        "principalId": "",
        "roleDefinitionId": "",
        "directoryScopeId": "/"
    }
    payload['principalId'] = content_user
    payload['roleDefinitionId'] = content_role
    post_role(url_api3 = url_api3, headers = headers, payload=payload)

if __name__ == "__main__":
    sys.exit(process_automation())

