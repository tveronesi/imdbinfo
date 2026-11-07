# Piano di Intervento: Configurazione Centralizzata con Pydantic-Settings

Questo documento definisce il piano per introdurre una gestione centralizzata della configurazione basata su **Pydantic-Settings** nella libreria `imdbinfo`, gestendo in primis il `locale`, i limiti `max_items` distinti per tipo di query e il supporto ai `proxies` (attualmente presente nel branch `test`), preservando la retrocompatibilità dei comportamenti di default.

---

## 1. Analisi dei Proxy: Cosa Sono e a Cosa Servono

Nel branch `test` (commit `24b0d89` e `69fed55`), è stato introdotto il supporto ai proxy:
1. **Cos'è un proxy in Python (niquests / curl_cffi)**:
   È un dizionario di mapping protocollo -> URL del proxy, tipicamente:
   ```python
   proxies = {
       "http": "http://user:password@proxy_host:8080",
       "https": "http://user:password@proxy_host:8080",
   }
   ```
2. **A cosa serve in `imdbinfo`**:
   - `imdbinfo` effettua scraping su IMDb e interrogazioni GraphQL ad alto volume.
   - IMDb adotta AWS WAF (Web Application Firewall) e rate limiting basato su IP. L'utilizzo di proxy rotanti o aziendali permette di:
     - Evitare ban/blocchi dell'IP chiamante.
     - Superare restrizioni di rete aziendali/firewall.
     - Distribuire il carico su più IP per scraping massivo.
3. **Come viene usato nei trasporti HTTP**:
   - In `_http_get()` (usato da `request_handler()` per HTML scraping e WAF challenge): passato come argomento `proxies=proxies` a `curl_requests.get()`.
   - In `request_graphql_url()`: passato come argomento `proxies=proxies` a `niquests.post()`.
4. **Implementazione attuale nel branch `test`**:
   - Creato modulo `imdbinfo/proxy.py` con una variabile globale mutable `_configured_proxy: Optional[Dict] = None`.
   - Funzioni helper `set_proxy(proxies: Optional[Dict])` e `get_proxy() -> Optional[Dict]`.
   - `services.py` invoca `get_proxy()` prima di ogni chiamata HTTP.
   - `tests/test_proxy.py` testa `set_proxy` e `get_proxy`.
   - `tests/test_waf_cookie_cache.py` aggiornato per accettare `proxies=None` negli stub di test.

**Conclusione**: Invece di mantenere un modulo separato `proxy.py` con stato globale ad hoc, i proxy devono diventare a pieno titolo un campo di configurazione di `Settings`, interoperabile con `IMDBINFO_PROXIES` (o stringa singola proxy URL), `config.proxies` e gli helper `set_proxy()` / `configure()`.

---

## 2. Obiettivi e Requisiti Concordati

1. **Libreria**: Adozione di `pydantic-settings` (`BaseSettings`) per supportare automaticamente variabili d'ambiente con prefisso `IMDBINFO_` (es. `IMDBINFO_LOCALE`, `IMDBINFO_MAX_ITEMS_SEARCH`, `IMDBINFO_MAX_ITEMS_AKAS`, `IMDBINFO_PROXIES` o `IMDBINFO_PROXY_URL`) e opzionale file `.env`.
2. **Validazione Rigida (`ValidationError`)**: Valori non ammessi (locale non supportato, uno dei limiti `max_items_* <= 0`, tipi o formati proxy non validi) sollevano immediatamente `pydantic.ValidationError`.
3. **Interfaccia Utente Flessibile**:
   - Accesso e modifica diretta dell'oggetto di configurazione: `config.locale = "it"`, `config.proxies = {"https": "..."}`.
   - Funzione helper unificata: `configure(locale="it", max_items_search=20, max_items_images=100, proxies={"https": "..."})`.
   - Compatibilità storica preservata sia per locale che per proxy:
     - `set_locale("it")` e `get_locale()` continuano a funzionare inoltrando a `config.locale`.
     - `set_proxy(proxies)` e `get_proxy()` continuano a funzionare inoltrando a `config.proxies`.
4. **Gerarchia delle Priorità**:
   ```text
   [1 - Massima] Parametri per-chiamata (es. get_movie(id, locale="fr"), get_akas(id, max_items=300))
          │
   [2]           Modifica esplicita a runtime (configure(...) o config.attribute = ...)
          │
   [3]           Variabili d'ambiente di sistema (IMDBINFO_LOCALE, IMDBINFO_MAX_ITEMS_*, IMDBINFO_PROXIES)
          │
   [4]           File .env (se presente)
          │
   [5 - Minima]  Default cablato nel codice (locale="en", limiti max_items_* correnti, proxies=None)
   ```
5. **Parametri Iniziali nella Config**:
   - `locale`: codice lingua/paese predefinito (default: `"en"`).
   - Limiti configurabili separatamente per ogni campo `first:` presente nelle query GraphQL. I valori iniziali restano quelli attuali in `services.py`:
     - `max_items_search`: `mainSearch(first: 50)` (ricerca titoli).
     - `max_items_images`: `images(first: 50)`.
     - `max_items_interests`: `interests(first: 20)`.
     - `max_items_akas`: `akas(first: 200)`.
     - `max_items_trivia`: `trivia(first: 50)`.
     - `max_items_reviews`: `reviews(first: 50)`.
     - `max_items_guide_items`: `guideItems(first: 10)` nel parental guide.
     - `max_items_quotes`: `quotes(first: 100)`.
     - `max_items_credits`: `credits(first: 250)` nella query filmography.
     Tutti i limiti devono essere interi maggiori di zero. I nomi corrispondenti delle variabili d'ambiente usano il prefisso `IMDBINFO_` (ad es. `IMDBINFO_MAX_ITEMS_AKAS`).
   - `proxies`: dizionario proxy per HTTP / HTTPS (default: `None`, tipo: `Optional[Dict[str, str]]`).
     - Normalizzatore flessibile: accetta sia un `dict` (`{"http": "...", "https": "..."}`) sia una stringa URL singola (`"http://proxy:8080"` -> convertita automaticamente in `{"http": "http://proxy:8080", "https": "http://proxy:8080"}`).

---

## 3. Architettura dei Componenti

```text
imdbinfo/
  config.py       <-- NUOVO: modello Settings, singleton config, helper configure(), reset_config()
  locale.py       <-- REFACTOR: facciata retrocompatibile su config.locale
  proxy.py        <-- REFACTOR: facciata retrocompatibile su config.proxies (set_proxy, get_proxy)
  services.py     <-- AGGIORNATO: usa config.locale, config.max_items_*, config.proxies; invalida cache al cambio config
  __init__.py     <-- EXPORT: esporta config, configure, Settings, set_locale, get_locale, set_proxy, get_proxy
```

### A. Nuovo modulo `imdbinfo/config.py`

- Definizione del tipo dei locale ammessi:
  ```python
  SupportedLocale = Literal[
      "en", "fr-ca", "fr", "hi", "de", "it", "es", "pt", "es-es"
  ]
  ```
- Modello `Settings(BaseSettings)` con:
  - `model_config = SettingsConfigDict(env_prefix="IMDBINFO_", env_file=".env", extra="ignore", validate_assignment=True)`
  - `validate_assignment=True` per validare anche le assegnazioni dirette (`config.locale = "foo"` o `config.max_items_akas = -1`).
  - Validatore con normalizzazione per `locale` (`strip().lower()`).
  - Campi `max_items_*: int = Field(default=<valore corrente della query>, gt=0)`, uno per ciascun `first:`:
    `search`, `images`, `interests`, `akas`, `trivia`, `reviews`, `guide_items`, `quotes` e `credits`.
  - Campo `proxies: Optional[Dict[str, str]] = Field(default=None)`.
    - Validatore per `proxies`: accetta `None`, `dict` di stringhe o stringa URL (espansa a `{"http": url, "https": url}`).
- Singleton globale: `config = Settings()`.
- Helper:
  - `configure(locale=..., max_items_search=..., max_items_images=..., max_items_interests=..., max_items_akas=..., max_items_trivia=..., max_items_reviews=..., max_items_guide_items=..., max_items_quotes=..., max_items_credits=..., proxies=...) -> Settings`
  - `reset_config() -> Settings` (ripristina lo stato iniziale, utile in test/teardown).

### B. Refactor di `imdbinfo/locale.py`

- Eliminazione della variabile globale non tipizzata `_configured_locale`.
- `set_locale(locale: str)`: invoca internamente `configure(locale=locale)`. Con la validazione rigida, un locale non supportato solleva `ValidationError`.
- `get_locale()`: legge da `config.locale` e restituisce `""` se `"en"`, altrimenti il codice locale (mantenendo la convenzione esistente usata negli URL).
- `_retrieve_url_lang(locale=None)` e `_get_country_code_from_lang_locale(locale=None)`:
  - Se `locale` è passato esplicitamente, usano quello; altrimenti fanno fallback su `config.locale`.

### C. Refactor di `imdbinfo/proxy.py`

- Diventa un layer di retrocompatibilità leggero:
  - `set_proxy(proxies: Optional[Union[Dict[str, str], str]]) -> None`: inoltra a `configure(proxies=proxies)` (oppure reset a `None` se passato `None`).
  - `get_proxy() -> Optional[Dict[str, str]]`: restituisce `config.proxies`.

### D. Integrazione in `imdbinfo/services.py`

- **Supporto Proxies nelle chiamate di trasporto**:
  - `_http_get(url: str, cookies: Optional[Dict] = None, proxies: Optional[Dict] = None)`: passa `proxies=proxies` a `curl_requests.get()` o a `niquests.get()`.
  - `request_handler(url: str)`: ricava `proxies = config.proxies` e lo passa a `_http_get()`.
  - `request_graphql_url(...)`: ricava `proxies = config.proxies` e lo passa a `niquests.post(..., proxies=proxies)`.
- **Limiti GraphQL indipendenti**:
  - Sostituire ciascun valore letterale `first: N` con il limite specifico corrispondente in configurazione, mantenendo `N` come default.
  - Aggiungere un override per-chiamata `max_items: Optional[int] = None` alle funzioni pubbliche che espongono il relativo insieme di risultati: `search_title`, `get_media_gallery`, `get_all_interests`, `get_akas`, `get_trivia`, `get_reviews`, `get_parental_guide`, `get_quotes` e `get_filmography`.
  - Risolvere l'override per-chiamata sul limite configurato del tipo pertinente; rifiutare valori non positivi con `ValidationError`.
  - `_get_extended_title_info()` costruisce una query condivisa contenente più campi `first:`. Passargli i limiti effettivi per tutti i campi, applicando l'override solo al campo richiesto e i valori configurati agli altri. La cache deve distinguere le richieste con limiti effettivi diversi (includendoli nella chiave) oppure essere invalidata in modo equivalente, per non restituire risultati con un limite obsoleto o diverso.
  - `_get_extended_name_info()` applica separatamente `max_items_credits` alla filmography e deve considerare tale limite nella propria cache.
- **Invalidazione Cache LRU**:
  - Quando la configurazione globale viene alterata a runtime tramite `configure()`, setter o `set_locale()`, ripulire le cache LRU delle funzioni che dipendono dal locale/config. In ogni caso le cache dei dati GraphQL devono distinguere i limiti effettivi; gli override per-chiamata non devono contaminare risultati richiesti con limiti differenti.

---

## 4. Fasi di Implementazione

```mermaid
flowchart TD
    Fase1["1. Dipendenze (pyproject.toml)"] --> Fase2["2. Modulo imdbinfo/config.py (locale, limiti max_items_*, proxies)"]
    Fase2 --> Fase3["3. Refactor locale.py & proxy.py"]
    Fase3 --> Fase4["4. Integrazione services.py (trasporti proxy, max_items, cache)"]
    Fase4 --> Fase5["5. Esportazione in imdbinfo/__init__.py"]
    Fase5 --> Fase6["6. Suite di Test (config, locale, proxy, waf cache)"]
    Fase6 --> Fase7["7. Documentazione"]
```

### Fase 1: Dipendenze
- Aggiungere `"pydantic-settings"` all'elenco `dependencies` in `pyproject.toml`.
- Aggiornare la tabella dipendenze in `AGENTS.md`.

### Fase 2: Implementazione di `imdbinfo/config.py`
- Scrivere la classe `Settings` con validatori e vincoli per:
  - `locale`: normalizzazione e validazione su `SupportedLocale`.
  - Ogni limite `max_items_*`: `int`, `gt=0`, con un default corrispondente al valore attuale del relativo `first:` in `services.py`.
  - `proxies`: `Optional[Dict[str, str]]`, normalizzazione da stringa singola URL o dict.
- Creare l'istanza singleton `config` e gli helper `configure()` e `reset_config()`.

### Fase 3: Refactor di `imdbinfo/locale.py` e `imdbinfo/proxy.py`
- Collegare `set_locale()` e `get_locale()` all'oggetto `config.locale`.
- Collegare `set_proxy()` e `get_proxy()` all'oggetto `config.proxies`.
- Mantenere le funzioni interne `_retrieve_url_lang` e `_get_country_code_from_lang_locale` retrocompatibili.

### Fase 4: Aggiornamento di `imdbinfo/services.py`
- Integrare `config.proxies` in `request_handler()` e `request_graphql_url()`.
- Parametrizzare tutti i valori `first:` con i rispettivi `max_items_*`, mantenendo gli attuali valori predefiniti.
- Aggiungere gli override per-chiamata `max_items` alle funzioni pubbliche pertinenti e verificare la corretta composizione delle query GraphQL condivise.
- Gestire la pulizia della cache LRU quando la configurazione globale cambia.

### Fase 5: Esportazione Pubblica
- Aggiornare `imdbinfo/__init__.py` per esporre:
  - `config`, `configure`, `Settings`
  - `set_locale`, `get_locale`
  - `set_proxy`, `get_proxy`
  - Aggiornare `__all__` e le docstring del modulo.

### Fase 6: Test Suite
- Creare `tests/test_config.py`:
  - Valori di default (`locale == "en"`, tutti i `max_items_*` uguali ai rispettivi valori attuali in `services.py`, `proxies is None`).
  - Modifica diretta (`config.locale = "it"`, `config.proxies = {"http": "..."}`).
  - Helper `configure(locale="fr", max_items_search=10, max_items_akas=300, proxies="http://proxy:8080")`.
  - Validazione rigida: `config.locale = "invalido"`, un qualsiasi `config.max_items_* = 0` e `config.proxies = 123` sollevano `ValidationError`.
  - Precedenza variabili d'ambiente (`IMDBINFO_LOCALE`, le variabili `IMDBINFO_MAX_ITEMS_*`, `IMDBINFO_PROXIES`).
  - Verificare che ogni query usi il proprio limite configurato e che gli override per-chiamata prevalgano senza alterare i limiti degli altri campi della query condivisa.
  - Reset della configurazione con `reset_config()`.
- Aggiornare o portare `tests/test_proxy.py`:
  - Verificare che `set_proxy()` e `get_proxy()` funzionino in sinergia con `config.proxies`.
  - Allineare i casi di tipo non valido a `ValidationError`.
- Aggiornare `tests/test_locale.py` per allineare i test sui casi non validi a `ValidationError`.
- Aggiornare `tests/test_waf_cookie_cache.py` con gli stub arricchiti del parametro `proxies`.
- Eseguire tutti i test in Docker:
  ```bash
  docker run --rm -v $PWD:/app -w /app -e PYTHONPATH=/app imdbinfo:latest pytest
  ```

### Fase 7: Documentazione
- Aggiornare `README.md` spiegando:
  - Come impostare i proxy sia da codice (`config.proxies = ...`, `configure(proxies=...)`, `set_proxy(...)`) sia via environment variable (`IMDBINFO_PROXIES`).
  - Come configurare `locale` e i limiti distinti `max_items_*` (da config, da environment variable, da helper), con tabella dei tipi di query e dei default correnti.
- Aggiornare `docs/guides/locales-and-caching.md` e la documentazione API, documentando anche gli override `max_items` per-chiamata.
