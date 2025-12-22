import requests
import json
import os
from datetime import datetime

ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("🚀 Güncelleme robotu başlatıldı...")
    
    # --- 1. MEVCUT ARŞİVİ OKU ---
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşivde {len(mevcut_veri)} kayıt var.")
            
            # Arşivdeki en güncel depremi bulalım (Kontrol için)
            if len(mevcut_veri) > 0:
                print(f"🗓️  Arşivdeki EN SON deprem tarihi: {mevcut_veri[0].get('date')}")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            return

    # --- 2. API'DEN VERİ ÇEK ---
    # Not: limit=500 çalışmıyorsa API kaynaklıdır, ama biz yine de isteyelim.
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    
    yeni_gelenler = []
    try:
        print("🌍 API'ye bağlanılıyor...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                yeni_gelenler = data["result"]
                print(f"📡 API'den {len(yeni_gelenler)} adet veri geldi.")
                
                if len(yeni_gelenler) > 0:
                    print(f"🔥 API'den gelen EN YENİ tarih: {yeni_gelenler[0].get('date')}")
            else:
                print("⚠️ API yanıtında 'result' bulunamadı.")
        else:
            print(f"❌ API Hatası: Kod {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # --- 3. KARŞILAŞTIR VE EKLE (DEBUG MODU) ---
    # Benzersizlik kontrolü için ID oluşturalım (Tarih + Yer)
    # Çünkü bazen tarih aynı kalıp veri değişebilir.
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    eklenenler = []
    
    # API'den gelenler (Yeniden eskiye doğru gelir, biz ters çevirip eskiden yeniye ekleyelim ki sıra bozulmasın)
    for deprem in reversed(yeni_gelenler):
        uid = f"{deprem.get('date')}_{deprem.get('title')}"
        
        # Eğer bu ID arşivde yoksa EKLE
        if uid not in mevcut_id_seti:
            # Önce arşive (listenin başına) ekle
            mevcut_veri.insert(0, deprem)
            # Sonra sete ekle (tekrarı önlemek için)
            mevcut_id_seti.add(uid)
            eklenenler.append(deprem)

    if len(eklenenler) > 0:
        print(f"✅ {len(eklenenler)} YENİ DEPREM BULUNDU ve eklendi!")
        print(f"🔎 Örnek Eklenen: {eklenenler[-1]['title']} - {eklenenler[-1]['date']}")
        
        # --- 4. DOSYALARI KAYDET ---
        try:
            # Ana arşivi güncelle
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            # Vitrin dosyasını güncelle (Sadece son 500)
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar başarıyla güncellendi.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
            
    else:
        print("💤 Yeni deprem yok. Arşiv zaten güncel.")
        # Arşivdeki ilk kayıtla API'nin ilk kaydı aynı mı kontrolü
        if len(yeni_gelenler) > 0 and len(mevcut_veri) > 0:
            print(f"   (Arşiv Başı: {mevcut_veri[0].get('date')} == API Başı: {yeni_gelenler[0].get('date')})")

if __name__ == "__main__":
    verileri_guncelle()
