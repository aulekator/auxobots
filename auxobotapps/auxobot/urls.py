from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'auxobot'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bot-setup/', views.bot_setup, name='bot_setup'),
    path('backtest/', TemplateView.as_view(template_name='auxobot/backtesting.html'), name='backtest'),
    path('api/run-backtest/', views.run_backtest, name='run_backtest'),
    path('demo/', views.demo_trading_dashboard, name='demo_trading'),
    path('demo/configure/', views.configure_demo_bot, name='configure_demo_bot'),
    path('demo/stop/', views.stop_demo_bot, name='stop_demo_bot'),
    path('download-logs/', views.download_bot_logs, name='download_bot_logs'),
    path('demo/start/', views.start_demo_bot, name='start_demo_bot'),

    path('live-bot/', views.live_trading_dashboard, name='live_trading'),
    path('live-bot/configure/', views.configure_live_bot, name='configure_live_bot'),
    path('live/stop/', views.stop_live_bot, name='stop_live_bot'),
    path('live/start/', views.start_live_bot, name='start_live_bot'),
    path('download-logs/', views.download_live_bot_logs, name='download_live_bot_logs'),


]