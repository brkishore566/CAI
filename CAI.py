from __future__ import print_function
from flask import Flask, request, jsonify
import json
import requests
from requests.auth import HTTPBasicAuth
from word2number import w2n
import os
import sys


app = Flask(__name__)
port = '5000'

@app.route('/lookup', methods=['POST'])
def index1():
  data = json.loads(request.get_data())
  ip = request.remote_addr
  try:
      anumber = data['nlp']['entities']['articlenumber'][0]['raw']
      print(anumber)

  except:
      anumber = data['conversation']['memory']['articlenumber']
      print(anumber)


  s = requests.Session()
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})
  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_srv/Products?$filter=Description%20eq%20%27"+anumber+"%27&$format=json", verify=False)

  print (r.text)
  token = r.headers['x-csrf-token']
  s.close()
  resp = json.loads(r.text)

  print("------*****LooKUP*****-------")
  print (resp)
  return jsonify(
    status=200,
    replies=[{
      'type': 'text',
      'content' : "Product Name : " + (resp['d']['results'][0]['Description']) + "\n\nBase EAN : " + resp['d']['results'][0]['BaseEan'] + "\n\n Stock Quantity : " + resp['d']['results'][0]['StockQuantity'] + ' ' + resp['d']['results'][0]['BaseUom']
    }],
    conversation = {
        'memory' : {
            'csrf' : token,
            'EAN' : resp['d']['results'][0]['BaseEan'],
            'articlenumber' : resp['d']['results'][0]['ProductNumber'],
            'articlenumber1' : resp['d']['results'][0]['ProductNumber']
            }
    }
  )
  print(data)

@app.route('/stock', methods=['POST'])
def index10():
  data = json.loads(request.get_data())


  try:
      anumber = data['nlp']['entities']['articlenumber'][0]['raw']
      print(anumber)

  except:
      anumber = data['conversation']['memory']['articlenumber']
      print(anumber)


  # token = data['conversation']['memory']['csrf']
  EAN = data['conversation']['memory']['EAN']
  # print (token)
  s = requests.Session()
  # Inserting the article into the worklist
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})
  r1 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/AddScannedProducts?ScannedEAN='" + EAN + "'&$format=json", verify=False)
  token = r1.headers['x-csrf-token']

  #Getting all the storage locations associated with the article.
  s.headers.update({'X-CSRF-Token': 'Fetch' , 'Authorization' : 'Basic Provide Basic Authorization here'})
  r2 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Products(ProductNumber='" + anumber + "')/StorageLocations?$format=json", verify=False)
  s.close()
  token2 = r2.headers['x-csrf-token']
  storageLocat = json.loads(r2.text)
  SLnumber = len(storageLocat['d']['results'])
  resp = json.loads(r2.text)
  StorageLocations = []

  for i in resp['d']['results']:
    StorageLocations.append((i['StorageLocationId']))

  return jsonify(
    status=200,
    replies=[
    {
    'type' : 'text',
    'content' : "Cool let's do this"
    }
    ],
    conversation = {
        'memory' : {
            'articlenumber' : anumber,
            'articlenumber1' : anumber,
            'StorageLen' : SLnumber,
            'SLocations' : StorageLocations,
            'EAN' : EAN
            }
    }
  )

@app.route('/adj_post_cust', methods=['POST'])
def index_adj_post():
    data = json.loads(request.get_data())
    try:
        anumber = data['nlp']['entities']['articlenumber1'][0]['raw']
        print(anumber)
        print(data)

    except:
        anumber = data['conversation']['memory']['articlenumber1']
        print(anumber)
        print(data)


    # token = data['conversation']['memory']['csrf']
    EAN = data['conversation']['memory']['EAN']
    quant1 = data['conversation']['memory']['QNT']
    quant1 = str(quant1)
    quant2 = w2n.word_to_num(quant1)
    print (quant2)
    print (type(quant2))
    #quant = str(quant2).decode("utf-8")
    quant = str(quant2).encode("utf-8").decode("utf-8")
    #quant = quant2
    # storageLoc = data['conversation']['memory']['SL']
    M_TYPE = data['conversation']['memory']['M_TYPE']
    # move_type = 0
    #
    # if M_TYPE == "Shrinkage":8
    #     move_type = '0001'
    # elif M_TYPE == "Theft":
    #     move_type = '0002'
    # else:
    #     move_type = '0000'



    s = requests.Session()
    s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})
    r1 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Products('" + anumber + "')?$format=json", verify=False)
    print (r1.text)
    # token = r1.headers['x-csrf-token']
    # print(token)



    s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here', 'Connection' : 'keep-alive'})
    r2 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/AddScannedProducts?ScannedEAN='" + EAN + "'&$format=json", verify=False)
    print (r2.text)
    token = r2.headers['x-csrf-token']
    resp1 = json.loads(r2.text)

    s.headers.update({'x-csrf-token': token , 'Authorization' : 'Basic Provide Basic Authorization here','Content-type': 'application/json', 'Connection' : 'keep-alive', 'Accept': 'application/json'})
    payload = {
	"ProductNumber": anumber,
	"SubmitFlg":"X",
	"SubmittedStock": quant,
	"StorageLoc":"0001",
	"ReasonMvt": M_TYPE,
	"BusinessTrx":"0001"
}
    r3 = s.put("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Shrinks(ProductNumber='" + anumber + "')", verify=False, data=json.dumps(payload))

    s.close()
    # resp2 = json.loads(r3.text)
    return jsonify(
      status=200,
      replies=[
      {
      'type' : 'text',
      'content' : "Successfully posted"
      },
      {
      'type' : 'text',
      'content' : r3.text
      }
      ],
      conversation = {
        'memory' : {
            'csrf' : token,
            'EAN' : resp['d']['results'][0]['BaseEan'],
            'articlenumber' : resp['d']['results'][0]['ProductNumber'],
            'articlenumber1' : resp['d']['results'][0]['ProductNumber']
            }
    }
    )

@app.route('/order', methods=['POST'])
def index_order():
  data = json.loads(request.get_data())
  ip = request.remote_addr
  try:
      anumber = data['nlp']['entities']['articlenumber'][0]['raw']
      print(anumber)

  except:
      anumber = data['conversation']['memory']['articlenumber']
      print(anumber)

  s = requests.Session()
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})

  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_ORDER_PRODUCT_SRV/Stores('ALE2')/Products?sap-client=210&$inlinecount=allpages&$top=20&search=" + anumber + "&$format=json", verify=False)

  token = r.headers['x-csrf-token']
  s.close()
  resp = json.loads(r.text)
  
  print(resp)

  print("-------------")
  return jsonify(
    status=200,
    replies=[{
      'type': 'text',
      'content' : "Product Name : " + resp['d']['results'][0]['ProductName'] + "\n\nEAN : " + (resp['d']['results'][0]['GlobalTradeItemNumber']) + "\n\nAvailable Stock : " + resp['d']['results'][0]['AvailableStockQuantity'] + "\n\n Order Quantity : " + resp['d']['results'][0]['OrderQuantity'] + ' ' + resp['d']['results'][0]['OrderQuantityUnitCode'] + "\n\n Delivery in : " + str(resp['d']['results'][0]['PlannedOrderDeliveryInDays']) + "days"
    }],
    conversation = {
        'memory' : {
            'csrf' : token,
            'EAN' : resp['d']['results'][0]['GlobalTradeItemNumber'],
            'articlenumber' : resp['d']['results'][0]['ProductID'],
            'articlenumber1' : resp['d']['results'][0]['ProductID']
            }
    }
  )

@app.route('/deliveries', methods=['POST'])
def index_deliveries():
  data = json.loads(request.get_data())
  ip = request.remote_addr
  try:
      anumber = data['nlp']['entities']['articlenumber1'][0]['raw']
      print(anumber)

  except:
      anumber = data['conversation']['memory']['articlenumber1']
      print(anumber)


  s = requests.Session()
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})
  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_PRODUCT_LKP_SRV/Sites?sap-client=210&$top=2&$skip=0&$filter=Assigned eq 'X'&$format=json", verify=False)
    
  print (r.text)
  s.close()
  resp = json.loads(r.text)
  store = resp['d']['results'][0]['SiteID']

#  print("------*****LooKUP*****-------")
#  print (resp)
  resp.clear()
  print (len(resp))
#----------------------------------------------------------------------------------------------------#  
  s = requests.Session()
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic Provide Basic Authorization here'})
  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_PRODUCT_LKP_SRV/Deliveries?sap-client=210&$filter=SiteID eq '" + store + "' and ArticleNumber eq '" + anumber + "' and Action eq 'DTODAY'&$format=json", verify=False)

  print (r.text)
  s.close()
  resp = json.loads(r.text)

# print("------*****LooKUP*****-------")
  
  print("  testing ", len(resp['d']['results']))
  
  length = len(resp['d']['results'])
  stringvar = ''
  for i in range(length):
    stringvar = stringvar + "\n\nDocument Number : " + (resp['d']['results'][i]['DocumentNumber']) + "\nDocument Type : " + resp['d']['results'][i]['ReceiptType'] + "\nQuantity : " + resp['d']['results'][i]['Quantity'] + ' ' + resp['d']['results'][i]['Unit']

#----------------------------------------------------------------------------------------------------#  
   
  return jsonify(
    status=200,
    replies=[{
      'type': 'text',
      'content' : stringvar
    }],
    conversation = {
        'memory' : {
            # push EAN to the buffer
            'articlenumber' : anumber,
            'articlenumber1' : anumber
            }
    }
  )

@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)

app.run(port=port, debug=False)
