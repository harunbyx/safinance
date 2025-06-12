# Safinance Backend API

BIST hisse senedi fiyatlarını sağlayan Flask API servisi.

## Özellikler

- 🏦 **117 BIST Hissesi**: BIST30 + BIST100'den seçilmiş hisseler
- ⚡ **Cache Sistemi**: 2 saatlik cache ile hızlı yanıt
- 🔄 **Gerçek Zamanlı Veri**: isyatirimhisse kütüphanesi ile güncel fiyatlar
- 🌐 **CORS Desteği**: Flutter uygulaması ile uyumlu

## API Endpoints

### GET /stocks
Tüm hisse fiyatlarını döndürür.

```json
{
  "THYAO": 278.75,
  "GARAN": 119.00,
  "AKBNK": 59.20,
  ...
}
```

### GET /stocks/{symbol}
Belirli bir hisse fiyatını döndürür.

```json
{
  "symbol": "THYAO",
  "price": 278.75
}
```

### GET /cache-info
Cache durumu hakkında bilgi verir.

```json
{
  "cache_valid": true,
  "last_update": "2025-06-13 01:32:02",
  "cache_age_minutes": 5.2,
  "stocks_count": 117,
  "update_interval_hours": 2.0
}
```

## Deployment

### Railway
Bu proje Railway'de deploy edilmek üzere hazırlanmıştır.

1. Railway hesabınıza giriş yapın
2. "New Project" → "Deploy from GitHub repo"
3. Bu repository'yi seçin
4. Otomatik deploy başlayacak

### Gerekli Dosyalar
- `requirements.txt`: Python bağımlılıkları
- `Procfile`: Railway start komutu
- `railway.json`: Railway konfigürasyonu

## Teknik Detaylar

- **Framework**: Flask 2.3.3
- **Veri Kaynağı**: isyatirimhisse 1.3.2
- **Cache**: 2 saat (7200 saniye)
- **Port**: Environment variable PORT (varsayılan: 5000)

## Hisse Listesi

### BIST30 (30 hisse)
Ana endeks hisseleri

### BIST100 Sektörleri
- **Bankacılık**: 8 hisse
- **Teknoloji**: 19 hisse  
- **Perakende**: 19 hisse
- **Enerji**: 20 hisse
- **Sanayi**: 20 hisse
- **Gayrimenkul**: 14 hisse

**Toplam**: 130 hisse tanımlı, ~117 hisse aktif

## Performans

- İlk cache yüklemesi: ~60 saniye
- Cache'den yanıt: <100ms
- Cache güncelleme: 2 saatte bir otomatik
- Hata toleransı: Veri alınamayan hisseler atlanır
