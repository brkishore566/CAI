
from __future__ import print_function
from flask import Flask, request, jsonify
import json
import requests
from requests.auth import HTTPBasicAuth
from word2number import w2n
import os
#import cv2
import sys

#import pyzbar.pyzbar as pyzbar
#import numpy as np
#import cv2


app = Flask(__name__)
port = '5000'

def decode(im) :
  # Find barcodes and QR codes
  decodedObjects = pyzbar.decode(im)

  # Print results
  for obj in decodedObjects:
    print ('rin')
    print('Type : ', obj.type)
    print('Data : ', obj.data,'\n')

  return decodedObjects


# Display barcode and QR code location
def display(im, decodedObjects):

  # Loop over all decoded objects
  for decodedObject in decodedObjects:
    points = decodedObject.polygon

    # If the points do not form a quad, find convex hull
    if len(points) > 4 :
      hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
      hull = list(map(tuple, np.squeeze(hull)))
    else :
      hull = points;

    # Number of points in the convex hull
    n = len(hull)

    # Draw the convext hull
    for j in range(0,n):
      cv2.line(im, hull[j], hull[ (j+1) % n], (255,0,0), 3)




@app.route('/scanner', methods=['POST'])
def index():

  cv2.namedWindow('ImageWindowName', cv2.WINDOW_NORMAL)
  p = 0
  video_capture = cv2.VideoCapture(0)
  while True:
    ret, frame = video_capture.read()
    decodedObjects = decode(frame)

    cv2.imshow('ImageWindowName', frame)
    for obj in decodedObjects:
      print ('hello')
      print('Type : ', obj.type)
      print('Data : ', obj.data,'\n')
      rin = obj.data
      rin1 = obj.type
      print ('This is rinnegannnn' , rin)
      p = 1

    if cv2.waitKey(1) & 0xFF == ord('q') or p ==1:
        break

  video_capture.release()
  cv2.destroyAllWindows()
  s = requests.Session()
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic SlVERTpDQUxFQlRIRW1hbjAwNw=='})
  r = s.get("https://ldciuyt.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Products('" + rin + "')?$format=json", verify=False)
  token = r.headers['x-csrf-token']
  resp = json.loads(r.text)
  return jsonify(
    status=200,
    replies=[{
      'type': 'text',
      'content' : "Product Number of the article is :\n" + resp['d']['ProductNumber'] + "\n\nDescription of the article : \n" + (resp['d']['Description']) + "\n\nBarcode type : \n" + rin1 + "\n\nBase EAN : \n" + resp['d']['BaseEan'] + "\n\n Stock Quantity : \n" + resp['d']['StockQuantity']
    }],
    conversation = {
        'memory' : {
            'articlenumber' : rin,
            'csrf' : token,
            'EAN' : resp['d']['BaseEan']
            }
    }
  )

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
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic SlVERTpXZWxjb21lMSE='})
  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_srv/Products?$filter=Description%20eq%20%27"+anumber+"%27&$format=json", verify=False)
#  r = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Products('" + anumber + "')?$format=json", verify=False)
  print (r.text)
  token = r.headers['x-csrf-token']
  s.close()
  resp = json.loads(r.text)

  print("-------------")
  print (resp)
  return jsonify(
    status=200,
    replies=[{
      'type': 'text',
      'content' : "Product Number of the article is :\n" + resp['d']['results'][0]['ProductNumber'] + "\n\nDescription of the article : \n" + (resp['d']['results'][0]['Description']) + "\n\nBase EAN : \n" + resp['d']['results'][0]['BaseEan'] + "\n\n Stock Quantity : \n" + resp['d']['results'][0]['StockQuantity'] + ' ' + resp['d']['results'][0]['BaseUom']
    }],
    conversation = {
        'memory' : {
            'csrf' : token,
            'EAN' : resp['d']['results'][0]['BaseEan'],
            'articlenumber1' : resp['d']['results'][0]['ProductNumber']
            }
    }
  )

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
  s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic SlVERTpDQUxFQlRIRW1hbjAwNw=='})
  r1 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/AddScannedProducts?ScannedEAN='" + EAN + "'&$format=json", verify=False)
  token = r1.headers['x-csrf-token']

  #Getting all the storage locations associated with the article.
  s.headers.update({'X-CSRF-Token': 'Fetch' , 'Authorization' : 'Basic SlVERTpDQUxFQlRIRW1hbjAwNw=='})
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

    except:
        anumber = data['conversation']['memory']['articlenumber1']
        print(anumber)


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
    s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic SlVERTpXZWxjb21lMSE='})
    r1 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/Products('" + anumber + "')?$format=json", verify=False)
    print (r1.text)
    # token = r1.headers['x-csrf-token']
    # print(token)



    s.headers.update({'X-CSRF-Token': 'Fetch', 'Authorization' : 'Basic SlVERTpXZWxjb21lMSE=', 'Connection' : 'keep-alive'})
    r2 = s.get("https://ldciuyr.wdf.sap.corp:44300/sap/opu/odata/SAP/RETAILSTORE_STOCK_CORR_SRV/AddScannedProducts?ScannedEAN='" + EAN + "'&$format=json", verify=False)
    print (r2.text)
    token = r2.headers['x-csrf-token']
    resp1 = json.loads(r2.text)

    s.headers.update({'x-csrf-token': token , 'Authorization' : 'Basic SlVERTpXZWxjb21lMSE=','Content-type': 'application/json', 'Connection' : 'keep-alive', 'Accept': 'application/json'})
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
      ]
      # ,
      # conversation = {
      #     'memory' : {
      #           'csrf'  : token
      # #         'articlenumber' : anumber,
      # #         'StorageLen' : SLnumber,
      # #         'SLocations' : StorageLocations
      #         }
      # }
    )



@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)

app.run(port=port, debug=True)
