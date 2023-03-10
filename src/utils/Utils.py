import calendar
import logging
import math
import time
import uuid
from datetime import datetime

from config.Config import get_holidays
from models.Direction import Direction
from trademgmt.TradeState import TradeState

class Utils:
  
  dateFormat = "%Y-%m-%d"
  timeFormat = "%H:%M:%S"
  dateTimeFormat = "%Y-%m-%d %H:%M:%S"
  
  @staticmethod
  def roundToNSEPrice(price):
    """
    Rounds the given price to the nearest multiple of 0.05, which is a typical price tick size used in the National Stock Exchange (NSE).
    
    Args:
    price (float): The price to be rounded.
    
    Returns:
    float: The rounded price.
    """
    
    x = round(price, 2) * 20
    y = math.ceil(x)
    return y / 20

  @staticmethod
  def roundOff(price):  # Round off to 2 decimal places
    return round(price, 2)

  @staticmethod
  def isMarketOpen():
    """
    Determines whether the stock market is currently open or closed based on the current date and time.
    
    Returns:
    bool: True if the market is open, False otherwise.
    """
    
    if Utils.isTodayHoliday():
      return False
    now = datetime.now()
    marketStartTime = Utils.getMarketStartTime()
    marketEndTime = Utils.getMarketEndTime()
    return now >= marketStartTime and now <= marketEndTime

  @staticmethod
  def isMarketClosedForTheDay():
    """
    Determine whether the market is closed for the day based on the current time and the market end time,
    as determined by the `getMarketEndTime` function in the `Utils` module.
    
    Returns:
        A boolean value indicating whether the market is closed for the day.
        
    Raises:
        None
    """
    # This method returns true if the current time is > marketEndTime
    # Please note this will not return true if current time is < marketStartTime on a trading day
    if Utils.isTodayHoliday():
      return True
    now = datetime.now()
    marketEndTime = Utils.getMarketEndTime()
    return now > marketEndTime

  @staticmethod
  def waitTillMarketOpens(context):
    """
    Wait until the market opens, as determined by the `getMarketStartTime` function in the `Utils` module.
    
    Args:
        context: A string representing the context in which the method is being called. This could be used
                 for logging purposes.
                 
    Returns:
        None
        
    Raises:
        None
    """
    nowEpoch = Utils.getEpoch(datetime.now())
    marketStartTimeEpoch = Utils.getEpoch(Utils.getMarketStartTime())
    waitSeconds = marketStartTimeEpoch - nowEpoch
    if waitSeconds > 0:
      logging.info("%s: Waiting for %d seconds till market opens...", context, waitSeconds)
      time.sleep(waitSeconds)

  @staticmethod
  def getEpoch(datetimeObj = None):
    # This method converts given datetimeObj to epoch seconds
    if datetimeObj == None:
      datetimeObj = datetime.now()
    epochSeconds = datetime.timestamp(datetimeObj)
    return int(epochSeconds) # converting double to long

  @staticmethod
  def getMarketStartTime():
    return Utils.getTimeOfToDay(9, 15, 0)

  @staticmethod
  def getMarketEndTime():
    return Utils.getTimeOfToDay(15, 30, 0)

  @staticmethod
  def getTimeOfToDay(hours, minutes, seconds):
    datetimeObj = datetime.now()
    datetimeObj = datetimeObj.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
    return datetimeObj

  @staticmethod
  def getTodayDateStr():
    now = datetime.now()
    return now.strftime(Utils.dateFormat)

  @staticmethod
  def isTodayHoliday():
    now = datetime.now()
    dayOfWeek = calendar.day_name[now.weekday()]
    if dayOfWeek == 'Saturday' or dayOfWeek == 'Sunday':
      return True

    todayDate = Utils.getTodayDateStr()
    holidays = get_holidays()
    if (todayDate in holidays):
      return True
    else:
      return False

  @staticmethod
  def generateTradeID():
    return str(uuid.uuid4())

  @staticmethod
  def calculateTradePnl(trade):
    if trade.tradeState == TradeState.ACTIVE:
      if trade.cmp > 0:
        if trade.direction == Direction.LONG:
          trade.pnl = Utils.roundOff(trade.filledQty * (trade.cmp - trade.entry))
        else:  
          trade.pnl = Utils.roundOff(trade.filledQty * (trade.entry - trade.cmp))
    else:
      if trade.exit > 0:
        if trade.direction == Direction.LONG:
          trade.pnl = Utils.roundOff(trade.filledQty * (trade.exit - trade.entry))
        else:  
          trade.pnl = Utils.roundOff(trade.filledQty * (trade.entry - trade.exit))
    tradeValue = trade.entry * trade.filledQty
    if tradeValue > 0:
      trade.pnlPercentage = Utils.roundOff(trade.pnl * 100 / tradeValue)
    return trade
