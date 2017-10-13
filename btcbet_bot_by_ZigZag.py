#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Example of using API btcbet.cc 
# Link to server: https://btcbet.cc/r/07RBg5
# Author: ZigZagBet@mail.ru
# Tested on Python 3.6
# BTC wallet to make donations 1KGL83H2Xtw8rnnCpDenf4ZqwhtQSpEYWX

import requests
from sys import exc_info,stdout
from datetime import datetime
import logging
from time import sleep
from  logging import handlers
import json
    
class btcbet_api():
    
    #API key 
    #Replace with your own generated on https://btcbet.cc/r/07RBg5
    #Required
    key = "INSERT_HERE_YOUR_API_KEY"    
    
    #Telegram bot unique authentication token 
    #see https://core.telegram.org/bots/api
    #Replace with with your own
    #Optional
    bot_uat = "INSERT_HERE_YOUR_BOT_UNIQUE_AUTHENTICATION_TOKEN_STRING" 
                        
    #Your personal chat with registered bot
    #Required to filter possible messages from other people
    #Replace with with your own
    #Optional                                                                 
    chat_id = 000000000
    
    info =  {}
    lastTelegramMsgId = 0
    stopBet = False 
    
    def sendMessage(self,message):
        requests.post("https://api.telegram.org/bot%s/sendMessage" % (self.bot_uat), data={'chat_id':self.chat_id,'text':message,'parse_mode':'HTML'})
    
    #Some simple commands for Telegram bot      
    #stopbet - Stop betting
    #startbet - Start betting  
    def checkTelegramRequest(self):
        try:
            if len(self.bot_uat) != 55: # Some check if correct unique authentication token was not insert
                offset = -1 if self.lastTelegramMsgId == 0 else self.lastTelegramMsgId 
                updates = json.loads(requests.post("https://api.telegram.org/bot%s/getUpdates" % (self.bot_uat), data={'allowed_updates':'message','offset':str(offset)}).text)
                lastmsg = updates['result'][-1]
                if (lastmsg['message']['from']['id'] == self.chat_id):
                    msg = lastmsg['message']['text'].lower()
                    if msg == 'hello':
                        self.sendMessage("<em>Hello!</em>")
                    elif msg == '/start':
                        pass
                    elif msg == 'stopbet':
                        self.stopBet = True
                        self.sendMessage("<em>Betting stopped!</em>") 
                    elif msg == 'startbet':
                        self.stopBet = False    
        except Exception:
            logger.warn("checkTelegramRequest %s: %s" % (exc_info()[0], exc_info()[1]))            
        
    def getPeriodInfo(self,id=""):
        try:
            self.info = requests.get("https://btcbet.cc/api/public/%s" % (id)).json()
            return self.info['timer']
        except Exception:
            logger.warn("getPeriodInfo %s: %s" % (exc_info()[0], exc_info()[1]))
            return -1
    
    # make bet   
    def make_bet(self,session_id,amount,where):
        try:
            if (self.stopBet == False):
                json = requests.post("https://btcbet.cc/make_bet/",data={'session_id' : session_id, 'key' : self.key, 'amount' : amount, 'where' : where}).json()
            return json
        except Exception:
            return {'status':0,'error_message':'%s: %s' % (exc_info()[0], exc_info()[1])}

#Main loop
def main():
        while True:
            try:
                if (bb.getPeriodInfo() > 0):
                    #calculate seconds before period will be closed
                    timeleft = (datetime.strptime(bb.info['period_from'], '%Y-%m-%dT%H:%M:%S.%fZ') - datetime.strptime(bb.info['date'], '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() + 300
                    #fix current session id
                    session_id = bb.info['id']
                    logger.warn("Session %s: Time before closed - %.3f sec" % (session_id,timeleft))
                    #wait timeleft - 2 sec
                    sleep(timeleft-2)
                    if (bb.getPeriodInfo(session_id) > 0):
                        # !!!!!!!!!!!! Make bet here !!!!!!!!!!!!!
                        # print current session information
                        logger.warn("Session %s: %s" % (bb.info['id'],bb.info))
                        
                        # Next block just for example. Replace with you own logic
                        # Start 
                        
                        # bet UP 0.001 BTC if somebody make opposite bet
                        #if bb.info['count_d'] > 0:
                        #    logger.warn("Bet Up: %s" % (bb.make_bet(session_id,0.001, 1))) 
                        
                        # bet DOWN 0.001 BTC if somebody make opposite bet
                        #if bb.info['count_u'] > 0:
                        #    logger.warn("Bet Down: %s" % (bb.make_bet(session_id,0.001, 0))) # bet DOWN 0.001 BTC
                        # End  
                         
                    else:
                        logger.warn("Session already closed or connection error")
                 
                sleep(10) # wait next period 
                bb.checkTelegramRequest()
            except Exception:
                logger.warn("main while %s: %s" % (exc_info()[0], exc_info()[1]))

if __name__ == '__main__':
   
    logger = logging.getLogger()
    logger.setLevel(logging.WARN)
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    # print to stdout
    ch = logging.StreamHandler(stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # save to log file
    ch1 = handlers.TimedRotatingFileHandler('btcbet_bot.log', when='D', interval=1, backupCount=7,encoding='utf-8')
    ch1.setFormatter(formatter)
    logger.addHandler(ch1)
    
    bb = btcbet_api()
    main() 
