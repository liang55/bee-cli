# -*- coding: utf-8 -*-
import requests
import json
import time

DEBUG_API='http://localhost:1635'
MIN_AMOUNT=1000

def getPeers():
	cheque_url="%s/chequebook/cheque"%(DEBUG_API)
	rtn_content = requests.get(cheque_url).json()
	lastcheques=rtn_content.get('lastcheques')
	peers=[]
	for info in lastcheques:
		peers.append(info.get('peer'))
	print('chequebook:',str(len(peers)),peers)
	return peers

def getCumulativePayout(peer) :
	cheque_url="%s/chequebook/cheque/%s"%(DEBUG_API,peer)
	rtn_content = requests.get(cheque_url).json()
	#print(rtn_content)
	lastreceived=rtn_content.get('lastreceived')
	cumulativePayout=None
	if lastreceived:
		cumulativePayout=lastreceived.get('payout')
	if cumulativePayout:
		return cumulativePayout
	else:
		return 0

def getLastCashedPayout(peer):
	cashout_url="%s/chequebook/cashout/%s"%(DEBUG_API,peer)
	rtn_content = requests.get(cashout_url).json()		
	cashout=rtn_content.get('cumulativePayout')
	#print(rtn_content)
	if cashout:
		return cashout
	else:
		return 0	 

def getUncashedAmount(peer):
	cumulativePayout=getCumulativePayout(peer)
	if cumulativePayout == 0:
		return 0
	else:
		cashedPayout=getLastCashedPayout(peer)
		uncashedAmount=cumulativePayout-cashedPayout
		return uncashedAmount

def listAllUncashed():
	peers=getPeers()
	for peer in peers:
		uncashedAmount=getUncashedAmount(peer)
		if uncashedAmount > 0:
			print(peer,uncashedAmount)

def cashout(peer):
	cashout_url="%s/chequebook/cashout/%s"%(DEBUG_API,peer)
	rtn_content = requests.post(cashout_url).json()
	txHash=rtn_content.get('transactionHash')
	print('cashing out cheque for %s in transaction %s'%(peer,txHash))

	result= requests.get(cashout_url).json().get('result')
	while  1:
		if result:
			break
		time.sleep(5)
		result= requests.get(cashout_url).json().get('result')
		if result:
			break


def cashoutAll(minAmount):
	peers=getPeers()
	for peer in peers:
		uncashedAmount=getUncashedAmount(peer)
		if uncashedAmount > minAmount:
			print ("uncashed cheque for %s %s uncashed"%(peer,str(uncashedAmount)) )
			cashout(peer)

if __name__ == '__main__':
	#listAllUncashed()
	cashoutAll(MIN_AMOUNT)