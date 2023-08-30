import requests
from pprint import pprint
import pandas as pd

class NotionRequest:
    def __init__(self,token,database_id):
        self.token = token
        self.database_id = database_id
    def request(self,num_pages=None):
        headers = {
        "Authorization": "Bearer " + self.token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
        }
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query" 
        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        # Comment this out to dump all data to a file
        # import json
        # with open('db.json', 'w', encoding='utf8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)

        results = data["results"]
        return results
    def get_interest_points_properties(self,interest_points):
        interest_points_properties = list()
        for interest_point in interest_points:
            interest_points_properties.append(list(map(lambda x:(x[0],x[1]['type'],x[1]),interest_point['properties'].items())))
        return interest_points_properties
    
    def get_value_propertie(self,properties):
        if properties[1] == 'select':
            return properties[0],properties[2]['select']['name']
        elif properties[1] == 'title':
            return properties[0],properties[2]['title'][0]['plain_text']
        elif properties[1] == 'unique_id':
            return properties[0],properties[2]['unique_id']['number']
        elif properties[1] == 'url':
            return properties[0],properties[2]['url']
        elif properties[1] == 'rich_text' and properties[2]['rich_text'] :
            return properties[0],properties[2]['rich_text'][0]['plain_text']
        elif properties[1] == 'rollup' and properties[2]['rollup']['array'] :
            return properties[0],properties[2]['rollup']['array'][0]['unique_id']['number']
        elif properties[1] == 'formula':
            return properties[0],properties[2]['formula']['number']
        elif properties[1] == 'date':
            return properties[0],properties[2]['date']['start']
        else:
            return properties[0],None
        
    def get_properties_table(self,propert):
        df_prop = pd.DataFrame(data =propert[1])
        df_prop_transpose = df_prop.transpose()
        df_prop = df_prop_transpose.rename(columns=df_prop_transpose.iloc[0]).loc[1:]
        df_prop.drop(1,inplace=True)
        for p in propert:
            df_properties = pd.DataFrame(data=p)
            df_properties_t = df_properties.transpose()
            df_properties = df_properties_t.rename(columns=df_properties_t.iloc[0]).loc[1:]
            df_prop=pd.concat([df_prop,df_properties],ignore_index=True)
        return df_prop
def main():
    notion = NotionRequest('API_KEI','TABLE_ID')
    interest_points=notion.request()
    interest_points_properties = notion.get_interest_points_properties(interest_points)
    properties = list()
    for prop in interest_points_properties:
        properties.append(list((map(lambda x:notion.get_value_propertie(x),prop))))
    df_properties = notion.get_properties_table(properties)
    print(df_properties)

if __name__ == '__main__':
    main()
    

