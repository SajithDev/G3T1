from __future__ import annotations

import base64
import importlib
from pathlib import Path
from time import perf_counter
import tkinter as tk    
from tkinter import font as tkfont
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

from aes import AES128
from rsa import rsa_decrypt, rsa_encrypt
from vigenere import vigenere_decrypt, vigenere_encrypt


triple_des_module = importlib.import_module("3des")
decrypt_3des = triple_des_module.decrypt_3des
encrypt_3des = triple_des_module.encrypt_3des


MAX_DISPLAY_CHARS = 12000
DISPLAY_HEAD_CHARS = 8000
DISPLAY_TAIL_CHARS = 3000


class CryptoGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.colors = {
            "bg": "#08111f",
            "panel": "#0f1b2d",
            "panel_alt": "#15253c",
            "input": "#0b1627",
            "border": "#22385a",
            "accent": "#49d6ff",
            "accent_hover": "#7ae4ff",
            "text": "#f3f7ff",
            "muted": "#9db1cc",
            "success": "#7ae0a5",
            "danger": "#ff8a8a",
            "warning": "#ffbf69",
            "info": "#7eb6ff",
        }

        self.root.title("G3T1 Crypto GUI")
        self.root.geometry("940x680")
        self.root.minsize(820, 620)
        self.root.configure(bg=self.colors["bg"])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        self.style = ttk.Style(self.root)
        self._configure_styles()

        self.algorithm_var = tk.StringVar(value="AES")
        self.operation_var = tk.StringVar(value="Encrypt")
        self.input_mode_var = tk.StringVar(value="Text")
        self.file_path_var = tk.StringVar()
        self.hex_mode_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Idle.")
        self.stats_var = tk.StringVar(value="Time: -- | Size: --")
        self.input_hint_var = tk.StringVar()

        self.key_entries: dict[str, ttk.Entry] = {}
        self.current_result: bytes | str | None = None
        self.current_display_kind = "text"
        self.current_save_kind = "text"
        self.current_save_text = ""
        self.current_save_bytes = b""
        self.current_display_text = ""
        self.current_visible_display_text = ""
        self.display_was_truncated = False

        self._build_ui()
        self.on_algorithm_change()
        self.update_input_hint()
        self.set_status("Idle.", "gray")

    def _configure_styles(self) -> None:
        self.style.theme_use("clam")

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family="Cascadia Code", size=10)

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family="Cascadia Code", size=10)

        self.root.option_add("*TCombobox*Listbox*Background", self.colors["panel"])
        self.root.option_add("*TCombobox*Listbox*Foreground", self.colors["text"])
        self.root.option_add("*TCombobox*Listbox*selectBackground", self.colors["accent"])
        self.root.option_add("*TCombobox*Listbox*selectForeground", self.colors["bg"])

        self.style.configure("App.TFrame", background=self.colors["bg"])
        self.style.configure("Card.TFrame", background=self.colors["panel"])
        self.style.configure(
            "HeroTitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 20),
        )
        self.style.configure(
            "HeroSubtitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "CardTitle.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 11),
        )
        self.style.configure(
            "CardDescription.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Field.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 10),
        )
        self.style.configure(
            "Muted.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Stats.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Cascadia Code", 10),
        )
        self.style.configure(
            "Primary.TButton",
            background=self.colors["accent"],
            foreground=self.colors["bg"],
            borderwidth=0,
            focusthickness=0,
            focuscolor=self.colors["accent"],
            padding=(16, 10),
            font=("Segoe UI Semibold", 10),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.colors["accent_hover"]), ("pressed", self.colors["accent"])],
            foreground=[("disabled", self.colors["muted"])],
        )
        self.style.configure(
            "Secondary.TButton",
            background=self.colors["panel_alt"],
            foreground=self.colors["text"],
            borderwidth=0,
            focusthickness=0,
            focuscolor=self.colors["panel_alt"],
            padding=(16, 10),
            font=("Segoe UI Semibold", 10),
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#1b3050"), ("pressed", self.colors["panel_alt"])],
        )
        self.style.configure(
            "Scroll.Vertical.TScrollbar",
            background=self.colors["panel_alt"],
            troughcolor=self.colors["bg"],
            bordercolor=self.colors["bg"],
            arrowcolor=self.colors["accent"],
            darkcolor=self.colors["panel_alt"],
            lightcolor=self.colors["panel_alt"],
        )
        self.style.configure(
            "Modern.TEntry",
            fieldbackground=self.colors["input"],
            background=self.colors["input"],
            foreground=self.colors["text"],
            insertcolor=self.colors["text"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            padding=8,
        )
        self.style.map(
            "Modern.TEntry",
            fieldbackground=[("readonly", self.colors["input"])],
            foreground=[("readonly", self.colors["text"])],
            bordercolor=[("focus", self.colors["accent"])],
            lightcolor=[("focus", self.colors["accent"])],
            darkcolor=[("focus", self.colors["accent"])],
        )
        self.style.configure(
            "Modern.TCombobox",
            fieldbackground=self.colors["input"],
            background=self.colors["input"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["accent"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            padding=6,
        )
        self.style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", self.colors["input"])],
            foreground=[("readonly", self.colors["text"])],
            bordercolor=[("focus", self.colors["accent"])],
            lightcolor=[("focus", self.colors["accent"])],
            darkcolor=[("focus", self.colors["accent"])],
            arrowcolor=[("active", self.colors["accent_hover"])],
        )
        self.style.configure(
            "Card.TRadiobutton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        self.style.map(
            "Card.TRadiobutton",
            background=[("active", self.colors["panel"])],
            foreground=[("active", self.colors["accent"]), ("selected", self.colors["accent"])],
        )
        self.style.configure(
            "Card.TCheckbutton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        self.style.map(
            "Card.TCheckbutton",
            background=[("active", self.colors["panel"])],
            foreground=[("active", self.colors["accent"]), ("selected", self.colors["accent"])],
        )

    def _create_card(
        self,
        parent: ttk.Frame,
        row: int,
        title: str,
        description: str,
        *,
        expand: bool = False,
    ) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(card, text=description, style="CardDescription.TLabel").grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        content = ttk.Frame(card, style="Card.TFrame")
        content.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        content.columnconfigure(0, weight=1)

        if expand:
            card.rowconfigure(2, weight=1)

        return content

    def _style_text_widget(self, widget: ScrolledText, *, height: int) -> None:
        widget.configure(
            height=height,
            font=("Cascadia Code", 10),
            background=self.colors["input"],
            foreground=self.colors["text"],
            insertbackground=self.colors["text"],
            selectbackground="#204a74",
            selectforeground=self.colors["text"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            padx=14,
            pady=14,
        )
        widget.vbar.configure(
            background=self.colors["panel_alt"],
            activebackground=self.colors["accent"],
            troughcolor=self.colors["bg"],
            borderwidth=0,
            relief=tk.FLAT,
        )

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            shell,
            background=self.colors["bg"],
            highlightthickness=0,
            borderwidth=0,
            yscrollincrement=16,
        )
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            shell,
            orient="vertical",
            command=canvas.yview,
            style="Scroll.Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        outer = ttk.Frame(canvas, style="App.TFrame", padding=12)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(5, weight=1)
        self.scroll_window = canvas.create_window((0, 0), window=outer, anchor="nw")
        self.scroll_canvas = canvas
        self.scroll_content = outer

        outer.bind("<Configure>", self._sync_scroll_region)
        canvas.bind("<Configure>", self._on_canvas_resize)
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        header = ttk.Frame(outer, style="App.TFrame", padding=(0, 0, 0, 4))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="G3T1 Crypto GUI",
            style="HeroTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Encrypt and decrypt text or files with a cleaner, faster-to-read control panel.",
            style="HeroSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        settings_frame = self._create_card(
            outer,
            1,
            "1. Configure the run",
            "Pick the algorithm and whether you want to encrypt or decrypt.",
        )
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Algorithm", style="Field.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.algorithm_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.algorithm_var,
            values=("AES", "3DES", "RSA", "Vigenere"),
            state="readonly",
            style="Modern.TCombobox",
        )
        self.algorithm_combo.grid(row=0, column=1, sticky="ew")
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        ttk.Label(settings_frame, text="Operation", style="Field.TLabel").grid(
            row=0, column=2, sticky="w", padx=(16, 10)
        )
        op_frame = ttk.Frame(settings_frame, style="Card.TFrame")
        op_frame.grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(
            op_frame,
            text="Encrypt",
            value="Encrypt",
            variable=self.operation_var,
            command=self.on_operation_change,
            style="Card.TRadiobutton",
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(
            op_frame,
            text="Decrypt",
            value="Decrypt",
            variable=self.operation_var,
            command=self.on_operation_change,
            style="Card.TRadiobutton",
        ).grid(row=0, column=1)

        input_frame = self._create_card(
            outer,
            2,
            "2. Add your input",
            "Work with text directly or point the tool at a file on disk.",
        )
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(2, weight=1)

        mode_frame = ttk.Frame(input_frame, style="Card.TFrame")
        mode_frame.grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            mode_frame,
            text="Text Input",
            value="Text",
            variable=self.input_mode_var,
            command=self.on_input_mode_change,
            style="Card.TRadiobutton",
        ).grid(row=0, column=0, padx=(0, 10))
        self.file_radio = ttk.Radiobutton(
            mode_frame,
            text="File Upload",
            value="File",
            variable=self.input_mode_var,
            command=self.on_input_mode_change,
            style="Card.TRadiobutton",
        )
        self.file_radio.grid(row=0, column=1)

        ttk.Label(
            input_frame,
            textvariable=self.input_hint_var,
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(10, 10))

        self.input_stack = ttk.Frame(input_frame, style="Card.TFrame")
        self.input_stack.grid(row=2, column=0, sticky="nsew")
        self.input_stack.columnconfigure(0, weight=1)
        self.input_stack.rowconfigure(0, weight=1)

        self.text_input = ScrolledText(self.input_stack, wrap=tk.WORD, height=8)
        self.text_input.grid(row=0, column=0, sticky="nsew")
        self._style_text_widget(self.text_input, height=5)

        self.file_input_frame = ttk.Frame(self.input_stack, style="Card.TFrame")
        self.file_input_frame.grid(row=0, column=0, sticky="ew")
        self.file_input_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.file_input_frame,
            text="Browse...",
            command=self.browse_file,
            style="Secondary.TButton",
        ).grid(
            row=0, column=0, padx=(0, 10)
        )
        ttk.Entry(
            self.file_input_frame,
            textvariable=self.file_path_var,
            state="readonly",
            style="Modern.TEntry",
        ).grid(row=0, column=1, sticky="ew")

        self.key_frame = self._create_card(
            outer,
            3,
            "3. Configure the key",
            "Each algorithm exposes only the fields it needs for the current operation.",
        )
        self.key_frame.columnconfigure(0, weight=1)

        self.key_container = ttk.Frame(self.key_frame, style="Card.TFrame")
        self.key_container.grid(row=0, column=0, sticky="ew")
        self.key_container.columnconfigure(0, weight=1)

        action_frame = ttk.Frame(outer, style="App.TFrame")
        action_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)

        ttk.Button(action_frame, text="Run", command=self.on_run_clicked, style="Primary.TButton").grid(
            row=0, column=0, sticky="e", padx=(0, 6)
        )
        ttk.Button(
            action_frame,
            text="Clear All",
            command=self.clear_all,
            style="Secondary.TButton",
        ).grid(
            row=0, column=1, sticky="w", padx=(6, 0)
        )

        output_frame = self._create_card(
            outer,
            5,
            "4. Review the output",
            "Copy, save, or switch between Base64 and hex when binary data is involved.",
            expand=True,
        )
        output_frame.grid_configure(sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        output_frame.rowconfigure(0, weight=0)

        toolbar = ttk.Frame(output_frame, style="Card.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        toolbar.columnconfigure(2, weight=1)

        ttk.Button(
            toolbar,
            text="Copy to Clipboard",
            command=self.copy_output,
            style="Secondary.TButton",
        ).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(
            toolbar,
            text="Save to File...",
            command=self.save_output_to_file,
            style="Secondary.TButton",
        ).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Checkbutton(
            toolbar,
            text="Display / parse hex",
            variable=self.hex_mode_var,
            command=self.on_binary_format_change,
            style="Card.TCheckbutton",
        ).grid(row=0, column=2, sticky="w")

        ttk.Label(toolbar, textvariable=self.stats_var, style="Stats.TLabel").grid(
            row=0, column=3, sticky="e"
        )

        output_surface = tk.Frame(
            output_frame,
            bg=self.colors["input"],
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
        )
        output_surface.grid(row=1, column=0, sticky="nsew")
        output_surface.grid_columnconfigure(0, weight=1)
        output_surface.grid_rowconfigure(1, weight=1)
        output_surface.grid_propagate(False)
        output_surface.configure(height=150)

        tk.Label(
            output_surface,
            text="Output Preview",
            bg=self.colors["input"],
            fg=self.colors["muted"],
            anchor="w",
            padx=14,
            pady=8,
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=0, sticky="ew")

        self.output_text = ScrolledText(output_surface, wrap=tk.WORD, height=14, state=tk.DISABLED)
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
        self._style_text_widget(self.output_text, height=5)

        status_frame = tk.Frame(
            self.root,
            bg=self.colors["panel_alt"],
            highlightthickness=1,
            highlightbackground=self.colors["border"],
        )
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            anchor="w",
            bg=self.colors["panel_alt"],
            fg=self.colors["muted"],
            padx=14,
            pady=8,
            font=("Segoe UI", 10),
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        self.on_input_mode_change()

    def _sync_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self.scroll_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.delta:
            self.scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def on_algorithm_change(self, _event: object | None = None) -> None:
        for child in self.key_container.winfo_children():
            child.destroy()
        self.key_entries.clear()

        algorithm = self.algorithm_var.get()

        if algorithm == "AES":
            self._render_single_key("AES Key (16 bytes)", "key")
            self.enable_file_input()
        elif algorithm == "3DES":
            labels = ("Key 1 (8 bytes)", "Key 2 (8 bytes)", "Key 3 (8 bytes)")
            key_frame = ttk.Frame(self.key_container, style="Card.TFrame")
            key_frame.grid(row=0, column=0, sticky="ew")
            for index, label in enumerate(labels):
                key_frame.columnconfigure(index, weight=1)
                field = ttk.Frame(key_frame, style="Card.TFrame")
                field.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 0))
                ttk.Label(field, text=label, style="Field.TLabel").grid(row=0, column=0, sticky="w")
                entry = ttk.Entry(field, style="Modern.TEntry")
                entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
                self.key_entries[f"key{index + 1}"] = entry
        elif algorithm == "RSA":
            self.enable_file_input()
            key_frame = ttk.Frame(self.key_container, style="Card.TFrame")
            key_frame.grid(row=0, column=0, sticky="ew")
            for index, (field_name, label) in enumerate(
                (
                    ("e", "Public Exponent e"),
                    ("d", "Private Exponent d"),
                    ("n", "Modulus n"),
                )
            ):
                key_frame.columnconfigure(index, weight=1)
                field = ttk.Frame(key_frame, style="Card.TFrame")
                field.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 0))
                ttk.Label(field, text=label, style="Field.TLabel").grid(row=0, column=0, sticky="w")
                entry = ttk.Entry(field, style="Modern.TEntry")
                entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
                self.key_entries[field_name] = entry
            ttk.Label(
                self.key_container,
                text="Encrypt uses e and n. Decrypt uses d and n. Decimal or 0x-prefixed values are accepted.",
                style="Muted.TLabel",
            ).grid(row=1, column=0, sticky="w", pady=(8, 0))
        else:
            self._render_single_key("Vigenere Key (Alphabetic)", "key")
            self.force_text_input_mode()

        self.update_input_hint()
        self.on_input_mode_change()

    def on_operation_change(self) -> None:
        self.update_input_hint()

    def on_input_mode_change(self) -> None:
        text_mode = self.input_mode_var.get() == "Text"
        if text_mode:
            self.file_input_frame.grid_remove()
            self.text_input.grid()
        else:
            self.text_input.grid_remove()
            self.file_input_frame.grid()
        self.update_input_hint()

    def on_binary_format_change(self) -> None:
        self.update_input_hint()
        self.refresh_output_display()

    def _render_single_key(self, label: str, name: str) -> None:
        ttk.Label(self.key_container, text=label, style="Field.TLabel").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(self.key_container, style="Modern.TEntry")
        entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.key_entries[name] = entry

    def enable_file_input(self) -> None:
        self.file_radio.configure(state=tk.NORMAL)

    def force_text_input_mode(self) -> None:
        self.file_radio.configure(state=tk.DISABLED)
        self.input_mode_var.set("Text")

    def update_input_hint(self) -> None:
        algorithm = self.algorithm_var.get()
        operation = self.operation_var.get()

        if algorithm == "Vigenere":
            self.input_hint_var.set("Vigenere works on text only.")
        elif self.input_mode_var.get() == "File":
            self.input_hint_var.set("File mode reads raw bytes from disk.")
        elif operation == "Encrypt":
            self.input_hint_var.set("Text mode is encoded as UTF-8 before encryption.")
        else:
            self.input_hint_var.set(
                "Paste ciphertext as Base64 or hex. The checkbox only changes how binary output is displayed."
            )

    def browse_file(self) -> None:
        path = filedialog.askopenfilename()
        if not path:
            return

        self.file_path_var.set(path)
        self.set_status(f"Selected file: {path}", "gray")

    def on_run_clicked(self) -> None:
        self.set_status("Processing...", "blue")

        try:
            self.validate_inputs()
            data = self.get_input_data()
            started = perf_counter()
            result = self.execute_backend(data)
            elapsed_ms = (perf_counter() - started) * 1000
            self.store_result_state(result)
            self.refresh_output_display()
            self.update_stats(elapsed_ms, result)

            if self.current_display_kind == "binary" and self.operation_var.get() == "Decrypt":
                self.set_status("Success: Decryption complete. Output is binary, so it is displayed as encoded text.", "orange")
            else:
                action = "Encryption" if self.operation_var.get() == "Encrypt" else "Decryption"
                self.set_status(f"Success: {action} complete.", "green")
        except Exception as exc:
            self.set_status(f"Error: {self.format_error_message(exc)}", "red")

    def validate_inputs(self) -> None:
        input_mode = self.input_mode_var.get()
        algorithm = self.algorithm_var.get()

        if input_mode == "Text":
            raw_text = self.text_input.get("1.0", "end-1c")
            if not raw_text.strip():
                raise ValueError("Input text cannot be empty")
        else:
            path = self.file_path_var.get().strip()
            if not path:
                raise ValueError("Please choose a file")
            if not Path(path).is_file():
                raise FileNotFoundError("Selected file does not exist")

        if algorithm == "AES":
            key = self.key_entries["key"].get()
            if len(key.encode("utf-8")) != 16:
                raise ValueError("AES key must be exactly 16 bytes")
        elif algorithm == "3DES":
            for index in range(1, 4):
                key = self.key_entries[f"key{index}"].get()
                if len(key.encode("utf-8")) != 8:
                    raise ValueError(f"3DES Key {index} must be exactly 8 bytes")
        elif algorithm == "Vigenere":
            key = self.key_entries["key"].get()
            if not key:
                raise ValueError("Vigenere key cannot be empty")
            if not key.isalpha():
                raise ValueError("Vigenere key must contain only letters")
        elif algorithm == "RSA":
            self.parse_rsa_fields()

    def get_input_data(self) -> bytes | str:
        algorithm = self.algorithm_var.get()
        operation = self.operation_var.get()
        input_mode = self.input_mode_var.get()

        if input_mode == "File":
            with open(self.file_path_var.get(), "rb") as source_file:
                return source_file.read()

        raw_text = self.text_input.get("1.0", "end-1c")
        if algorithm == "Vigenere":
            return raw_text

        if operation == "Encrypt":
            return raw_text.encode("utf-8")

        return self.parse_binary_text(raw_text)

    def parse_binary_text(self, value: str) -> bytes:
        cleaned = "".join(value.split())
        if not cleaned:
            raise ValueError("Ciphertext cannot be empty")

        parsers = []
        if self.hex_mode_var.get():
            parsers = [("hex", self._parse_hex), ("Base64", self._parse_base64)]
        else:
            parsers = [("Base64", self._parse_base64), ("hex", self._parse_hex)]

        for _name, parser in parsers:
            try:
                return parser(cleaned)
            except ValueError:
                continue

        raise ValueError("Could not parse ciphertext as Base64 or hex")

    def _parse_base64(self, value: str) -> bytes:
        try:
            return base64.b64decode(value, validate=True)
        except Exception as exc:
            raise ValueError("invalid Base64 input") from exc

    def _parse_hex(self, value: str) -> bytes:
        try:
            return bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("invalid hex input") from exc

    def execute_backend(self, data: bytes | str) -> bytes | str:
        algorithm = self.algorithm_var.get()
        encrypting = self.operation_var.get() == "Encrypt"

        if algorithm == "AES":
            key = self.key_entries["key"].get().encode("utf-8")
            cipher = AES128(key)
            return cipher.encrypt(data) if encrypting else cipher.decrypt(data)

        if algorithm == "3DES":
            key1 = self.key_entries["key1"].get().encode("utf-8")
            key2 = self.key_entries["key2"].get().encode("utf-8")
            key3 = self.key_entries["key3"].get().encode("utf-8")
            if encrypting:
                return encrypt_3des(data, key1, key2, key3)
            return decrypt_3des(data, key1, key2, key3)

        if algorithm == "RSA":
            rsa_values = self.parse_rsa_fields()
            if encrypting:
                return rsa_encrypt(data, rsa_values["e"], rsa_values["n"])
            return rsa_decrypt(data, rsa_values["d"], rsa_values["n"])

        key = self.key_entries["key"].get()
        if encrypting:
            return vigenere_encrypt(data, key)
        return vigenere_decrypt(data, key)

    def store_result_state(self, result: bytes | str) -> None:
        self.current_result = result

        if isinstance(result, str):
            self.current_display_kind = "text"
            self.current_save_kind = "text"
            self.current_save_text = result
            self.current_save_bytes = result.encode("utf-8")
            return

        if self.operation_var.get() == "Encrypt":
            self.current_display_kind = "binary"
            self.current_save_kind = "bytes"
            self.current_save_text = ""
            self.current_save_bytes = result
            return

        try:
            decoded = result.decode("utf-8")
        except UnicodeDecodeError:
            self.current_display_kind = "binary"
            self.current_save_kind = "bytes"
            self.current_save_text = ""
            self.current_save_bytes = result
        else:
            self.current_display_kind = "text"
            self.current_save_kind = "text"
            self.current_save_text = decoded
            self.current_save_bytes = result

    def refresh_output_display(self) -> None:
        if self.current_result is None:
            self.current_display_text = ""
            self.current_visible_display_text = ""
            self.display_was_truncated = False
            self.set_output_text("")
            return

        if self.current_display_kind == "text":
            if isinstance(self.current_result, str):
                self.current_display_text = self.current_result
            else:
                self.current_display_text = self.current_save_text
        else:
            self.current_display_text = self.format_binary(self.current_save_bytes)

        self.current_visible_display_text = self.truncate_display_text(self.current_display_text)
        self.set_output_text(self.current_visible_display_text)

    def truncate_display_text(self, value: str) -> str:
        if len(value) <= MAX_DISPLAY_CHARS:
            self.display_was_truncated = False
            return value

        self.display_was_truncated = True
        hidden_chars = len(value) - (DISPLAY_HEAD_CHARS + DISPLAY_TAIL_CHARS)
        return (
            f"{value[:DISPLAY_HEAD_CHARS]}\n\n"
            f"... output truncated in preview; {hidden_chars} characters hidden ...\n\n"
            f"{value[-DISPLAY_TAIL_CHARS:]}"
        )

    def format_binary(self, data: bytes) -> str:
        if self.hex_mode_var.get():
            return data.hex()
        return base64.b64encode(data).decode("utf-8")

    def set_output_text(self, value: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", value)
        self.output_text.configure(state=tk.DISABLED)

    def copy_output(self) -> None:
        if not self.current_display_text:
            self.set_status("Nothing to copy.", "red")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_display_text)
        if self.display_was_truncated:
            self.set_status("Full output copied to clipboard. The preview in the output box is truncated.", "green")
        else:
            self.set_status("Output copied to clipboard.", "green")

    def save_output_to_file(self) -> None:
        if self.current_result is None:
            self.set_status("Nothing to save.", "red")
            return

        path = filedialog.asksaveasfilename()
        if not path:
            return

        try:
            if self.current_save_kind == "text":
                with open(path, "w", encoding="utf-8") as output_file:
                    output_file.write(self.current_save_text)
            else:
                with open(path, "wb") as output_file:
                    output_file.write(self.current_save_bytes)
        except Exception as exc:
            self.set_status(f"Error: {exc}", "red")
            return

        self.set_status(f"File saved successfully to {path}", "green")

    def clear_all(self) -> None:
        self.text_input.delete("1.0", tk.END)
        self.file_path_var.set("")
        self.current_result = None
        self.current_display_text = ""
        self.current_visible_display_text = ""
        self.current_save_text = ""
        self.current_save_bytes = b""
        self.display_was_truncated = False
        self.set_output_text("")
        self.stats_var.set("Time: -- | Size: --")

        for entry in self.key_entries.values():
            entry.delete(0, tk.END)

        self.set_status("Cleared input, output, and keys.", "gray")

    def update_stats(self, elapsed_ms: float, result: bytes | str) -> None:
        size = len(result.encode("utf-8")) if isinstance(result, str) else len(result)
        self.stats_var.set(f"Time: {elapsed_ms:.2f} ms | Size: {size} bytes")

    def parse_rsa_fields(self) -> dict[str, int]:
        encrypting = self.operation_var.get() == "Encrypt"
        required_fields = ("e", "n") if encrypting else ("d", "n")
        values: dict[str, int] = {}

        for field_name, label in (
            ("e", "RSA exponent e"),
            ("d", "RSA exponent d"),
            ("n", "RSA modulus n"),
        ):
            raw_value = self.key_entries[field_name].get().strip()

            if not raw_value:
                if field_name in required_fields:
                    raise ValueError(f"{label} is required")
                continue

            try:
                parsed_value = int(raw_value, 0)
            except ValueError as exc:
                raise ValueError(f"{label} must be a valid integer") from exc

            if parsed_value <= 0:
                raise ValueError(f"{label} must be greater than zero")

            values[field_name] = parsed_value

        if "n" in values and values["n"] <= 1:
            raise ValueError("RSA modulus n must be greater than 1")

        return values

    def format_error_message(self, exc: Exception) -> str:
        algorithm = self.algorithm_var.get()
        decrypting = self.operation_var.get() == "Decrypt"
        message = str(exc)

        if decrypting and algorithm in {"AES", "3DES"}:
            if message == "Invalid padding":
                return "Decryption failed. The key is likely incorrect, or the ciphertext is corrupted."
            if message in {"Invalid padded data length", "Invalid ciphertext length", "Ciphertext must be multiple of 8 bytes"}:
                return "Decryption failed because the ciphertext size is invalid for the selected algorithm."

        return message

    def set_status(self, message: str, color: str) -> None:
        color_map = {
            "gray": "#5f6368",
            "green": "#1e8e3e",
            "red": "#c5221f",
            "blue": "#1a73e8",
            "orange": "#b06000",
        }
        self.status_var.set(message)
        self.status_label.configure(fg=color_map.get(color, color))


def main() -> None:
    root = tk.Tk()
    CryptoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
