import os
import uuid
import tempfile
import csv
from pathlib import Path
from .forms import BotConfigForm
from .models import BotConfig
from .models import DemoBotConfig
from .models import LiveTrade
from .models import LiveBotLog
from .models import ExtraConfig
from .models import DemoBotLog
from .models import EXCHANGE_CHOICES
from .models import INSTRUMENT_CHOICES
from .models import RISK_CHOICES
from .models import DemoTrade
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from auxobotapps.auxobot.core.trading.bactest_bot import run_nautilus_backtest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
from binance.client import Client
from binance.exceptions import BinanceAPIException
import threading
import logging
logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    return render(request, 'auxobot/dashboard.html')

@require_POST
@csrf_exempt 
def run_backtest(request):
    try:
        usdt_balance = Decimal(request.POST.get('usdt_balance', '1000'))
        sol_amount = Decimal(request.POST.get('sol_amount', '0'))  
        grid_levels = int(request.POST.get('grid_levels', '15'))
        trade_size = Decimal(request.POST.get('trade_size', '1.000'))  
        grid_profit = float(request.POST.get('grid_profit', '1.2')) 

        csv_file: UploadedFile = request.FILES.get('csv_file')
        if not csv_file:
            return JsonResponse({
                'success': False,
                'error': 'No CSV file uploaded. Please select a historical data file.'
            }, status=400)

        temp_dir = tempfile.mkdtemp()
        csv_path = Path(temp_dir) / f"backtest_{uuid.uuid4()}.csv"

        with open(csv_path, 'wb') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        results = run_nautilus_backtest(
            usdt_balance=usdt_balance,
            sol_amount=sol_amount,
            grid_levels=grid_levels,
            trade_size=trade_size,
            grid_profit=grid_profit,
            csv_path=csv_path,
        )

        # === Cleanup Temporary File ===
        try:
            os.unlink(csv_path)
            os.rmdir(temp_dir)
        except OSError:
            pass 

        return JsonResponse({
            'success': True,
            'summary': results['summary'],
            'account_report': results['account_report'],
            'performance_report': results['performance_report'],
            'metrics': results['metrics'],
        })

    except ValueError as ve:
        logger.error(f"Validation error in backtest: {ve}")
        return JsonResponse({
            'success': False,
            'error': f"Invalid input: {str(ve)}"
        }, status=400)

    except Exception as e:
        logger.exception("Backtest view failed")
        return JsonResponse({
            'success': False,
            'error': 'Backtest failed. Please check server logs or try again.'
        }, status=500)


@login_required
def bot_setup(request):
    is_demo = request.POST.get('mode') == 'demo' if request.method == 'POST' else False

    if is_demo:
        config, created = DemoBotConfig.objects.get_or_create(user=request.user)
    else:
        config, created = BotConfig.objects.get_or_create(
            user=request.user,
            defaults={'exchange': 'binance'}
        )

    if request.method == 'POST':
        config.exchange = request.POST.get('exchange', config.exchange)
        config.instrument = request.POST.get('instrument', config.instrument)

        if request.POST.get('api_key', '').strip():
            if is_demo:
                config.demo_api_key = request.POST['api_key'].strip()
            else:
                config.api_key = request.POST['api_key'].strip()

        if request.POST.get('api_secret', '').strip():
            if is_demo:
                config.demo_api_secret = request.POST['api_secret'].strip()
            else:
                config.api_secret = request.POST['api_secret'].strip()

        qty = request.POST.get('custom_quantity', '').strip()
        if qty:
            try:
                config.custom_quantity = Decimal(qty)
            except:
                pass
        else:
            config.custom_quantity = None

        config.save()

        mode_name = "Demo" if is_demo else "Live"
        messages.success(request, f"{mode_name} bot configuration saved securely!")

        return redirect('auxobot:dashboard')

    context = {
        'is_demo': is_demo,
        'current_exchange': config.exchange,
        'current_instrument': config.instrument,
        'current_quantity': config.custom_quantity,
        'current_api_key': config.demo_api_key if is_demo else config.api_key,
        'current_api_secret': config.demo_api_secret if is_demo else config.api_secret,
        'exchanges': EXCHANGE_CHOICES,
        'instruments': INSTRUMENT_CHOICES,
    }

    return render(request, 'auxobot/bot_setup.html', context)

@login_required
def demo_trading_dashboard(request):
    config, _ = DemoBotConfig.objects.get_or_create(user=request.user)

    recent_trades = DemoTrade.objects.filter(user=request.user).order_by('-timestamp')[:20]
    recent_logs = DemoBotLog.objects.filter(user=request.user).order_by('-timestamp')[:200]

    open_orders = []
    binance_open_positions = []
    binance_trade_history = []
    unrealized_pnl = Decimal('0.00')
    total_wallet_balance = Decimal('0.00')
    margin_ratio = "0.00%"
    maintenance_margin = Decimal('0.00')
    margin_balance = Decimal('0.00')
    api_error = None
    total_api_orders = 0
    symbol_matched_orders = 0

    if config.demo_api_key and config.demo_api_secret:
        try:
            client = Client(
                api_key=config.demo_api_key,
                api_secret=config.demo_api_secret,
                testnet=True
            )

            instrument = config.instrument.upper().strip()
            symbol = f"{instrument}USDT" if not instrument.endswith('USDT') else instrument

            print(f"DEBUG: Looking for orders with symbol: {symbol}")

            # Account info
            try:
                account = client.futures_account()
                for asset in account['assets']:
                    if asset['asset'] == 'USDT':
                        margin_balance = Decimal(asset['walletBalance'])
                        maintenance_margin = Decimal(asset['maintenanceMargin'])
                        unrealized_pnl = Decimal(asset['unrealizedProfit'])
                        margin_ratio = asset['marginRatio'] if asset['marginRatio'] != '0' else "0.00%"
                        total_wallet_balance = Decimal(asset['availableBalance'])
                        break
            except Exception:
                pass

            # Open orders
            try:
                try:
                    symbol_orders = client.futures_get_open_orders(symbol=symbol)
                except BinanceAPIException as e:
                    if e.code == -1121:
                        symbol_orders = client.futures_get_open_orders()
                    else:
                        raise

                for o in symbol_orders:
                    order_symbol = o.get('symbol', '')
                    if order_symbol.upper() != symbol.upper():
                        continue

                    price = o.get('price', '0')
                    if price in ('0', '0.0', '0.00', '', '0.0000'):
                        price = None
                    else:
                        try:
                            price = Decimal(str(price))
                        except:
                            price = None

                    open_orders.append({
                        'side': o.get('side', 'UNKNOWN'),
                        'type': o.get('type', 'UNKNOWN'),
                        'price': price,
                        'quantity': Decimal(str(o.get('origQty', '0'))),
                        'filled_qty': Decimal(str(o.get('executedQty', '0'))),
                        'status': o.get('status', 'UNKNOWN'),
                        'client_order_id': o.get('clientOrderId', '–'),
                        'symbol': order_symbol,
                    })
            except Exception:
                pass

            try:
                positions = account.get('positions', [])
                for pos in positions:
                    if pos.get('symbol', '').upper() != symbol.upper():
                        continue
                    position_amt = Decimal(str(pos.get('positionAmt', '0')))
                    if position_amt == 0:
                        continue

                    side = "LONG" if position_amt > 0 else "SHORT"
                    qty = abs(position_amt)
                    entry_price = Decimal(str(pos.get('entryPrice', '0')))
                    pos_unreal_pnl = Decimal(str(pos.get('unrealizedProfit', '0')))

                    binance_open_positions.append({
                        'side': side,
                        'quantity': qty,
                        'avg_px_open': entry_price,
                        'unrealized_pnl': pos_unreal_pnl,
                        'unrealized_pnl_pct': (pos_unreal_pnl / (qty * entry_price) * 100) if entry_price > 0 else Decimal('0'),
                    })
                    unrealized_pnl += pos_unreal_pnl
            except Exception:
                pass

            try:
                trades = client.futures_account_trades(symbol=symbol, limit=50)
                for t in trades:
                    binance_trade_history.append({
                        'time': t.get('time'),
                        'side': t.get('side', 'UNKNOWN'),
                        'price': Decimal(str(t.get('price', '0'))),
                        'qty': Decimal(str(t.get('qty', '0'))),
                        'commission': Decimal(str(t.get('commission', '0'))),
                        'commission_asset': t.get('commissionAsset', 'USDT'),
                    })
            except Exception:
                pass

        except Exception:
            pass

    context = {
        'config': config,
        'demo_bot_active': config.is_active,
        'current_instrument_display': config.get_instrument_display(),
        'total_pnl': config.total_pnl,
        'realized_pnl': config.realized_pnl,
        'unrealized_pnl': unrealized_pnl,
        'win_rate': config.win_rate,
        'total_trades': config.total_trades,
        'wallet_balance': total_wallet_balance,
        'open_orders': open_orders,
        'open_positions': binance_open_positions,
        'trade_history': binance_trade_history[:20],
        'margin_ratio': margin_ratio,
        'maintenance_margin': maintenance_margin,
        'margin_balance': margin_balance,
        'api_error': api_error,
        'total_api_orders': total_api_orders,
        'symbol_matched_orders': symbol_matched_orders,
        'recent_trades': recent_trades,
        'recent_logs': recent_logs,
        'exchanges': EXCHANGE_CHOICES,
        'instruments': INSTRUMENT_CHOICES,
        'risk_levels': RISK_CHOICES,
    }

    return render(request, 'auxobot/demo_trading.html', context)

@login_required
def configure_demo_bot(request):
    """
    Handles configuring the demo bot settings.
    Saves settings and sets is_active = True.
    The systemd runner will automatically start or restart the bot.
    """
    config = get_object_or_404(DemoBotConfig, user=request.user)
    extra_config, _ = ExtraConfig.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update basic config
        config.exchange = request.POST.get('exchange') or config.exchange
        config.instrument = request.POST.get('instrument') or config.instrument
        config.risk_level = request.POST.get('risk_level') or config.risk_level

        qty_input = request.POST.get('custom_quantity', '').strip()
        if qty_input:
            try:
                config.custom_quantity = Decimal(qty_input)
            except (InvalidOperation, ValueError):
                pass  # Keep old value if invalid
        else:
            config.custom_quantity = None

        if 'demo_api_key' in request.POST:
            config.demo_api_key = request.POST['demo_api_key'].strip() or None

        if 'demo_api_secret' in request.POST:
            config.demo_api_secret = request.POST['demo_api_secret'].strip() or None

        config.save()

        # Update extra price config
        price_fields = {
            'price_sol': 'SOLUSDT',
            'price_doge': 'DOGEUSDT',
            'price_eth': 'ETHUSDT',
            'price_btc': 'BTCUSDT',
            'price_bnb': 'BNBUSUT',
            'price_ada': 'ADAUSDT',
            'price_xrp': 'XRPUSDT',
            'price_pepe': 'PEPEUSDT',
            'price_shib': '1000SHIBUSDT',
        }

        updated = False
        for field, symbol in price_fields.items():
            value = request.POST.get(field, '').strip()
            if value:
                try:
                    setattr(extra_config, field, Decimal(value))
                    updated = True
                except (InvalidOperation, ValueError):
                    messages.warning(request, f"Invalid price for {symbol}. Ignored.")
        if updated:
            extra_config.save()

        # Set is_active = True so systemd runner starts/restarts the bot
        was_active = config.is_active
        config.is_active = True
        config.save(update_fields=['is_active'])

        # User feedback
        if was_active:
            messages.success(request, "Settings updated! Bot will restart with new config in a few seconds.")
        else:
            messages.success(request, f"Bot configured and start signal sent! Launching in a few seconds...")

        return redirect('auxobot:demo_trading')

    return redirect('auxobot:demo_trading')


@login_required
def start_demo_bot(request):
    """
    Handles the "Start Bot Now" button.
    Only sets the is_active flag.
    The systemd runner will detect it and launch the bot.
    """
    if request.method == 'POST':
        config = get_object_or_404(DemoBotConfig, user=request.user)
        
        if config.is_active:
            messages.info(request, "Bot is already running.")
        else:
            # Quick validation
            if not config.demo_api_key or not config.demo_api_secret:
                messages.error(request, "Please configure API keys first in Settings.")
            elif not config.instrument:
                messages.error(request, "Please select a trading pair.")
            else:
                config.is_active = True
                config.save(update_fields=['is_active'])
                messages.success(request, "Start signal sent! Bot launching in a few seconds...")
        
        return redirect('auxobot:demo_trading')
    
    return redirect('auxobot:demo_trading')


def stop_demo_bot(request):
    if request.method == 'POST':
        config = get_object_or_404(DemoBotConfig, user=request.user)
        if config.is_active:
            config.is_active = False
            config.save(update_fields=['is_active'])
            messages.success(request, "Stop signal sent. Bot will shut down gracefully in a few seconds.")
        else:
            messages.info(request, "Bot is already stopped.")
        return redirect('auxobot:demo_trading')

def download_bot_logs(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    logs = DemoBotLog.objects.filter(user=request.user).order_by('timestamp')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bot_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message'])
    for log in logs:
        writer.writerow([log.timestamp, log.level, log.message])

    return response

#--------------------- end of demo trading function ----------------
#--------------------- live trading function ---------------------------

@login_required
def live_trading_dashboard(request):
    config, _ = BotConfig.objects.get_or_create(user=request.user)

    recent_trades = LiveTrade.objects.filter(user=request.user).order_by('-timestamp')[:20]
    recent_logs = LiveBotLog.objects.filter(user=request.user).order_by('-timestamp')[:200]

    open_orders = []
    binance_open_positions = []
    binance_trade_history = []
    unrealized_pnl = Decimal('0.00')
    total_wallet_balance = Decimal('0.00')
    margin_ratio = "0.00%"
    maintenance_margin = Decimal('0.00')
    margin_balance = Decimal('0.00')
    api_error = None
    total_api_orders = 0
    symbol_matched_orders = 0

    if config.api_key and config.api_secret:
        try:
            client = Client(
                api_key=config.api_key,
                api_secret=config.api_secret,
                testnet=False
            )

            instrument = config.instrument.upper().strip()
            symbol = f"{instrument}USDT" if not instrument.endswith('USDT') else instrument

            print(f"DEBUG: Looking for orders with symbol: {symbol}")

            # Account info
            try:
                account = client.futures_account()
                for asset in account['assets']:
                    if asset['asset'] == 'USDT':
                        margin_balance = Decimal(asset['walletBalance'])
                        maintenance_margin = Decimal(asset['maintenanceMargin'])
                        unrealized_pnl = Decimal(asset['unrealizedProfit'])
                        margin_ratio = asset['marginRatio'] if asset['marginRatio'] != '0' else "0.00%"
                        total_wallet_balance = Decimal(asset['availableBalance'])
                        break
            except Exception:
                pass

            # Open orders
            try:
                try:
                    symbol_orders = client.futures_get_open_orders(symbol=symbol)
                except BinanceAPIException as e:
                    if e.code == -1121:
                        symbol_orders = client.futures_get_open_orders()
                    else:
                        raise

                for o in symbol_orders:
                    order_symbol = o.get('symbol', '')
                    if order_symbol.upper() != symbol.upper():
                        continue

                    price = o.get('price', '0')
                    if price in ('0', '0.0', '0.00', '', '0.0000'):
                        price = None
                    else:
                        try:
                            price = Decimal(str(price))
                        except:
                            price = None

                    open_orders.append({
                        'side': o.get('side', 'UNKNOWN'),
                        'type': o.get('type', 'UNKNOWN'),
                        'price': price,
                        'quantity': Decimal(str(o.get('origQty', '0'))),
                        'filled_qty': Decimal(str(o.get('executedQty', '0'))),
                        'status': o.get('status', 'UNKNOWN'),
                        'client_order_id': o.get('clientOrderId', '–'),
                        'symbol': order_symbol,
                    })
            except Exception:
                pass

            try:
                positions = account.get('positions', [])
                for pos in positions:
                    if pos.get('symbol', '').upper() != symbol.upper():
                        continue
                    position_amt = Decimal(str(pos.get('positionAmt', '0')))
                    if position_amt == 0:
                        continue

                    side = "LONG" if position_amt > 0 else "SHORT"
                    qty = abs(position_amt)
                    entry_price = Decimal(str(pos.get('entryPrice', '0')))
                    pos_unreal_pnl = Decimal(str(pos.get('unrealizedProfit', '0')))

                    binance_open_positions.append({
                        'side': side,
                        'quantity': qty,
                        'avg_px_open': entry_price,
                        'unrealized_pnl': pos_unreal_pnl,
                        'unrealized_pnl_pct': (pos_unreal_pnl / (qty * entry_price) * 100) if entry_price > 0 else Decimal('0'),
                    })
                    unrealized_pnl += pos_unreal_pnl
            except Exception:
                pass

            try:
                trades = client.futures_account_trades(symbol=symbol, limit=50)
                for t in trades:
                    binance_trade_history.append({
                        'time': t.get('time'),
                        'side': t.get('side', 'UNKNOWN'),
                        'price': Decimal(str(t.get('price', '0'))),
                        'qty': Decimal(str(t.get('qty', '0'))),
                        'commission': Decimal(str(t.get('commission', '0'))),
                        'commission_asset': t.get('commissionAsset', 'USDT'),
                    })
            except Exception:
                pass

        except Exception:
            pass

    context = {
        'config': config,
        'live_bot_active': config.is_active,
        'current_instrument_display': config.get_instrument_display(),
        'total_pnl': config.total_pnl,
        'realized_pnl': config.realized_pnl,
        'unrealized_pnl': unrealized_pnl,
        'win_rate': config.win_rate,
        'total_trades': config.total_trades,
        'wallet_balance': total_wallet_balance,
        'open_orders': open_orders,
        'open_positions': binance_open_positions,
        'trade_history': binance_trade_history[:20],
        'margin_ratio': margin_ratio,
        'maintenance_margin': maintenance_margin,
        'margin_balance': margin_balance,
        'api_error': api_error,
        'total_api_orders': total_api_orders,
        'symbol_matched_orders': symbol_matched_orders,
        'recent_trades': recent_trades,
        'recent_logs': recent_logs,
        'exchanges': EXCHANGE_CHOICES,
        'instruments': INSTRUMENT_CHOICES,
        'risk_levels': RISK_CHOICES,
    }

    return render(request, 'auxobot/live_trade_bot.html', context)

@login_required
def configure_live_bot(request):
    """
    Handles configuring the live bot settings.
    Saves settings and sets is_active = True.
    The systemd runner will automatically start or restart the bot.
    """
    config = get_object_or_404(BotConfig, user=request.user)
    extra_config, _ = ExtraConfig.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update basic config
        config.exchange = request.POST.get('exchange') or config.exchange
        config.instrument = request.POST.get('instrument') or config.instrument
        config.risk_level = request.POST.get('risk_level') or config.risk_level

        qty_input = request.POST.get('custom_quantity', '').strip()
        if qty_input:
            try:
                config.custom_quantity = Decimal(qty_input)
            except (InvalidOperation, ValueError):
                pass  
        else:
            config.custom_quantity = None

        if 'api_key' in request.POST:
            config.api_key = request.POST['api_key'].strip() or None

        if 'api_secret' in request.POST:
            config.demo_api_secret = request.POST['api_secret'].strip() or None

        config.save()

        # Update extra price config
        price_fields = {
            'price_sol': 'SOLUSDT',
            'price_doge': 'DOGEUSDT',
            'price_eth': 'ETHUSDT',
            'price_btc': 'BTCUSDT',
            'price_bnb': 'BNBUSUT',
            'price_ada': 'ADAUSDT',
            'price_xrp': 'XRPUSDT',
            'price_pepe': 'PEPEUSDT',
            'price_shib': '1000SHIBUSDT',
        }

        updated = False
        for field, symbol in price_fields.items():
            value = request.POST.get(field, '').strip()
            if value:
                try:
                    setattr(extra_config, field, Decimal(value))
                    updated = True
                except (InvalidOperation, ValueError):
                    messages.warning(request, f"Invalid price for {symbol}. Ignored.")
        if updated:
            extra_config.save()

        # Set is_active = True so systemd runner starts/restarts the bot
        was_active = config.is_active
        config.is_active = True
        config.save(update_fields=['is_active'])

        # User feedback
        if was_active:
            messages.success(request, "Settings updated! Bot will restart with new config in a few seconds.")
        else:
            messages.success(request, f"Bot configured and start signal sent! Launching in a few seconds...")

        return redirect('auxobot:live_trading')

    return redirect('auxobot:live_trading')


@login_required
def start_live_bot(request):
    """
    Handles the "Start Bot Now" button.
    Only sets the is_active flag.
    The systemd runner will detect it and launch the bot.
    """
    if request.method == 'POST':
        config = get_object_or_404(BotConfig, user=request.user)
        
        if config.is_active:
            messages.info(request, "Bot is already running.")
        else:
            if not config.api_key or not config.api_secret:
                messages.error(request, "Please configure API keys first in Settings.")
            elif not config.instrument:
                messages.error(request, "Please select a trading pair.")
            else:
                config.is_active = True
                config.save(update_fields=['is_active'])
                messages.success(request, "Start signal sent! Bot launching in a few seconds...")
        
        return redirect('auxobot:live_trading')
    
    return redirect('auxobot:live_trading')


def stop_live_bot(request):
    if request.method == 'POST':
        config = get_object_or_404(BotConfig, user=request.user)
        if config.is_active:
            config.is_active = False
            config.save(update_fields=['is_active'])
            messages.success(request, "Stop signal sent. Bot will shut down gracefully in a few seconds.")
        else:
            messages.info(request, "Bot is already stopped.")
        return redirect('auxobot:live_trading')

def download_live_bot_logs(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    logs = LiveBotLog.objects.filter(user=request.user).order_by('timestamp')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bot_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message'])
    for log in logs:
        writer.writerow([log.timestamp, log.level, log.message])

    return response

 