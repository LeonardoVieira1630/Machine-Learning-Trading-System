import backtrader as bt

class MLStrategy(bt.Strategy):
    """
    Machine Learning-based Long-only Trading Strategy.

    This strategy uses machine learning predictions to determine when to enter
    a long position. It buys if the next day's prediction is positive.

    Parameters:
        - None

    Attributes:
        - data_predicted (bt.DataLine): Series of machine learning predictions.
        - data_open (bt.DataLine): Series of open prices.
        - data_close (bt.DataLine): Series of close prices.
        - order (bt.Order): Pending order object.
        - price (float): Last executed price.
        - comm (float): Last executed commission.

    Methods:
        - __init__: Initializes the strategy.
        - log: Logging function to print timestamped messages.
        - notify_order: Handles order notifications.
        - notify_trade: Handles trade notifications.
        - next_open: Executes the strategy logic on the next open.

    Usage:
        Instantiate this strategy and add it to a Backtrader Cerebro engine.
    """

    params = dict()

    def __init__(self):
        """
        Initialize the strategy.

        Initializes necessary variables to keep track of prices, predictions, and orders.
        """
        self.data_predicted = self.datas[0].predicted
        self.data_open = self.datas[0].open
        self.data_close = self.datas[0].close
        self.order = None
        self.price = None
        self.comm = None

    def log(self, txt):
        """
        Logging function to print timestamped messages.

        Parameters:
            - txt (str): Message to be logged.
        """
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')

    def notify_order(self, order):
        """
        Handles order notifications.

        Parameters:
            - order (bt.Order): The order object.
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Order already submitted/accepted - no action required
            return

        # Report executed order
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}')
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log(f'SELL EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}')

        # Report failed order
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Failed')

        # Set no pending order
        self.order = None

    def notify_trade(self, trade):
        """
        Handles trade notifications.

        Parameters:
            - trade (bt.Trade): The trade object.
        """
        if not trade.isclosed:
            return
        self.log(f'OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')

    def next_open(self):
        """
        Executes the strategy logic on the next open.

        Determines whether to enter a long position based on machine
        learning predictions.
        """
        if not self.position:
            if self.data_predicted > 0:
                # Calculate the max number of shares ('all-in')
                size = int(self.broker.getcash() / self.datas[0].open)
                # Buy order
                self.log(f'LONG CREATED --- Size: {size}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                self.buy(size=size)
        else:
            if self.data_predicted < 0:
                # Sell order
                self.log(f'SELL CREATED --- Size: {self.position.size}')
                self.sell(size=self.position.size)
