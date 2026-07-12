import { useMemo, useState } from "react";
import { Command, Search } from "lucide-react";
import { Modal, ModalContent, ModalTrigger } from "./dialog";
import { Button } from "./button";
import { Input } from "./input";
import { cn } from "../utils";
import { useKeyboardShortcut } from "../hooks";

export type CommandAction = {
  id: string;
  label: string;
  description?: string;
  group?: string;
  onSelect: () => void;
};

export function CommandPalette({ actions }: { actions: CommandAction[] }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  useKeyboardShortcut(["meta", "k"], () => setOpen(true));
  useKeyboardShortcut(["ctrl", "k"], () => setOpen(true));

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return actions;
    return actions.filter((action) => `${action.label} ${action.description ?? ""} ${action.group ?? ""}`.toLowerCase().includes(q));
  }, [actions, query]);

  return (
    <Modal open={open} onOpenChange={setOpen}>
      <ModalTrigger asChild>
        <Button variant="outline">
          <Command aria-hidden="true" className="h-4 w-4" />
          Command
        </Button>
      </ModalTrigger>
      <ModalContent title="Command Palette">
        <div className="relative mb-4">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} className="pl-9" placeholder="Search commands..." />
        </div>
        <div role="listbox" aria-label="Commands" className="max-h-[420px] overflow-y-auto">
          {filtered.map((action) => (
            <button
              key={action.id}
              type="button"
              className={cn("flex w-full flex-col rounded-ds px-3 py-3 text-left outline-none transition-colors hover:bg-white/[0.05] focus:bg-white/[0.05]")}
              onClick={() => {
                action.onSelect();
                setOpen(false);
              }}
            >
              <span className="text-sm font-medium text-white">{action.label}</span>
              {action.description ? <span className="mt-1 text-xs text-slate-400">{action.description}</span> : null}
            </button>
          ))}
        </div>
      </ModalContent>
    </Modal>
  );
}
