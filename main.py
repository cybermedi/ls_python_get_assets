#Set enviroment vailables LS_SITE_ID and LS_IDENTITY_CODE
import http.client
import json
import os

conn = http.client.HTTPSConnection("api.lansweeper.com")

def getAssetData(identity_code, site_id, limit, page, cursor):
    if page=="FIRST":
        assetPagination="limit: %d, page: FIRST" % (limit)
    else:
        assetPagination="limit: %d, page: NEXT, cursor: \"%s\"" % (limit,cursor)

    query="""query getAssetResources {
    site(id: "%s") {
        assetResources(
        assetPagination: { %s }
        fields: [
            "assetBasicInfo.name"
            "assetBasicInfo.userDomain"
            "assetBasicInfo.description"
            "url"
        ]
        ) {
        total
        pagination {
            limit
            current
            next
            page
        }
        items
        }
    }
    }""" % (site_id,assetPagination)

    payload={
        "query": query
    }

    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {identity_code}'
    }
    conn.request("POST", "/api/v2/graphql", json.dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


def main():
    allAssets=[]
    site_id=os.environ.get('LS_SITE_ID')
    identity_code=os.environ.get('LS_IDENTITY_CODE')
    print("Loading the first page")
    response=getAssetData(identity_code,site_id,500,"FIRST","")
    allAssets.extend(response['data']['site']['assetResources']['items'])
    while response['data']['site']['assetResources']['pagination']['next']!=None:
        print("Loading page with a cursor: %s " % (response['data']['site']['assetResources']['pagination']['next']))
        response=getAssetData(identity_code,site_id,500,"NEXT" ,response['data']['site']['assetResources']['pagination']['next'])
        allAssets.extend(response['data']['site']['assetResources']['items'])    
    print("Loaded %d assets." % (len(allAssets)))

main()