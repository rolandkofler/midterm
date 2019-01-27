from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime # For datetime objects
import os.path  # To manage paths
import sys      # To find out the script name (in argv[0])
import backtrader as bt

# TODO: Taxes must be integrated in the decision. Especially the Haltefrist
# TODO: You cant cash out 2.5 Million in one row
# TODO: really the closeprice against the moving average?


# Create a Stratey
class MovingAverageStrategy(bt.Strategy):

    # Parameters: moving average period to 12 ticks
    params = (
        ('maperiod', 12),
        ('tolerance', 0)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        #self.sma = bt.indicators.SimpleMovingAverage(  self.datas[0], period = self.params.maperiod)
        # self.sma2 = bt.indicators.SimpleMovingAverage( self.datas[1], period = self.params.maperiod)

        # Indicators for the plotting show
        self.cross = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod, subplot=False)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        #bt.indicators.StochasticSlow(self.datas[0])
        #bt.indicators.MACDHisto(self.datas[0])
        #rsi = bt.indicators.RSI(self.datas[0])
        #bt.indicators.SmoothedMovingAverage(rsi, period=10)
        #bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):# -*- coding: utf-8 -*-

        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.cross[0] + self.params.tolerance:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.cross[0] - self.params.tolerance:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MovingAverageStrategy, maperiod=18)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath("midterm/"))
    data0path = os.path.join(modpath, 'kraken-btceur.csv')
    
    # Create a Data Feed
    data0 = bt.feeds.GenericCSVData(
        dataname=data0path,
        # Do not pass values before this date
        fromdate=datetime.datetime(2016, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2025, 1, 14),
        dtformat=('%Y-%m-%d'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1)
    
    #LOG    
    data0.plotinfo.plotlog = True
    data0.plotinfo.plotylimited = False

    # Add the Data Feed to Cerebro
    cerebro.adddata(data0)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

    # Kraken is assumed to have 0.26% commission
    KrakenCommission = 0 #0.26/100
    # Set the commission, since the margin parameter is False, it is a percentage
    cerebro.broker.setcommission(commission=KrakenCommission, margin=False, mult=1)

    # remember the starting conditions   
    startValue= cerebro.broker.getvalue()

    # Run over everything
    cerebro.run()
    
    # print the starting conditions
    print ( '{:>30s} {:>15,.2f}'.format('Starting Portfolio Value:', startValue))
    
    # Print out the final result
    finalValue = cerebro.broker.getvalue()
    print ('{:>30s} {:>15,.2f}'.format('Final Portfolio Value:', finalValue))

    # print the difference
    print ('{:>30s} {:>15,.2f}'.format('Difference Portfolio Value:', finalValue - startValue))

    # Plot the result
    cerebro.plot()