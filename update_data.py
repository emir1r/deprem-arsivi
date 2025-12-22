import requests
import json
import os
import time
from datetime import datetime, timedelta

# GitHub Actions ortamında dosyalar ana dizindedir
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

# Geçmişe dönük kaç gün taranacak? (7 gün, eksikleri kapatır)
GUN_SAYISI = 7

def verileri_tamir_et():
    print("🚑 GITHUB ACTIONS TAMİR MODU BAŞLATILDI...")
    print(f"Hedef: Geçmiş {GUN_SAYISI} gün taranacak ve eksikler tamamlanacak.")
    
    # 1. MEVCUT DOSYAYI OKU
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşivde şu an {len(mevcut_veri)} kayıt var.")
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

    toplam_kurtarilan = 0
    bugun = datetime.now()

    # 2. GÜN GÜN GERİYE GİDEREK TARA
    for i in range(GUN_SAYISI):
        # Tarihi hesapla
        taranacak_tarih = bugun - timedelta(days=i)
        tarih_str = taranacak_tarih.strftime("%Y-%m-%d")
        
        # URL: Archive endpoint + Date parametresi
        url = f"https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=1000&date={tarih_str}"
        
        print(f"📅 Taranıyor: {tarih_str} ...")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    ham_liste = data["result"]
                    
                    gunluk_eklenen = 0
                    for item in ham_liste:
                        # --- İSİM DÜZELTME ---
                        if "date_time" in item:
                            item["date"] = item["date_time"]
                        
                        # Büyüklük Filtresi (3.0+)
                        try:
                            mag = float(item.get("mag", 0))
                            if mag >= 3.0:
                                uid = f"{item.get('date')}_{item.get('title')}"
                                
                                # Eğer bizde yoksa ekle
                                if uid not in mevcut_id_seti:
                                    mevcut_veri.insert(0, item)
                                    mevcut_id_seti.add(uid)
                                    gunluk_eklenen += 1
                                    toplam_kurtarilan += 1
                                    print(f"   ✅ KURTARILDI: {item['date']} - {item['title']}")
                        except:
                            continue
                    
            else:
                print("   ❌ Veri yok.")
            
            # API'yi yormamak için 1 sn bekle
            time.sleep(1) 

        except Exception as e:
            print(f"   ❌ Hata: {e}")

    # 3. KAYDET (YAML dosyası bunları commit yapacak)
    if toplam_kurtarilan > 0:
        print(f"\n🎉 SONUÇ: Toplam {toplam_kurtarilan} eksik deprem arşive eklendi!")
        
        # Tarihe göre yeniden sırala (Actions'ta karışıklık olmasın)
        mevcut_veri.sort(key=lambda x: x.get('date', ''), reverse=True)

        try:
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
            print("💾 Dosyalar güncellendi. Actions commit yapacak.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
            exit(1) # Hata koduyla çık ki Actions uyarsın
    else:
        print("\n💤 Eksik veri bulunamadı, arşiv zaten tam.")

if __name__ == "__main__":
    verileri_tamir_et()
