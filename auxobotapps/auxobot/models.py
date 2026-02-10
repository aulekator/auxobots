from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedTextField
from decimal import Decimal
from django.utils import timezone

INSTRUMENT_CHOICES = [
    ('SOLUSDT', 'SOLUSDT (High Volatility)'),
    ('DOGEUSDT', 'DOGEUSDT (Meme Coin)'),
    ('ETHUSDT', 'ETHUSDT'),
    ('BTCUSDT', 'BTCUSDT'),
    ('BNBUSDT', 'BNBUSDT'),
    ('ADAUSDT', 'ADAUSDT'),
    ('XRPUSDT', 'XRPUSDT'),
    ('PEPEUSDT', 'PEPEUSDT (Extreme Volatility)'),
    ('1000SHIBUSDT', '1000SHIBUSDT'),
]

EXCHANGE_CHOICES = [
    ('binance', 'Binance'),
    ('bybit', 'Bybit'),
    ('kucoin', 'KuCoin'),
    ('okx', 'OKX'),
    ('gateio', 'Gate.io'),
    ('ftx', 'FTX'),
    ('kraken', 'Kraken'),
    ('coinbase', 'Coinbase Pro'),
    ('huobi', 'Huobi'),
    ('bitfinex', 'Bitfinex'),
    ('poloniex', 'Poloniex'),
    ('bittrex', 'Bittrex'),
    ('bitstamp', 'Bitstamp'),
]

RISK_CHOICES = [
    ('low', 'Low Risk'),
    ('medium', 'Medium Risk'),
    ('high', 'High Risk'),
]

class BotConfig(models.Model):

    """Live Trading Bot Configuration"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_bot_configs')
    exchange = models.CharField(max_length=20, choices=EXCHANGE_CHOICES, default='binance')
    api_key = EncryptedTextField()
    api_secret = EncryptedTextField()
    instrument = models.CharField(max_length=20, choices=INSTRUMENT_CHOICES, default='SOLUSDT', help_text="Select the perpetual futures pair for grid trading")
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custom_quantity = models.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True,help_text="Custom order quantity per grid level (overrides risk default)")
    total_pnl = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'),help_text="Total realized + unrealized PnL in USDT")
    realized_pnl = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'),help_text="Realized PnL from closed trades")
    unrealized_pnl = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'),help_text="Unrealized PnL from open positions")
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Win rate percentage")
    total_trades = models.PositiveIntegerField(default=0)
    class Meta:
        app_label = 'auxobot'
        unique_together = ('user', 'exchange', 'instrument')

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username} - {self.exchange.upper()} - {self.get_instrument_display()} ({status})"


class DemoBotConfig(models.Model):

    """Demo/Paper Trading Bot Configuration"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='demo_bot_config')
    exchange = models.CharField(max_length=20, choices=EXCHANGE_CHOICES, default='binance')
    demo_api_key = EncryptedTextField(blank=True, null=True)
    demo_api_secret = EncryptedTextField(blank=True, null=True)
    instrument = models.CharField(max_length=20, choices=INSTRUMENT_CHOICES, default='SOLUSDT')
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wallet_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0.00000000'))
    total_pnl = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'),)
    realized_pnl = models.DecimalField(max_digits=18,decimal_places=8,default=Decimal('0.00000000'),)
    unrealized_pnl = models.DecimalField(max_digits=18,decimal_places=8, default=Decimal('0.00000000'),)
    custom_quantity = models.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True,help_text="Custom order quantity per grid level (overrides risk default)")
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'),)
    total_trades = models.PositiveIntegerField(default=0)
    high_risk_accepted = models.BooleanField(default=False, help_text="User has confirmed high risk for small accounts (<$200)")

    class Meta:
        app_label = 'auxobot'

    def __str__(self):
        status = "Active" if self.is_active else "Stopped"
        return f"{self.user.username} - Demo ({self.get_instrument_display()} - {status})"
    
    
class ExtraConfig(models.Model):
    """User-specific extra configuration like approximate mid prices for grid centering"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extra_config')

    # User-editable approximate mid prices (used when bot starts)
    price_sol = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('130.00'), verbose_name="SOLUSDT Approx Price")
    price_doge = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0.150000'), verbose_name="DOGEUSDT Approx Price")
    price_eth = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('3400.00'), verbose_name="ETHUSDT Approx Price")
    price_btc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('68000.00'), verbose_name="BTCUSDT Approx Price")
    price_bnb = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('600.00'), verbose_name="BNBUSDT Approx Price")
    price_ada = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.6000'), verbose_name="ADAUSDT Approx Price")
    price_xrp = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.6500'), verbose_name="XRPUSDT Approx Price")
    price_pepe = models.DecimalField(max_digits=12, decimal_places=8, default=Decimal('0.00001200'), verbose_name="PEPEUSDT Approx Price")
    price_shib = models.DecimalField(max_digits=12, decimal_places=8, default=Decimal('0.00002500'), verbose_name="1000SHIBUSDT Approx Price")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extra Config - {self.user.username}"

    class Meta:
        app_label = 'auxobot'
        verbose_name = "Extra Configuration"
        verbose_name_plural = "Extra Configurations"

    # Helper to get price by instrument
    def get_price_for_instrument(self, instrument):
        mapping = {
            'SOLUSDT': self.price_sol,
            'DOGEUSDT': self.price_doge,
            'ETHUSDT': self.price_eth,
            'BTCUSDT': self.price_btc,
            'BNBUSDT': self.price_bnb,
            'ADAUSDT': self.price_ada,
            'XRPUSDT': self.price_xrp,
            'PEPEUSDT': self.price_pepe,
            '1000SHIBUSDT': self.price_shib,
        }
        return mapping.get(instrument, Decimal('100.00'))  # fallback
    
class DemoTrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demo_trades')
    instrument = models.CharField(max_length=20)  # e.g. 'SOLUSDT'
    side = models.CharField(max_length=10)  # 'BUY' or 'SELL'
    price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=3)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'auxobot'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.side} {self.quantity} {self.instrument} @ {self.price} | {self.timestamp}"
    

class LiveTrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_trades')
    instrument = models.CharField(max_length=20)  # e.g. 'SOLUSDT'
    side = models.CharField(max_length=10)  # 'BUY' or 'SELL'
    price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=3)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'auxobot'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.side} {self.quantity} {self.instrument} @ {self.price} | {self.timestamp}"

class DemoBotLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demo_bot_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    level = models.CharField(max_length=20, default='INFO')  

    class Meta:
        app_label = 'auxobot'
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['user', '-timestamp'])]

    def __str__(self):
        return f"[{self.level}] {self.timestamp} {self.user.username}: {self.message}"
    
class LiveBotLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_bot_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    level = models.CharField(max_length=20, default='INFO')  

    class Meta:
        app_label = 'auxobot'
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['user', '-timestamp'])]

    def __str__(self):
        return f"[{self.level}] {self.timestamp} {self.user.username}: {self.message}"