import re


def extract_address_info(address):
    #building_number = re.findall(r'\b\d+-\d+\b+|\b\d+|\b[Bb]\d+\b|\b[Gg]+/+[Ff]\s*\d+\b|\b[Bb]\s*\d+\b', address) 
    #address = re.sub(r"[ㄱ-ㅣ가-힣]", "", address)
    address = re.sub(r'[(]', '', address)
    
    #building_number = re.findall(r'\b\d+-\d+\b|\b\d+|\b\d+(?!\S)', address) 
    road_name = re.findall(r'(\S+(?:-ro|-daero|-gil)|(?:로|ro|길)\b)', address)
    
    #gil_name = re.findall(r'\s*([^,\s]+(?:gil|길))', address)  
    city_name = re.findall(r'(\S+(?:구|gu|군|gun)\b|(\S+(?:-gu|-si|-gun)))', address)
    #si_name = re.findall(r',\s*([^,\s]+(?:-si|시))', address, re.IGNORECASE) 
    #si_name = re.findall(r'\s*(\S+(?:-si|시))', address, re.IGNORECASE)
    #province_name = re.findall(r',\s*(\S+(?:-do|도)\b)', address)
    
    #building_number = building_number[0]if building_number else ""
    road_name = road_name[0] if road_name else ""
    #gil_name = gil_name[0] if gil_name else ""
    city_name = city_name[0][0] if city_name else ""
    #si_name = si_name[0] if si_name else ""
    #province_name = province_name[0] if province_name else ""
    
    
    #reordered_address = f"{building_number}, {road_name}, {gil_name}, {city_name}, {si_name}, {province_name}"
    return  road_name , city_name