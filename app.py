import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from isyatirimhisse import StockData
import pandas as pd
import json
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# BIST100 + BIST30 Kapsamlı Hisse Listesi (130 hisse)
TEST_STOCKS = [
    # BIST30 Ana Hisseler (En büyük 30 şirket)
    'AKBNK', 'ARCLK', 'ASELS', 'BIMAS', 'EKGYO', 'EREGL', 'FROTO', 'GARAN', 'GUBRF', 'HALKB',
    'ISCTR', 'KCHOL', 'KOZAL', 'KOZAA', 'KRDMD', 'MGROS', 'PETKM', 'PGSUS', 'SAHOL', 'SASA',
    'SISE', 'SOKM', 'TAVHL', 'TCELL', 'THYAO', 'TKFEN', 'TOASO', 'TUPRS', 'VAKBN', 'YKBNK',
    
    # BIST100 Bankacılık Sektörü
    'TSKB', 'ALBRK', 'ICBCT', 'QNBFB', 'DENIZ', 'SKBNK', 'ZIRAA', 'KLNMA',
    
    # BIST100 Teknoloji ve Telekomünikasyon
    'TTKOM', 'NETAS', 'LOGO', 'LINK', 'INDES', 'ARENA', 'DGATE', 'SELEC', 'KRONT', 'DESPC',
    'ARMDA', 'ESCOM', 'FONET', 'KAREL', 'KFEIN', 'PAMEL', 'SMART', 'VERTU', 'ALCTL',
    
    # BIST100 Perakende ve Tüketim
    'BIZIM', 'MAVI', 'DESA', 'MPARK', 'ROYAL', 'ADEL', 'CRFSA', 'HATEK', 'ULKER', 'BANVT',
    'CCOLA', 'KNFRT', 'PETUN', 'PINSU', 'TATGD', 'TUKAS', 'VANGD', 'AEFES', 'KENT',
    
    # BIST100 Enerji ve Petrokimya
    'TPAO', 'AYGAZ', 'AKSA', 'ZORLU', 'ZOREN', 'AKSEN', 'SOKE', 'ALKIM', 'BAGFS', 'BRISA',
    'DYOBY', 'EGEEN', 'ENKAI', 'GOODY', 'HEKTS', 'IZMDC', 'KAPLM', 'KLMSN', 'OTKAR', 'PARSN',
    
    # BIST100 Sanayi ve İmalat
    'SARKY', 'BFREN', 'VESTL', 'CEMTS', 'DOHOL', 'FMIZP', 'GOLTS', 'IHLAS', 'KARSN', 'KONYA',
    'MRSHL', 'NUHCM', 'PRKME', 'SILVR', 'TMPOL', 'TRKCM', 'UNYEC', 'YATAS', 'ANACM', 'BRSAN',
    
    # BIST100 Gayrimenkul ve İnşaat
    'EMLAK', 'GOZDE', 'ISGYO', 'KOSGB', 'METUR', 'NUGYO', 'OZKGY', 'RYGYO', 'TRGYO', 'VAKGM',
    'VKGYO', 'YKGYO', 'AKGRT', 'DEVA'
]

# Gelecekte kullanılacak tam liste (şimdilik yorum satırında)
"""
FULL_BIST_STOCKS = [
    # Tüm 200+ hisse buraya gelecek
    # Şimdilik performans için 50 hisse ile test ediyoruz
]
"""

# StockData sınıfını başlat
stock_data = StockData()

# Cache sistemi
CACHE = {
    'data': {},
    'last_update': None,
    'update_interval': 7200  # 2 saat (saniye cinsinden)
}

def is_cache_valid():
    """Cache'in geçerli olup olmadığını kontrol et"""
    if CACHE['last_update'] is None:
        return False
    
    time_diff = datetime.now() - CACHE['last_update']
    return time_diff.total_seconds() < CACHE['update_interval']

def update_cache():
    """Cache'i güncelle"""
    print("🔄 Cache güncelleniyor...")
    start_time = time.time()
    
    prices = {}
    for symbol in TEST_STOCKS:
        try:
            print(f"🔄 {symbol} için veri çekiliyor...")
            
            # Son 5 işlem gününün verisini çek (borsa kapalıysa son işlem günü)
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%d-%m-%Y')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%d-%m-%Y')
            
            data = stock_data.get_data(
                symbols=[symbol],
                start_date=start_date,
                end_date=end_date,
                exchange='0',  # TRY
                frequency='1d'
            )
            
            if not data.empty:
                # CODE sütununda hisse sembolü var mı kontrol et
                if 'CODE' in data.columns and 'CLOSING_TL' in data.columns:
                    # İlgili hisse için verileri filtrele
                    symbol_data = data[data['CODE'] == symbol]
                    
                    if not symbol_data.empty:
                        # En son kapanış fiyatını al
                        latest_price = symbol_data['CLOSING_TL'].iloc[-1]
                        if pd.notna(latest_price):
                            prices[symbol] = round(float(latest_price), 2)
                            print(f"✅ {symbol}: {latest_price:.2f}")
            
            time.sleep(0.1)  # Çok kısa bekleme
            
        except Exception as e:
            print(f"❌ {symbol} hatası: {str(e)}")
            continue
    
    CACHE['data'] = prices
    CACHE['last_update'] = datetime.now()
    
    elapsed_time = time.time() - start_time
    print(f"✅ Cache güncellendi! {len(prices)} hisse, {elapsed_time:.1f} saniye")
    
    return prices

@app.route('/stocks', methods=['GET'])
def get_stocks():
    try:
        # Cache kontrol et
        if is_cache_valid():
            print("✅ Cache'den veri döndürülüyor")
            cache_age = (datetime.now() - CACHE['last_update']).total_seconds()
            print(f"📊 Cache yaşı: {cache_age/60:.1f} dakika")
            return jsonify(CACHE['data'])
        
        # Cache geçersizse güncelle
        print("🔄 Cache geçersiz, yeni veri çekiliyor...")
        prices = update_cache()
        
        if not prices:
            # Test verisi döndür
            test_prices = {
                'THYAO': 100.50,
                'GARAN': 85.25,
                'AKBNK': 45.75,
                'EREGL': 55.30,
                'PGSUS': 120.80
            }
            print("⚠️ Gerçek veri alınamadı, test verisi döndürülüyor")
            return jsonify(test_prices)
            
        return jsonify(prices)
        
    except Exception as e:
        print(f"❌ Genel hata: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda test verisi döndür
        test_prices = {
            'THYAO': 100.50,
            'GARAN': 85.25,
            'AKBNK': 45.75,
            'EREGL': 55.30,
            'PGSUS': 120.80
        }
        return jsonify(test_prices)

@app.route('/stocks/<symbol>', methods=['GET'])
def get_stock(symbol):
    try:
        # Önce cache'den kontrol et
        if is_cache_valid() and symbol in CACHE['data']:
            price = CACHE['data'][symbol]
            print(f"✅ {symbol} cache'den alındı: {price}")
            return jsonify({
                "symbol": symbol,
                "price": price
            })
        
        # Cache'de yoksa veya geçersizse gerçek zamanlı çek
        print(f"🔄 {symbol} için gerçek zamanlı veri çekiliyor...")
        
        # Son 5 işlem gününün verisini çek
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%d-%m-%Y')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%d-%m-%Y')
        
        data = stock_data.get_data(
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            exchange='0',  # TRY
            frequency='1d'
        )
        
        if data.empty:
            print(f"❌ {symbol} için veri bulunamadı")
            return jsonify({"error": "Hisse bulunamadı"}), 404
        
        # CODE sütununda hisse sembolü var mı kontrol et
        if 'CODE' in data.columns and 'CLOSING_TL' in data.columns:
            symbol_data = data[data['CODE'] == symbol]
            
            if not symbol_data.empty:
                latest_price = symbol_data['CLOSING_TL'].iloc[-1]
                if pd.notna(latest_price):
                    price = round(float(latest_price), 2)
                    print(f"✅ {symbol}: {price}")
                    
                    # Cache'i güncelle
                    CACHE['data'][symbol] = price
                    
                    return jsonify({
                        "symbol": symbol,
                        "price": price
                    })
        
        print(f"❌ {symbol} için fiyat verisi bulunamadı")
        return jsonify({"error": "Fiyat verisi bulunamadı"}), 404
            
    except Exception as e:
        print(f"❌ {symbol} için hata: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/cache-info', methods=['GET'])
def cache_info():
    """Cache durumu hakkında bilgi döndür"""
    if CACHE['last_update']:
        cache_age = (datetime.now() - CACHE['last_update']).total_seconds()
        next_update = CACHE['update_interval'] - cache_age
        
        return jsonify({
            "cache_valid": is_cache_valid(),
            "last_update": CACHE['last_update'].strftime('%Y-%m-%d %H:%M:%S'),
            "cache_age_minutes": round(cache_age / 60, 1),
            "next_update_minutes": round(next_update / 60, 1) if next_update > 0 else 0,
            "stocks_count": len(CACHE['data']),
            "update_interval_hours": CACHE['update_interval'] / 3600
        })
    else:
        return jsonify({
            "cache_valid": False,
            "message": "Cache henüz oluşturulmadı"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('RAILWAY_ENVIRONMENT') != 'production'
    
    print("🚀 Safinance Backend başlatılıyor...")
    print(f"📊 Cache güncelleme aralığı: {CACHE['update_interval']/3600} saat")
    print(f"📈 Toplam hisse sayısı: {len(TEST_STOCKS)}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 