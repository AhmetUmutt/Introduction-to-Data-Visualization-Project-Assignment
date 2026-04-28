# AI-Powered Semantic Data Visualizer

Bu proje, metin yığınlarını analiz ederek içerisindeki teknik verileri cımbızla çeken ve bu verileri profesyonel grafiklere (Sütun ve Radar) dönüştüren yapay zeka destekli bir asistandır. 

## 🚀 Öne Çıkan Özellikler

* **Anlamsal Veri Çıkarımı:** Gemini 3 Flash modelini kullanarak metinde sayı olmasa bile ürünleri tanır ve teknik verilerini hafızasından çağırır.
* **Asenkron Mimari (Threading & Queue):** Yapay zeka ve grafik oluşturma işlemleri arka planda çalışır, arayüz asla donmaz.
* **Akıllı Görselleştirme:**
    * **Normalizasyon:** Radar grafiklerinde farklı birimlerin (beygir, bagaj hacmi vb.) birbirini ezmesini engeller.
    * **Otomatik Eksen Düzenleme:** Sütun grafiklerinde yazıların çakışmasını önlemek için 45 derece eğim kullanır.
* **Global Erişim:** F8 kısayolu ile herhangi bir uygulama üzerinden (tarayıcı, PDF, not defteri) seçili metni saniyeler içinde işler.
* **Kaydetme Özelliği:** Oluşturulan grafikleri PNG formatında yüksek çözünürlüklü olarak kaydedebilir.

## 🛠️ Teknik Detaylar

* **Dil:** Python
* **Model:** Gemini 3 Flash (Ollama API üzerinden)
* **Arayüz:** Tkinter (Koyu tema entegrasyonu)
* **Grafik Kütüphanesi:** Matplotlib
* **Görüntü İşleme:** Pillow (PIL)

## 📦 Kurulum ve Kullanım

1.  **Ollama Kurulumu:** Bilgisayarınızda [Ollama](https://ollama.com/) kurulu olmalı ve `gemini-3-flash-preview` modeli aktif olmalıdır.
2.  **Kütüphanelerin Kurulması:**
    ```bash
    pip install pyperclip pynput pyautogui matplotlib requests pillow
    ```
3.  **Çalıştırma:** `BASLAT.bat` dosyasına tıklayın veya terminalden `pythonw main.pyw` komutunu çalıştırın.
4.  **Kullanım:** Herhangi bir metni seçin ve **F8** tuşuna basın. Açılan menüden istediğiniz analiz türünü seçin.

## 👨‍💻 Mühendislik Yaklaşımı

Bu proje, bir yazılım mühendisliği öğrencisi tarafından; veri madenciliği, doğal dil işleme (NLP) ve GUI tasarımı disiplinlerini birleştirmek amacıyla geliştirilmiştir. Özellikle veri setleri arasındaki uçurumları kapatmak için kullanılan normalizasyon algoritmaları ve çoklu iş parçacığı (multithreading) yönetimi projenin teknik temelini oluşturur.

```mermaid
flowchart TD
    %% Ana Akış Başlangıcı
    Start([Uygulama Başlatıldı]) --> Listen[Klavye Dinleyicisi: F8 Bekleniyor]
    
    %% Kullanıcı Etkileşimi ve Veri Yakalama
    Listen --> Selection[Kullanıcı Metni Seçer ve F8'e Basar]
    Selection --> Copy[Metin Panoya Kopyalanır & Sentinel Kontrolü]
    Copy --> Menu{İşlem Menüsü}
    
    %% Multithreading Katmanı
    Menu -->|İşlem Seçildi| Thread[Arka Plan İş Parçacığı - Threading]
    
    subgraph AI_Core [Yapay Zeka İşleme Modülü]
        Thread --> Prompt[Prompt Mühendisliği & JSON Yapılandırma]
        Prompt --> Ollama[Ollama API: Gemini 3 Flash]
        Ollama --> Parser[JSON Parser & Teknik Veri Ayıklama]
    end
    
    %% Grafik ve Analiz Katmanı
    Parser --> Viz_Type{Görselleştirme Modu}
    
    subgraph Graphics_Engine [Grafik ve Analiz Motoru]
        Viz_Type -->|Sütun| Bar[Matplotlib: 45 Derece Eksen Düzenleme]
        Viz_Type -->|Radar| Radar[Matplotlib: Veri Normalizasyonu]
        Bar --> Render[Grafik Render Edilir .png]
        Radar --> Render
    end
    
    %% Sonuç ve Çıktı Katmanı
    Render --> Queue[GUI Queue: Sonuç Ana İş Parçacığına Aktarılır]
    Queue --> Window[Sonuç Penceresi: Grafik + Tablo + AI Yorumu]
    Window --> Save[Opsiyonel: Grafiği Kaydet]
    Save --> End([Bitiş])

    %% Görsel Stillendirme
    style AI_Core fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Graphics_Engine fill:#f0f7ff,stroke:#0056b3,stroke-width:2px
    style Start fill:#dcfce7,stroke:#166534
    style End fill:#fee2e2,stroke:#991b1b
```
