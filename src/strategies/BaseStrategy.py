import logging
import time
from datetime import datetime

from models.ProductType import ProductType
from core.Quotes import Quotes
from trademgmt.TradeManager import TradeManager

from utils.Utils import Utils

class BaseStrategy:
  def __init__(self, name):
    # NOTE: All the below properties should be set by the Derived Class (Specific to each strategy)
    self.name = name # strategy name
    self.enabled = True # Strategy will be run only when it is enabled
    self.productType = ProductType.MIS # MIS/NRML/CNC etc
    self.symbols = [] # List of stocks to be traded under this strategy
    self.slPercentage = 0
    self.targetPerncetage = 0
    self.startTimestamp = Utils.getMarketStartTime() # When to start the strategy. Default is Market start time
    self.stopTimestamp = None # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
    self.squareOfTimestamp = None # Square off time
    self.capital = 10000 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
    self.leverage = 1 # 2x, 3x Etc
    self.maxTradesPerDay = 1 # Max number of trades per day under this strategy
    self.isFnO = False # Does this strategy trade in FnO or not
    self.capitalPerSet = 0 # Applicable if isFnO is True (Set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
    self.tradesCreatedSymbols = [] # Add symbol to this list when a trade is created
    # Register strategy with trade manager
    TradeManager.registerStrategy(self)

  def getName(self):
    return self.name

  def isEnabled(self):
    return self.enabled

  def setDisabled(self):
    self.enabled = False

  def process(self):
    # Implementation is specific to each strategy - To defined in derived class
    logging.info("BaseStrategy process is called.")
    pass

  def calculateCapitalPerTrade(self):
    capitalPerTrade = int(self.capital * self.leverage / self.maxTradesPerDay)
    return capitalPerTrade

  def canTradeToday(self):
    # Derived class should override the logic if the strategy to be traded only on specific days of the week
    return True

  def run(self):
    # NOTE: This should not be overriden in Derived class
    if self.enabled == False:
      logging.warn("%s: Not going to run strategy as its not enabled.", self.getName())
      return

    if Utils.isMarketClosedForTheDay():
      logging.warn("%s: Not going to run strategy as market is closed.", self.getName())
      return

    now = datetime.now()
    if now < Utils.getMarketStartTime():
      Utils.waitTillMarketOpens(self.getName())

    if self.canTradeToday() == False:
      logging.warn("%s: Not going to run strategy as it cannot be traded today.", self.getName())
      return

    if now < self.startTimestamp:
      waitSeconds = now - self.startTimestamp
      logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...", self.getName(), waitSeconds)
      time.sleep(waitSeconds)      

    # Run in an loop and keep processing
    while True:
      if Utils.isMarketClosedForTheDay():
        logging.warn("%s: Exiting the strategy as market closed.", self.getName())
        break

      # Derived class specific implementation will be called when process() is called
      self.process()

      # Sleep and wake up on every 30th second
      now = datetime.now()
      waitSeconds = 30 - (now.second % 30) 
      time.sleep(waitSeconds)

  def shouldPlaceTrade(self, trade, tick):
    # Each strategy should call this function from its own shouldPlaceTrade() method before working on its own logic
    if trade == None:
      return False
    if trade.qty == 0:
      return False
    numOfTradesPlaced = TradeManager.getNumberOfTradesPlacedByStrategy(self.getName())
    if numOfTradesPlaced >= self.maxTradesPerDay:
      TradeManager.disableTrade(trade, 'MaxTradesPerDayReached')
      return False

    return True

  def getQuote(self, tradingSymbol):
    return Quotes.getQuote(tradingSymbol)