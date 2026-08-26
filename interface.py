"""Componentes visuais do Vsy ytd."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

from engine import VERSION, VIDEO_QUALITIES, AUDIO_FORMATS

BG, CARD, FIELD = "#1b1a20", "#141318", "#201e26"
TEXT, MUTED, BORDER = "#f1edf7", "#aaa3b5", "#36313f"
PURPLE, CYAN = "#b478ef", "#67ddcb"


class Interface:
    def _label(self, parent, text=None, size=10, color=TEXT, bold=False, **kw):
        label = tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                         font=("Segoe UI", size, "bold" if bold else "normal"), anchor="w", **kw)
        return label

    def _card(self, parent):
        outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        inside = tk.Frame(outer, bg=CARD)
        inside.pack(fill="both", expand=True, padx=18, pady=12)
        return outer, inside

    def _style(self):
        self.configure(bg=BG)
        self.option_add("*Font", "{Segoe UI} 10")
        self.option_add("*TCombobox*Listbox.background", FIELD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", "#513272")
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TButton", background=BG, foreground=TEXT, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, padding=(15, 8), font=("Segoe UI", 10), focuscolor=PURPLE)
        s.map("TButton", background=[("disabled", BG), ("pressed", "#3b2b4c"), ("active", "#302937")],
              foreground=[("disabled", "#756e80")])
        s.configure("Accent.TButton", background="#8950be", bordercolor="#a566dc", foreground="white", font=("Segoe UI", 10, "bold"))
        s.map("Accent.TButton", background=[("disabled", "#39303f"), ("pressed", "#693991"), ("active", "#a365d8")])
        s.configure("Selected.TButton", background="#30223e", foreground="#d5afff", bordercolor=PURPLE)
        s.configure("TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=PURPLE, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, padding=8)
        s.configure("TCombobox", fieldbackground=FIELD, background=FIELD, foreground=TEXT, arrowcolor=PURPLE,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=7)
        s.map("TCombobox", fieldbackground=[("readonly", FIELD), ("disabled", CARD)],
              foreground=[("disabled", "#777080"), ("readonly", TEXT)], selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", TEXT)])
        for name in ("TCheckbutton", "TRadiobutton"):
            s.configure(name, background=CARD, foreground=TEXT, indicatorbackground=FIELD,
                        indicatorforeground=PURPLE, font=("Segoe UI", 10), padding=3)
            s.map(name, background=[("active", CARD)], foreground=[("disabled", "#756e80")],
                  indicatorbackground=[("selected", "#8950be")])
        s.configure("Horizontal.TProgressbar", troughcolor=FIELD, background=PURPLE,
                    lightcolor=PURPLE, darkcolor=PURPLE, bordercolor=FIELD, thickness=5)
        s.configure("Vertical.TScrollbar", background=BORDER, troughcolor=CARD, arrowcolor=MUTED,
                    bordercolor=CARD, lightcolor=BORDER, darkcolor=BORDER)
        s.map("Vertical.TScrollbar", background=[("active", "#685475"), ("!active", BORDER)])
        s.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])

    def _build_ui(self):
        self._style()
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True, padx=30, pady=22)
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=(0, 20))
        asset = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "assets" / "vstube-icon.png"
        if asset.exists():
            photo = tk.PhotoImage(file=str(asset))
            self.brand_icon = photo.subsample(max(1, photo.width() // 48))
            tk.Label(header, image=self.brand_icon, bg=BG).pack(side="left", padx=(0, 12))
        self._label(header, "Vsy ytd", 25, bold=True).pack(side="left")
        nav = tk.Frame(header, bg=BG)
        nav.pack(side="right", pady=8)
        self.nav = {}
        for key, title in (("downloads", "Downloads"), ("activity", "Atividade"), ("settings", "Preferências"), ("about", "Sobre")):
            button = ttk.Button(nav, text=title, command=lambda k=key: self.show_page(k))
            button.pack(side="left", padx=(6, 0))
            self.nav[key] = button

        self.page_host = tk.Frame(root, bg=BG)
        self.page_host.pack(fill="both", expand=True)
        self.page_host.rowconfigure(0, weight=1)
        self.page_host.columnconfigure(0, weight=1)
        self.pages = {}
        for key in self.nav:
            page = tk.Frame(self.page_host, bg=BG)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page
        self.inputs = []
        self._downloads_page()
        self._settings_page()
        self._activity_page()
        self._about_page()

        footer = tk.Frame(root, bg=BG)
        footer.pack(side="bottom", before=self.page_host, fill="x", pady=(18, 0))
        statusrow = tk.Frame(footer, bg=BG)
        statusrow.pack(fill="x")
        self._label(statusrow, textvariable=self.status, color=CYAN).pack(side="left")
        self._label(statusrow, textvariable=self.progress_text, color=MUTED).pack(side="right")
        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(9, 12))
        actions = tk.Frame(footer, bg=BG)
        actions.pack(fill="x")
        self._label(actions, "Seus arquivos, no seu computador.", 9, MUTED).pack(side="left")
        self.download_button = ttk.Button(actions, text="↓  Baixar agora", style="Accent.TButton", command=self.start_download)
        self.download_button.pack(side="right")
        self.cancel_button = ttk.Button(actions, text="Cancelar", state="disabled", command=self.cancel)
        self.cancel_button.pack(side="right", padx=8)
        ttk.Button(actions, text="Abrir pasta", command=self.open_folder).pack(side="right")
        self.show_page("downloads")

    def _intro(self, parent, title, subtitle):
        self._label(parent, title, 18, bold=True).pack(anchor="w")
        self._label(parent, subtitle, color=MUTED).pack(anchor="w", pady=(4, 17))

    def _downloads_page(self):
        page = self.pages["downloads"]
        self._intro(page, "O próximo download começa aqui", "Cole seus links, escolha o formato e deixe o resto com o Vsy.")
        # Pack the destination first at the bottom to preserve its space on short screens.
        outer, dest = self._card(page)
        outer.pack(side="bottom", fill="x", pady=(14, 0))
        desthead = tk.Frame(dest, bg=CARD)
        desthead.pack(fill="x", pady=(0, 8))
        self._label(desthead, "Pasta de destino", 11, bold=True).pack(side="left")
        self._label(desthead, "Salva automaticamente", 9, MUTED).pack(side="right")
        row = tk.Frame(dest, bg=CARD)
        row.pack(fill="x")
        choose = ttk.Button(row, text="Escolher…", command=self.choose_output)
        choose.pack(side="right", padx=(10, 0))
        entry = ttk.Entry(row, textvariable=self.output_dir)
        entry.pack(side="left", fill="x", expand=True)
        self.inputs.extend([choose, entry])

        columns = tk.Frame(page, bg=BG)
        columns.pack(fill="both", expand=True)
        columns.columnconfigure(0, weight=1)
        columns.columnconfigure(1, weight=0, minsize=310)
        columns.rowconfigure(0, weight=1)
        outer, links = self._card(columns)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        head = tk.Frame(links, bg=CARD)
        head.pack(fill="x")
        self._label(head, "Links para baixar", 12, bold=True).pack(side="left")
        self._label(head, textvariable=self.link_count, color=MUTED, size=9).pack(side="right")
        self._label(links, "YouTube e sites compatíveis · um link por linha", 9, MUTED).pack(anchor="w", pady=(5, 12))
        textrow = tk.Frame(links, bg=CARD)
        textrow.pack(fill="both", expand=True)
        self.urls = tk.Text(textrow, height=3, width=25, wrap="word", undo=True, font=("Segoe UI", 11),
                            bg=FIELD, fg=TEXT, insertbackground=PURPLE, selectbackground="#533670",
                            relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=PURPLE,
                            padx=12, pady=10)
        scroll = ttk.Scrollbar(textrow, command=self.urls.yview)
        self.urls.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.urls.pack(side="left", fill="both", expand=True)
        self.urls.bind("<<Modified>>", self._links_changed)
        controls = tk.Frame(links, bg=CARD)
        controls.pack(side="bottom", before=textrow, fill="x", pady=(12, 0))
        for title, callback in (("Colar links", self.paste), ("Limpar", self.clear_links)):
            button = ttk.Button(controls, text=title, command=callback)
            button.pack(side="left", padx=(0, 8))
            self.inputs.append(button)
        self.inputs.append(self.urls)

        side = tk.Frame(columns, bg=BG)
        side.grid(row=0, column=1, sticky="nsew")
        self.mode_cards = {}
        for mode, title, hint in (("video", "Vídeo", "Imagem e som, na qualidade escolhida."),
                                   ("audio", "Somente áudio", "Sua trilha em MP3 ou M4A.")):
            outer, inner = self._card(side)
            self.mode_cards[mode] = outer
            outer.pack(fill="both", expand=True, pady=(0, 10 if mode == "video" else 0))
            radio = ttk.Radiobutton(inner, text=title, variable=self.mode, value=mode, command=self._toggle_mode)
            radio.pack(anchor="w")
            self.inputs.append(radio)
            self._label(inner, hint, 9, MUTED).pack(anchor="w", pady=(4, 10))
            combo = ttk.Combobox(inner, textvariable=self.video_quality if mode == "video" else self.audio_format,
                                 values=VIDEO_QUALITIES if mode == "video" else AUDIO_FORMATS, state="readonly", width=23)
            combo.pack(fill="x")
            setattr(self, "video_combo" if mode == "video" else "audio_combo", combo)

    def _settings_page(self):
        page = self.pages["settings"]
        self._intro(page, "Do seu jeito", "Suas escolhas ficam salvas para a próxima vez.")
        outer, inner = self._card(page)
        outer.pack(fill="x")
        self._label(inner, "Comportamento dos downloads", 13, bold=True).pack(anchor="w", pady=(0, 12))
        for title, hint, var in (("Baixar a playlist inteira", "Desativado: baixa apenas o vídeo do link, quando disponível.", self.playlist),
                                 ("Abrir a pasta ao concluir", "Abre o destino quando o lote termina sem erros.", self.open_after)):
            check = ttk.Checkbutton(inner, text=title, variable=var)
            check.pack(anchor="w", pady=(8, 2))
            self._label(inner, hint, 10, MUTED).pack(anchor="w", padx=24, pady=(0, 12))
            self.inputs.append(check)
        self._label(inner, "Formato, qualidade e pasta também são lembrados automaticamente.", 10, color=CYAN).pack(anchor="w", pady=(16, 0))

    def _activity_page(self):
        page = self.pages["activity"]
        self._intro(page, "Atividade", "Acompanhe o download e a conversão sem abrir o terminal.")
        outer, inner = self._card(page)
        outer.pack(fill="both", expand=True)
        self.log = tk.Text(inner, height=8, wrap="word", state="disabled", bg=CARD, fg=MUTED,
                           font=("Consolas", 10), relief="flat", padx=6, pady=8)
        scroll = ttk.Scrollbar(inner, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)
        self._label(page, "Registro desta sessão. Não é salvo em disco.", 9, MUTED).pack(anchor="w", pady=(10, 0))

    def _about_page(self):
        page = self.pages["about"]
        self._intro(page, "Simples por fora. Completo por dentro.", "Vsy ytd  •  " + VERSION)
        outer, inner = self._card(page)
        outer.pack(fill="x")
        for title, description in (("Vídeo e áudio, sem complicação", "Interface local para yt-dlp, FFmpeg, FFprobe e Deno."),
                                    ("Sem conta ou telemetria", "Conecta-se aos sites dos links para buscar e baixar os arquivos."),
                                    ("Use com permissão", "Baixe conteúdo próprio, de domínio público ou autorizado pelo titular.")):
            self._label(inner, title, 12, bold=True).pack(anchor="w", pady=(8, 4))
            self._label(inner, description, color=MUTED).pack(anchor="w", pady=(0, 16))
        self._label(inner, "Mantido por @frsttw", color=PURPLE).pack(anchor="w", pady=8)

    def show_page(self, key):
        self.pages[key].tkraise()
        self.current_page = key
        for name, button in self.nav.items():
            button.configure(style="Selected.TButton" if name == key else "TButton")
