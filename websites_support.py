import urllib
import json
import re
import requests

################ IVORY ###########################
def check_ivory_availability(ivory_serial_number):
    # ivory serial number presented in the website is different from the id used in their internal search
    ivory_product_id = ivory_serial_2_title(ivory_serial_number, key='id')

    ivory_url = f"https://www.ivory.co.il/catalog-items/ws/check_balance/{ivory_product_id}"
    ivory_req = urllib.request.Request(ivory_url, data=None, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}, origin_req_host=None, unverifiable=False, method=None)

    ivory_res = urllib.request.urlopen(ivory_req)
    ivory_res_as_text = ivory_res.read().decode("utf-8")
    ivory_res_as_dict = json.loads(ivory_res_as_text)

    ivory_available_branches = []
    for branch_availability in ivory_res_as_dict['Data']:
        if 'isAvailable' in branch_availability.keys():
            if branch_availability['isAvailable']:
                ivory_available_branches.append(branch_availability['friendlyURL'].replace("ivory_store_", ""))

    return ivory_available_branches

def ivory_serial_2_title(ivory_serial_number, key='title'):
    ivory_serial_number = ivory_serial_number.replace("/", "***")
    url = f'https://www.ivory.co.il/search/ws/main-site-search/{ivory_serial_number}'
    ivory_search_request = urllib.request.Request(url, data=None, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}, origin_req_host=None, unverifiable=False, method=None)

    ivory_search_res = urllib.request.urlopen(ivory_search_request)
    ivory_search_result_as_text = ivory_search_res.read().decode("utf-8")
    try:
        results = json.loads(ivory_search_result_as_text)["Results"]
        _key = results["catalog"]["products"][0][key]
        return _key
    except:
        return None

################ KSP ###########################

def check_ksp_availability(ksp_serial_number):
    ksp_url = f"https://ksp.co.il/m_action/api/mlay/{ksp_serial_number}"
    
    headers = dict()
    headers["lang"] = "en"
    headers["user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    
    ksp_res = requests.get(ksp_url, headers=headers)
    ksp_res_as_text = ksp_res.content.decode()
    ksp_res_as_dict = json.loads(ksp_res_as_text)


    ksp_available_branches = []
    for ksp_branch in ksp_res_as_dict['result'].values():
        if ksp_branch['qnt']:
            ksp_available_branches.append(ksp_branch['name'])

    return ksp_available_branches

def ksp_serial_2_title(ksp_serial_number):
    url = f'https://ksp.co.il/m_action/api/search/?q={ksp_serial_number}'
     
    ksp_search_request = urllib.request.Request(url, data=None, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}, origin_req_host=None, unverifiable=False, method=None)
    headers = dict()
    headers["lang"] = "en"
    headers["user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
   
    ksp_search_res = requests.get(url, headers=headers)
    ksp_search_result_as_text = ksp_search_res.content.decode()
    ksp_search_result_as_dict = json.loads(ksp_search_result_as_text)['result']
    try:
        for item in ksp_search_result_as_dict['items']:
            if item['uinsql'] == f'{ksp_serial_number}':
                title = item['name']
                return title

    except:
        pass
    return None

################ BUG ###########################

def check_bug_availability(bug_serial_number):
    # bug serial number presented in the website is different from the id used in their internal search
    bug_product_id = bug_serial_2_title(bug_serial_number, key='id')
    bug_url = f'https://www.bug.co.il/product/check-inventory?productId={bug_product_id}'
    bug_req = urllib.request.Request(bug_url, data=None, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}, origin_req_host=None, unverifiable=False, method=None)

    bug_res = urllib.request.urlopen(bug_req)
    bug_res_as_text = bug_res.read().decode("utf-8")

    # remove img tags because they are not closed
    img_tags = '<img (.+?)>'
    bug_res_as_text = re.sub(img_tags, '', bug_res_as_text )
    all_branches = re.findall("(<span class='branch-label'.*?</span></span>)", bug_res_as_text)

    bug_available_branches = []
    for branch in all_branches:
        (bug_branch_name,) = re.compile("<span class='branch-label'.*>(.*)<span").search(str(branch)).groups(0)
        (availability,) = re.compile("<span data-inventory='(\d)'>.*").search(str(branch)).groups(0)
        if availability == "1":
            bug_available_branches.append(bug_branch_name)
    return bug_available_branches

def bug_serial_2_title(bug_serial_number : str, key='shortTitle'):
    url = f'https://n2.nixale.com/q?customer=bug&q={bug_serial_number}&key=UeyeetXzpYKpZR3rm2gYTUjohPYdMod0&autocomplete=true&getClassification=true'
    bug_search_request = urllib.request.Request(url, data=None, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}, origin_req_host=None, unverifiable=False, method=None)

    bug_search_res = urllib.request.urlopen(bug_search_request)
    bug_search_result_as_text = bug_search_res.read().decode("utf-8")
    try:
        results = json.loads(bug_search_result_as_text)['products']
        _key = results[0][key]
        return _key
    except:
        return None
