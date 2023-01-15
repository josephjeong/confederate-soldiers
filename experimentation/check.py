import requests

# send a post request to the endpoint https://www.fold3.com/fold31-search/doc-search



# send a post request to the endpoint https://www.fold3.com/fold31-search/doc-search
def send_request():

    headers = {
        "authority": "www.fold3.com",
        "cookie": "gcl_au=1.1.2079603617.1673338985;lastIid=2584; lastSid=2584; an_split=21; an_s_split=59; _ga=GA1.2.820516181.1673338986;AMCVS_ED3301AC512D2A290A490D4C%40AdobeOrg=1; s_cc=true; AMCV_ED3301AC512D2A290A490D4C%40AdobeOrg=359503849%7CMCIDTS%7C19373%7CMCMID%7C44596303942405762696092491596750002773%7CMCOPTOUT-1673762117s%7CNONE%7CMCAID%7CNONE%7CMCAAMLH-1674359717%7C8%7CMCAAMB-1674359717%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-19375%7CvVersion%7C5.0.1; _gid=GA1.2.1624402709.1673754919; _hjSessionUser_1216908=eyJpZCI6ImEyZWIwMDliLWE3YWMtNTViNC1iMjRhLTcxNjY0MDY0MDUzYiIsImNyZWF0ZWQiOjE2NzMzMzg5ODYzMDcsImV4aXN0aW5nIjp0cnVlfQ==;_hjIncludedInSessionSample=0; _hjSession_1216908=eyJpZCI6IjY3OTcyNDFhLTdjNDEtNGJhOC05ZTVhLTNmMWVjMWNhYzdkZSIsImNyZWF0ZWQiOjE2NzM3NTQ5MjAzMDcsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=1; AMP_TOKEN=%24NOT_FOUND; f3av=62; f3ll=1; s_sq=%5B%5BB%5D%5D; sess=eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJGMyIsImRlc2MiOiJ7J3UnOnsnYSc6MjYyNCwndSc6ODEwMTI5NCwndW4nOidmZWRlcmljb21hc2VyYTU1MScsJ3MnOidmcmVldHJpYWwnLCdhcyc6J2ZyZWUtdHJpYWwnLCdzcyc6J2ZyZWUtdHJpYWwnLCdhdSc6J2ZlZGVyaWNvX21hc2VyYScsJ2UnOidmZWRlcmljby5tYXNlcmFAZ21haWwuY29tJywnaic6MTY3MTAzMjQyNCwncCc6MSwncic6MCwnZic6MTAwfSwncCc6eydhbSc6J0ZPTEQzJywnYXQnOjE2NzM3NTQ5NDkzNDMsJ2lhbSc6bnVsbCwnaWF0JzpudWxsLCdsJzonZW4tVVMnLCdnJzonVVMnfX0iLCJpYXQiOjE2NzM3NTU3NzUsImV4cCI6MTcwNTI5MTc3NX0.LOpjCCqjgiF6QJ8-vlunJJ62Nfd--fwEGJpC8ZXAI_7aoZMvB7EWZxJVeXWb6ZXx; utag_main=v_id:01859ac69cf20015b13f487f7a4a05081001e07900fb8$_sn:2$_se:4$_ss:0$_st:1673757576731$vapi_domain:fold3.com$ses_id:1673754917578%3Bexp-session$_pn:4%3Bexp-session; _uetsid=6e2c8cb0948811ed97a3d98a012b58fe; _uetvid=0451da5090c011ed91ad8f2b216dc45b"
    }

    data = {"environment":{"origin":"regiment"},"facetRequests":[{"type":"place","maxCount":200,"placeLevel":"COUNTRY"},{"type":"place","maxCount":200,"placeLevel":"STATE","placeParents":["rel.148838"]},{"type":"military.service.branch","maxCount":200},{"type":"general.title.id","maxCount":10000},{"type":"general.title.content.type","maxCount":200},{"type":"general.title.provider.id","maxCount":200}],"filters":[{"type":"military.conflict","values":["Civil War (Confederate)"]},{"type":"general.title.content.sub-type","values":["SERVICEPERSON"]},{"type":"general.title.content.collection","values":["us-civil-war-confederate"]}],"highlight":{"highlight":True},"maxCount":100}

    req = requests.post('https://www.fold3.com/fold31-search/doc-search', json=data, headers=headers)
    print(req.text)
    # print(req.json())

if __name__ == '__main__':
    send_request()