import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "./button";
import { cn } from "../utils";
import { motionPresets } from "../animations";

export const Modal = DialogPrimitive.Root;
export const ModalTrigger = DialogPrimitive.Trigger;
export const ModalClose = DialogPrimitive.Close;

export function ModalContent({ className, children, title, ...props }: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & { title: string }) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />
      <DialogPrimitive.Content asChild {...props}>
        <motion.div
          {...motionPresets.modal}
          className={cn("fixed left-1/2 top-1/2 z-50 w-[min(92vw,640px)] -translate-x-1/2 -translate-y-1/2 rounded-ds-xl border border-white/10 bg-elevated p-6 shadow-modal", className)}
        >
          <div className="mb-5 flex items-center justify-between gap-4">
            <DialogPrimitive.Title className="text-lg font-semibold text-white">{title}</DialogPrimitive.Title>
            <DialogPrimitive.Close asChild>
              <Button variant="ghost" size="icon" aria-label="Close modal">
                <X aria-hidden="true" className="h-4 w-4" />
              </Button>
            </DialogPrimitive.Close>
          </div>
          {children}
        </motion.div>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export const Drawer = DialogPrimitive.Root;
export const DrawerTrigger = DialogPrimitive.Trigger;

export function DrawerContent({ className, children, title, ...props }: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & { title: string }) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" />
      <DialogPrimitive.Content asChild {...props}>
        <motion.aside
          {...motionPresets.drawer}
          className={cn("fixed right-0 top-0 z-50 h-dvh w-[min(92vw,440px)] border-l border-white/10 bg-elevated p-6 shadow-modal", className)}
        >
          <div className="mb-5 flex items-center justify-between gap-4">
            <DialogPrimitive.Title className="text-lg font-semibold text-white">{title}</DialogPrimitive.Title>
            <DialogPrimitive.Close asChild>
              <Button variant="ghost" size="icon" aria-label="Close drawer">
                <X aria-hidden="true" className="h-4 w-4" />
              </Button>
            </DialogPrimitive.Close>
          </div>
          {children}
        </motion.aside>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}
