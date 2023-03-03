

class BrokerAppDetails:
  def __init__(self, broker):
    self.broker = broker

  def setClientID(self, clientID):
    self.clientID = clientID

  def setAppKey(self, appKey):
    self.appKey = appKey

  def setAppSecret(self, appSecret):
    self.appSecret = appSecret

  def setTOTP(self,totp_key):
    self.totp_key = totp_key