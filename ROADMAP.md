# Tray-Vision — Roadmap de Melhorias Futuras

> **Status atual:** v2.0 funcional — câmera, YOLO em thread, grid 4×3, alertas NG, QSS Light V2.
> As ideias abaixo são organizadas por impacto e esforço.

---

## Fase A — Quick Wins *(baixo esforço, alto impacto)*

### A1. ROI Interativo com Mouse
**O que é:** O usuário arrasta um retângulo sobre o frame da câmera para definir a área exata da bandeja.

**Como implementar:**
- Subclassar `QLabel` em `roi_dialog.py` → sobrescrever `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`
- Armazenar ponto inicial e final → desenhar `QRect` com `QPainter` em tempo real
- Salvar coordenadas normalizadas `(x, y, w, h)` em `config/settings.json`
- No `DetectorWorker`, aplicar crop no frame antes de passar ao YOLO: `frame = frame[y1:y2, x1:x2]`

```python
# roi_label.py (novo widget)
class ROILabel(QLabel):
    roi_defined = Signal(QRect)
    
    def mousePressEvent(self, e): self._start = e.pos()
    def mouseMoveEvent(self, e):  self._end = e.pos(); self.update()
    def mouseReleaseEvent(self, e):
        self.roi_defined.emit(QRect(self._start, self._end).normalized())
    def paintEvent(self, e):
        super().paintEvent(e)
        # draw live rectangle
```

**Esforço:** ~3h | **Impacto:** ⭐⭐⭐⭐⭐

---

### A2. Alertas Sonoros Customizados
**O que é:** Som diferente para NG vs OK vs sessão completa.

**Como implementar:**
- Usar `PySide6.QtMultimedia.QSoundEffect` (já incluso no PySide6)
- Adicionar `sounds/alert_ng.wav` e `sounds/alert_ok.wav` em `resources/sounds/`
- No `AlertManager`, trocar `QApplication.beep()` por:

```python
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

self.sound_ng = QSoundEffect()
self.sound_ng.setSource(QUrl.fromLocalFile("resources/sounds/alert_ng.wav"))
self.sound_ng.setVolume(0.8)
self.sound_ng.play()
```

- Na `SettingsDialog`, adicionar `QFileDialog` para escolher arquivo WAV

**Esforço:** ~2h | **Impacto:** ⭐⭐⭐⭐

---

### A3. Captura de Imagem com Timestamp
**O que é:** Botão 📷 na toolbar da câmera salva o frame atual com overlay.

**Como implementar:**
- O botão 📷 já existe no `CameraPanel` (toolbar inferior)
- Conectar ao slot no `MainWindow`:

```python
def capture_snapshot(self):
    if self.camera_panel.current_frame is None: return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"captures/snapshot_{ts}.jpg"
    os.makedirs("captures", exist_ok=True)
    cv2.imwrite(path, self.camera_panel.current_frame)
    # Exibir QMessageBox de confirmação
```

**Esforço:** ~1h | **Impacto:** ⭐⭐⭐

---

## Fase B — Persistência e Histórico *(médio esforço, alto valor)*

### B1. Banco de Dados de Inspeções (SQLite)
**O que é:** Cada inspeção completada é salva localmente com resultados, modelo usado, timestamp e imagem.

**Como implementar:**
- Criar `app/core/database.py` com `sqlite3`
- Schema:

```sql
CREATE TABLE inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    model_name TEXT,
    ok_count INTEGER,
    ng_count INTEGER,
    na_count INTEGER,
    result TEXT,       -- "PASS" | "FAIL"
    image_path TEXT    -- path to saved snapshot
);

CREATE TABLE slot_details (
    inspection_id INTEGER,
    slot_index INTEGER,
    status TEXT,
    confidence REAL,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);
```

- No `MainWindow`, ao pressionar "Nova Inspeção", salvar automaticamente no DB
- `DatabaseManager` como singleton com métodos `save_inspection()`, `get_history()`

**Esforço:** ~4h | **Impacto:** ⭐⭐⭐⭐⭐

---

### B2. Dashboard de Histórico
**O que é:** Painel lateral ou aba separada mostrando estatísticas de inspeções anteriores.

**Depende de:** B1 (banco de dados)

**Como implementar:**
- Novo painel `app/ui/panels/history_panel.py`
- `QTableWidget` com colunas: Data/Hora | Modelo | OK | NG | NA | Resultado
- Gráfico de pizza ou barra com `matplotlib` embarcado em `FigureCanvasQTAgg`:

```python
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
```

- Filtros por período (hoje, semana, mês) com `QDateEdit`
- Modo de acesso: novo botão "📊 Histórico" na sidebar

**Esforço:** ~6h | **Impacto:** ⭐⭐⭐⭐⭐

---

### B3. Exportar Relatório (PDF/Excel)
**O que é:** Gerar relatório da sessão atual ou do histórico em PDF ou Excel.

**Como implementar:**
- **PDF:** usar `reportlab` (`pip install reportlab`)
- **Excel:** usar `openpyxl` (`pip install openpyxl`)
- Botão "💾 Exportar" na `ControlPanel` já existe (placeholder)

```python
# report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Image

def export_pdf(inspection_data, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    # Adicionar tabela de resultados, imagem da inspeção, logo
```

**Esforço:** ~4h | **Impacto:** ⭐⭐⭐⭐

---

## Fase C — Configurações e Usabilidade

### C1. Configurações Persistidas (settings.json completo)
**O que é:** Todas as configurações do usuário são salvas entre sessões.

**Como implementar:**
- Criar `app/config/config_manager.py`:

```python
class ConfigManager:
    def __init__(self, path="app/config/settings.json"):
        self.path = path
        self.data = self._load()
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self._save()
```

- Salvar: câmera selecionada, modelo selecionado, threshold, tamanho da janela, ROI
- Restaurar no startup: `QTimer.singleShot(0, self._restore_settings)`

**Esforço:** ~2h | **Impacto:** ⭐⭐⭐⭐

---

### C2. Sistema de Login por Operador
**O que é:** Tela de login simples para identificar o operador. O nome aparece nos logs e relatórios.

**Como implementar:**
- `app/ui/dialogs/login_dialog.py` com `QLineEdit` para nome/matrícula
- Mostrar antes da `MainWindow` ou ao iniciar inspeção
- Armazenar `operator_name` no `ConfigManager` e incluir em cada registro do DB

```python
# main.py — antes de window.show():
login = LoginDialog()
if login.exec() == QDialog.Accepted:
    window.set_operator(login.operator_name)
```

**Esforço:** ~2h | **Impacto:** ⭐⭐⭐

---

### C3. Modo Fullscreen para Chão de Fábrica
**O que é:** Tecla F11 alterna para fullscreen ocultar a barra de título.

**Como implementar:**
```python
# main_window.py
def keyPressEvent(self, event):
    if event.key() == Qt.Key_F11:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
```

- Esconder o `HeaderBar` customizado em fullscreen e mostrar só o status mínimo
- Aumentar tamanho dos botões em fullscreen (`QPushButton.primary { min-height: 64px; }`)

**Esforço:** ~1h | **Impacto:** ⭐⭐⭐

---

## Fase D — Features Avançadas

### D1. Suporte a Múltiplos Modelos por Produto
**O que é:** Diferentes produtos têm diferentes modelos `.pt`. O usuário seleciona o produto e o modelo correto é carregado automaticamente.

**Como implementar:**
- Novo conceito: `ProductProfile` — mapeia produto → modelo + configurações
- `app/config/profiles.json`:

```json
{
  "Produto A": { "model": "models/produto_a.pt", "grid": "4x3", "conf": 0.85 },
  "Produto B": { "model": "models/produto_b.pt", "grid": "3x3", "conf": 0.90 }
}
```

- Dropdown de "Produto" na `ControlPanel` que carrega automaticamente modelo + threshold

**Esforço:** ~3h | **Impacto:** ⭐⭐⭐⭐⭐

---

### D2. Monitor de Performance em Tempo Real
**O que é:** Gráfico de linha mostrando FPS e latência de inference ao longo do tempo.

**Como implementar:**
- `app/ui/widgets/perf_chart.py` com `matplotlib` embarcado
- `collections.deque(maxlen=60)` para manter últimos 60 pontos
- Atualizar a cada segundo via `QTimer`

**Esforço:** ~3h | **Impacto:** ⭐⭐

---

### D3. Suporte a Câmera IP (RTSP/HTTP)
**O que é:** Conectar a câmeras industriais ou IP via URL em vez de índice USB.

**Como implementar:**
- Na `SettingsDialog`, adicionar campo `QLineEdit` para URL RTSP
- No `CameraWorker`, aceitar string como `camera_id`:

```python
# Já suportado! camera_id: int | str = 0
cap = cv2.VideoCapture("rtsp://192.168.1.100:554/stream")
```

- Adicionar botão "Câmera IP" que abre `QInputDialog` para digitar a URL
- Salvar URL no `settings.json`

**Esforço:** ~2h | **Impacto:** ⭐⭐⭐⭐

---

## Visão Geral de Prioridades

| Feature | Fase | Esforço | Impacto | Dependências |
|---------|------|---------|---------|--------------|
| ROI Interativo | A1 | 3h | ⭐⭐⭐⭐⭐ | — |
| Alertas Sonoros | A2 | 2h | ⭐⭐⭐⭐ | — |
| Captura de Imagem | A3 | 1h | ⭐⭐⭐ | — |
| SQLite — Banco de Dados | B1 | 4h | ⭐⭐⭐⭐⭐ | — |
| Dashboard de Histórico | B2 | 6h | ⭐⭐⭐⭐⭐ | B1 |
| Exportar Relatório | B3 | 4h | ⭐⭐⭐⭐ | B1 |
| Configurações Persistidas | C1 | 2h | ⭐⭐⭐⭐ | — |
| Login por Operador | C2 | 2h | ⭐⭐⭐ | C1 |
| Fullscreen F11 | C3 | 1h | ⭐⭐⭐ | — |
| Perfis por Produto | D1 | 3h | ⭐⭐⭐⭐⭐ | C1 |
| Monitor de Performance | D2 | 3h | ⭐⭐ | — |
| Câmera IP (RTSP) | D3 | 2h | ⭐⭐⭐⭐ | — |

---

## Sequência Recomendada

```
Fase A (Quick Wins)
  A3 Captura → A2 Sons → A1 ROI
        ↓
Fase C (Fundação)  
  C1 Settings → C3 Fullscreen → C2 Login
        ↓
Fase B (Dados)
  B1 SQLite → B3 Export → B2 Dashboard
        ↓
Fase D (Avançado)
  D3 Câmera IP → D1 Perfis → D2 Performance
```

> [!TIP]
> **Por onde começar:** A3 (captura de imagem) + C1 (settings.json) são as duas features de maior custo-benefício — baixo esforço, e desbloqueiam quase todas as outras.
