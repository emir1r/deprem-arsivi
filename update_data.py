import requests
import json
import os
import time
from datetime import datetime, timedelta

# GitHub Actions için dosya yolları (Klasör adı yok)
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

# Kaç gün geriye gidelim? (Arayı kapatmak için 5 gün yeterli)
GUN_SAYISI = 5 

def verileri_guncelle():
    print("🚑 TAMİR MODU: update_data.py çalıştı. Geçmiş 5 gün taranıyor...")
    
    # 1. MEVCUT DOSYAYI OKU
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Okuma hatası: {e}")
            return
    else:
        print("⚠️ Dosya bulunamadı, yeni oluşturulacak.")

    # ID Seti (Hızlı kontrol için)
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    toplam_eklenen = 0
    bugun = datetime.now()

    # 2. SON 5 GÜNÜ TARİH TARİH TARA
    for i in range(GUN_SAYISI):
        # Tarihi hesapla
        taranacak_tarih = bugun - timedelta(days=i)
        tarih_str = taranacak_tarih.strftime("%Y-%m-%d")
        
        # URL (Archive Endpoint)
        url = f"https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=1000&date={tarih_str}"
        
        print(f"📅 Taranıyor: {tarih_str} ...")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    ham_liste = data["result"]
                    
                    for item in ham_liste:
                        # --- İSİM DÜZELTME (Önemli!) ---
                        if "date_time" in item:
                            item["date"] = item["date_time"]
                        
                        # Büyüklük Filtresi (3.0+)
                        try:
                            mag = float(item.get("mag", 0))
                            if mag >= 3.0:
                                uid = f"{item.get('date')}_{item.get('title')}"
                                
                                if uid not in mevcut_id_seti:
                                    mevcut_veri.insert(0, item)
                                    mevcut_id_seti.add(uid)
                                    toplam_eklenen += 1
                                    print(f"   ✅ EKLENDİ: {item['date']} - {item['title']}")
                        except:
                            continue
            
            time.sleep(1) # API'yi yormamak için bekle
            
        except Exception as e:
            print(f"   ❌ Hata ({tarih_str}): {e}")

    # 3. KAYDET
    if toplam_eklenen > 0:
        print(f"\n🎉 TOPLAM {toplam_eklenen} EKSİK DEPREM EKLENDİ.")
        
        # Tarihe göre sırala (Eskiden yeniye veya tam tersi karışıklık olmasın)
        # String tarih karşılaştırması "2024..." şeklinde olduğu için düzgün çalışır.
        mevcut_veri.sort(key=lambda x: x.get('date', ''), reverse=True)

        try:
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
            print("💾 Dosyalar GitHub sunucusunda güncellendi.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
    else:
        print("\n💤 Eksik veri bulunamadı veya zaten tam.")

if __name__ == "__main__":
    verileri_guncelle()
