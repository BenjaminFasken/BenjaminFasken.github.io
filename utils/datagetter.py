import requests
import json
import os
import re
from urllib.parse import unquote

stationId = "8600020"  # Replace with the actual stop ID you want to request

url = 'https://webapp.rejseplanen.dk/bin/rest.exe/departureBoard?id=' + str(stationId) + '&format=json'
print("url", url)
def makeDirectories(stationName):
    directory = "utils/traffic_data/" + str(stationName)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(directory + "/shapes"):
        os.makedirs(directory + "/shapes")
    if not os.path.exists(directory + "/lines"):
        os.makedirs(directory + "/lines")
    return directory

def extract_trainid_part(url):
    regex = r'ref=([^&]+)'
    match = re.search(regex, url)
    if match:
        decoded = unquote(match.group(1))
        return decoded.split('?')[0]
    return None

def toDanish(text):
    return text.replace("\u00f8", "ø").replace("\u00e6", "æ").replace("\u00e5", "å").replace("\u00c6", "Æ").replace("\u00d8", "Ø").replace("\u00c5", "Å")

# hi = {'DepartureBoard': {'noNamespaceSchemaLocation': 'http://webapp.rejseplanen.dk/xml/rest/hafasRestDepartureBoard.xsd', 'Departure': [{'name': 'X Bus 970X', 'type': 'EXB', 'stop': 'Aalborg St. (Perron C5)', 'time': '12:40', 'date': '30.07.24', 'id': '851100105', 'line': '970X', 'messages': '1', 'track': 'C5', 'rtTime': '12:44', 'rtDate': '30.07.24', 'finalStop': 'Thisted St.', 'direction': 'Thisted St.', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=280857%2F103673%2F800344%2F306553%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100105%26%26format%3Djson'}}, {'name': 'Bybus S2', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:41', 'date': '30.07.24', 'id': '851801201', 'line': 'S2', 'messages': '0', 'track': 'A', 'rtTime': '12:44', 'rtDate': '30.07.24', 'finalStop': 'City Syd (Aalborg)', 'direction': 'City Syd', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=97422%2F67205%2F80746%2F7903%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801201%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Aalborg St. (Område B / Kennedy Arkaden)', 'time': '12:42', 'date': '30.07.24', 'id': '851920102', 'line': '1', 'messages': '0', 'track': 'B1', 'rtTime': '12:45', 'rtDate': '30.07.24', 'finalStop': 'Liselund vendeplads (Huttel-Sørensens vej/', 'direction': 'Vodskov', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=529410%2F210260%2F60888%2F146037%2F86%3Fdate%3D30.07.24%26station_evaId%3D851920102%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:42', 'date': '30.07.24', 'id': '851801201', 'line': '1', 'messages': '0', 'track': 'A', 'rtTime': '12:44', 'rtDate': '30.07.24', 'finalStop': 'Ferslev Skole (Rævedalsvej / Ferslev)', 'direction': 'Ferslev', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=256125%2F119179%2F286384%2F57822%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801201%26%26format%3Djson'}}, {'name': 'Bybus 15', 'type': 'BUS', 'stop': 'Budolfi Plads (Vingårdsgade / Aalborg)', 'time': '12:42', 'date': '30.07.24', 'id': '851101103', 'line': '15', 'messages': '0', 'rtTime': '12:44', 'rtDate': '30.07.24', 'finalStop': 'Nøvling Skole (Aalborg Kommune)', 'direction': 'Nøvling Skole', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=239994%2F114311%2F311232%2F75618%2F86%3Fdate%3D30.07.24%26station_evaId%3D851101103%26%26format%3Djson'}}, {'name': 'Bybus 2', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:43', 'date': '30.07.24', 'id': '851801204', 'line': '2', 'messages': '0', 'track': 'D', 'rtTime': '12:44', 'rtDate': '30.07.24', 'finalStop': 'Væddeløbsbanen (Skydebanevej / Aalborg)', 'direction': 'Væddeløbsbanen', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=442737%2F182162%2F458148%2F81516%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801204%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:44', 'date': '30.07.24', 'id': '851801204', 'line': '1', 'messages': '0', 'track': 'D', 'rtTime': '12:47', 'rtDate': '30.07.24', 'finalStop': 'Liselund vendeplads (Huttel-Sørensens vej/', 'direction': 'Vodskov', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=944550%2F348640%2F846002%2F108162%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801204%26%26format%3Djson'}}, {'name': 'Bus 56', 'type': 'BUS', 'stop': 'Aalborg St. (Perron C4)', 'time': '12:45', 'date': '30.07.24', 'id': '851100104', 'line': '56', 'messages': '0', 'track': 'C4', 'finalStop': 'Egense Fyr (Kystvej / Aalborg Kommune)', 'direction': 'Egense', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=639846%2F221476%2F281920%2F72322%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100104%26%26format%3Djson'}}, {'name': 'Bybus 14', 'type': 'BUS', 'stop': 'Aalborg St. (Område B / Kennedy Arkaden)', 'time': '12:45', 'date': '30.07.24', 'id': '851920104', 'line': '14', 'messages': '0', 'track': 'B2', 'rtTime': '12:47', 'rtDate': '30.07.24', 'finalStop': 'Rødhøjvej (Storvorde)', 'direction': 'Storvorde', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=240924%2F114525%2F336572%2F87983%2F86%3Fdate%3D30.07.24%26station_evaId%3D851920104%26%26format%3Djson'}}, {'name': 'Bybus S2', 'type': 'BUS', 'stop': 'Aalborg St. (Område B / Kennedy Arkaden)', 'time': '12:46', 'date': '30.07.24', 'id': '851920103', 'line': 'S2', 'messages': '0', 'track': 'B4', 'rtTime': '12:49', 'rtDate': '30.07.24', 'finalStop': 'City Syd (Aalborg)', 'direction': 'City Syd', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=898614%2F334269%2F307780%2F145652%2F86%3Fdate%3D30.07.24%26station_evaId%3D851920103%26%26format%3Djson'}}, {'name': 'Togbus BLÅ', 'type': 'TOG', 'stop': 'Aalborg St. (togbus)', 'time': '12:47', 'date': '30.07.24', 'id': '8650020', 'line': 'BLÅ', 'messages': '1', 'finalStop': 'Aarhus H (togbus)', 'direction': 'Aarhus H (togbus)', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=329193%2F138791%2F582190%2F181371%2F86%3Fdate%3D30.07.24%26station_evaId%3D8650020%26%26format%3Djson'}}, {'name': 'X Bus 60X', 'type': 'EXB', 'stop': 'Aalborg St. (Perron C3)', 'time': '12:48', 'date': '30.07.24', 'id': '851100103', 'line': '60X', 'messages': '0', 'track': 'C3', 'finalStop': 'Aalborg St. (Område C / Regionalbus)', 'direction': 'Støvring', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=570162%2F201691%2F530872%2F75382%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100103%26%26format%3Djson'}}, {'name': 'Bybus 15', 'type': 'BUS', 'stop': 'Aalborg St. (Område A / John F. Kennedys Plads)', 'time': '12:48', 'date': '30.07.24', 'id': '851002702', 'line': '15', 'messages': '0', 'track': 'A1', 'finalStop': 'Nøvling Skole (Aalborg Kommune)', 'direction': 'Nøvling Skole', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=182964%2F95301%2F227466%2F52745%2F86%3Fdate%3D30.07.24%26station_evaId%3D851002702%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Aalborg St. (Område B / Kennedy Arkaden)', 'time': '12:49', 'date': '30.07.24', 'id': '851920101', 'line': '1', 'messages': '0', 'track': 'B3', 'finalStop': 'Ferslev Skole (Rævedalsvej / Ferslev)', 'direction': 'Ferslev', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=293277%2F131563%2F296898%2F50695%2F86%3Fdate%3D30.07.24%26station_evaId%3D851920101%26%26format%3Djson'}}, {'name': 'Bybus 2', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:49', 'date': '30.07.24', 'id': '851801201', 'line': '2', 'messages': '0', 'track': 'A', 'finalStop': 'AAU Busterminal (Sigrid Undsetsvej / Aalborg)', 'direction': 'Universitetet', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=597306%2F233679%2F123778%2F137231%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801201%26%26format%3Djson'}}, {'name': 'Bus 42', 'type': 'BUS', 'stop': 'Aalborg St. (Perron C6)', 'time': '12:50', 'date': '30.07.24', 'id': '851100106', 'line': '42', 'messages': '1', 'track': 'C6', 'finalStop': 'Ultvedvej (Luneborgvej / Tylstrup)', 'direction': 'Tylstrup', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=907023%2F313809%2F921850%2F158586%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100106%26%26format%3Djson'}}, {'name': 'Togbus LILLA', 'type': 'TOG', 'stop': 'Aalborg St. (Område C / Regionalbus)', 'time': '12:50', 'date': '30.07.24', 'id': '851100102', 'line': 'LILLA', 'messages': '0', 'track': 'C2', 'finalStop': 'Brønderslev St.', 'direction': 'Brønderslev St.', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=380727%2F138718%2F32728%2F110553%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100102%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Aalborg St. (Område B / Kennedy Arkaden)', 'time': '12:50', 'date': '30.07.24', 'id': '851920102', 'line': '1', 'messages': '0', 'track': 'B1', 'finalStop': 'Hals (Østergade)', 'direction': 'Hals', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=997557%2F366270%2F636104%2F14467%2F86%3Fdate%3D30.07.24%26station_evaId%3D851920102%26%26format%3Djson'}}, {'name': 'Bus 52', 'type': 'BUS', 'stop': 'Aalborg St. (Perron C4)', 'time': '12:52', 'date': '30.07.24', 'id': '851100104', 'line': '52', 'messages': '0', 'track': 'C4', 'finalStop': 'Aalestrup Busterminal (Vesthimm. Komm.)', 'direction': 'Aalestrup', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=137025%2F53431%2F201736%2F55193%2F86%3Fdate%3D30.07.24%26station_evaId%3D851100104%26%26format%3Djson'}}, {'name': 'Bybus 1', 'type': 'BUS', 'stop': 'Nytorv (Østeraagade / Aalborg)', 'time': '12:52', 'date': '30.07.24', 'id': '851801204', 'line': '1', 'messages': '0', 'track': 'D', 'finalStop': 'Hals (Østergade)', 'direction': 'Hals', 'JourneyDetailRef': {'ref': 'http://webapp.rejseplanen.dk/bin//rest.exe/journeyDetail?ref=381075%2F160776%2F587324%2F166637%2F86%3Fdate%3D30.07.24%26station_evaId%3D851801204%26%26format%3Djson'}}]}}
# print("first ref", hi



# exit()

response = requests.get(url)

if response.status_code == 200:
    stboard_json = response.json()
    directory = makeDirectories(stationId)

    with open(directory + "/stboard.json", "w", encoding='utf-8') as file:
        file.write(toDanish(json.dumps(stboard_json, indent=4)))
        print("Data saved to stboard.txt")     

        for i, journey in enumerate(stboard_json['DepartureBoard']['Departure']):
            lineurl = journey['JourneyDetailRef']['ref']
            line_response = requests.get(lineurl)

            if line_response.status_code == 200:
                line_json = line_response.json()
                with open(directory + "/lines/" + str(i) + ".json", "w", encoding='utf-8') as linefile:
                    linefile.write(toDanish(json.dumps(line_json, indent=4)))
            
            shapeurl = "https://webapp.rejseplanen.dk/bin/query.exe/mny?look_trainid=" + extract_trainid_part(journey['JourneyDetailRef']['ref']) + "&tpl=chain2json3&performLocating=16&format_xy_n&"
            shape_response = requests.get(shapeurl)

            if shape_response.status_code == 200:
                with open(directory + "/shapes/" + str(i) + ".json", "w", encoding='utf-8') as shapefile:
                    shapefile.write(toDanish(shape_response.text))

    print("url", url)
            
else:
    print("Failed to make the stboard request")
        
