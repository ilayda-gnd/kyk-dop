# 🏢 KYK Dijital Oda Protokolü (DOP)
> **Toplu Yaşam Alanlarında Çatışma Çözümü ve Kaynak Yönetimi İçin Bulut Tabanlı Çok Kiracılı Mikro-Yönetim Platformu**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dop-kyk.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20Supabase-green.svg)](https://supabase.com/)

## 📌 Proje Hakkında
**Dijital Oda Protokolü (DOP)**, yükseköğretim öğrenci yurtlarında (KYK) çoklu paylaşımlı odalarda yaşanan temizlik rotasyonu, ortak harcama takibi ve iletişim kaynaklı sosyal sürtüşmeleri; insan faktöründeki sübjektifliği ortadan kaldıran bulut tabanlı bir sistemle çözen bir **GovTech / Sosyal İnovasyon** yazılımıdır.

Proje, yurt idareleri üzerindeki dilekçe, oda nakil ve şikayet yükünü kaynağında hafifletmeyi hedefler.

---

## ✨ Öne Çıkan Özellikler

* **🔒 Çok Kiracılı Mimari (Multi-Tenancy):** Oda kodu ve PIN tabanlı veri izolasyonu sayesinde her oda sadece kendi verisine erişir.
* **💸 İkili Borç Netleştirme Motoru (*Pairwise Netting*):** Ortak harcamalarda kişiler arası çapraz borç matrisini hesaplayarak gereksiz para akışını önler ve tek satırlık net ödeme talimatı üretir.
* **📜 Değiştirilemez Denetim İzi (*Audit Trail*):** Çöp atma veya borç silme gibi tüm kritik işlemleri zaman damgasıyla (`timestamp`) silinemez bir kütüğe kaydeder.
* **🛡️ Gizlilik Odaklı Tasarım (*Privacy-by-Design*):** T.C. Kimlik No, telefon veya e-posta gibi hassas kişisel veriler yerine rumuz ve emoji tabanlı temsil modeliyle tam KVKK uyumu sağlar.
* **📣 Anonim Pano:** Birebir tartışmaları önlemek amacıyla oda içi yapıcı bildirimlerin kimliksiz paylaşılmasına olanak tanır.

---

## 🛠️ Teknoloji Yığını (Tech Stack)

* **Frontend / UI:** Python & Streamlit (Reaktif Web / Mobil Uyumlu)
* **Backend / Database:** PostgreSQL (Supabase BaaS Altyapısı)
* **Deployment:** Streamlit Community Cloud

---

## 🚀 Yerel Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için:

1. **Depoyu klonlayın:**
   ```bash
   git clone [https://github.com/ilayda-gnd/kyk-dop.git](https://github.com/ilayda-gnd/kyk-dop.git)
   cd kyk-dop
