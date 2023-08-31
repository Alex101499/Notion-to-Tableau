import requests
from pprint import pprint
import pandas as pd
from google_sheets_api import GoogleSheets

class NotionRequest:
    def __init__(self,token):
        self.token = token
    def request(self,database_id,num_pages=None):
        headers = {
        "Authorization": "Bearer " + self.token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
        }
        url = f"https://api.notion.com/v1/databases/{database_id}/query" 
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
        elif properties[1] == 'rollup':
            if properties[2]['rollup']['type']== 'array' and properties[2]['rollup']['array']:
                return properties[0],properties[2]['rollup']['array'][0]['unique_id']['number']
            elif properties[2]['rollup']['type']=='number':
                return properties[0],properties[2]['rollup']['number']
            else:
                return properties[0],None

        elif properties[1] == 'formula':
            return properties[0],properties[2]['formula']['number'] if properties[2]['formula']['type'] == 'number'else properties[2]['formula']['string']
        elif properties[1] == 'date':
            return properties[0],properties[2]['date']['start']
        else:
            return properties[0],None
        
    def add_rows_table(self,interest_points):
        properties = list()
        for prop in interest_points:
            properties.append(list((map(lambda x:self.get_value_propertie(x),prop))))
        return properties

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
    def get_dataframe(self,request):
        json_properties = self.get_interest_points_properties(request)
        properties = self.add_rows_table(json_properties)
        df_properties = self.get_properties_table(properties)
        return df_properties


def main():
    notion = NotionRequest('API_KEY')
    interest_points=notion.request('TABLE_ID')
    visit_places = notion.request('TABLE_ID')
    trips = notion.request('TABLE_ID')
    df_interest_points = notion.get_dataframe(interest_points)
    df_visit_places = notion.get_dataframe(visit_places)
    df_trips = notion.get_dataframe(trips)
    google_sheets = GoogleSheets('OurTravelBook')
    google_sheets.export_google_sheet(df_visit_places,0)
    google_sheets.export_google_sheet(df_interest_points,1)
    google_sheets.export_google_sheet(df_trips,2)

if __name__ == '__main__':
    main()
    

