"""
    checkout:
        - strategy specific docs here : https://algobulls.github.io/pyalgotrading/strategies/macd_crossover/
        - generalised docs in detail here : https://algobulls.github.io/pyalgotrading/strategies/strategy_guides/common_strategy_guide/
"""


class MACDCrossover(StrategyBase):
    name = 'MACD Crossover'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timeperiod_fast = self.strategy_parameters['TIMEPERIOD_FAST']
        self.timeperiod_slow = self.strategy_parameters['TIMEPERIOD_SLOW']
        self.timeperiod_signal = self.strategy_parameters['TIMEPERIOD_SIGNAL']
        self.main_order_map = None

    def initialize(self):
        self.main_order_map = {}

    def get_crossover(self, instrument):
        hist_data = self.get_historical_data(instrument)
        macdline, macdsignal, _ = talib.MACD(hist_data['close'], fastperiod=self.timeperiod_fast, slowperiod=self.timeperiod_slow, signalperiod=self.timeperiod_signal)
        crossover_value = self.utils.crossover(macdline, macdsignal)
        return crossover_value

    def strategy_select_instruments_for_entry(self, candle, instruments_bucket):
        selected_instruments, meta = [], []

        for instrument in instruments_bucket:
            if self.main_order_map.get(instrument) is None:
                crossover = self.get_crossover_value(instrument)
                action_constants = {1: 'BUY', -1: 'SELL'}

                if crossover in [-1, 1]:
                    selected_instruments.append(instrument)
                    meta.append({'action': action_constants[crossover]})

        return selected_instruments, meta

    def strategy_enter_position(self, candle, instrument, sideband_info):
        self.main_order_map[instrument] = _ = self.broker.OrderRegular(instrument, sideband_info['action'], quantity=self.number_of_lots * instrument.lot_size)
        return _

    def strategy_select_instruments_for_exit(self, candle, instruments_bucket):
        selected_instruments, meta = [], []

        for instrument in instruments_bucket:
            if self.main_order_map.get(instrument) is not None:
                crossover = self.get_crossover(instrument)
                if crossover in [1, -1]:
                    selected_instruments.append(instrument)
                    meta.append({'action': 'EXIT'})

        return selected_instruments, meta

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order_map[instrument].exit_position()
            self.main_order_map[instrument] = None
            return True

        return False
