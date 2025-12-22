import requests
import json
import os
import time
from datetime import datetime, timedelta

# Dosya yolları
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

# Taranacak günler (Bugünden geriye 5 gün)
GUN_SAYISI = 5 

def bosluk_doldur_tarihli():
    print("🚑 TARİH BAZLI Boşluk Doldurma Operasyonu Başladı...")
    print(f"📂 Hedef Dosya: {ANA_DOSYA}")

    # 1. MEVCUT ARŞİVİ YÜKLE
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Mevcut arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            return
    else:
        print("🚨 Dosya bulunamadı!")
        return

    # ID Seti
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    toplam_eklenen = 0

    # 2. GÜNLERİ TEK TEK TARA
    bugun = datetime.now()
    
    for i in range(GUN_SAYISI):
        # Tarihi hesapla (Bugün, Dün, Önceki Gün...)
        taranacak_tarih = bugun - timedelta(days=i)
        tarih_str = taranacak_tarih.strftime("%Y-%m-%d")
        
        # URL'ye tarih parametresi ekliyoruz
        url = f"https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=1000&date={tarih_str}"
        
        print(f"\n📅 Taranıyor: {tarih_str} ...")
        
        try:
            response = requests.get(url, timeout=20)
            data = response.json()
            
            if response.status_code == 200 and "result" in data:
                ham_liste = data["result"]
                print(f"   📡 {len(ham_liste)} veri geldi.")
                
                sayfa_eklenen = 0
                for item in ham_liste:
                    # Tarih düzeltmesi
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # Büyüklük (3.0+)
                    try:
                        mag = float(item.get("mag", 0))
                        if mag >= 3.0:
                            uid = f"{item.get('date')}_{item.get('title')}"
                            
                            if uid not in mevcut_id_seti:
                                mevcut_veri.insert(0, item)
                                mevcut_id_seti.add(uid)
                                sayfa_eklenen += 1
                                toplam_eklenen += 1
                                print(f"      ✅ EKLENDİ: {item['date']} - {item['title']}")
                    except:
                        continue
                
                if sayfa_eklenen == 0:
                    print("   💤 Bu tarihteki 3.0+ depremler zaten arşivde var.")
            else:
                print("   ❌ Bu tarih için veri dönmedi.")

            time.sleep(1) # API dinlensin

        except Exception as e:
            print(f"   ❌ Hata: {e}")

    # 3. KAYDET
    if toplam_eklenen > 0:
        print(f"\n🎉 SONUÇ: {toplam_eklenen} adet eksik deprem kurtarıldı!")
        
        # Tarihe göre sırala (Garanti olsun)
        mevcut_veri.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        with open(ANA_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
        
        with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
            
        print("💾 Dosyalar kaydedildi. Push edebilirsin!")
    else:
        print("\n💤 Eksik veri bulunamadı.")

if __name__ == "__main__":
    bosluk_doldur_tarihli()
