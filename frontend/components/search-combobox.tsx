"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Search, X } from "lucide-react";

export type ComboOption = { id: string; label: string; secondary?: string };

type Props = {
  label: string;
  placeholder: string;
  emptyMessage: string;
  clearLabel: string;
  value: string;
  selectedLabel?: string;
  onChange: (id: string, option?: ComboOption) => void;
  fetchOptions: (query: string) => Promise<ComboOption[]>;
};

export function SearchCombobox({ label, placeholder, emptyMessage, clearLabel, value,
  selectedLabel, onChange, fetchOptions }: Props) {
  const inputId = useId();
  const listId = `${inputId}-list`;
  const fetchRef = useRef(fetchOptions);
  fetchRef.current = fetchOptions;
  const [text, setText] = useState(selectedLabel || "");
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState<ComboOption[]>([]);
  const [active, setActive] = useState(-1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (value && selectedLabel) setText(selectedLabel);
    if (!value && !open) setText("");
  }, [value, selectedLabel, open]);
  useEffect(() => {
    if (!open) return;
    let live = true;
    const timer = window.setTimeout(() => {
      setLoading(true);
      fetchRef.current(text).then((items) => {
        if (live) { setOptions(items); setActive(-1); }
      }).catch(() => { if (live) setOptions([]); })
        .finally(() => { if (live) setLoading(false); });
    }, 180);
    return () => { live = false; window.clearTimeout(timer); };
  }, [text, open]);

  function choose(option: ComboOption) {
    onChange(option.id, option);
    setText(option.label);
    setOpen(false);
  }
  return (
    <div className="field combo-field">
      <label htmlFor={inputId}>{label}</label>
      <div className="combo-input-wrap">
        <Search size={17} aria-hidden="true" />
        <input id={inputId} type="text" role="combobox" autoComplete="off"
          aria-autocomplete="list" aria-expanded={open} aria-controls={listId}
          aria-activedescendant={open && active >= 0 ? `${listId}-${active}` : undefined}
          placeholder={placeholder} value={text}
          onFocus={() => setOpen(true)}
          onBlur={() => setOpen(false)}
          onChange={(event) => { setText(event.target.value); onChange(""); setOpen(true); }}
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") { event.preventDefault(); setOpen(true); setActive((n) => Math.min(n + 1, options.length - 1)); }
            if (event.key === "ArrowUp") { event.preventDefault(); setActive((n) => Math.max(n - 1, 0)); }
            if (event.key === "Enter" && open && active >= 0 && options[active]) { event.preventDefault(); choose(options[active]); }
            if (event.key === "Escape") setOpen(false);
          }} />
        {value && <button type="button" className="combo-clear" aria-label={clearLabel}
          onMouseDown={(event) => event.preventDefault()}
          onClick={() => { onChange(""); setText(""); setOpen(true); }}><X size={16} /></button>}
      </div>
      {open && <div id={listId} role="listbox" className="combo-list">
        {options.map((option, index) => <div key={option.id} id={`${listId}-${index}`}
          role="option" aria-selected={index === active} className={`combo-option ${index === active ? "active" : ""}`}
          onMouseDown={(event) => event.preventDefault()} onClick={() => choose(option)}>
          <strong>{option.label}</strong>{option.secondary && <small>{option.secondary}</small>}
        </div>)}
        {!loading && options.length === 0 && <div className="combo-empty">{emptyMessage}</div>}
      </div>}
    </div>
  );
}
